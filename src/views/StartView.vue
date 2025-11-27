<template>
  <div class="form-container">
    <!-- Форма для загрузки изображения и Function Name -->
    <a-form v-if="mode === 'photo'" :model="photoFormState" name="photoForm" layout="vertical">
      <a-form-item label="Загрузить изображение" name="imageFileList">
        <a-upload v-model:file-list="photoFormState.imageFileList" :customRequest="uploadAction" list-type="picture-card" :preview="false" maxCount="1">
          <div v-if="photoFormState.imageFileList.length < 1">
            <plus-outlined />
            <div style="margin-top: 8px;">Выберите файл</div>
          </div>
        </a-upload>
      </a-form-item>
    </a-form>

    <!-- Форма для ввода RTSP Link и Function Name -->
    <a-form v-else-if="mode === 'video'" :model="videoFormState" name="videoForm" layout="vertical">
      <a-form-item label="Источник (rtsp ссылка или путь к видео)" name="source">
        <a-input v-model:value="videoFormState.source" />
      </a-form-item>

      <!--<a-form-item label="Режим распознавания" name="functionName">
        <a-input v-model:value="videoFormState.functionName" />
      </a-form-item>-->

      <a-form-item  style="margin-bottom: 16px;">
        <select v-model="videoFormState.functionName" style="width: 100%; padding: 4px;
        background-color: #fff; border: 1px solid #d9d9d9; border-radius: 4px;">
            <option value="">-- Выберите камеру --</option>
            <option value="зона въезда">зона въезда</option>
            <option value="зона выезда">зона выезда</option>
        </select>
      </a-form-item>

      <a-form-item>
       <div style="display: flex; gap: 8px; margin: 0;">
            <a-button type="primary" @click="submitVideoForm">Начать запись</a-button>
            <a-button type="primary" @click="stopVideoForm">Остановить запись</a-button>
        </div>
      </a-form-item>
    </a-form>

    <a-result
      v-else
      status="success"
      title="Успешно"
      sub-title=" "
    >
      <template #extra>
        <a-button key="console" type="primary" @click="() => {
          router.push('/results');
          mode = 'video';
        }">Перейти в результаты</a-button>
        <a-button key="buy" @click="mode = 'video'">Вернуться</a-button>
      </template>
    </a-result>

    <div v-if="!showVideo" style="
        width: 100%;
        height: 20%;
        background-image: url('src/assets/99.png');
        background-size: cover;
        background-position: center;
        border-radius: 20px;
        border: 2px solid white;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #555;">
    </div>

    <img v-if="showVideo"
        src="http://localhost:5000/video_feed/1"
        alt="Ожидание начала записи..."
        style="max-width: 100%;
            max-height: 100%;
            margin: 0% 0% 0% 0%;
            border-radius: 20px;
            background-color: #ffffff;
            border: 2px solid white;">
  </div>
</template>

<script setup>
import { PlusOutlined } from '@ant-design/icons-vue';
import { reactive, ref} from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { UndoOutlined } from '@ant-design/icons-vue';
import { h } from 'vue';

const router = useRouter();

// Режим (по умолчанию выбрано "видео")
const mode = ref('video');

const image = ref(null);
let intervalId = null;

const imageParams = ref({
  width: 600,
  height: 400,
});

const videoFormState = reactive({
  source: '',
  functionName: ''
});

const showVideo = ref(false);

// Функция для переключения
function showVideoFunc() {
  showVideo.value = true;
}

// Функция для переключения
function stopVideoFunc() {
  showVideo.value = false;
}

const submitVideoForm = async () => {
  console.log('Source:', videoFormState.rtspLink);
  console.log('Function Name:', videoFormState.functionName);
  try {
    await axios.post('http://localhost:5000/start-detection', {
      source: videoFormState.source,
      function_name: videoFormState.functionName
    });
    mode.value = 'result';
    showVideoFunc()
  } catch (error) {
    console.error('Error uploading video:', error);
  }
};

const stopVideoForm = async () => {
  console.log('Source:', videoFormState.rtspLink);
  console.log('Function Name:', videoFormState.functionName);
  try {
    await axios.post('http://localhost:5000/stop-detection', {
      function_name: videoFormState.functionName
    });
    mode.value = 'result';
    stopVideoFunc()
  } catch (error) {
    console.error('Error uploading video:', error);
  }
};
function onClickImage(event) {
  activeCoordinates.value = [
    ...activeCoordinates.value,
    {
      x: event.offsetX - Number(image.value?.offsetTop),
      y: event.offsetY - Number(image.value?.offsetLeft),
      xn:
        (event.offsetX - Number(image.value?.offsetTop)) / Number(image.value?.offsetWidth),
      yn:
        (event.offsetY - Number(image.value?.offsetLeft)) / Number(image.value?.offsetHeight),
    },
  ];
  console.log(activeCoordinates.value);
}
</script>

<style scoped>
.form-container {
  margin: 20px auto;
  display: flex;
  flex-direction: column;
}

.image-annotation {
  width: fit-content;
  border: 1px solid #8686865c;
}

.image-annotation__marker {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.stream-image {
  width: auto;
  height: 450px;
  cursor: pointer;
}

.polygon {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #ff00ff5c;
}
</style>