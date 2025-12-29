<template>
  <div class="create-question-view">
    <div class="header">
      <h1><i class="fas fa-brain"></i> Crea tu Encuesta</h1>
      <p class="subtitle">Propón preguntas a la comunidad y vota por las mejores ideas</p>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button 
        :class="['tab-button', { active: activeTab === 'vote' }]" 
        @click="activeTab = 'vote'"
      >
        <i class="fas fa-vote-yea"></i>
        Votar Propuestas ({{ pendingCount }})
      </button>
      <button 
        :class="['tab-button', { active: activeTab === 'create' }]" 
        @click="activeTab = 'create'"
      >
        <i class="fas fa-plus-circle"></i>
        Crear Nueva
      </button>
    </div>

    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-item">
        <i class="fas fa-users"></i>
        <span>{{ stats.total_users }} Usuarios</span>
      </div>
      <div class="stat-item">
        <i class="fas fa-chart-line"></i>
        <span>{{ stats.approval_threshold }} votos para aprobar</span>
      </div>
      <div class="stat-item success">
        <i class="fas fa-check-circle"></i>
        <span>{{ stats.approved_proposals }} aprobadas</span>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- PESTAÑA 1: Votar Propuestas -->
      <div v-if="activeTab === 'vote'" class="vote-tab">
        <div v-if="loading" class="loading">
          <i class="fas fa-spinner fa-spin"></i> Cargando propuestas...
        </div>
        
        <div v-else-if="proposals.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No hay propuestas pendientes</p>
          <p class="sub">¡Sé el primero en crear una!</p>
        </div>

        <div v-else class="proposals-grid">
          <div 
            v-for="proposal in proposals" 
            :key="proposal.id" 
            class="proposal-card"
          >
            <div class="proposal-header">
              <div class="category-badge">
                <i :class="getCategoryIcon(proposal.category_name)"></i>
                {{ proposal.category_name }}
              </div>
              <div class="vote-count">
                <i class="fas fa-heart"></i>
                {{ proposal.votes_count }} / {{ proposal.approval_threshold }}
              </div>
            </div>

            <h3 class="proposal-title">{{ proposal.title }}</h3>

            <div class="options">
              <div class="option">
                <i class="fas fa-check"></i> {{ proposal.option1_text }}
              </div>
              <div class="option">
                <i class="fas fa-check"></i> {{ proposal.option2_text }}
              </div>
            </div>

            <div class="proposal-footer">
              <div class="creator">
                <i class="fas fa-user-circle"></i>
                por {{ proposal.creator_username }}
              </div>
              <button 
                v-if="!proposal.user_has_voted" 
                @click="voteProposal(proposal.id)"
                class="vote-button"
                :disabled="voting"
              >
                <i class="fas fa-thumbs-up"></i>
                Me gusta
              </button>
              <span v-else class="voted-badge">
                <i class="fas fa-check-circle"></i> Ya votaste
              </span>
            </div>

            <!-- Progress Bar -->
            <div class="progress-wrapper">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: getProgressPercent(proposal) + '%' }"
                ></div>
              </div>
              <span class="progress-text">
                {{ getProgressPercent(proposal) }}% completado
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- PESTAÑA 2: Crear Encuesta -->
      <div v-if="activeTab === 'create'" class="create-tab">
        <div class="create-form">
          <div class="form-group">
            <label for="title">
              <i class="fas fa-question-circle"></i>
              Pregunta
            </label>
            <input 
              id="title"
              v-model="newProposal.title" 
              type="text"
              placeholder="¿Cuál es la mejor pizza?"
              maxlength="500"
              required
            />
            <span class="char-count">{{ newProposal.title.length }}/500</span>
          </div>

          <div class="form-group">
            <label for="category">
              <i class="fas fa-tag"></i>
              Categoría
            </label>
            <select id="category" v-model="newProposal.category" required>
              <option value="">-- Selecciona una categoría --</option>
              <option value="politica">Política</option>
              <option value="sociedad">Sociedad</option>
              <option value="deporte">Deporte</option>
              <option value="tecnologia">Tecnología</option>
              <option value="entretenimiento">Entretenimiento</option>
              <option value="mundial">Internacional</option>
              <option value="educacion">Educación</option>
              <option value="salud">Salud</option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="option1">
                <i class="fas fa-a"></i>
                Opción 1
              </label>
              <input 
                id="option1"
                v-model="newProposal.option1_text" 
                type="text"
                placeholder="Hawaiana"
                maxlength="200"
                required
              />
            </div>

            <div class="form-group">
              <label for="option2">
                <i class="fas fa-b"></i>
                Opción 2
              </label>
              <input 
                id="option2"
                v-model="newProposal.option2_text" 
                type="text"
                placeholder="Pepperoni"
                maxlength="200"
                required
              />
            </div>
          </div>

          <div class="info-box">
            <i class="fas fa-info-circle"></i>
            <div>
              <strong>¿Cómo funciona?</strong>
              <p>Tu propuesta necesita {{ stats.approval_threshold }} votos de la comunidad para ser aprobada y publicada automáticamente.</p>
            </div>
          </div>

          <button 
            @click="submitProposal" 
            class="submit-button"
            :disabled="submitting || !isFormValid"
          >
            <i class="fas fa-paper-plane"></i>
            {{ submitting ? 'Enviando...' : 'Enviar Propuesta' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'vue-toastification';
import axios from '@/store/axiosInstance.js';

const store = useStore();
const toast = useToast();

const activeTab = ref('vote');
const loading = ref(false);
const voting = ref(false);
const submitting = ref(false);

const proposals = ref([]);
const stats = ref({
  total_users: 0,
  approval_threshold: 20,
  pending_proposals: 0,
  approved_proposals: 0
});

const newProposal = ref({
  title: '',
  category: '',
  option1_text: '',
  option2_text: ''
});

const pendingCount = computed(() => proposals.value.length);

const isFormValid = computed(() => {
  return newProposal.value.title.length > 0 &&
         newProposal.value.category.length > 0 &&
         newProposal.value.option1_text.length > 0 &&
         newProposal.value.option2_text.length > 0;
});

const getCategoryIcon = (category) => {
  const icons = {
    'politica': 'fas fa-balance-scale',
    'sociedad': 'fas fa-users',
    'deporte': 'fas fa-futbol',
    'tecnologia': 'fas fa-laptop',
    'entretenimiento': 'fas fa-film',
    'mundial': 'fas fa-earth-americas',
    'educacion': 'fas fa-graduation-cap',
    'salud': 'fas fa-medkit'
  };
  return icons[category] || 'fas fa-tag';
};

const getProgressPercent = (proposal) => {
  return Math.min(100, Math.round((proposal.votes_count / proposal.approval_threshold) * 100));
};

const fetchProposals = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/proposals/?status=pending');
    // Handle paginated response
    proposals.value = response.data.results || response.data;
  } catch (error) {
    console.error('Error fetching proposals:', error);
    toast.error('Error al cargar propuestas');
  } finally {
    loading.value = false;
  }
};

const fetchStats = async () => {
  try {
    const response = await axios.get('/proposals/stats/');
    stats.value = response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
  }
};

const voteProposal = async (proposalId) => {
  if (!store.getters.isAuthenticated) {
    toast.warning('Debes iniciar sesión para votar');
    return;
  }

  voting.value = true;
  try {
    const response = await axios.post(`/proposals/${proposalId}/vote/`);
    toast.success(response.data.message);
    
    if (response.data.auto_approved) {
      toast.success('¡La propuesta fue aprobada y publicada!', {
        timeout: 5000
      });
    }
    
    await fetchProposals();
    await fetchStats();
  } catch (error) {
    const errorMsg = error.response?.data?.error || 'Error al votar';
    toast.error(errorMsg);
  } finally {
    voting.value = false;
  }
};

const submitProposal = async () => {
  if (!store.getters.isAuthenticated) {
    toast.warning('Debes iniciar sesión para crear propuestas');
    return;
  }

  if (!isFormValid.value) {
    toast.error('Por favor completa todos los campos');
    return;
  }

  submitting.value = true;
  try {
    await axios.post('/proposals/', newProposal.value);
    toast.success('¡Propuesta creada exitosamente!');
    
    newProposal.value = {
      title: '',
      category: '',
      option1_text: '',
      option2_text: ''
    };
    
    activeTab.value = 'vote';
    
    await fetchProposals();
    await fetchStats();
  } catch (error) {
    console.error('Error creating proposal:', error);
    toast.error('Error al crear propuesta');
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  fetchProposals();
  fetchStats();
});
</script>

<style scoped>
.create-question-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 2.5rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
}

.header h1 i {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: var(--colorsecondary);
  font-size: 1.1rem;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: center;
}

.tab-button {
  padding: 12px 30px;
  border: none;
  border-radius: 12px;
  background: var(--colorquaternary);
  color: var(--colortext);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-button:hover {
  background: var(--colortertiary);
  transform: translateY(-2px);
}

.tab-button.active {
  background: var(--gradient-primary);
  color: white;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.stats-bar {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.stat-item {
  background: var(--glass-bg);
  backdrop-filter: var(--backdrop-blur);
  padding: 12px 20px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--colortext);
}

.stat-item i {
  color: var(--colorprimary);
  font-size: 1.2rem;
}

.stat-item.success i {
  color: #4ADE80;
}

.proposals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.proposal-card {
  background: var(--glass-bg);
  backdrop-filter: var(--backdrop-blur);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
}

.proposal-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.proposal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.category-badge {
  background: var(--gradient-primary);
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

.vote-count {
  color: var(--colorprimary);
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 5px;
}

.proposal-title {
  font-size: 1.2rem;
  color: var(--colortext);
  margin-bottom: 15px;
  line-height: 1.4;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
}

.option {
  background: var(--colorquaternary);
  padding: 10px;
  border-radius: 8px;
  color: var(--colortext);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.option i {
  color: var(--colorprimary);
}

.proposal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.creator {
  color: var(--colorsecondary);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 5px;
}

.vote-button {
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.vote-button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.vote-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.voted-badge {
  color: #4ADE80;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--colorquaternary);
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--gradient-primary);
  transition: width 0.5s ease;
}

.progress-text {
  color: var(--colorsecondary);
  font-size: 0.85rem;
  font-weight: 600;
  min-width: 80px;
  text-align: right;
}

.create-form {
  max-width: 700px;
  margin: 0 auto;
  background: var(--glass-bg);
  backdrop-filter: var(--backdrop-blur);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  color: var(--colortext);
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  background: var(--colorquaternary);
  border: 2px solid var(--glass-border);
  border-radius: 8px;
  color: var(--colortext);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--colorprimary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.char-count {
  display: block;
  text-align: right;
  color: var(--colorsecondary);
  font-size: 0.85rem;
  margin-top: 5px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.info-box {
  background: rgba(59, 130, 246, 0.1);
  border-left: 4px solid var(--colorprimary);
  padding: 15px;
  border-radius: 8px;
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.info-box i {
  color: var(--colorprimary);
  font-size: 1.2rem;
}

.info-box strong {
  color: var(--colortext);
  display: block;
  margin-bottom: 5px;
}

.info-box p {
  color: var(--colorsecondary);
  margin: 0;
  font-size: 0.9rem;
}

.submit-button {
  width: 100%;
  padding: 15px;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--colorsecondary);
}

.loading i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
}

.empty-state .sub {
  color: var(--colortext);
  margin-top: 10px;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
  }

  .proposals-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .tabs {
    flex-direction: column;
  }

  .stats-bar {
    flex-direction: column;
  }
}
</style>
