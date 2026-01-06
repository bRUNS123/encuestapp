<template>
  <div class="dashboard-view">
    <h1 class="page-title">Dashboard</h1>
    
    <div v-if="loading" class="loading">Cargando estadísticas...</div>
    
    <div v-else class="dashboard-grid">
      <!-- Stats Cards -->
      <div class="stat-card">
        <div class="stat-icon users"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <h3>Total Usuarios</h3>
          <p class="stat-value">{{ stats.total_users }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon votes"><i class="fas fa-vote-yea"></i></div>
        <div class="stat-info">
          <h3>Total Votos</h3>
          <p class="stat-value">{{ stats.total_votes }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon anon"><i class="fas fa-user-secret"></i></div>
        <div class="stat-info">
          <h3>Votos Anónimos</h3>
          <p class="stat-value">{{ stats.anonymous_votes }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon age"><i class="fas fa-users-cog"></i></div>
        <div class="stat-info">
          <h3>Edad Promedio</h3>
          <p class="stat-value">{{ stats.average_age }} años</p>
        </div>
      </div>
    </div>

    <!-- Admin Actions Section -->
    <div class="admin-actions" v-if="!loading">
      <h2>Acciones de Administrador</h2>
      <div class="actions-grid">
        <div class="action-card">
          <div class="action-icon">
            <i class="fas fa-sync-alt"></i>
          </div>
          <div class="action-info">
            <h3>Recargar Preguntas PERSONAL</h3>
            <p>Recarga preguntas de categoría PERSONAL con duración infinita (∞)</p>
            <button 
              @click="reloadPersonalQuestions" 
              :disabled="loadingPersonal"
              class="action-btn"
            >
              <i class="fas fa-sync-alt" :class="{'fa-spin': loadingPersonal}"></i>
              {{ loadingPersonal ? 'Cargando...' : 'Recargar Preguntas' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Output Display -->
      <div v-if="reloadOutput" class="output-display">
        <h3>Resultado:</h3>
        <pre>{{ reloadOutput }}</pre>
      </div>
    </div>

    <div class="charts-section" v-if="!loading">
      <div class="chart-container">
        <h2>Top 5 Preguntas</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Pregunta</th>
              <th>Votos</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(q, index) in stats.top_questions" :key="index">
              <td>{{ q.title }}</td>
              <td>{{ q.cantidad_votos }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="chart-container">
        <h2>Distribución por Categoría</h2>
         <table class="data-table">
          <thead>
            <tr>
              <th>Categoría</th>
              <th>Votos</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(c, index) in stats.votes_by_category" :key="index">
              <td>{{ c.question__category__name }}</td>
              <td>{{ c.count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/store/axiosInstance';
import { useToast } from 'vue-toastification';

const toast = useToast();
const stats = ref({});
const loading = ref(true);
const loadingPersonal = ref(false);
const reloadOutput = ref('');

const fetchStats = async () => {
  try {
    const response = await axios.get('questions/statistics/');
    stats.value = response.data;
  } catch (error) {
    console.error("Error fetching stats:", error);
  } finally {
    loading.value = false;
  }
};

const reloadPersonalQuestions = async () => {
  loadingPersonal.value = true;
  reloadOutput.value = '';
  
  try {
    const response = await axios.post('admin/load-personal-questions/');
    
    if (response.data.success) {
      toast.success('Preguntas PERSONAL recargadas exitosamente');
      reloadOutput.value = response.data.output;
      // Refresh stats after reload
      await fetchStats();
    } else {
      toast.error('Error al recargar preguntas');
      reloadOutput.value = response.data.error || 'Error desconocido';
    }
  } catch (error) {
    console.error("Error reloading personal questions:", error);
    toast.error('Error de conexión al recargar preguntas');
    reloadOutput.value = error.response?.data?.error || error.message;
  } finally {
    loadingPersonal.value = false;
  }
};

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
.page-title {
  margin-bottom: 30px;
  font-size: 2rem;
  font-weight: bold;
  color: white; /* Ensure visibility */
  border-bottom: 2px solid var(--colortertiary);
  padding-bottom: 10px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background-color: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon.users { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.stat-icon.votes { background: linear-gradient(135deg, #10b981, #059669); }
.stat-icon.anon { background: linear-gradient(135deg, #6366f1, #4f46e5); }
.stat-icon.age { background: linear-gradient(135deg, #f59e0b, #d97706); }

.stat-info h3 {
  margin: 0;
  font-size: 0.9rem;
  color: #aaa;
}

.stat-value {
  margin: 5px 0 0 0;
  font-size: 1.8rem;
  font-weight: bold;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-container {
  background-color: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-container h2 {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 1.2rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  text-align: left;
  padding: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.data-table th {
  color: #aaa;
  font-size: 0.9rem;
}

.admin-actions {
  margin: 40px 0;
}

.admin-actions h2 {
  margin-bottom: 20px;
  font-size: 1.5rem;
  color: white;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.action-card {
  background-color: rgba(255, 255, 255, 0.05);
  padding: 25px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.action-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  color: white;
  flex-shrink: 0;
}

.action-info {
  flex: 1;
}

.action-info h3 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  color: white;
}

.action-info p {
  margin: 0 0 15px 0;
  font-size: 0.9rem;
  color: #aaa;
}

.action-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.output-display {
  background-color: rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.output-display h3 {
  margin: 0 0 15px 0;
  color: #10b981;
}

.output-display pre {
  color: #d1d5db;
  font-size: 0.85rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

</style>
