<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50">
    <nav class="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-2xl">🛍️</span>
        <h1 class="text-xl font-bold text-orange-800">Shopping List</h1>
      </div>
      <router-link to="/dashboard" class="text-sm text-blue-600 hover:underline">← Back</router-link>
    </nav>

    <div class="max-w-3xl mx-auto p-6 space-y-6">

      <!-- Auto-generate button -->
      <div class="bg-white rounded-2xl p-5 shadow flex items-center justify-between">
        <div>
          <p class="font-semibold text-gray-700">Auto-Generate from Inventory</p>
          <p class="text-sm text-gray-500">Adds expired &amp; consumed grocery items to this list.</p>
        </div>
        <button @click="generateList" :disabled="generating"
          class="px-5 py-2 bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white rounded-xl text-sm font-semibold transition">
          {{ generating ? 'Generating...' : 'Generate' }}
        </button>
      </div>

      <!-- Add Item -->
      <div class="bg-white rounded-2xl p-6 shadow">
        <h2 class="text-lg font-semibold text-gray-700 mb-4">Add Item Manually</h2>
        <form @submit.prevent="addItem" class="grid grid-cols-3 gap-4">
          <input v-model="form.name" placeholder="Item name" required
            class="px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400" />
          <input v-model="form.quantity" placeholder="Quantity" required
            class="px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400" />
          <input v-model="form.category" placeholder="Category" required
            class="px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400" />
          <button type="submit" class="col-span-3 bg-orange-500 hover:bg-orange-600 text-white py-2 rounded-xl font-semibold transition">
            Add to List
          </button>
        </form>
      </div>

      <!-- Shopping Items -->
      <div class="bg-white rounded-2xl p-6 shadow space-y-3">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-lg font-semibold text-gray-700">Your List ({{ items.length }})</h2>
          <span class="text-sm text-gray-500">{{ purchasedCount }} / {{ items.length }} purchased</span>
        </div>

        <p v-if="!items.length" class="text-gray-400 text-sm text-center py-6">
          Your shopping list is empty. Generate one from inventory or add items manually.
        </p>

        <div v-for="item in items" :key="item.id"
          :class="item.is_purchased ? 'bg-green-50 opacity-60' : 'bg-gray-50'"
          class="flex items-center gap-4 p-3 rounded-xl border border-gray-100 transition">
          <input type="checkbox" :checked="item.is_purchased" @change="togglePurchased(item)"
            class="w-5 h-5 rounded accent-green-500 cursor-pointer" />
          <div class="flex-1 min-w-0">
            <p :class="item.is_purchased ? 'line-through text-gray-400' : 'text-gray-800'"
              class="font-medium">{{ item.name }}</p>
            <p class="text-xs text-gray-500">{{ item.quantity }} · {{ item.category }}</p>
            <p v-if="item.notes" class="text-xs text-gray-400">{{ item.notes }}</p>
          </div>
          <button @click="deleteItem(item.id)"
            class="text-xs bg-red-100 hover:bg-red-200 text-red-600 px-3 py-1 rounded-lg transition">
            Remove
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store/auth';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const auth = useAuthStore();
const headers = () => ({ Authorization: `Bearer ${auth.token}` });

const items = ref([]);
const generating = ref(false);
const form = reactive({ name: '', quantity: '', category: '', notes: '' });
const purchasedCount = computed(() => items.value.filter(i => i.is_purchased).length);

const fetchItems = async () => {
  const res = await axios.get(`${API}/shopping/`, { headers: headers() });
  items.value = res.data;
};

const addItem = async () => {
  await axios.post(`${API}/shopping/`, form, { headers: headers() });
  Object.assign(form, { name: '', quantity: '', category: '', notes: '' });
  fetchItems();
};

const togglePurchased = async (item) => {
  await axios.put(`${API}/shopping/${item.id}`, { is_purchased: !item.is_purchased }, { headers: headers() });
  fetchItems();
};

const deleteItem = async (id) => {
  await axios.delete(`${API}/shopping/${id}`, { headers: headers() });
  fetchItems();
};

const generateList = async () => {
  generating.value = true;
  try {
    await axios.post(`${API}/shopping/generate`, {}, { headers: headers() });
    fetchItems();
  } finally {
    generating.value = false;
  }
};

onMounted(fetchItems);
</script>
