<template>
  <div class="navbar-container">
    <router-link to="/" class="text">ENCUESTAPP</router-link>
    <div class="icons">
      <!-- Theme Toggle -->
      <div class="menu" @click="toggleDarkMode" style="cursor: pointer; margin-right: 15px;" title="Cambiar Tema">
         <i :class="['fas', isDarkMode ? 'fa-sun' : 'fa-moon']"></i>
      </div>

      <router-link
        v-for="item in filteredMenuItems"
        :key="item.id"
        :to="item.enlace"
        class="menu"
        :class="{ 'activo': route.path === item.enlace, 'selected': selectedMenuItem === item.id && route.path !== item.enlace }"
        @click="selectMenuItem(item.id, item.enlace, item.action)"
      >
        <i :class="'fas fa-' + item.icono"></i>
        <span class="menu-name">{{ item.nombre }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter, useRoute } from 'vue-router';
import { seleccionarCategoria } from '/src/utils/categoriaUtils.js';
import { useToast } from 'vue-toastification';
const toast = useToast();

const isDarkMode = ref(true);

const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value;
    if (isDarkMode.value) {
        document.body.classList.remove('light-mode');
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.classList.add('light-mode');
        localStorage.setItem('theme', 'light');
    }
};


const store = useStore();
const router = useRouter();
const route = useRoute();

const isAuthenticated = computed(() => store.getters.isAuthenticated);
const isAdmin = computed(() => store.state.user && store.state.user.is_staff);
const selectedMenuItem = ref(null);


onMounted(() => {
  console.log('Navbar mounted, checking authentication');
  
  const storedTheme = localStorage.getItem('theme');
  if (storedTheme === 'light') {
      isDarkMode.value = false;
      document.body.classList.add('light-mode');
  } else {
      isDarkMode.value = true;
      document.body.classList.remove('light-mode');
  }

  store.dispatch('checkAuthentication').then(() => {
    console.log('Authentication checked, isAuthenticated:', isAuthenticated.value);
  });
});

const logout = async () => {
  try {
      await store.dispatch('logout');
      toast.success('Sesión cerrada');
      seleccionarCategoria(1); // ID del elemento "/" en el menú de categorías
    } catch (error) {
      const errorMessage = error.email ? error.email[0] : 'Error al cerrar sesión. Intente nuevamente.';
      toast.error(errorMessages[errorMessage] || errorMessage);
    }
};

const menuItems = [
  { id: 1, nombre: 'ACCEDER', icono: 'user', enlace: '/auth', auth: false },
  { id: 2, nombre: 'PERFIL', icono: 'users', enlace: '/perfil', auth: true },
  { id: 99, nombre: 'ADMIN', icono: 'user-shield', enlace: '/admin', adminOnly: true },
  { id: 3, nombre: 'APOYO', icono: 'info-circle', enlace: '/apoyo', auth: false },
  { id: 4, nombre: 'ESTADÍSTICAS', icono: 'pie-chart', enlace: '/estadisticas' },
  { id: 5, nombre: 'CERRAR SESIÓN', icono: 'sign-out-alt', enlace: '#', auth: true, action: logout },
];

const filteredMenuItems = computed(() => {
  return menuItems.filter(item => {
    if (item.adminOnly && !isAdmin.value) return false;
    if (item.auth === undefined) return true;
    return item.auth === isAuthenticated.value;
  });
});

const selectMenuItem = (id, enlace, action) => {
  selectedMenuItem.value = id;
  seleccionarCategoria(null); // Desmarcar categorías del leftbar
  if (action) {
    action();
  }
  // router-link handles navigation automatically via :to prop
};
</script>

<style scoped>
.navbar-container {
  display: grid;
  grid-template-areas: "texto icons";
  grid-template-columns: auto auto;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  background-color: var(--colortertiary);
  padding: 0 30px;
}

.menu-categorias {
  display: none;
}

.text {
  grid-area: texto;
  justify-self: center;
  color: var(--colortext);
  font-size: 1.5rem;
  font-weight: bold;
  animation: changeColor 20s infinite;
  cursor: pointer;
  text-decoration: none;
}

.text:hover {
  color: var(--colorprimary)!important;
}

@keyframes changeColor {
  0% {
    color: var(--colortext);
  }
  50% {
    color: var(--colorprimary);
  }
  100% {
    color: var(--colortext);
  }
}

.icons {
  grid-area: icons;
  grid-auto-flow: column;
  display: flex;
  font-weight: bold;
  gap: 15px;
  cursor: pointer;
}

.menu {
  color: var(--colortext);
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 8px;
  text-decoration: none;
}

.menu.activo {
  color: var(--colorprimary);
  background-color: rgba(0, 0, 0, 0.2); /* Subtle active background */
}

.menu.selected {
  color: var(--colortext);
}

.menu-name {
  display: inline-block;
  margin-left: 8px;
}

.menu:hover {
  color: var(--colorprimary);
  background-color: var(--colorbase); /* Contrast against tertiary navbar */
  transform: translateY(-2px); /* Slight lift */
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

@media (max-width: 430px) {
  .navbar-container {
    padding: 0 15px;
    justify-content: center;
  }
  .text {
    display: none;
  }
  .icons {
    display: flex; /* Use flex for better control than grid */
    flex-direction: row;
    align-items: center;
    justify-content: space-between; /* Spread icons evenly */
    width: 100%; /* Take full width */
    max-width: 350px; /* Limit max width for large phones */
    font-size: 1.3rem; /* Larger icons */
    gap: 0; /* Let justify-content handle spacing */
  }
  
  .menu {
    padding: 10px; /* larger touch target */
  }

  .menu[title="Cambiar Tema"] {
    margin-right: 0 !important; /* Remove inline margin on mobile */
  }
}

/* Consolidate extra media queries for cleanness */
@media (max-width: 344px) {
    .icons {
        font-size: 1.1rem; /* Slightly smaller on very small screens */
    }
}
</style>
