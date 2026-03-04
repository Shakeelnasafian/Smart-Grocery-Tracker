<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 to-teal-50">
    <nav class="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-2xl">💰</span>
        <h1 class="text-xl font-bold text-green-800">Budget Tracker</h1>
      </div>
      <router-link to="/dashboard" class="text-sm text-blue-600 hover:underline">← Back</router-link>
    </nav>

    <div class="max-w-3xl mx-auto p-6 space-y-6">

      <!-- Add Budget -->
      <div class="bg-white rounded-2xl p-6 shadow">
        <h2 class="text-lg font-semibold text-gray-700 mb-4">Set Monthly Budget</h2>
        <div v-if="error" class="mb-3 bg-red-100 text-red-700 px-4 py-2 rounded-lg text-sm">{{ error }}</div>
        <form @submit.prevent="createBudget" class="grid grid-cols-3 gap-4">
          <select v-model="form.month" class="px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-400">
            <option v-for="(m, i) in months" :key="i" :value="i + 1">{{ m }}</option>
          </select>
          <input type="number" v-model="form.year" placeholder="Year" min="2020" max="2035"
            class="px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-400" />
          <input type="number" v-model="form.limit_amount" placeholder="Budget limit ($)" step="0.01" min="0"
            class="px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-400" />
          <button type="submit" class="col-span-3 bg-green-600 hover:bg-green-700 text-white py-2 rounded-xl font-semibold transition">
            Set Budget
          </button>
        </form>
      </div>

      <!-- Budget List -->
      <div class="space-y-4">
        <p v-if="!budgets.length" class="text-center text-gray-400 py-10">No budgets yet. Set your first one above!</p>
        <div v-for="b in budgets" :key="b.id" class="bg-white rounded-2xl p-5 shadow">
          <div class="flex justify-between items-center mb-3">
            <h3 class="font-semibold text-gray-700">{{ months[b.month - 1] }} {{ b.year }}</h3>
            <span :class="b.spent_amount > b.limit_amount ? 'text-red-600' : 'text-green-600'"
              class="font-bold text-lg">
              ${{ b.spent_amount.toFixed(2) }} / ${{ b.limit_amount.toFixed(2) }}
            </span>
          </div>
          <div class="w-full bg-gray-100 rounded-full h-4 overflow-hidden">
            <div :class="spentPercent(b) >= 100 ? 'bg-red-500' : spentPercent(b) >= 80 ? 'bg-amber-400' : 'bg-green-500'"
              class="h-4 rounded-full transition-all"
              :style="`width: ${Math.min(spentPercent(b), 100)}%`"></div>
          </div>
          <div class="flex justify-between text-xs text-gray-500 mt-1">
            <span>{{ spentPercent(b).toFixed(0) }}% used</span>
            <span v-if="b.limit_amount > b.spent_amount" class="text-green-600">
              ${{ (b.limit_amount - b.spent_amount).toFixed(2) }} remaining
            </span>
            <span v-else class="text-red-600">
              ${{ (b.spent_amount - b.limit_amount).toFixed(2) }} over budget!
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store/auth';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const auth = useAuthStore();
const headers = () => ({ Authorization: `Bearer ${auth.token}` });

const budgets = ref([]);
const error = ref('');
const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

const now = new Date();
const form = reactive({ month: now.getMonth() + 1, year: now.getFullYear(), limit_amount: '' });

const spentPercent = (b) => b.limit_amount > 0 ? (b.spent_amount / b.limit_amount) * 100 : 0;

const fetchBudgets = async () => {
  const res = await axios.get(`${API}/budget/`, { headers: headers() });
  budgets.value = res.data;
};

const createBudget = async () => {
  error.value = '';
  try {
    await axios.post(`${API}/budget/`, { month: form.month, year: form.year, limit_amount: parseFloat(form.limit_amount) }, { headers: headers() });
    form.limit_amount = '';
    fetchBudgets();
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create budget.';
  }
};

onMounted(fetchBudgets);
</script>
