<template>
  <div class="form-container">
    <!-- Свитчер для выбора режима Фото или Видео/Камера -->
    <!--<a-radio-group v-model:value="mode" button-style="solid" style="margin-bottom: 0px; width: 0%;">
       <a-radio-button value="video">Видео</a-radio-button>
    </a-radio-group>-->

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
            <option value="camera_in">зона въезда</option>
            <option value="camera_out">зона выезда</option>
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
      sub-title="Запущено распознавание гос номеров ТС"
    >
      <template #extra>
        <a-button key="console" type="primary" @click="() => {
          router.push('/results');
          mode = 'video';
        }">Перейти в результаты</a-button>
        <a-button key="buy" @click="mode = 'video'">Вернуться</a-button>
      </template>
    </a-result>
  </div>
</template>

<script setup>
import { PlusOutlined } from '@ant-design/icons-vue';
import { reactive, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { UndoOutlined } from '@ant-design/icons-vue';
import { h } from 'vue';

const router = useRouter();

// Режим (по умолчанию выбрано "видео")
const mode = ref('video');

const image = ref(null);

const imgPlaceholder =
    'iVBORw0KGgoAAAANSUhEUgAAARAAAAC5CAMAAADXsJC1AAAAS1BMVEX5+fmMjIyKior9/f34+PjAwMDe3t6Hh4e4uLiWlpby8vLr6+ujo6PU1NSPj4/v7++xsbGnp6fm5uba2tqrq6uamprHx8fPz8/Dw8PB1aGXAAAC2ElEQVR4nO3aW3OqMBSG4ZwgcjBoK9b//0t3FmCntlXDxW6nrPdxpiPWC/lmZSVAjAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAPC8av8Nu/9ie0VXXJr+ryXFWF3/61/19oo3PWFYm2VVAjrUvJ5kjsc861CkqktTYddoUU5CGBNMPKphr8hpORQDqzaq7ZdiNZAqlXGIxM11s1BeJNX9BUF/F10yUyV4jvbSpKI89JGgLxORDXFLEp1joCsfuSfhpOVksgbl9wnj4cNQUSns8dugKR43uZLGHpCmQ65/BtKMFoDCSvyad16NcT9teQlAXih6o/vHy9UvFvRmmF9C5f/L58OuHg69hd36sKxO9jSskebk84+G6M5+uBrkDOMeUlfH9zwrmdHqw9hvlDZYHUUiFu96lCzlbG0XKgKpDgd9G5cZCqWDprnnderaR01lgh+bA+7/NfP0goeaEefDuMeRQld1Q5y0wLEamP49jNC/lgTk76SlrGjK5ApkVqzsFX1o558s0f+IuVEZPsMmZ0BSLH0j72UhOj3Ck09VQdksg8ZjQGYrpmaqN95400kDmP1LzMg0lbINI14pRBTsQc4jWP5C7yf4WB+GoJIcV+F9M8YuSOaz9NO+oCycuOZZRIJ03vb5Nc4+gbMvm6pbm20c/sRV0geZZtT/H7OHIgo9wWURaIudyLQxLptAUi1y3iTh4yz2w+EP/+KFMqpEtRns7de2rXq+ghzjZ5TTpXSDs81KmYdt3ybHe6/H/4VQ0r1WCGD0NGnr48kCflzQeSI6jrOpjCJ3fbrxAz7R0yxhQ+29UQyKyXbR8lu6nUBGLtqWgjYrP1/SGL44P1x81aZPMbZhZ9LNvNLBuaZUvVdjfdTbx5q8rJ7eZNByLT7bp9qk9WcH/d9ztCHinZa/SnhVWJhHVfBwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARf4B5RoxAeWTQE0AAAAASUVORK5CYII=';

const imageBase64 = ref(imgPlaceholder);
const imageParams = ref({
  width: 600,
  height: 400,
});

// Состояния форм
const photoFormState = reactive({
  imageFileList: [],
  functionName: ''
});

const videoFormState = reactive({
  source: '',
  functionName: ''
});

const regionColor = ref({ r: 255, g: 105, b: 0 });
const regions = ref([]);
const activeCoordinates = ref([]);

const toBase64 = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
});

function uploadAction(event) {
  let file = photoFormState.imageFileList.find((item) => item.uid === event.file.uid);
  file.status = 'done';
}

// Обработчики отправки форм
const getFrame = async () => {
  console.log('RTSP Link:', videoFormState.rtspLink);
  console.log('Function Name:', videoFormState.functionName);
  try {
    const { imageInBase64, width, height } = await axios.post('http://localhost:5000/get-frame', {
      source: videoFormState.source,
    });
    imageParams.value = {
      width: width,
      height: height,
    };
    imageBase64.value = imageInBase64;

    mode.value = 'video2';
  } catch (error) {
    console.error('Error uploading video:', error);
  }
};
const submitVideoForm = async () => {
  console.log('Source:', videoFormState.rtspLink);
  console.log('Function Name:', videoFormState.functionName);
  try {
    await axios.post('http://localhost:5000/start-detection', {
      source: videoFormState.source,
      function_name: videoFormState.functionName
    });
    mode.value = 'result';
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
function polygonCoordinates() {
  let result = [];
  activeCoordinates.value.map((item) => {
    result.push(`${item.xn * 100}% ${item.yn * 100}%`);
  });
  return result.join(', ');
}
function deleteRegion(i) {
  regions.value.splice(i, 1);
}
function undo() {
  activeCoordinates.value = activeCoordinates.value.slice(0, -1);
}
function add() {
  if (activeCoordinates.value.length < 4) {
    return;
  }
  let result = {
    coordinates: activeCoordinates.value,
    color: regionColor.value,
  };
  regions.value.push(result);
  activeCoordinates.value = [];
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