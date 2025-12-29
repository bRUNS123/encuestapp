<template>
  <div class="statistics-container">
    <h1 class="page-title">Estadísticas Globales</h1>
    
    <div v-if="loading" class="loading">Cargando estadísticas...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else-if="stats" class="stats-content">
      <!-- KPIs -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon"><i class="fas fa-users"></i></div>
          <div class="kpi-info">
            <h3>Total Usuarios</h3>
            <p class="kpi-value">{{ stats.total_users || 0 }}</p>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon"><i class="fas fa-vote-yea"></i></div>
          <div class="kpi-info">
            <h3>Total Votos</h3>
            <p class="kpi-value">{{ stats.total_votes }}</p>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon"><i class="fas fa-birthday-cake"></i></div>
          <div class="kpi-info">
            <h3>Edad Promedio</h3>
            <p class="kpi-value">{{ stats.average_age }} años</p>
          </div>
        </div>
      </div>

      <!-- Gráficos -->
      <div class="charts-section-grid">
        <div class="chart-card" @click="openModal('userType', 'Anónimos vs Registrados')" @mouseenter="setHover('userType', true)" @mouseleave="setHover('userType', false)">
          <h3>Anónimos vs Registrados</h3>
          <div class="chart-wrapper"><canvas ref="userTypeChartRef"></canvas></div>
        </div>
        
        <div class="chart-card" @click="openModal('gender', 'Distribución de Género')" @mouseenter="setHover('gender', true)" @mouseleave="setHover('gender', false)">
          <h3>Género</h3>
          <div class="chart-wrapper"><canvas ref="genderChartRef"></canvas></div>
        </div>
        
        <div class="chart-card" @click="openModal('category', 'Votos por Categoría')" @mouseenter="setHover('category', true)" @mouseleave="setHover('category', false)">
          <h3>Votos x Categoría</h3>
          <div class="chart-wrapper"><canvas ref="categoryChartRef"></canvas></div>
        </div>

        <div class="chart-card" @click="openModal('questionsCategory', 'Preguntas por Categoría')" @mouseenter="setHover('questionsCategory', true)" @mouseleave="setHover('questionsCategory', false)">
          <h3>Preguntas x Categoría</h3>
          <div class="chart-wrapper"><canvas ref="questionsCategoryChartRef"></canvas></div>
        </div>

        <div class="chart-card" @click="openModal('topQuestions', 'Top 5 Preguntas')" @mouseenter="setHover('topQuestions', true)" @mouseleave="setHover('topQuestions', false)">
          <h3>Top 5 Preguntas</h3>
          <div class="chart-wrapper"><canvas ref="topQuestionsChartRef"></canvas></div>
        </div>

        <div class="chart-card" @click="openModal('votesDay', 'Actividad por Día')" @mouseenter="setHover('votesDay', true)" @mouseleave="setHover('votesDay', false)">
          <h3>Actividad x Día</h3>
          <div class="chart-wrapper"><canvas ref="votesDayChartRef"></canvas></div>
        </div>

        <div class="chart-card full-span" @click="openModal('votesTime', 'Tendencia (7 Días)')" @mouseenter="setHover('votesTime', true)" @mouseleave="setHover('votesTime', false)">
          <h3>Tendencia (7 Días)</h3>
          <div class="chart-wrapper-large"><canvas ref="votesTimeChartRef"></canvas></div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ modalTitle }}</h2>
          <button class="close-btn" @click="closeModal"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body"><canvas ref="modalChartRef"></canvas></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import { useStore } from 'vuex';
import axiosInstance from '@/store/axiosInstance';
import Chart from 'chart.js/auto';

const store = useStore();
const stats = computed(() => store.state.globalStats);
const loading = ref(true); // Managed by store ideally, but local for now
const error = ref(null);

const userTypeChartRef = ref(null);
const genderChartRef = ref(null);
const categoryChartRef = ref(null);
const questionsCategoryChartRef = ref(null);
const topQuestionsChartRef = ref(null);
const votesTimeChartRef = ref(null);
const votesDayChartRef = ref(null);
const modalChartRef = ref(null);

// Chart instances
const charts = {};
const showModal = ref(false);
const modalTitle = ref('');
let modalChart = null;

// Color schemes
const BLACK = '#1a1a1a';
const WHITE = '#ffffff';

const destroyChart = (key) => {
  if (charts[key]) {
    charts[key].destroy();
    charts[key] = null;
  }
};

const setHover = (chartType, isHover) => {
  const color = isHover ? WHITE : BLACK;
  const chart = charts[chartType];
  if (!chart) return;
  
  // Update legend colors
  if (chart.options.plugins?.legend?.labels) {
    chart.options.plugins.legend.labels.color = color;
  }
  
  // Update scale colors
  if (chart.options.scales) {
    Object.values(chart.options.scales).forEach(scale => {
      if (scale.ticks) scale.ticks.color = color;
      if (scale.pointLabels) scale.pointLabels.color = color;
      if (scale.grid) scale.grid.color = isHover ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)';
      if (scale.angleLines) scale.angleLines.color = isHover ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)';
    });
  }
  
  chart.update('none');
};

const openModal = async (chartType, title) => {
  modalTitle.value = title;
  showModal.value = true;
  await nextTick();
  renderModalChart(chartType);
};

const closeModal = () => {
  showModal.value = false;
  if (modalChart) { modalChart.destroy(); modalChart = null; }
};

const renderModalChart = (chartType) => {
  if (!modalChartRef.value || !stats.value) return;
  if (modalChart) modalChart.destroy();
  const ctx = modalChartRef.value;
  
  // Detect theme
  const isLightMode = document.body.classList.contains('light-mode');
  const textColor = isLightMode ? '#1e3a5f' : '#e2e8f0';
  const gridColor = isLightMode ? 'rgba(30,58,95,0.15)' : 'rgba(255,255,255,0.15)';
  
  // Full day names for modal
  const dayNamesFull = { 1: 'Domingo', 2: 'Lunes', 3: 'Martes', 4: 'Miércoles', 5: 'Jueves', 6: 'Viernes', 7: 'Sábado' };
  
  const configs = {
    userType: { 
      type: 'doughnut', 
      data: { labels: ['Votos Anónimos', 'Votos Registrados'], datasets: [{ data: [stats.value.anonymous_votes, stats.value.registered_votes], backgroundColor: ['#94a3b8', '#3b82f6'], borderWidth: 2, borderColor: isLightMode ? '#fff' : '#1a1a2e' }] }, 
      options: { responsive: true, maintainAspectRatio: true, cutout: '50%', plugins: { legend: { position: 'bottom', labels: { color: textColor, font: { size: 14, weight: 'bold' }, padding: 15, boxWidth: 15 } } } } 
    },
    gender: { 
      type: 'pie', 
      data: { labels: stats.value.gender_distribution.map(g => g.gender || 'No especificado'), datasets: [{ data: stats.value.gender_distribution.map(g => g.count), backgroundColor: ['#ec4899', '#3b82f6', '#f59e0b', '#10b981'], borderWidth: 2, borderColor: isLightMode ? '#fff' : '#1a1a2e' }] }, 
      options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { color: textColor, font: { size: 14, weight: 'bold' }, padding: 15, boxWidth: 15 } } } } 
    },
    category: { 
      type: 'bar', 
      data: { labels: stats.value.votes_by_category.map(x => x.question__category__name), datasets: [{ label: 'Cantidad de Votos', data: stats.value.votes_by_category.map(x => x.count), backgroundColor: '#8b5cf6', borderRadius: 8, barPercentage: 0.7 }] }, 
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true, labels: { color: textColor, font: { size: 14, weight: 'bold' } } } }, scales: { y: { beginAtZero: true, ticks: { color: textColor, font: { size: 14, weight: 'bold' } }, grid: { color: gridColor } }, x: { ticks: { color: textColor, font: { size: 12, weight: 'bold' } }, grid: { display: false } } } } 
    },
    questionsCategory: { 
      type: 'doughnut', 
      data: { labels: stats.value.questions_by_category.map(x => x.category__name), datasets: [{ data: stats.value.questions_by_category.map(x => x.count), backgroundColor: ['#ec4899', '#3b82f6', '#f59e0b', '#10b981', '#8b5cf6'], borderWidth: 2, borderColor: isLightMode ? '#fff' : '#1a1a2e' }] }, 
      options: { responsive: true, maintainAspectRatio: true, cutout: '40%', plugins: { legend: { position: 'right', labels: { color: textColor, font: { size: 12, weight: 'bold' }, padding: 10, boxWidth: 12 } } } } 
    },
    topQuestions: { 
      type: 'bar', 
      data: { labels: stats.value.top_questions.map(q => q.title), datasets: [{ label: 'Votos', data: stats.value.top_questions.map(q => q.cantidad_votos), backgroundColor: '#f59e0b', borderRadius: 8, barPercentage: 0.6 }] }, 
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: textColor, font: { size: 14, weight: 'bold' } }, grid: { color: gridColor } }, y: { ticks: { color: textColor, font: { size: 11, weight: 'bold' } } } } } 
    },
    votesDay: { 
      type: 'radar', 
      data: { labels: stats.value.votes_by_day.map(d => dayNamesFull[d.day]), datasets: [{ label: 'Actividad', data: stats.value.votes_by_day.map(d => d.count), backgroundColor: 'rgba(59, 130, 246, 0.25)', borderColor: '#3b82f6', borderWidth: 3, pointBackgroundColor: '#3b82f6', pointRadius: 6 }] }, 
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true, labels: { color: textColor, font: { size: 14, weight: 'bold' } } } }, scales: { r: { angleLines: { color: gridColor }, grid: { color: gridColor }, pointLabels: { color: textColor, font: { size: 14, weight: 'bold' } }, ticks: { display: true, color: textColor, backdropColor: 'transparent' } } } } 
    },
    votesTime: { 
      type: 'line', 
      data: { labels: stats.value.votes_over_time.map(v => v.date), datasets: [{ label: 'Votos por Día', data: stats.value.votes_over_time.map(v => v.count), borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.15)', tension: 0.4, fill: true, borderWidth: 3, pointRadius: 5, pointBackgroundColor: '#10b981' }] }, 
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: textColor, font: { size: 14, weight: 'bold' } } } }, scales: { y: { beginAtZero: true, ticks: { color: textColor, font: { size: 14, weight: 'bold' } }, grid: { color: gridColor } }, x: { ticks: { color: textColor, font: { size: 12, weight: 'bold' } }, grid: { color: gridColor } } } } 
    }
  };
  
  modalChart = new Chart(ctx, configs[chartType]);
};

const fetchStats = async () => {
  loading.value = true;
  await store.dispatch('fetchGlobalStats');
  loading.value = false;
  
  // Wait for DOM to update so refs are available
  await nextTick();
  renderCharts();
};

// Watch for changes in real-time
watch(stats, async (newStats) => {
    // Only trigger if not currently loading (initial load handled by fetchStats)
    if (newStats && !loading.value) {
        await nextTick();
        renderCharts();
    }
}, { deep: true });

const renderCharts = () => {
  if (!stats.value) return;
  
  // Detect if dark mode is active (assuming 'dark' class on body or html)
  // You might need to adjust this check based on your app's theme implementation
  const isDarkMode = document.body.classList.contains('dark-mode') || document.documentElement.classList.contains('dark'); 
  const c = isDarkMode ? WHITE : BLACK; 
  const gridColor = isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

  if (userTypeChartRef.value) {
    destroyChart('userType');
    charts.userType = new Chart(userTypeChartRef.value, {
      type: 'doughnut',
      data: { labels: ['Anónimos', 'Registrados'], datasets: [{ data: [stats.value.anonymous_votes, stats.value.registered_votes], backgroundColor: ['#94a3b8', '#3b82f6'], borderWidth: 0 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: c, font: { size: 8, weight: 'bold' }, boxWidth: 8, padding: 4 } } } }
    });
  }
  if (genderChartRef.value) {
    destroyChart('gender');
    charts.gender = new Chart(genderChartRef.value, {
      type: 'pie',
      data: { labels: stats.value.gender_distribution.map(g => g.gender || 'N/A'), datasets: [{ data: stats.value.gender_distribution.map(g => g.count), backgroundColor: ['#ec4899', '#3b82f6', '#f59e0b', '#10b981'], borderWidth: 0 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: c, font: { size: 8, weight: 'bold' }, boxWidth: 8, padding: 4 } } } }
    });
  }

  if (categoryChartRef.value) {
    destroyChart('category');
    charts.category = new Chart(categoryChartRef.value, {
      type: 'bar',
      data: { labels: stats.value.votes_by_category.map(x => x.question__category__name), datasets: [{ data: stats.value.votes_by_category.map(x => x.count), backgroundColor: '#8b5cf6', borderRadius: 4, barThickness: 12 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { color: c, font: { size: 8, weight: 'bold' } }, grid: { color: gridColor } }, x: { ticks: { color: c, font: { size: 7, weight: 'bold' } }, grid: { display: false } } } }
    });
  }

  if (questionsCategoryChartRef.value) {
    destroyChart('questionsCategory');
    charts.questionsCategory = new Chart(questionsCategoryChartRef.value, {
      type: 'doughnut',
      data: { labels: stats.value.questions_by_category.map(x => x.category__name), datasets: [{ data: stats.value.questions_by_category.map(x => x.count), backgroundColor: ['#ec4899', '#3b82f6', '#f59e0b', '#10b981', '#8b5cf6'], borderWidth: 0 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: c, font: { size: 7, weight: 'bold' }, boxWidth: 8 } } } }
    });
  }

  if (topQuestionsChartRef.value) {
    destroyChart('topQuestions');
    charts.topQuestions = new Chart(topQuestionsChartRef.value, {
      type: 'bar',
      data: { labels: stats.value.top_questions.map(q => q.title.substring(0, 15) + '...'), datasets: [{ data: stats.value.top_questions.map(q => q.cantidad_votos), backgroundColor: '#f59e0b', borderRadius: 4, barThickness: 12 }] },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: c, font: { size: 8, weight: 'bold' } }, grid: { color: gridColor } }, y: { ticks: { color: c, font: { size: 7, weight: 'bold' } } } } }
    });
  }

  if (votesTimeChartRef.value) {
    destroyChart('votesTime');
    charts.votesTime = new Chart(votesTimeChartRef.value, {
      type: 'line',
      data: { labels: stats.value.votes_over_time.map(v => v.date), datasets: [{ data: stats.value.votes_over_time.map(v => v.count), borderColor: '#10b981', tension: 0.4, fill: true, backgroundColor: 'rgba(16, 185, 129, 0.1)' }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { color: c, font: { size: 8, weight: 'bold' } }, grid: { color: gridColor } }, x: { ticks: { color: c, font: { size: 8, weight: 'bold' } }, grid: { color: gridColor } } } }
    });
  }

  if (votesDayChartRef.value) {
    destroyChart('votesDay');
    const dayNames = { 1: 'D', 2: 'L', 3: 'M', 4: 'X', 5: 'J', 6: 'V', 7: 'S' };
    charts.votesDay = new Chart(votesDayChartRef.value, {
      type: 'radar',
      data: { labels: stats.value.votes_by_day.map(d => dayNames[d.day]), datasets: [{ data: stats.value.votes_by_day.map(d => d.count), backgroundColor: 'rgba(59, 130, 246, 0.2)', borderColor: '#3b82f6', pointBackgroundColor: '#3b82f6' }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { r: { angleLines: { color: gridColor }, grid: { color: gridColor }, pointLabels: { color: c, font: { size: 8, weight: 'bold' } }, ticks: { display: false } } } }
    });
  }
};

onMounted(() => { fetchStats(); });
</script>

<style scoped>
.statistics-container {
  padding: 0.5rem;
  color: var(--colortext);
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
  grid-column: 1 / -1; /* Force full width span */
}

.page-title {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  text-align: center;
  font-weight: 800;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-transform: uppercase;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.4rem;
  margin-bottom: 0.5rem;
}

.kpi-card {
  background: var(--colorsecondary);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 0.4rem 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.kpi-card:hover {
  transform: translateY(-2px);
  background: var(--colortertiary);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.kpi-card:hover .kpi-info h3,
.kpi-card:hover .kpi-value {
  color: #ffffff;
}

.kpi-icon {
  font-size: 0.8rem;
  color: var(--colorprimary);
  background: rgba(59, 130, 246, 0.1);
  padding: 0.3rem;
  border-radius: 4px;
}

.kpi-info h3 {
  font-size: 0.5rem;
  color: #1a1a1a;
  margin: 0;
  text-transform: uppercase;
  transition: color 0.3s;
}

.kpi-value {
  font-size: 0.9rem;
  font-weight: 800;
  margin: 0;
  color: #1a1a1a;
  transition: color 0.3s;
}

.charts-section-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.4rem;
}

.chart-card {
  background: var(--colorsecondary);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 0.4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.chart-card:hover {
  background: var(--colortertiary);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
  transform: translateY(-2px);
}

.chart-card:hover h3 {
  color: #ffffff;
}

.chart-card.full-span {
  grid-column: 1 / -1;
}

.chart-card h3 {
  margin-bottom: 0.25rem;
  color: #1a1a1a;
  font-size: 0.55rem;
  font-weight: 800;
  text-transform: uppercase;
  text-align: center;
  transition: color 0.3s;
}

.chart-wrapper {
  width: 100%;
  height: 100px;
  position: relative;
}

.chart-wrapper-large {
  width: 100%;
  height: 100px;
  position: relative;
}

.loading, .error {
  text-align: center;
  font-size: 0.9rem;
  margin-top: 2rem;
  color: var(--colortext);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 0.5rem;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: var(--colorbase);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
  animation: slideUp 0.3s ease;
  display: flex;
  flex-direction: column;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: var(--colorsecondary);
}

.modal-header h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--colortext);
}

.close-btn {
  background: none;
  border: none;
  color: var(--colortext);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #ef4444;
  transform: scale(1.1);
}

.modal-body {
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--colorbase);
  min-height: 350px;
}

.modal-body canvas {
  max-width: 100%;
  max-height: 300px;
}

@media (min-width: 768px) {
  .statistics-container { padding: 0.75rem; }
  .page-title { font-size: 1.2rem; margin-bottom: 0.75rem; }
  .kpi-card { padding: 0.6rem 0.8rem; gap: 0.6rem; }
  .kpi-icon { font-size: 1rem; padding: 0.5rem; }
  .kpi-info h3 { font-size: 0.6rem; }
  .kpi-value { font-size: 1.1rem; }
  .charts-section-grid { grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
  .chart-card { padding: 0.6rem; border-radius: 8px; }
  .chart-card h3 { font-size: 0.7rem; margin-bottom: 0.4rem; }
  .chart-wrapper { height: 140px; }
  .chart-wrapper-large { height: 160px; }
}
</style>
