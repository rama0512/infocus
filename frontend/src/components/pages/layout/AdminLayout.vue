<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function logout() {
  localStorage.removeItem('token') // or sessionStorage
  router.push('/') // redirect to login
}

</script>

<template>
    <div class="admin-layout">
      
    <header class="header">
      <nav class="nav-links">
        <router-link to="/Admin/Dashboard">Home</router-link>
        <router-link to="/admin/users">Users</router-link>
        <router-link to="/Admin/summary">Search Summary</router-link>
        <!--<a href="#" @click="logout()">Logout</a>-->
        <router-link to="/" @click="logout()">logout</router-link>

      </nav>
    </header>
    <main class="content">
      <slot />
    </main>
    
  </div>

</template>

<style scoped>




.admin-layout {
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: 50vh;
}

/* Light brown header to complement dark brown theme */
.header {
  width: 100%;
  display:flex;
  justify-content: center;
  background-color: #a97c50; /* warm light brown */
  padding: 1rem;
  /*text-align: center;
  align-items: center;*/
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); /* subtle depth */
}

.nav-links {
  display: flex;
  justify-content: center;
  gap: 6rem; /* slightly reduced gap for balance */
}

/* Creamy white text with hover effect */
.nav-links a {
  color: #fdf6e3; /* creamy white */
  text-decoration: overline;
  font-weight: bold;
  font-size: 1rem;
  transition: color 0.5s ease-in-out;
}

.nav-links a:hover {
  color: #141103; /* lighter cream on hover */
}

.content {
  flex: 1;
  padding: 2rem;
  background-color: #1626da;
}
</style>