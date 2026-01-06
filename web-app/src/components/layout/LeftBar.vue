<template>
  <router-link 
    v-for="categoria in filteredCategorias" 
    :key="categoria.id" 
    :to="categoria.enlace" 
    class="categoria-container" 
    :class="{ 'activo': categoria.isActive }" 
    @click="seleccionarCategoria(categoria.id)"
  >
    <div class="contenido-categoria">
      <i :class="['icono', categoria.icono]"></i>
      <span class="nombre">{{ categoria.nombre }}</span>
    </div>
  </router-link>
</template>

<script setup>
import { onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from 'vuex';
import { categorias, seleccionarCategoria } from '/src/utils/categoriaUtils.js';

// Obtener el objeto de la ruta actual
const route = useRoute();
const store = useStore();

const isAuthenticated = computed(() => store.getters.isAuthenticated);

const filteredCategorias = computed(() => {
  return categorias.value.filter(categoria => {
    // If auth property is true, require authentication
    if (categoria.auth) {
      return isAuthenticated.value;
    }
    // Otherwise show to everyone
    return true;
  });
});

const updateActiveCategory = () => {
  const path = route.path;
  const params = route.params;
  console.log("Ruta actual:", path, "Parámetros:", params); // Depuración

  let categoriaActual = categorias.value.find(categoria => categoria.enlace === path);
  
  if (!categoriaActual && params.categoria) {
    // Si no se encuentra por el path, buscar por el parámetro de la ruta
    categoriaActual = categorias.value.find(categoria => categoria.enlace === `/${params.categoria}`);
  }

  if (categoriaActual) {
    console.log("Categoría encontrada:", categoriaActual); // Depuración
    seleccionarCategoria(categoriaActual.id);
  } else if (path === '/') {
    seleccionarCategoria(1); // Asegúrate de que "MÁS VOTADAS" tiene el id 1
  } else {
    seleccionarCategoria(null);
  }
};

onMounted(() => {
  updateActiveCategory();
});

watch(route, () => {
  updateActiveCategory();
});
</script>

<style scoped>
.activo {
  background: var(--colortertiary); /* Solid background for cleaner look */
  border-left: 3px solid var(--colorprimary);
  /* box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1); Subtle shadow */
}

.activo .nombre {
  color: var(--colorprimary); /* Use primary color for text too */
  font-weight: 700;
}

.activo .icono {
  color: var(--colorprimary);
}

.categoria-container {
  display: flex;
  flex-direction: row; /* Horizontal alignment for desktop */
  align-items: center; /* Center items vertically */
  justify-content: flex-start; /* Align content to the start */
  transition: all 0.2s ease;
  cursor: pointer;
  padding: 16px 20px; /* Spacious horizontal padding */
  min-width: 90px;
  border-radius: 12px;
  margin-bottom: 12px;
  width: 100%; /* Full width */
  box-sizing: border-box;
}

/* ... existing hover styles ... */
/* ... existing hover styles ... */
.categoria-container:hover {
  background-color: var(--colortertiary);
  /* transform: translateX(4px); Removed to prevent scroll */
}

.categoria-container:hover, .categoria-container:hover .nombre {
  text-decoration: none;
}

.contenido-categoria {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  transition: transform 0.2s ease; /* Smooth nudge for content */
}

.categoria-container:hover .contenido-categoria {
  transform: translateX(4px); /* Nudge content inside the box */
}

.icono {
  grid-area: unset;
  color: var(--colorsecondary);
  font-size: 18px; /* Balanced icon size */
  margin-bottom: 0; /* Remove vertical margin */
  margin-right: 12px; /* Horizontal separation */
  display: block;
  transition: color 0.3s ease;
  width: 24px; /* Fixed width for alignment */
  text-align: center;
}

.nombre {
  grid-area: unset;
  font-weight: 700; /* Bold per user request */
  color: var(--colorsecondary);
  font-size: 11px; /* Slightly more readable */
  letter-spacing: 0.5px; /* PROFESSIONAL: Letter spacing */
  white-space: nowrap;
  transition: color 0.3s ease;
}

.categoria-container:hover .icono {
  color: var(--colorprimary);
}

.categoria-container:hover .nombre {
  color: var(--colortext);
}

/* Mobile specific adjustments */
@media (max-width: 1024px) {
  .categoria-container {
    flex-direction: column;
    margin: 0; 
    padding: 14px 0; /* Slightly more padding for better touch targets */
    border-radius: 0;
    min-width: unset !important;
    margin-bottom: 0;
    width: 100%;
    justify-content: center;
    align-items: center; /* Center horizontally */
  }

  .contenido-categoria {
    justify-content: center; /* Center the icon inside */
  }

  .icono {
    font-size: 24px; /* Slightly larger for better visibility */
    margin-right: 0;
    width: auto;
    margin-bottom: 0;
  }
  
  .nombre {
    display: none !important;
  }

  /* Active state for mobile - remove left border, use background */
  .categoria-container.activo {
    background: rgba(59, 130, 246, 0.15); /* Subtle blue background */
    border-left: none; /* Remove left border for centered look */
    border-bottom: none;
    box-shadow: none;
  }
  
  .categoria-container.activo .icono {
    color: var(--colorprimary);
    transform: scale(1.15); /* Slightly larger scale for emphasis */
  }
}
</style>
