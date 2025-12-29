import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

// Configuración de las opciones de Toastification
const toastOptions = {
  position: "bottom-right",
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false,
};

// Cookies
import { setCookie, getCookie } from "./store/cookies";
import { v4 as uuidv4 } from "uuid";

// Graphs
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

// Styles
import "./assets/main.css";

const COOKIE_NAME = "user_token";
if (!getCookie(COOKIE_NAME)) {
  const token = uuidv4();
  setCookie(COOKIE_NAME, token, 30); // La cookie caducará en 30 días
}

// Google Login
import vue3GoogleLogin from 'vue3-google-login';

const app = createApp(App);

app.use(store);
app.use(router);
app.use(Toast, toastOptions);
app.use(vue3GoogleLogin, {
  clientId: '419930149880-325o4917akvnt56j11f87aklik25grje.apps.googleusercontent.com'
});

store.dispatch("checkAuthentication").then(() => {
  console.log("Authentication checked on app load");
  app.mount("#app");
});
