<template>
  <div class="suggestions-view">
    <div class="header-section">
      <h1>💡 Buzón de Sugerencias</h1>
      <p class="subtitle">¡Ayúdanos a mejorar! Tu opinión cuenta.</p>
    </div>

    <!-- Create Suggestion Section -->
    <div class="create-section" v-if="isAuthenticated">
      <div class="create-card">
        <h3>Nueva Sugerencia</h3>
        <textarea 
          v-model="newContent" 
          placeholder="Describe tu idea para mejorar la plataforma..." 
          class="suggestion-input"
          rows="3"
        ></textarea>
        <div class="create-actions">
           <button @click="createSuggestion" class="btn-submit" :disabled="!newContent.trim() || creating">
             <i class="fas fa-paper-plane"></i> {{ creating ? 'Enviando...' : 'Publicar Sugerencia' }}
           </button>
        </div>
      </div>
    </div>
    <div v-else class="login-prompt">
      <p>Inicia sesión para compartir tus ideas y votar.</p>
      <router-link to="/auth" class="btn-login">Acceder</router-link>
    </div>

    <!-- List Section -->
    <div class="list-section">
      <div class="filters">
        <button 
            @click="setOrdering('-created_at')" 
            :class="{ active: ordering === '-created_at' }"
        >Más Recientes</button>
        <button 
            @click="setOrdering('likes')" 
            :class="{ active: ordering === 'likes' }"
        >Más Votadas</button>
      </div>

      <div v-if="loading" class="loading">Cargando sugerencias...</div>
      
      <div v-else-if="suggestions.length === 0" class="no-data">
        No hay sugerencias aún. ¡Sé el primero!
      </div>

      <div v-else class="suggestions-grid">
        <div v-for="sug in suggestions" :key="sug.id" class="suggestion-card">
           <div class="card-header">
             <div class="user-info">
               <img :src="sug.user_avatar" class="avatar-small" v-if="sug.user_avatar">
               <i class="fas fa-user-circle avatar-placeholder" v-else></i>
               <span class="nickname">{{ sug.user_nickname }}</span>
             </div>
             <span class="date">{{ formatDate(sug.created_at) }}</span>
           </div>
           
           <div class="card-body">
             <p>{{ sug.content }}</p>
           </div>

           <div class="card-footer">
             <button 
                @click="toggleLike(sug)" 
                class="btn-like" 
                :class="{ 'liked': sug.is_liked_by_user, 'disabled': !isAuthenticated }"
                :title="isAuthenticated ? 'Apoyar esta idea' : 'Inicia sesión para votar'"
             >
                <i class="fas fa-thumbs-up"></i>
                <span class="count">{{ sug.likes_count }}</span>
             </button>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';
import axios from '@/store/axiosInstance';
import { useToast } from 'vue-toastification';

const store = useStore();
const toast = useToast();
const isAuthenticated = computed(() => store.getters.isAuthenticated);

const suggestions = ref([]);
const loading = ref(true);
const newContent = ref('');
const creating = ref(false);
const ordering = ref('-created_at');

const fetchSuggestions = async () => {
    loading.value = true;
    try {
        const response = await axios.get(`suggestions/?ordering=${ordering.value}`);
        suggestions.value = response.data.results || response.data;
    } catch (error) {
        console.error(error);
        toast.error("Error al cargar sugerencias");
    } finally {
        loading.value = false;
    }
};

const setOrdering = (order) => {
    ordering.value = order;
    fetchSuggestions();
};

const createSuggestion = async () => {
    if (!newContent.value.trim()) return;
    creating.value = true;
    try {
        await axios.post('suggestions/', { content: newContent.value });
        newContent.value = '';
        toast.success("¡Sugerencia publicada!");
        fetchSuggestions(); // Refresh list
    } catch (error) {
        console.error(error);
        toast.error("Error al publicar sugerencia");
    } finally {
        creating.value = false;
    }
};

const toggleLike = async (sug) => {
    if (!isAuthenticated.value) return;
    
    // Optimistic update
    const originalLiked = sug.is_liked_by_user;
    const originalCount = sug.likes_count;
    
    sug.is_liked_by_user = !sug.is_liked_by_user;
    sug.likes_count += sug.is_liked_by_user ? 1 : -1;

    try {
        const response = await axios.post(`suggestions/${sug.id}/toggle_like/`);
        // Sync with server response to be sure
        sug.likes_count = response.data.likes_count;
        sug.is_liked_by_user = response.data.liked;
    } catch (error) {
        console.error(error);
        toast.error("Error al votar");
        // Revert
        sug.is_liked_by_user = originalLiked;
        sug.likes_count = originalCount;
    }
};

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric'
    });
};

onMounted(() => {
    fetchSuggestions();
});
</script>

<style scoped>
.suggestions-view {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
    color: white;
}

.header-section {
    text-align: center;
    margin-bottom: 40px;
}

.header-section h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #FBBF24, #F59E0B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: #9CA3AF;
    font-size: 1.1rem;
}

.create-section {
    margin-bottom: 40px;
}

.create-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.create-card h3 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #FBBF24;
}

.suggestion-input {
    width: 100%;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    padding: 15px;
    font-size: 1rem;
    resize: vertical;
    outline: none;
    transition: border-color 0.3s;
}

.suggestion-input:focus {
    border-color: #FBBF24;
}

.create-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
}

.btn-submit {
    background: linear-gradient(135deg, #F59E0B, #D97706);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: transform 0.2s;
}

.btn-submit:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn-submit:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.login-prompt {
    text-align: center;
    background: rgba(59, 130, 246, 0.1);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 40px;
    border: 1px solid rgba(59, 130, 246, 0.2);
}

.btn-login {
    display: inline-block;
    margin-top: 10px;
    background: #3B82F6;
    color: white;
    text-decoration: none;
    padding: 8px 20px;
    border-radius: 20px;
    font-weight: bold;
}

.filters {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 15px;
}

.filters button {
    background: transparent;
    border: none;
    color: #9CA3AF;
    font-size: 1rem;
    cursor: pointer;
    padding: 5px 10px;
    font-weight: 500;
    transition: color 0.3s;
}

.filters button.active {
    color: #FBBF24;
    border-bottom: 2px solid #FBBF24;
}

.filters button:hover:not(.active) {
    color: white;
}

.suggestion-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: transform 0.2s;
}

.suggestion-card:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.08);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 10px;
}

.avatar-small {
    width: 32px;
    height: 32px;
    border-radius: 50%;
}

.avatar-placeholder {
    font-size: 32px;
    color: #6B7280;
}

.nickname {
    font-weight: bold;
    color: #E5E7EB;
}

.date {
    color: #9CA3AF;
    font-size: 0.85rem;
}

.card-body p {
    color: #D1D5DB;
    line-height: 1.6;
    margin-bottom: 15px;
    white-space: pre-wrap;
}

.card-footer {
    display: flex;
    justify-content: flex-end;
}

.btn-like {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #9CA3AF;
    padding: 6px 15px;
    border-radius: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s;
}

.btn-like:hover:not(.disabled) {
    background: rgba(16, 185, 129, 0.1);
    color: #10B981;
    border-color: rgba(16, 185, 129, 0.3);
}

.btn-like.liked {
    background: rgba(16, 185, 129, 0.2);
    color: #10B981;
    border-color: rgba(16, 185, 129, 0.5);
}

.btn-like.disabled {
    cursor: default;
    opacity: 0.5;
}

.loading, .no-data {
    text-align: center;
    padding: 40px;
    color: #9CA3AF;
    font-style: italic;
}
</style>
