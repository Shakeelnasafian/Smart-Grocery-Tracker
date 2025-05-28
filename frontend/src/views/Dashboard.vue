<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 p-6">
    <div class="max-w-4xl mx-auto bg-white shadow-2xl rounded-3xl p-8 space-y-8">
      <h2 class="text-3xl font-extrabold text-blue-800 text-center">🛒 My Grocery Tracker</h2>

      <!-- Form Section -->
      <form @submit.prevent="addItem" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <input
          v-model="newItem.name"
          placeholder="Item name"
          class="col-span-1 px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
        <input
          v-model="newItem.quantity"
          placeholder="Quantity"
          class="col-span-1 px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
        <input
          v-model="newItem.category"
          placeholder="Category"
          class="col-span-1 px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
        <input
          type="date"
          v-model="newItem.expiry_date"
          class="col-span-1 px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
        <button
          type="submit"
          class="md:col-span-2 bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-xl font-semibold transition-all duration-200 shadow-md"
        >
          ➕ Add Item
        </button>
      </form>

      <!-- Grocery List Section -->
      <div class="space-y-4">
        <div
          v-for="item in items"
          :key="item.id"
          class="flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition p-4 rounded-xl shadow-sm border"
        >
          <div>
            <p class="text-lg font-bold text-gray-800">{{ item.name }} <span class="text-sm text-gray-500">({{ item.quantity }})</span></p>
            <p class="text-sm text-gray-600">🗂️ {{ item.category }}</p>
            <p class="text-sm text-gray-400">📅 Expires: {{ item.expiry_date }}</p>
          </div>
          <button
            @click="deleteItem(item.id)"
            class="text-sm bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg shadow transition duration-150"
          >
            🗑 Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store/auth';

const items = ref([]);
const newItem = ref({
  name: '',
  quantity: '',
  category: '',
  expiry_date: '',
});
const auth = useAuthStore();

const fetchItems = async () => {
  const res = await axios.get('http://localhost:8000/grocery/', {
    headers: { Authorization: `Bearer ${auth.token}` },
  });
  items.value = res.data;
};

const addItem = async () => {
  await axios.post('http://localhost:8000/grocery/', newItem.value, {
    headers: { Authorization: `Bearer ${auth.token}` },
  });
  newItem.value = { name: '', quantity: '', category: '', expiry_date: '' };
  fetchItems();
};

const deleteItem = async (id) => {
  await axios.delete(`http://localhost:8000/grocery/${id}`, {
    headers: { Authorization: `Bearer ${auth.token}` },
  });
  fetchItems();
};

onMounted(fetchItems);
</script>
