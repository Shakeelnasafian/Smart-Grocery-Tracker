<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
    <!-- Nav -->
    <nav class="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-2xl">📊</span>
        <h1 class="text-xl font-bold text-purple-800">Analytics</h1>
      </div>
      <router-link to="/dashboard" class="text-sm text-blue-600 hover:underline">← Back to Dashboard</router-link>
    </nav>

    <div class="max-w-5xl mx-auto p-6 space-y-6">
      <div v-if="loading" class="text-center py-20 text-gray-400">Loading analytics...</div>

      <template v-else-if="data">
        <!-- Summary Cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-white rounded-2xl p-5 shadow text-center">
            <div class="text-3xl font-bold text-blue-600">{{ data.total_items }}</div>
            <div class="text-sm text-gray-500 mt-1">Total Items</div>
          </div>
          <div class="bg-white rounded-2xl p-5 shadow text-center">
            <div class="text-3xl font-bold text-green-600">${{ data.total_spent.toFixed(2) }}</div>
            <div class="text-sm text-gray-500 mt-1">Total Spent</div>
          </div>
          <div class="bg-white rounded-2xl p-5 shadow text-center">
            <div class="text-3xl font-bold text-amber-500">{{ data.expiry_stats.expiring_soon }}</div>
            <div class="text-sm text-gray-500 mt-1">Expiring Soon</div>
          </div>
          <div class="bg-white rounded-2xl p-5 shadow text-center">
            <div class="text-3xl font-bold text-red-500">{{ data.expiry_stats.expired }}</div>
            <div class="text-sm text-gray-500 mt-1">Expired Items</div>
          </div>
        </div>

        <!-- Expiry Breakdown -->
        <div class="bg-white rounded-2xl p-6 shadow">
          <h2 class="text-lg font-semibold text-gray-700 mb-4">Inventory Health</h2>
          <div class="grid grid-cols-3 gap-4 text-center">
            <div class="bg-green-50 rounded-xl p-4">
              <div class="text-2xl font-bold text-green-600">{{ data.expiry_stats.fresh }}</div>
              <div class="text-sm text-gray-500">Fresh</div>
            </div>
            <div class="bg-amber-50 rounded-xl p-4">
              <div class="text-2xl font-bold text-amber-500">{{ data.expiry_stats.expiring_soon }}</div>
              <div class="text-sm text-gray-500">Expiring Soon</div>
            </div>
            <div class="bg-red-50 rounded-xl p-4">
              <div class="text-2xl font-bold text-red-500">{{ data.expiry_stats.expired }}</div>
              <div class="text-sm text-gray-500">Expired</div>
            </div>
          </div>
          <div class="mt-4">
            <div class="flex justify-between text-xs text-gray-500 mb-1">
              <span>Waste rate (consumed items)</span>
              <span>{{ data.waste_rate }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-blue-500 h-2 rounded-full" :style="`width: ${data.waste_rate}%`"></div>
            </div>
          </div>
        </div>

        <!-- Category Breakdown -->
        <div class="bg-white rounded-2xl p-6 shadow">
          <h2 class="text-lg font-semibold text-gray-700 mb-4">Spending by Category</h2>
          <div v-if="!data.category_breakdown.length" class="text-gray-400 text-sm">No category data yet.</div>
          <div v-else class="space-y-3">
            <div v-for="cat in sortedCategories" :key="cat.category">
              <div class="flex justify-between text-sm mb-1">
                <span class="font-medium text-gray-700">{{ cat.category }}</span>
                <span class="text-gray-500">{{ cat.count }} items · ${{ cat.total_spent.toFixed(2) }}</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-2.5">
                <div class="bg-purple-500 h-2.5 rounded-full" :style="`width: ${catPercent(cat)}%`"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Monthly Spending -->
        <div class="bg-white rounded-2xl p-6 shadow">
          <h2 class="text-lg font-semibold text-gray-700 mb-4">Monthly Spending</h2>
          <div v-if="!data.monthly_spending.length" class="text-gray-400 text-sm">No spending data yet. Add items with prices!</div>
          <div v-else class="space-y-3">
            <div v-for="m in data.monthly_spending" :key="`${m.year}-${m.month}`"
              class="flex items-center gap-4">
              <span class="text-sm text-gray-600 w-24">{{ monthName(m.month) }} {{ m.year }}</span>
              <div class="flex-1 bg-gray-100 rounded-full h-3">
                <div class="bg-blue-500 h-3 rounded-full" :style="`width: ${monthPercent(m)}%`"></div>
              </div>
              <span class="text-sm font-medium text-gray-700 w-20 text-right">${{ m.total.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store/auth';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const auth = useAuthStore();
const headers = computed(() => ({ Authorization: `Bearer ${auth.token}` }));
const data = ref(null);
const loading = ref(true);

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const monthName = (m) => MONTHS[m - 1];

const sortedCategories = computed(() =>
  [...(data.value?.category_breakdown || [])].sort((a, b) => b.total_spent - a.total_spent)
);

const maxCatSpend = computed(() => Math.max(...sortedCategories.value.map(c => c.total_spent), 1));
const catPercent = (cat) => Math.round((cat.total_spent / maxCatSpend.value) * 100);

const maxMonthSpend = computed(() => Math.max(...(data.value?.monthly_spending || []).map(m => m.total), 1));
const monthPercent = (m) => Math.round((m.total / maxMonthSpend.value) * 100);

onMounted(async () => {
  try {
    const res = await axios.get(`${API}/analytics/`, { headers: headers.value });
    data.value = res.data;
  } finally {
    loading.value = false;
  }
});
</script>
