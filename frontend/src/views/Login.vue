<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <div class="max-w-md w-full bg-white shadow-lg rounded-2xl p-8 space-y-6">
      <div class="text-center">
        <div class="text-5xl mb-2">🛒</div>
        <h2 class="text-2xl font-bold text-gray-800">Smart Grocery Tracker</h2>
        <p class="text-sm text-gray-500 mt-1">Sign in to manage your groceries</p>
      </div>

      <div v-if="successMsg" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg text-sm">
        {{ successMsg }}
      </div>
      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg text-sm">
        {{ error }}
      </div>

      <div class="space-y-4">
        <input v-model="username" type="email" placeholder="Email"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />

        <input v-model="password" type="password" placeholder="Password"
          @keyup.enter="handleLogin"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />

        <button @click="handleLogin" :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 px-4 rounded-lg transition duration-200">
          {{ loading ? 'Signing in...' : 'Login' }}
        </button>
      </div>

      <p class="text-center text-sm text-gray-500">
        Don't have an account?
        <router-link to="/register" class="text-blue-500 hover:underline">Register</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../store/auth';

const username = ref('');
const password = ref('');
const error = ref('');
const successMsg = ref('');
const loading = ref(false);
const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

onMounted(() => {
  if (route.query.registered) successMsg.value = 'Account created! Please log in.';
});

const handleLogin = async () => {
  error.value = '';
  loading.value = true;
  try {
    await auth.login(username.value, password.value);
    router.push('/dashboard');
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed. Check your credentials.';
  } finally {
    loading.value = false;
  }
};
</script>
