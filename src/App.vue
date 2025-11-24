<script setup>
import { h, ref, watch } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import { useRouter } from 'vue-router';
import { MailOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons-vue';

const router = useRouter();

const current = ref(['start']);
const items = ref([
  {
    key: 'start',
    icon: () => h(SettingOutlined),
    label: 'Запуск',
    title: 'Запуск',
  },
  {
    key: 'results',
    icon: () => h(AppstoreOutlined),
    label: 'Результаты',
    title: 'Результаты',
  },
  {
    key: 'report',
    icon: () => h(MailOutlined),
    label: 'Отчет',
    title: 'Отчет',
  },
]);

watch(
  () => router.currentRoute.value,
  () => {
    current.value = [router.currentRoute.value.name];
  }
)
</script>

<template>
  <header>
    <img alt="Cifra Academy" class="logo" src="@/assets/cifra-logo.png" height="60" />
    <img alt="Programming Store" class="logo" src="@/assets/prosto-logo.svg" height="40" />
    <img alt="Zool.ai" class="logo" src="@/assets/zool-logo.svg" height="125" />
  </header>
  <a-menu v-model:selectedKeys="current" mode="horizontal" :items="items" @select="({ key }) => router.push(key)" />
  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 200px;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
  max-width: 150px;
  object-fit: contain;
}

nav {
  width: 100%;
  font-size: 18px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    justify-content: space-between;
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
