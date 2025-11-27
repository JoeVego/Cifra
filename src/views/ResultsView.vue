<template>
  <div class="result-list">
    <a-table :data-source="results" :columns="columns" row-key="id" @change="onChange">
      <template #image="{ record }">
        <a-image
          :width="100"
          :src="record.image"
        />
      </template>
      <template #date="{ record }">
        {{ formatDate(record.date) }}
      </template>
      <template #source="{ record }">
        <div>{{ record.source }}</div>
      </template>
      <template #description="{ record }">
        {{ record.description }}
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import axios from 'axios';

const results = ref([]);

const columns = computed(() => [
  {
    title: 'Изображение',
    dataIndex: 'image',
    slots: { customRender: 'image' },
  },
  {
    title: 'Дата',
    dataIndex: 'date',
    slots: { customRender: 'date' },
  },
  {
    title: 'Зона',
    dataIndex: 'source',
    slots: { customRender: 'source' },
  },
  {
    title: 'Госномер ТС',
    dataIndex: 'description',
    slots: { customRender: 'description' },
  },
]);

//py - datetime.now
function formatDate(date) {
  return new Intl.DateTimeFormat('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
}

function onChange(pagination, filters, sorter) {
  //scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// см onMounted
const getResults = async () => {
  try {
    const response = await axios.get('http://localhost:5000/get-results');
    results.value = response.data.map(item => ({
        image: item.image,
        date: item.date,
        source: item.source,
        description: item.description,
    }));
  } catch (error) {
    console.error('Error fetching results:', error);
  }
};

//Вызывается 1 раз при запуске
onMounted(() => {
  getResults();
});
</script>

<style scoped>
.result-list {
  margin: 20px auto;
}
</style>