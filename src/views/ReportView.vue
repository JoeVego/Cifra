<template>
  <div class="report-list">
    <a-table :data-source="report" :columns="columns" row-key="id" @change="onChange">
      <template #client_type="{ record }">
        <div>{{ record.client_type }}</div>
      </template>
      <template #status="{ record }">
        {{ record.status }}
      </template>
      <template #counter="{ record }">
        {{ record.counter }}
      </template>
    </a-table>

    <!-- Вторая таблица -->
    <a-table :data-source="timeReport" :columns="timeColumns" row-key="id" @change="onChange" style="margin-top: 40px;">
      <template #licPlate="{ record }">
        {{ record.licPlate }}
      </template>
      <template #time="{ record }">
        {{ record.time }}
      </template>
      <template #clint_type="{ record }">
        {{ record.clint_type }}
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import axios from 'axios';

const report = ref([]);
const timeReport = ref([]); // Данные для второй таблицы

const columns = computed(() => [
  {
    title: 'Тип клиента',
    dataIndex: 'client_type',
    slots: { customRender: 'client_type' },
  },
  {
    title: 'Тип заявки',
    dataIndex: 'status',
    slots: { customRender: 'status' },
  },
  {
    title: 'Количество',
    dataIndex: 'counter',
    slots: { customRender: 'counter' },
  },
]);

const timeColumns = [
  {
    title: 'Гос номер',
    dataIndex: 'licPlate',
    slots: { customRender: 'licPlate' },
  },
  {
    title: 'Время',
    dataIndex: 'time',
    slots: { customRender: 'time' },
  },
  {
    title: 'Тип клиента',
    dataIndex: 'client_type',
    slots: { customRender: 'client_type' },
  },
];

function onChange(pagination, filters, sorter) {
  //scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// см onMounted
const getReport = async () => {
  try {
    const response_report = await axios.get('http://localhost:5000/get-report');
    report.value = response_report.data.map(item => ({
        client_type: item.client_type,
        status: item.status,
        counter: item.counter
    }));
  } catch (error) {
    console.error('Error fetching results:', error);
  }
};

// Получение данных для второй таблицы
const getTimeReport = async () => {
  try {
    const response_time = await axios.get('http://localhost:5000/get-time-report');
    timeReport.value = response_time.data.map(item => ({
      licPlate: item.licPlate,
      time: item.time,
      client_type: item.client_type
    }));
  } catch (error) {
    console.error('Error fetching second report:', error);
  }
};

//Вызывается 1 раз при запуске
onMounted(() => {
  getReport();
  getTimeReport();
});
</script>

<style scoped>
.result-list {
  margin: 20px auto;
}
</style>