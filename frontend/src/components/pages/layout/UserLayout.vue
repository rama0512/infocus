<script setup>
import { useRouter,useRoute } from 'vue-router'

const router = useRouter();
const route = useRoute();
const id=route.params.id;

function logout() {
  localStorage.removeItem('token') 
  router.push('/') 
}
</script>

<template>
    <div class="user-layout">
    <header class="header">
      <nav class="nav-links">
        <router-link :to="`/user/dashboard/${id}`">Home</router-link>
        <!--<a href="" @click.prevent="logout">Logout</a>-->
        <router-link to="/" @click="logout()">logout</router-link>
      </nav>
      </header>
      <main class="content">
      <slot />
    </main>
    
  </div>
</template>

<style scoped>
.user-layout {
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Light brown header to complement dark brown theme */
.header {
  width: 100%;
  background-color: #a97c50; /* warm light brown */
  padding: 1rem;
  text-align: center;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); /* subtle depth */
}

.nav-links {
  display: flex;
  justify-content: center;
  gap: 6rem; /* slightly reduced gap for balance */
}

/* Creamy white text with hover effect */
.nav-links a,
.nav-links router-link {
  color: #fdf6e3; /* creamy white */
  text-decoration: none;
  font-weight: bold;
  font-size: 1rem;
  transition: color 0.2s ease-in-out;
}

.nav-links a:hover,
.nav-links router-link:hover {
  color: #fffbe6; /* lighter cream on hover */
}

.content {
  flex: 1;
  padding: 2rem;
  background-color: #fdf6e3;
}
</style>