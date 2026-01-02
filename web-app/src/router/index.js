import { createRouter, createWebHistory } from "vue-router";

import AuthView from "@/views/LoginView.vue";
import ProfileView from "@/views/ProfileView.vue";
import StatisticsView from "@/views/StatisticsView.vue";
import NewestView from "@/views/NewestView.vue";
import MostVotedView from "@/views/MostVotedView.vue";
import CategoriaView from "@/views/CategoryView.vue";
import SuggestionsView from "@/views/SuggestionsView.vue";
import CreateQuestionView from "@/views/CreateQuestionView.vue";
import BestRatedView from "@/views/BestRatedView.vue";
import ForgotPasswordView from "@/views/ForgotPasswordView.vue";
import PublicProfileView from "@/views/PublicProfileView.vue";
import LogsView from "@/views/LogsView.vue";

import AdminLayout from '@/views/admin/AdminLayout.vue';
import AdminDashboard from '@/views/admin/AdminDashboard.vue';
import AdminUsers from '@/views/admin/AdminUsers.vue';
import AdminQuestions from '@/views/admin/AdminQuestions.vue';
import store from '@/store';

const routes = [
  {
    path: "/",
    name: "mostvoted",
    component: MostVotedView,
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAdmin: true, fullWidth: true },
    children: [
      { path: '', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'users', name: 'AdminUsers', component: AdminUsers },
      { path: 'questions', name: 'AdminQuestions', component: AdminQuestions },
    ]
  },
  {
    path: "/profile/:id",
    name: "PublicProfile",
    component: PublicProfileView,
    meta: {
      fullWidth: true,
    }
  },
  {
    path: "/newest",
    name: "newest",
    component: NewestView,
  },
  {
    path: "/best-rated",
    name: "best-rated",
    component: BestRatedView,
  },
  {
    path: "/perfil",
    name: "perfil",
    component: ProfileView,
  },
  {
    path: "/estadisticas",
    name: "statistics",
    component: StatisticsView,
  },
  {
    path: "/sugerencias",
    name: "sugerencias",
    component: SuggestionsView,
  },
  {
    path: "/forgot-password",
    name: "forgot-password",
    component: ForgotPasswordView,
    meta: {
      fullWidth: true,
    },
  },
  {
    path: "/auth",
    name: "auth",
    component: AuthView,
  },
  {
    path: "/crear-encuesta",
    name: "crear-encuesta",
    component: CreateQuestionView,
    meta: {
      fullWidth: true,
    },
  },
  {
    path: "/logs",
    name: "logs",
    component: LogsView,
    meta: {
      fullWidth: true,
    },
  },
  // WILDCARD MUST BE LAST - catches all category routes
  {
    path: "/:categoria",
    name: "Categoria",
    component: CategoriaView,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAdmin)) {
    let user = store.state.user;
    if (!user) {
      // Try to restore session if token exists
      if (localStorage.getItem('access_token')) {
        await store.dispatch('checkAuthentication');
        user = store.state.user;
      }
    }

    if (user && user.is_staff) {
      next();
    } else {
      next('/');
    }
  } else {
    next();
  }
});

export default router;
