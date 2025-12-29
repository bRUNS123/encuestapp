<template>
  <div class="user-profile public-view">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Cargando perfil...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <router-link to="/" class="btn-back">Volver al Inicio</router-link>
    </div>

    <!-- Content -->
    <div v-else-if="profile" class="profile-content">
      <div class="header-actions">
        <button @click="$router.go(-1)" class="btn-back-icon"><i class="fas fa-arrow-left"></i> Volver</button>
      </div>

      <div class="profile-header">
        <div class="bg-overlay"></div>
        <div class="avatar-container">
          <img v-if="profile.photo_url" :src="profile.photo_url" alt="Avatar" class="avatar-img">
          <i v-else class="fas fa-user"></i>
        </div>
        <h2 class="user-email">{{ profile.nickname || 'Usuario' }}</h2>
        <div class="user-badge">Miembro de la Comunidad</div>
        
        <!-- Friendship Actions -->
        <div class="friend-actions">
            <button v-if="friendshipStatus === 'none'" @click="sendRequest" class="btn-friend-action">
                <i class="fas fa-user-plus"></i> Añadir Amigo
            </button>
            <button v-else-if="friendshipStatus === 'pending_sent'" class="btn-friend-action disabled">
                <i class="fas fa-clock"></i> Pendiente
            </button>
            <div v-else-if="friendshipStatus === 'pending_received'" class="friend-response-actions">
                    <button @click="acceptRequest" class="btn-friend-accept"><i class="fas fa-check"></i> Aceptar</button>
                    <button @click="rejectRequest" class="btn-friend-reject"><i class="fas fa-times"></i> Rechazar</button>
            </div>
            <div v-else-if="friendshipStatus === 'friends'" class="friend-indicator">
                <i class="fas fa-user-check"></i> Amigos
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon votes"><i class="fas fa-check-circle"></i></div>
                <div class="stat-info">
                    <span class="stat-value">{{ profile.votes_count || 0 }}</span>
                    <span class="stat-label">Votos</span>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon year"><i class="fas fa-birthday-cake"></i></div>
                <div class="stat-info">
                    <span class="stat-value">{{ profile.birth_year || 'N/A' }}</span>
                    <span class="stat-label">Año Nac.</span>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon gender"><i class="fas fa-venus-mars"></i></div>
                <div class="stat-info">
                    <span class="stat-value">{{ profile.gender || 'N/A' }}</span>
                    <span class="stat-label">Género</span>
                </div>
            </div>
        </div>
      </div>

      <!-- Votaciones Grid -->
      <div v-if="friendshipStatus === 'friends'" class="votaciones-section">
        <h3>Votaciones Publicas</h3>
        <div v-if="loadingVotes" class="loading-votes">Cargando votos...</div>
        <div v-else-if="votes && votes.length > 0" class="questions-grid-profile">
             <div v-for="item in votes" :key="item.question.id" class="vote-card-wrapper">
                <Pregunta 
                    :questionId="item.question.id" 
                    :pregunta="item.question.title" 
                    :questionType="item.question.question_type || 'binary'"
                    :allOptions="item.question.options || []"
                    :respuesta1Id="item.question.options?.[0]?.id" 
                    :respuesta2Id="item.question.options?.[1]?.id" 
                    :respuesta1="item.question.options?.[0] || {title: 'Sin respuesta', votes: 0}" 
                    :respuesta2="item.question.options?.[1] || {title: 'Sin respuesta', votes: 0}" 
                    :categoria="item.question.category" 
                    :fecha="item.question.creation_date" 
                    :votos="item.question.cantidad_votos || 0"
                    :profileId="profile.id"
                    :readOnly="true"
                    :forcedVoteId="item.friend_vote_id"
                />
             </div>
        </div>
        <div v-else class="no-data">
            Este usuario no ha realizado votos públicos recientemente.
        </div>
      </div>
      <div v-else class="private-profile-msg">
        <i class="fas fa-lock"></i>
        <p>Debes ser amigo de {{ profile.nickname || 'este usuario' }} para ver sus votaciones detalladas.</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useStore } from 'vuex';
import { useRoute } from 'vue-router';
import Pregunta from '/src/components/preguntas/Pregunta.vue';
import { useToast } from 'vue-toastification';

const store = useStore();
const route = useRoute();
const toast = useToast();

const profile = ref(null);
const loading = ref(true);
const error = ref(null);
const votes = ref([]);
const loadingVotes = ref(false);

const userId = route.params.id;

// Computed friendship status
const friendshipStatus = computed(() => {
    if (!profile.value) return 'none';
    // Check local profile state first if available, or fetch fresh?
    // We will use the store's profile list to get current status if possible, 
    // but better to rely on what fetchUserProfile returns or separate check.
    // For now, let's assume fetchUserProfile populates it or we map it from store.
    
    // Check if in profilesList store
    const inStore = store.state.profilesList.find(p => p.id === parseInt(userId));
    if (inStore) return inStore.friendship_status;
    
    return profile.value.friendship_status || 'none';
});

const loadProfile = async () => {
    loading.value = true;
    try {
        // We can reuse fetchUserProfile action, but it usually sets 'user' state (current user).
        // We need a specific generic fetch. We'll use axios directly or a new store action.
        // It's safer to use axios here to avoid overwriting 'currentUser' state.
        // Actually store has fetchUserProfile which sets SET_USER? 
        // Let's check store actions.
        // Only fetchUserProfile(userId) -> SET_USER. This is dangerous if specific for CURRENT user.
        // But checking store, fetchCurrentUser -> SET_USER.
        // fetchUserProfile -> SET_USER.
        // It seems the store is designed for "Current Viewing User" or "Logged In User"?
        // If we navigate to another profile, we shouldn't overwrite "state.user" (which is the logged in user).
        
        // We will fetch manually via axios instance imported from store or similar.
        // Or we use the store's "profilesList" if available.
        
        // Let's ensure we have the list
        if (store.state.profilesList.length === 0) {
            await store.dispatch('fetchProfiles');
        }
        
        const found = store.state.profilesList.find(p => p.id === parseInt(userId));
        if (found) {
            profile.value = found;
        } else {
            // Fetch individually if not in list (unlikely but possible)
            error.value = "Usuario no encontrado.";
        }
    } catch (e) {
        error.value = "Error cargando perfil.";
    } finally {
        loading.value = false;
        if (profile.value && friendshipStatus.value === 'friends') {
            loadVotes();
        }
    }
};

const loadVotes = async () => {
    loadingVotes.value = true;
    try {
        // We use the store action but retrieve the result directly or observe state
        // store.dispatch('fetchFriendVotes', userId) updates state.friendVotes
        await store.dispatch('fetchFriendVotes', userId);
        votes.value = store.state.friendVotes;
    } catch (e) {
        console.error(e);
    } finally {
        loadingVotes.value = false;
    }
};

const sendRequest = async () => {
    try {
        await store.dispatch('sendFriendRequest', profile.value.id);
        toast.success("Solicitud enviada");
        // Update local state or re-fetch
        profile.value.friendship_status = 'pending_sent';
    } catch (e) {
        toast.error("Error al enviar solicitud");
    }
};

const acceptRequest = async () => {
    try {
        await store.dispatch('acceptFriendRequest', profile.value.id);
        toast.success("Solicitud aceptada");
        // Update local state
        profile.value.friendship_status = 'friends';
        loadVotes();
    } catch (e) {
        toast.error("Error al aceptar");
    }
};

const rejectRequest = async () => {
     try {
        await store.dispatch('rejectFriendRequest', profile.value.id);
        toast.info("Solicitud rechazada");
        profile.value.friendship_status = 'none';
    } catch (e) {
        toast.error("Error al rechazar");
    }
};

onMounted(() => {
    loadProfile();
});
</script>

<style scoped>
.user-profile.public-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  color: white;
  animation: fadeIn 0.5s ease-out;
}

.header-actions {
    margin-bottom: 20px;
}

.btn-back-icon {
    background: transparent;
    color: #9CA3AF;
    border: none;
    font-size: 1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px;
    transition: color 0.3s;
}

.btn-back-icon:hover {
    color: white;
}

/* Similar header styles as ProfileView but adapted */
.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  margin-bottom: 40px;
}

.bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 120px;
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.2), transparent);
  z-index: 0;
}

.avatar-container {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #65BCF6, #3B82F6);
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
  border: 3px solid rgba(255, 255, 255, 0.1);
  z-index: 1;
}

.avatar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.avatar-container i {
  font-size: 2.5rem;
  color: white;
}

.user-email {
  font-size: 1.5rem;
  color: white;
  margin: 0 0 10px 0;
  font-weight: 700;
  z-index: 1;
}

.user-badge {
  background: rgba(16, 185, 129, 0.2);
  color: #34D399;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  z-index: 1;
  margin-bottom: 20px;
}

.friend-actions {
    margin-bottom: 30px;
    z-index: 1;
}

.btn-friend-action, .btn-friend-accept, .btn-friend-reject {
    padding: 10px 20px;
    border-radius: 30px;
    border: none;
    cursor: pointer;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: transform 0.2s;
}

.btn-friend-action { background: #3B82F6; color: white; }
.btn-friend-action:hover { background: #2563EB; transform: translateY(-2px); }
.btn-friend-action.disabled { background: #4B5563; cursor: default; transform: none; }

.friend-response-actions { display: flex; gap: 10px; }
.btn-friend-accept { background: #10B981; color: white; }
.btn-friend-reject { background: #EF4444; color: white; }
.friend-indicator { color: #10B981; font-weight: bold; font-size: 1.1rem; display: flex; align-items: center; gap: 8px; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 800px;
  z-index: 1;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s ease;
}

.stat-card:hover { transform: translateY(-3px); background: rgba(255,255,255,0.08); }
.stat-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
.stat-icon.votes { background: rgba(245, 158, 11, 0.2); color: #FBBF24; }
.stat-icon.year { background: rgba(236, 72, 153, 0.2); color: #F472B6; }
.stat-icon.gender { background: rgba(139, 92, 246, 0.2); color: #A78BFA; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 1.2rem; font-weight: 700; color: white; }
.stat-label { font-size: 0.8rem; color: #9CA3AF; }

.votaciones-section {
    margin-top: 20px;
}

.votaciones-section h3 {
    margin-bottom: 25px;
    font-size: 1.5rem;
    color: white;
    padding-left: 10px;
    border-left: 4px solid #3B82F6;
}

.questions-grid-profile {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 25px;
}

.private-profile-msg {
    text-align: center;
    padding: 60px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 20px;
    margin-top: 20px;
    color: #9CA3AF;
}

.private-profile-msg i { font-size: 3rem; margin-bottom: 20px; color: #6B7280; }
.no-data { text-align: center; color: #9CA3AF; padding: 40px; font-style: italic; }

.loading-container {
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    justify-content: center; 
    min-height: 50vh;
}
.spinner { width: 40px; height: 40px; border: 4px solid rgba(255,255,255,0.1); border-top-color: #3B82F6; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

</style>
