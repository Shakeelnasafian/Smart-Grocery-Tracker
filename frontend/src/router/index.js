import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../store/auth';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Dashboard from '../views/Dashboard.vue';
import Analytics from '../views/Analytics.vue';
import Budget from '../views/Budget.vue';
import Shopping from '../views/Shopping.vue';

const routes = [
  { path: '/', component: Login, meta: { guest: true } },
  { path: '/register', component: Register, meta: { guest: true } },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/analytics', component: Analytics, meta: { requiresAuth: true } },
  { path: '/budget', component: Budget, meta: { requiresAuth: true } },
  { path: '/shopping', component: Shopping, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.token) {
    return next('/');
  }
  if (to.meta.guest && auth.token) {
    return next('/dashboard');
  }
  next();
});

export default router;
