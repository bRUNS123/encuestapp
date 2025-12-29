import { createRouter, createWebHistory } from "vue-router";

import AuthView from "@/views/LoginView.vue";
import ProfileView from "@/views/ProfileView.vue";
import StatisticsView from "@/views/StatisticsView.vue";
import NewestView from "@/views/NewestView.vue";
import MostVotedView from "@/views/MostVotedView.vue";
import CategoriaView from "@/views/CategoryView.vue";
import SupportView from "@/views/SupportView.vue";
import CreateQuestionView from "@/views/CreateQuestionView.vue";
import BestRatedView from "@/views/BestRatedView.vue";
import ForgotPasswordView from "@/views/ForgotPasswordView.vue";
import PublicProfileView from "@/views/PublicProfileView.vue";

const routes = [
  {
    path: "/",
    name: "mostvoted",
    component: MostVotedView,
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
    meta: {
      fullWidth: true,
    },
    component: ProfileView,
  },
  {
    path: "/estadisticas",
    name: "statistics",
    meta: {
      fullWidth: true,
    },
    component: StatisticsView,
  },
  {
    path: "/apoyo",
    name: "apoyo",
    component: SupportView,
    meta: {
      fullWidth: true,
    },
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
    meta: {
      fullWidth: true,
    },
  },
  {
    path: "/crear-encuesta",
    name: "crear-encuesta",
    component: CreateQuestionView,
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

export default router;
