import { defineStore } from 'pinia';
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
  }),
  actions: {
    async login(username, password) {
      const res = await axios.post('http://localhost:8000/token', {
        username,
        password,
      }, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      this.token = res.data.access_token;
      localStorage.setItem('token', this.token);
    },
    logout() {
      this.token = '';
      localStorage.removeItem('token');
    }
  },
});
