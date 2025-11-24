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
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import axios from 'axios';

const report = ref([]);

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

//Вызывается 1 раз при запуске
onMounted(() => {
  getReport();
});
</script>

<style scoped>
.result-list {
  margin: 20px auto;
}
</style>