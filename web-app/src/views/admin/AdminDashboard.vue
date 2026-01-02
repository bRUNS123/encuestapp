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

const stats = ref({});
const loading = ref(true);

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

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
.page-title {
  margin-bottom: 30px;
  font-size: 2rem;
  font-weight: bold;
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
</style>
