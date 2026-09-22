<script setup>
import { onMounted, ref } from 'vue'
const username = ref('')
const email = ref('')
const password = ref('')
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const allow_admin_signup=ref(false)
const error_message=ref(null)
const isloading=ref(true)


async function handleSignup() {
  console.log('Creating account for:', username.value, email.value);
  try {
    const response = await fetch(`${API_BASE_URL}/signup_user`,{
      method:'POST',
      headers:{
        'Content-Type': 'application/json'
      },
      body:JSON.stringify ({
        username:username.value,
        email:email.value,
        password:password.value
      })     
    })
    const data =await response.json()
    if (response.ok) {
      alert("account created successfully");
    } else {
        alert("error: " + (data.detail || data.message || "Unknown error"));
    }
  }
  catch(error){
    alert('Failed to create account'+error.message);
  }

}
</script>

<template>
  <div class="container">
    <h1>Create Account</h1> 
    <form  >       <!--on submitting a form the site reloads the page v-on:submit.prevent="handleSignup" this happened because i typed button type="submit" using type="button" avoids this -->
      <div class="form-group">
        <label for="username">username</label>
        <input v-model="username" type="text" id="username" required />
        <label for="email">Email</label>
        <input v-model="email" type="email" id="email" required />
        <label for="password">Password</label>
        <input v-model="password" type="password" id="password" required />
      </div>
      <button type="button" v-on:click="handleSignup" class="signup-btn" >Sign Up</button>
    </form>

    <router-link to="/" class="login-link">← Back to Login</router-link>
  </div>
</template>

<style scoped>

</style>