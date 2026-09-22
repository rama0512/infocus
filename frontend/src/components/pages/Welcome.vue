<script setup>
import { ref,onBeforeMount } from 'vue'
import { useRouter } from 'vue-router'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
import { jwtDecode } from "jwt-decode";

function decode_token(token){  
try {
    const decoded = jwtDecode(token);
    const user_token={
        id: decoded.id,
        username: decoded.username,
        email: decoded.email
    }
    return user_token
} catch (error) {
    console.error("Invalid token:", error);
}
}


function handleCreateAccount() {
  router.push('/signup')  //  Navigate to Signup.vue
}
async function redirectDashboard() {
  
}
async function handleLogin() {
  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    });
    const data = await response.json();
    
    if (response.ok) {
      localStorage.setItem('token', data.access_token);     
      const user = decode_token(data.access_token);
      
      alert(`Welcome back, ${user.username}!`);
      router.push(`/user/Dashboard/${user.id}`); 
    } else {
      alert("Login failed: " + (data.detail || "Invalid Credentials"));
    }
  } catch (error) {
    console.error("Login error:", error);
    alert("Could not connect to the server.");
  }
}

</script>

<template>
  <div class="container">
    <h1>Login</h1>
    <form >   <!--on submitting a form the site reloads the page   v-on:submit.prevent="redirectDashboard"-->
      <div class="form-group">
        <label for="email">Email</label>
        <input v-model="email" type="email" id="email" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input v-model="password" type="password" id="password" required />
      </div>
      <button type="button" @click="handleLogin" class="login-btn">
        Login
      </button>
    </form>
    <button type="button" class="create-btn" @click="handleCreateAccount">
      Create Account
    </button>
  </div>
  
</template>

<style scoped>
.container {
  max-width: 400px;
  margin: 8vh auto;
  padding: 2rem;
  background: #ffffff;
  border-radius: 12px;

  /* Dark, pronounced shadow for separation from background */
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.4),  /* main deep shadow */
    0 4px 12px rgba(0, 0, 0, 0.3);  /* softer inner shadow */

  font-family: 'Inter', sans-serif;
}

h1 {
  text-align: center;
  font-weight: 600;
  font-size: 1.8rem;
  color: #222;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #333;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s ease-in-out;
  background-color: #fafafa;
}

input:focus {
  outline: none;
  border-color: #ffb347;
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(255, 179, 71, 0.25);
}

.login-btn {
  width: 100%;
  padding: 0.9rem;
  background-color: #ffb347;
  color: #1a1a1a;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.login-btn:hover {
  background-color: #ff9f1c;
}

.create-btn {
  margin-top: 1rem;
  width: 100%;
  padding: 0.9rem;
  background-color: transparent;
  color: #ffb347;
  border: 1px solid #ffb347;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.create-btn:hover {
  background-color: rgba(255, 179, 71, 0.1);
}

/* Page background */
:global(body) {
  margin: 0;
  background: linear-gradient(135deg, #3d2b1f, #2b1a13);
  background-attachment: fixed;
  background-size: cover;
}
</style>
