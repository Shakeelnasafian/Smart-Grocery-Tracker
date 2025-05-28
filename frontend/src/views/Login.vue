<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <div class="max-w-md w-full bg-white shadow-lg rounded-2xl p-8 space-y-6">
      <h2 class="text-2xl font-bold text-gray-800 text-center">Login to Your Account</h2>

      <div class="space-y-4">
        <input
          v-model="username"
          type="email"
          placeholder="Email"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          @click="handleLogin"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition duration-200"
        >
          Login
        </button>
      </div>

      <p class="text-center text-sm text-gray-500">
        Don’t have an account?
        <a href="#" class="text-blue-500 hover:underline">Register</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const username = ref('');
const password = ref('');
const auth = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  try {
    await auth.login(username.value, password.value);
    router.push('/dashboard');
  } catch (e) {
    alert("Login failed. Check credentials.");
  }
};
</script>
