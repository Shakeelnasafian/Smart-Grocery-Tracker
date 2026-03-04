<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <div class="max-w-md w-full bg-white shadow-lg rounded-2xl p-8 space-y-6">
      <h2 class="text-2xl font-bold text-gray-800 text-center">Create an Account</h2>

      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg text-sm">
        {{ error }}
      </div>

      <div class="space-y-4">
        <input v-model="email" type="email" placeholder="Email address"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />

        <input v-model="password" type="password" placeholder="Password (min 8 characters)"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />

        <input v-model="confirmPassword" type="password" placeholder="Confirm password"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />

        <button @click="handleRegister" :disabled="loading"
          class="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-2 px-4 rounded-lg transition duration-200">
          {{ loading ? 'Creating account...' : 'Create Account' }}
        </button>
      </div>

      <p class="text-center text-sm text-gray-500">
        Already have an account?
        <router-link to="/" class="text-blue-500 hover:underline">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const error = ref('');
const loading = ref(false);
const router = useRouter();

const handleRegister = async () => {
  error.value = '';
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.';
    return;
  }
  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters.';
    return;
  }

  loading.value = true;
  try {
    await axios.post(`${API}/register`, { email: email.value, password: password.value });
    router.push('/?registered=1');
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registration failed. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>
