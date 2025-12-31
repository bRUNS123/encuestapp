<template>
  <div class="logs-container">
    <div class="logs-header">
      <h1>Registro de Cambios (Changelog)</h1>
      <p class="subtitle">Historial de actualizaciones y mantenimiento de Encuestapp</p>
    </div>

    <div class="timeline">
      <div v-for="(log, index) in logs" :key="index" class="log-entry">
        <div class="log-date">{{ log.date }}</div>
        <div class="log-content">
          <div class="log-version">
            <span class="version-badge">{{ log.version }}</span>
            <span class="version-title">{{ log.title }}</span>
          </div>
          <ul class="log-details">
            <li v-for="(item, i) in log.items" :key="i" v-html="formatItem(item)"></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const logs = ref([
  {
    version: 'v1.2.1',
    date: '31/12/2025 16:55',
    title: 'Ajustes de UI y Logs',
    items: [
      'Eliminado indicador de versión en Navbar por estética.',
      'Creada página oculta <code>/logs</code> para seguimiento de cambios.',
    ]
  },
  {
    version: 'v1.2.0',
    date: '31/12/2025 16:40',
    title: 'Fix de Seguridad y Depuración',
    items: [
      'Habilitado logs detallados en la consola para depurar carga de preguntas.',
      '<strong>HOTFIX:</strong> Deshabilitada temporalmente restricción "IsAnonymous" en categoría Personal para pruebas.',
      'Añadido indicador visual temporal en Navbar (revertido).',
    ]
  },
  {
    version: 'v1.1.0',
    date: '31/12/2025 15:30',
    title: 'Mejoras en Navegación y Datos',
    items: [
      '<strong>Nuevo Sidebar:</strong> Reordenadas categorías ("Personal" después de "Mejores").',
      '<strong>Questions Refactor:</strong> Estructura JSON mejorada y script de carga optimizado.',
      '<strong>Sugerencias:</strong> Habilitado acceso universal (Logged In/Out) al menú "Sugerencias".',
    ]
  },
  {
    version: 'v1.0.0',
    date: '30/12/2025',
    title: 'Lanzamiento Inicial',
    items: [
      'Sistema de Autenticación (Login/Register/Social).',
      'Creación y votación de preguntas.',
      'Panel de Administración.',
      'Perfil de Usuario y Estadísticas.',
    ]
  }
]);

const formatItem = (text) => {
  return text;
};
</script>

<style scoped>
.logs-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
  color: var(--colortext);
}

.logs-header {
  margin-bottom: 40px;
  text-align: center;
}

.logs-header h1 {
  font-size: 2rem;
  margin-bottom: 10px;
  color: var(--colorprimary);
}

.subtitle {
  color: var(--color-text-muted, #888);
}

.timeline {
  position: relative;
  padding-left: 20px;
  border-left: 2px solid var(--color-border, #ddd);
}

.log-entry {
  margin-bottom: 40px;
  position: relative;
}

.log-entry::before {
  content: '';
  position: absolute;
  left: -27px;
  top: 0;
  width: 12px;
  height: 12px;
  background: var(--colorprimary);
  border-radius: 50%;
  border: 4px solid var(--color-bg, #fff);
}

.log-date {
  font-size: 0.85rem;
  color: var(--color-text-muted, #888);
  margin-bottom: 8px;
}

.log-version {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.version-badge {
  background: var(--colorprimary);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: bold;
}

.version-title {
  font-weight: 600;
  font-size: 1.1rem;
}

.log-details {
  list-style-type: none;
  padding: 0;
}

.log-details li {
  margin-bottom: 8px;
  line-height: 1.5;
  padding-left: 15px;
  position: relative;
}

.log-details li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--colorprimary);
}

code {
  background: rgba(0,0,0,0.1);
  padding: 2px 5px;
  border-radius: 4px;
  font-family: monospace;
}
</style>
