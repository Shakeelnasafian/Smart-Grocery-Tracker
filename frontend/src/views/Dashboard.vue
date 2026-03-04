<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
    <!-- Nav -->
    <nav class="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-2xl">🛒</span>
        <h1 class="text-xl font-bold text-blue-800">Smart Grocery Tracker</h1>
      </div>
      <div class="flex items-center gap-3">
        <router-link to="/analytics" class="text-sm text-blue-600 hover:underline">Analytics</router-link>
        <router-link to="/budget" class="text-sm text-blue-600 hover:underline">Budget</router-link>
        <router-link to="/shopping" class="text-sm text-blue-600 hover:underline">Shopping List</router-link>
        <button @click="sesLogout"
          class="text-sm bg-red-500 hover:bg-red-600 text-white px-4 py-1.5 rounded-lg transition">
          Logout
        </button>
      </div>
    </nav>

    <div class="max-w-5xl mx-auto p-6 space-y-6">

      <!-- Expiry Alert Banner -->
      <div v-if="expiringCount > 0"
        class="bg-amber-100 border border-amber-400 text-amber-800 px-5 py-3 rounded-xl flex items-center gap-2">
        <span class="text-xl">⚠️</span>
        <span><strong>{{ expiringCount }} item(s)</strong> expiring within 3 days!</span>
        <button @click="filterExpiring" class="ml-auto text-sm underline">Show only expiring</button>
      </div>

      <!-- Add Item Form -->
      <div class="bg-white shadow-lg rounded-2xl p-6">
        <h2 class="text-lg font-semibold text-gray-700 mb-4">
          {{ editMode ? '✏️ Edit Item' : '➕ Add New Item' }}
        </h2>
        <form @submit.prevent="editMode ? saveEdit() : addItem()" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input v-model="form.name" placeholder="Item name" required
            class="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          <input v-model="form.quantity" placeholder="Quantity (e.g. 2L, 500g)" required
            class="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          <input v-model="form.category" placeholder="Category" required
            class="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          <input type="date" v-model="form.expiry_date" required
            class="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          <input type="number" v-model="form.price" placeholder="Price (optional)" step="0.01" min="0"
            class="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          <input v-model="form.notes" placeholder="Notes (optional)"
            class="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          <div class="md:col-span-3 flex gap-3">
            <button type="submit"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-xl font-semibold transition">
              {{ editMode ? 'Save Changes' : 'Add Item' }}
            </button>
            <button v-if="editMode" type="button" @click="cancelEdit"
              class="px-6 bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 rounded-xl transition">
              Cancel
            </button>
          </div>
        </form>

        <!-- Food Search -->
        <div class="mt-4 border-t pt-4">
          <p class="text-sm text-gray-500 mb-2">Search Open Food Facts to auto-fill item details:</p>
          <div class="flex gap-2">
            <input v-model="foodSearch" placeholder="Search product name..."
              @keyup.enter="searchFood"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm" />
            <button @click="searchFood" :disabled="foodLoading"
              class="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl text-sm transition">
              {{ foodLoading ? '...' : 'Search' }}
            </button>
          </div>
          <div v-if="foodResults.length" class="mt-2 space-y-1">
            <button v-for="p in foodResults" :key="p.name" @click="fillFromFood(p)"
              class="w-full text-left px-3 py-2 bg-indigo-50 hover:bg-indigo-100 rounded-lg text-sm transition">
              <span class="font-medium">{{ p.name }}</span>
              <span class="text-gray-500 ml-2">{{ p.category }}</span>
              <span v-if="p.brands" class="text-gray-400 ml-2">· {{ p.brands }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white shadow rounded-2xl px-6 py-4 flex flex-wrap gap-3 items-center">
        <input v-model="filters.search" @input="fetchItems" placeholder="Search items..."
          class="flex-1 min-w-[180px] px-4 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        <input v-model="filters.category" @input="fetchItems" placeholder="Filter by category..."
          class="w-44 px-4 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        <label class="flex items-center gap-2 text-sm text-gray-600">
          <input type="checkbox" v-model="filters.show_consumed" @change="fetchItems" class="rounded" />
          Show consumed
        </label>
        <button @click="downloadCSV"
          class="ml-auto px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-xl text-sm transition">
          Export CSV
        </button>
      </div>

      <!-- Item List -->
      <div class="space-y-3">
        <p v-if="!items.length" class="text-center text-gray-400 py-10">
          No items found. Add your first grocery item above!
        </p>

        <div v-for="item in items" :key="item.id"
          :class="[
            'flex items-center justify-between p-4 rounded-xl shadow-sm border transition',
            isExpired(item) ? 'bg-red-50 border-red-200' :
            isExpiringSoon(item) ? 'bg-amber-50 border-amber-200' :
            'bg-white border-gray-100 hover:bg-gray-50'
          ]">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <p class="text-base font-bold text-gray-800">{{ item.name }}</p>
              <span class="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{{ item.quantity }}</span>
              <span v-if="item.is_consumed" class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Consumed</span>
              <span v-if="isExpired(item)" class="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full">Expired</span>
              <span v-else-if="isExpiringSoon(item)" class="text-xs bg-amber-100 text-amber-600 px-2 py-0.5 rounded-full">Expiring soon</span>
            </div>
            <p class="text-sm text-gray-500 mt-0.5">{{ item.category }} · Expires {{ item.expiry_date }}
              <span v-if="item.price" class="ml-2 text-green-600 font-medium">${{ item.price.toFixed(2) }}</span>
            </p>
            <p v-if="item.notes" class="text-xs text-gray-400 mt-0.5">{{ item.notes }}</p>
          </div>

          <div class="flex gap-2 ml-4 flex-shrink-0">
            <button @click="markConsumed(item)"
              :class="item.is_consumed ? 'bg-gray-200 text-gray-500' : 'bg-green-100 hover:bg-green-200 text-green-700'"
              class="text-xs px-3 py-1.5 rounded-lg transition">
              {{ item.is_consumed ? 'Undo' : 'Consumed' }}
            </button>
            <button @click="startEdit(item)"
              class="text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-1.5 rounded-lg transition">
              Edit
            </button>
            <button @click="deleteItem(item.id)"
              class="text-xs bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded-lg transition">
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.pages > 1" class="flex justify-center gap-2 pt-2">
        <button v-for="p in pagination.pages" :key="p" @click="goToPage(p)"
          :class="p === pagination.page ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'"
          class="w-9 h-9 rounded-lg border text-sm font-medium transition">
          {{ p }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store/auth';
import { useRouter } from 'vue-router';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const router = useRouter();
const auth = useAuthStore();
const headers = computed(() => ({ Authorization: `Bearer ${auth.token}` }));

const items = ref([]);
const expiringCount = ref(0);
const pagination = ref({ page: 1, pages: 1, total: 0 });
const editMode = ref(false);
const editId = ref(null);
const foodSearch = ref('');
const foodResults = ref([]);
const foodLoading = ref(false);

const form = reactive({ name: '', quantity: '', category: '', expiry_date: '', price: '', notes: '' });
const filters = reactive({ search: '', category: '', show_consumed: false, page: 1, expiring_within_days: null });

const fetchItems = async () => {
  const params = new URLSearchParams();
  if (filters.search) params.set('search', filters.search);
  if (filters.category) params.set('category', filters.category);
  if (filters.show_consumed) params.set('show_consumed', 'true');
  if (filters.expiring_within_days) params.set('expiring_within_days', filters.expiring_within_days);
  params.set('page', filters.page);
  params.set('page_size', '15');

  const res = await axios.get(`${API}/grocery/?${params}`, { headers: headers.value });
  items.value = res.data.items;
  pagination.value = { page: res.data.page, pages: res.data.pages, total: res.data.total };
};

const fetchExpiringCount = async () => {
  const res = await axios.get(`${API}/alerts/expiring?days=3`, { headers: headers.value });
  expiringCount.value = res.data.count;
};

const addItem = async () => {
  const payload = { ...form, price: form.price ? parseFloat(form.price) : null };
  await axios.post(`${API}/grocery/`, payload, { headers: headers.value });
  Object.assign(form, { name: '', quantity: '', category: '', expiry_date: '', price: '', notes: '' });
  fetchItems();
  fetchExpiringCount();
};

const startEdit = (item) => {
  editMode.value = true;
  editId.value = item.id;
  Object.assign(form, { name: item.name, quantity: item.quantity, category: item.category, expiry_date: item.expiry_date, price: item.price || '', notes: item.notes || '' });
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const saveEdit = async () => {
  const payload = { ...form, price: form.price ? parseFloat(form.price) : null };
  await axios.put(`${API}/grocery/${editId.value}`, payload, { headers: headers.value });
  cancelEdit();
  fetchItems();
};

const cancelEdit = () => {
  editMode.value = false;
  editId.value = null;
  Object.assign(form, { name: '', quantity: '', category: '', expiry_date: '', price: '', notes: '' });
};

const deleteItem = async (id) => {
  if (!confirm('Delete this item?')) return;
  await axios.delete(`${API}/grocery/${id}`, { headers: headers.value });
  fetchItems();
  fetchExpiringCount();
};

const markConsumed = async (item) => {
  await axios.put(`${API}/grocery/${item.id}`, { is_consumed: !item.is_consumed }, { headers: headers.value });
  fetchItems();
};

const filterExpiring = () => {
  filters.search = '';
  filters.category = '';
  filters.expiring_within_days = 3;
  filters.page = 1;
  fetchItems();
};

const clearExpiryFilter = () => {
  filters.expiring_within_days = null;
  fetchItems();
};

const downloadCSV = () => {
  window.open(`${API}/grocery/export/csv?token=${auth.token}`, '_blank');
};

const searchFood = async () => {
  if (!foodSearch.value.trim()) return;
  foodLoading.value = true;
  try {
    const res = await axios.get(`${API}/food/search?q=${encodeURIComponent(foodSearch.value)}`, { headers: headers.value });
    foodResults.value = res.data;
  } catch { foodResults.value = []; }
  finally { foodLoading.value = false; }
};

const fillFromFood = (product) => {
  form.name = product.name;
  form.category = product.category || '';
  form.quantity = product.quantity || '';
  foodResults.value = [];
  foodSearch.value = '';
};

const goToPage = (p) => {
  filters.page = p;
  fetchItems();
};

const isExpired = (item) => item.expiry_date && new Date(item.expiry_date) < new Date(new Date().toDateString());
const isExpiringSoon = (item) => {
  if (!item.expiry_date) return false;
  const d = new Date(item.expiry_date);
  const now = new Date(new Date().toDateString());
  const diff = (d - now) / (1000 * 60 * 60 * 24);
  return diff >= 0 && diff <= 3;
};

const sesLogout = async () => {
  try { await axios.post(`${API}/logout`, {}, { headers: headers.value }); } catch { }
  auth.logout();
  router.push('/');
};

onMounted(() => { fetchItems(); fetchExpiringCount(); });
</script>
