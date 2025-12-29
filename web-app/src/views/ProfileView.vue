<template>
  <div class="user-profile">
    <div class="tabs">
      <button @click="activeTab = 'personal'" :class="{ active: activeTab === 'personal' }">PERSONAL</button>
      <button @click="activeTab = 'votaciones'" :class="{ active: activeTab === 'votaciones' }">VOTACIONES</button>
      <button @click="activeTab = 'compatibilidad'" :class="{ active: activeTab === 'compatibilidad' }">COMPATIBILIDAD</button>
      <button @click="activeTab = 'comunidad'" :class="{ active: activeTab === 'comunidad' }">COMUNIDAD</button>
    </div>

    <div v-if="activeTab === 'personal'" class="tab-content personal-wrapper">
      <div class="personal-actions" v-if="user && !isEditingPersonal">
          <button @click="startEditing" class="btn-edit-personal"><i class="fas fa-edit"></i> Editar</button>
      </div>

      <div class="personal-actions" v-else-if="isEditingPersonal">
          <button @click="savePersonal" class="btn-save-personal"><i class="fas fa-save"></i> Guardar</button>
          <button @click="cancelEditing" class="btn-cancel-personal"><i class="fas fa-times"></i> Cancelar</button>
      </div>
      <div class="profile-header" v-if="user">
        <div class="avatar-container">
          <img v-if="user?.photo_url" :src="user.photo_url" alt="User Avatar" class="avatar-img">
          <i v-else class="fas fa-user"></i>
        </div>
        <h2 class="user-email">{{ user.nickname || user.email }}</h2>
        <div class="user-badge">Usuario Verificado</div>
      <div class="stats-grid">
        <div class="stat-card clickable" @click="activeTab = 'votaciones'">
          <div class="stat-icon votes">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ user.votes_count || user.votesCount || 0 }}</span>
            <span class="stat-label">Votos Realizados</span>
          </div>
        </div>

        <div class="stat-card clickable" @click="activeTab = 'comunidad'">
          <div class="stat-icon year">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-info">
            <div class="value-row">
                <span class="stat-value">{{ user.friends_count || 0 }}</span>
            </div>
            <span class="stat-label">Amig@s</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon gender">
            <i class="fas fa-venus-mars"></i>
          </div>
          <div class="stat-info">
            <div class="value-row" v-if="!isEditingPersonal">
                <span class="stat-value">{{ user.gender || 'No especificado' }}</span>
                <button v-if="user" @click.stop="togglePrivacy('gender')" class="privacy-btn" :title="user.is_gender_public ? 'Público' : 'Privado'">
                    <i :class="user.is_gender_public ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
                </button>
            </div>
            <select v-else v-model="editForm.gender" class="edit-input">
                <option value="Masculino">Masculino</option>
                <option value="Femenino">Femenino</option>
                <option value="Otro">Otro</option>
            </select>
            <span class="stat-label">Género</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon nickname">
            <i class="fas fa-id-card"></i>
          </div>
          <div class="stat-info">
            <span class="stat-value" v-if="!isEditingPersonal">{{ user.nickname || 'Sin Alias' }}</span>
            <input v-else v-model="editForm.nickname" type="text" class="edit-input nickname-input" placeholder="Alias">
            <span class="stat-label">Usuario (Alias)</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon email">
            <i class="fas fa-envelope"></i>
          </div>
          <div class="stat-info">
            <div class="value-row">
                <span class="stat-value">{{ user.email || 'Sin email' }}</span>
                <button v-if="user" @click.stop="togglePrivacy('email')" class="privacy-btn" :title="user.is_email_public ? 'Público' : 'Privado'">
                    <i :class="user.is_email_public ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
                </button>
            </div>
            <span class="stat-label">Email</span>
          </div>
        </div>
      </div>

      <!-- New Personal Questions Section -->
      <div class="section-divider">
          <h3>Personal</h3>
          <div v-if="loadingPersonal" class="loading">Cargando preguntas personales...</div>
          <div v-else class="questions-grid-profile">
              <div v-for="question in personalQuestions" :key="question.id" class="profile-question-item">
                  <div class="pq-icon" :class="getQuestionIconClass(question.title)">
                      <i :class="getQuestionIcon(question.title)"></i>
                  </div>
                  <div class="pq-content">
                      <label>{{ question.title }}</label>
                      
                      <!-- View Mode -->
                      <div v-if="!isEditingPersonal" class="pq-value">
                          <span v-if="getAnswerText(question)">{{ getAnswerText(question) }}</span>
                          <span v-else class="placeholder">No especificado</span>
                          
                          <!-- Privacy Toggle -->
                          <button v-if="user && getAnswerText(question)" @click.stop="togglePrivacy(question)" class="privacy-btn-small" :title="question.user_vote_is_public !== false ? 'Público' : 'Privado'">
                              <i :class="question.user_vote_is_public !== false ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
                          </button>
                      </div>

                      <!-- Edit Mode -->
                      <div v-else class="pq-input">
                          <select v-if="question.question_type === 'dropdown'" v-model="dynamicAnswers[question.id].option_id" class="edit-input">
                              <option :value="null" disabled>Selecciona una opción</option>
                              <option v-for="opt in question.options" :key="opt.id" :value="opt.id">{{ opt.title }}</option>
                          </select>
                          
                          <input v-else-if="question.question_type === 'open'" 
                                 type="text" 
                                 v-model="dynamicAnswers[question.id].text_answer" 
                                 class="edit-input" 
                                 placeholder="Escribe tu respuesta">

                          <div v-else-if="question.question_type === 'date'" class="edit-date-group">
                              <input 
                                type="date" 
                                v-model="dynamicAnswers[question.id].text_answer"
                                class="edit-input edit-date"
                              >
                          </div>

                          <div v-else-if="question.question_type === 'slider'" class="edit-slider-group">
                              <input 
                                type="number" 
                                v-model="dynamicAnswers[question.id].text_answer"
                                :min="question.options?.[0]?.title || 0"
                                :max="question.options?.[1]?.title || 100"
                                class="edit-input slider-number"
                              >
                              <input 
                                type="range" 
                                v-model="dynamicAnswers[question.id].text_answer"
                                :min="question.options?.[0]?.title || 0"
                                :max="question.options?.[1]?.title || 100"
                                :step="question.options?.[2]?.title || 1"
                                class="edit-range"
                              >
                          </div>
                          
                          <div v-else>Tipo no soportado</div>
                      </div>
                  </div>
              </div>
              </div>
          </div>
      </div>
    </div>
    <div v-else class="loading-profile">
      <p v-if="loading">Cargando perfil...</p>
      <h2 v-else class="anonymous-title">Usuario Anónimo</h2>
    </div>

    <div v-if="activeTab === 'votaciones'" class="tab-content votaciones-info">
      <div class="votaciones-header">
        <h2>Votaciones <span class="header-count" v-if="user">({{ user.votes_count || 0 }})</span></h2>
        <div class="filters">
            <select v-model="selectedCategory" class="filter-select">
                <option value="">Todas las Categorías</option>
                <option value="deporte">Deporte</option>
                <option value="politica">Política</option>
                <option value="tecnologia">Tecnología</option>
                <option value="salud">Salud</option>
                <option value="sociedad">Sociedad</option>
                <option value="entretenimiento">Entretenimiento</option>
                <option value="mundial">Mundial</option>
                <option value="educacion">Educación</option>
            </select>
            <select v-model="sortBy" class="filter-select">
                <option value="recent">Más Recientes</option>
                <option value="most_voted">Más Votadas</option>
            </select>
            
            <!-- Privacy Toggle integrated in filters -->
            <div class="filter-privacy" v-if="user && activeTab !== 'votaciones'">
                 <span class="privacy-label-small">Ver:</span>
                 <label class="switch-compact">
                    <input type="checkbox" v-model="showHiddenVotes">
                    <span class="slider-compact round"></span>
                 </label>
                 <span class="privacy-status-text">{{ showHiddenVotes ? 'Ocultos' : 'Públicos' }}</span>
            </div>
        </div>
      </div>
      <div v-if="!filteredPreguntas || filteredPreguntas.length === 0">No has votado en ninguna encuesta aún o no coinciden con los filtros.</div>
      <div class="questions-grid">
          <Pregunta 
            v-for="pregunta in filteredPreguntas"
            :key="pregunta.id"
            :questionId="pregunta.id"
            :pregunta="pregunta.title"
            :questionType="pregunta.question_type || 'binary'"
            :allOptions="pregunta.options || []"
            :respuesta1="pregunta.options[0] || { title: 'Sin respuesta', votes: 0 }"
            :respuesta2="pregunta.options[1] || { title: 'Sin respuesta', votes: 0 }"
            :respuesta1Id="pregunta.options[0] ? pregunta.options[0].id : null"
            :respuesta2Id="pregunta.options[1] ? pregunta.options[1].id : null"
            :categoria="pregunta.category"
            :fecha="pregunta.creation_date"
            :expirationDate="pregunta.expiration_date"
            :votos="pregunta.cantidad_votos"
            :profileId="user ? user.id : null"
            :allowPrivacy="true"
            :isPublic="pregunta.user_vote_is_public !== false"
          />
      </div>
    </div>

    <div v-if="activeTab === 'compatibilidad'" class="tab-content compatibility-wrapper">
        <h2>Compatibilidad con otros usuarios</h2>
        <div v-if="loading" class="loading">Cargando...</div>
        <div v-else-if="!compatibilityList || compatibilityList.length === 0" class="no-data">
            No se encontraron coincidencias suficientes o no has votado aún.
        </div>
        <div v-else class="compatibility-grid">
            <div v-for="match in compatibilityList" :key="match.id" class="match-card" @click="showDetails(match)">
                <div class="match-avatar">
                   <i class="fas fa-user-circle"></i>
                </div>
                <div class="match-info">
                    <div class="match-email">{{ match.nickname || match.email }}</div>
                    <div class="match-score-bar">
                        <div class="score-fill" :style="{ width: match.compatibility + '%' }"></div>
                    </div>
                    <div class="match-details">
                        <span class="score-text">
                            {{ match.matches || match.matching_votes }} de {{ match.common_count || match.total_common }} coinciden ({{ match.score || match.compatibility }}%)
                        </span>
                        <span v-if="match.friend_total_votes" class="score-text-sub" style="display:block; font-size: 0.75rem; color: #9CA3AF; margin-top: 4px;">
                            <i class="fas fa-poll" style="margin-right:4px;"></i> Total votos usuario: {{ match.friend_total_votes }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal de Detalles -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content compatibility-modal">
            <div class="modal-header">
                <div class="modal-title-group">
                    <div class="compatibility-badge-large">{{ selectedMatchPercentage }}%</div>
                    <div class="modal-user-info">
                        <h3>Coincidencias con</h3>
                        <span class="match-name">{{ selectedMatchName }}</span>
                    </div>
                </div>
                <button @click="closeModal" class="close-btn"><i class="fas fa-times"></i></button>
            </div>
            <div class="modal-body">
                <div v-if="loadingDetails" class="loading">
                    <i class="fas fa-spinner fa-spin"></i> Cargando coincidencias...
                </div>
                <div v-else-if="matchDetails.length === 0" class="no-matches">
                    No se encontraron detalles de coincidencias.
                </div>
                <ul v-else class="details-list">
                    <li v-for="(item, index) in matchDetails" :key="index" class="detail-item">
                        <div class="detail-content">
                            <!-- Header con Icono y Categoría en línea -->
                            <div class="detail-header" style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                                <div class="category-icon-small" style="width: 32px; height: 32px; background: rgba(96, 165, 250, 0.15); color: #60A5FA; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                                    <i :class="getCategoryIcon(item.category)"></i>
                                </div>
                                <span class="detail-category" style="color: #60A5FA; margin: 0;">{{ item.category || 'Sin categoría' }}</span>
                            </div>

                            <span class="detail-question" style="color: white; display:block; font-size: 1.1rem;">{{ item.question || 'Pregunta vacía' }}</span>
                            <div class="detail-answer" style="color: #4ADE80; margin-top:10px;">
                                <span style="color: #9CA3AF;">Ambos votaron:</span>
                                <strong>{{ item.option || 'Opción vacía' }}</strong>
                            </div>
                        </div>
                    </li>
                </ul>
            </div>
        </div>
    </div>

    <div v-if="activeTab === 'comunidad'" class="tab-content community-wrapper">
        
        <!-- Total Users Header -->
        <div class="community-header-stats">
             <span class="total-count-badge" v-if="profilesList">{{ profilesList.length }} Usuarios Totales</span>
        </div>

        <!-- SECCIÓN SOLICITUDES (NUEVA) -->
        <div class="community-section" v-if="pendingRequestsList.length > 0">
             <div class="community-header">
                 <h2 class="section-title text-warning">SOLICITUDES DE AMISTAD</h2>
                 <span class="member-count warning">{{ pendingRequestsList.length }}</span>
             </div>
             <div class="community-grid">
                <div v-for="profile in pendingRequestsList" :key="profile.id" class="community-card request-card" @click="openUserProfile(profile)">
                    <div class="c-avatar">
                        <i class="fas fa-user"></i>
                        <div class="request-badge"><i class="fas fa-exclamation"></i></div>
                    </div>
                    <div class="c-info">
                        <div class="c-name">{{ profile.nickname || 'Usuario' }}</div>
                        <div class="c-status">Quiere ser tu amig@</div>
                    </div>
                    <div class="c-actions">
                         <!-- Actions handled in modal, but visual cue here -->
                         <button class="btn-mini-accept">Ver</button>
                    </div>
                </div>
             </div>
        </div>
        
        <!-- SECCIÓN AMIG@S -->
        <div class="community-section" v-if="friendsList.length > 0">
             <div class="community-header">
                 <h2>AMIG@S</h2>
                 <span class="member-count">{{ friendsList.length }}</span>
             </div>
             <div class="community-grid">
                <div v-for="profile in friendsList" :key="profile.id" class="community-card friend-card" @click="openUserProfile(profile)">
                    <div class="c-avatar">
                        <i class="fas fa-user"></i>
                        <div class="friend-badge"><i class="fas fa-heart"></i></div>
                    </div>
                    <div class="c-info">
                        <div class="c-name">{{ profile.nickname || 'Usuario' }}</div>
                    </div>
                    <div class="c-stats">
                        <span class="c-votes"><i class="fas fa-check-circle"></i> {{ profile.votes_count || 0 }}</span>
                    </div>
                </div>
             </div>
        </div>

        <!-- SECCIÓN MIEMBROS -->
        <div class="community-section">
            <div class="community-header">
                 <h2>MIEMBR@S</h2>
                 <span class="member-count" v-if="membersList">{{ membersList.length }}</span>
            </div>
            <div v-if="loading" class="loading">Cargando comunidad...</div>
            <div v-else class="community-grid">
                <div v-for="profile in membersList" :key="profile.id" class="community-card" @click="openUserProfile(profile)">
                    <div class="c-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="c-info">
                        <div class="c-name">{{ profile.nickname || 'Usuario' }}</div>
                    </div>
                    <div class="c-stats">
                        <span class="c-votes"><i class="fas fa-check-circle"></i> {{ profile.votes_count || 0 }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- User Profile Modal -->
    <div v-if="showUserModal" class="modal-overlay" @click.self="closeUserModal">
        <div class="modal-content user-profile-modal">
            <button @click="closeUserModal" class="close-modal-btn"><i class="fas fa-times"></i></button>
            <div class="up-header">
                <div class="up-avatar">
                    <img v-if="selectedProfile?.photo_url" :src="selectedProfile.photo_url" alt="Avatar" class="avatar-img">
                    <i v-else class="fas fa-user"></i>
                </div>
                <h3 class="up-name">{{ selectedProfile?.nickname || 'Usuario' }}</h3>
                <span class="up-email">{{ selectedProfile?.email }}</span>
                <span class="up-badge">Miembro Verificado</span>
                <div class="friend-actions">
                    <button v-if="selectedProfile?.friendship_status === 'none'" @click.stop="sendRequest(selectedProfile.id)" class="btn-friend-action">Añadir Amigo</button>
                    <button v-else-if="selectedProfile?.friendship_status === 'pending_sent'" class="btn-friend-action disabled">Pendiente</button>
                    <div v-else-if="selectedProfile?.friendship_status === 'pending_received'" class="friend-response-actions">
                         <button @click.stop="acceptRequest(selectedProfile.id)" class="btn-friend-accept"><i class="fas fa-check"></i></button>
                         <button @click.stop="rejectRequest(selectedProfile.id)" class="btn-friend-reject"><i class="fas fa-times"></i></button>
                    </div>
                     <div v-else-if="selectedProfile?.friendship_status === 'friends'" class="friend-indicator">
                        <i class="fas fa-user-friends"></i> Amigos
                    </div>
                </div>
            </div>
            <div class="up-body">
                <div class="up-stats-grid">
                    <div class="up-stat">
                        <i class="fas fa-check-circle"></i>
                        <span class="up-stat-value">{{ selectedProfile?.votes_count || 0 }}</span>
                        <span class="up-stat-label">Votos</span>
                    </div>
                    <div class="up-stat">
                        <i class="fas fa-birthday-cake"></i>
                        <span class="up-stat-value">{{ selectedProfile?.birth_year || 'N/A' }}</span>
                        <span class="up-stat-label">Año Nac.</span>
                    </div>
                    <div class="up-stat">
                        <i class="fas fa-venus-mars"></i>
                        <span class="up-stat-value">{{ selectedProfile?.gender || 'N/A' }}</span>
                        <span class="up-stat-label">Género</span>
                    </div>
                </div>
                <div class="up-extra-info">
                    <p>Unido recientemente a la comunidad.</p>
                </div>
                 
                 <!-- Full Profile Link -->
                 <div class="modal-footer-actions" style="margin-top: 20px; text-align: center;">
                    <button @click="goToFullProfile" class="btn-full-profile">
                        <i class="fas fa-external-link-alt"></i> Ver Perfil Completo
                    </button>
                 </div>

                 <div v-if="selectedProfile?.friendship_status === 'friends'" class="friend-votes-section">
                    <h4>Últimas Votaciones (20)</h4>
                    <div v-if="loading" class="loading-votes">Cargando...</div>
                    <div v-else-if="friendVotes && friendVotes.length > 0" class="fv-list">
                        <div v-for="item in friendVotes.slice(0, 20)" :key="item.question.id" class="fv-item">
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
                                :profileId="selectedProfile.id"
                                :readOnly="true"
                                :forcedVoteId="item.friend_vote_id"
                            />
                        </div>
                    </div>
                    <div v-else class="no-votes">Sin votos públicos recientes.</div>
                </div>

            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, reactive } from 'vue';
import { useStore } from 'vuex';
import { useRoute } from 'vue-router';
import Pregunta from '/src/components/preguntas/Pregunta.vue';
import { useToast } from 'vue-toastification';

const toast = useToast();
const store = useStore();
const route = useRoute();

onMounted(() => {
    if (route.query.tab) {
       // activeTab is expected to be defined in the component scope
       try {
           activeTab.value = route.query.tab;
       } catch (e) {
           console.warn("Could not set activeTab from route", e);
       }
    }
});

// Watch for route changes (e.g. clicking links while already on profile)
watch(() => route.query.tab, (newTab) => {
    if (newTab) {
        try {
            activeTab.value = newTab;
        } catch (e) {
             console.warn("Could not update activeTab from route", e);
        }
    }
});
const user = computed(() => store.state.user);
const preguntas = computed(() => store.state.preguntas);
const compatibilityList = computed(() => store.state.compatibilityList);
const profilesList = computed(() => store.state.profilesList);
const friendVotes = computed(() => store.state.friendVotes);
const filteredProfiles = computed(() => {
    if (!profilesList.value) return [];
    return profilesList.value;
});

const friendsList = computed(() => {
    if (!profilesList.value) return [];
    return profilesList.value.filter(p => p.friendship_status === 'friends');
});

const pendingRequestsList = computed(() => {
     if (!profilesList.value) return [];
     return profilesList.value.filter(p => p.friendship_status === 'pending_received');
});

const membersList = computed(() => {
    if (!profilesList.value) return [];
    // Exclude friends and pending received requests (which are shown in other sections)
    return profilesList.value.filter(p => p.friendship_status !== 'friends' && p.friendship_status !== 'pending_received');
});

// Community Modal State
const showUserModal = ref(false);
const selectedProfile = ref(null);

const openUserProfile = (profile) => {
    selectedProfile.value = profile;
    showUserModal.value = true;
    if (profile.friendship_status === 'friends' || profile.id === store.state.user?.id) {
        console.log('Fetching votes for profile:', profile.id);
        store.dispatch('fetchFriendVotes', profile.id);
    } else {
        store.commit('SET_FRIEND_VOTES', []);
    }
};

const closeUserModal = () => {
    showUserModal.value = false;
    selectedProfile.value = null;
};

const goToFullProfile = () => {
    if (selectedProfile.value) {
        // Navigate
        router.push({ name: 'PublicProfile', params: { id: selectedProfile.value.id } });
        closeUserModal();
    }
};

const sendRequest = async (id) => {
    await store.dispatch('sendFriendRequest', id);
    toast.success("Solicitud enviada");
};

const acceptRequest = async (id) => {
    await store.dispatch('acceptFriendRequest', id);
    toast.success("Amistad aceptada");
    store.dispatch('fetchFriendVotes', id);
};

const rejectRequest = async (id) => {
    await store.dispatch('rejectFriendRequest', id);
    toast.success("Solicitud rechazada");
};
const loading = computed(() => store.state.loading);

// Compatibility Details State
const showModal = ref(false);
const selectedMatchName = ref('');
const selectedMatchPercentage = ref(0);
const matchDetails = ref([]);
const loadingDetails = ref(false);

const showDetails = async (match) => {
    selectedMatchName.value = match.nickname || match.email;
    selectedMatchPercentage.value = match.compatibility;
    showModal.value = true;
    loadingDetails.value = true;
    matchDetails.value = [];
    try {
        const details = await store.dispatch('fetchCompatibilityDetails', { targetId: match.id, targetType: match.type });
        matchDetails.value = details;
    } catch (error) {
        toast.error("Error al cargar detalles");
    } finally {
        loadingDetails.value = false;
    }
};

const closeModal = () => {
    showModal.value = false;
};

// State for editing personal info

// State for editing personal info
const isEditingPersonal = ref(false);
const editForm = reactive({
    birth_year: '',
    gender: '',
    nickname: ''
});

// Dynamic Personal Questions
const personalQuestions = ref([]);
const loadingPersonal = ref(false);
const dynamicAnswers = reactive({});

const fetchPersonalQuestions = async () => {
    loadingPersonal.value = true;
    try {
        const questions = await store.dispatch('fetchQuestionsByCategory', 'PERSONAL');
        personalQuestions.value = questions;
        
        // Initialize answers
        questions.forEach(q => {
            dynamicAnswers[q.id] = {
                option_id: q.current_user_answer?.option_id || null,
                text_answer: q.current_user_answer?.text_answer || ''
            };
        });
    } catch (e) {
        console.error("Error loading personal questions", e);
    } finally {
        loadingPersonal.value = false;
    }
};

// Helper for icons
const getQuestionIcon = (title) => {
    const map = {
        'Estado Civil': 'fas fa-heart',
        'Nacionalidad': 'fas fa-flag',
        'Profesión': 'fas fa-user-md',
        'Profesión / Oficio': 'fas fa-user-md',
        'Nivel Educacional': 'fas fa-graduation-cap',
        'Situación Laboral': 'fas fa-briefcase',
        'Religión / Creencia': 'fas fa-praying-hands',
        'Tendencia Política': 'fas fa-vote-yea',
        'Tipo de Vivienda': 'fas fa-home',
        'Previsión de Salud': 'fas fa-notes-medical'
    };
    return map[title] || 'fas fa-question-circle';
};

const getQuestionIconClass = (title) => {
     // Check for exact matches first, then keywords
     const map = {
        'Estado Civil': 'icon-civil',
        'Nacionalidad': 'icon-nation',
        'Profesión': 'icon-job',
        'Profesión / Oficio': 'icon-job',
        'Nivel Educacional': 'icon-edu',
        'Situación Laboral': 'icon-work',
        'Religión / Creencia': 'icon-rel',
        'Tendencia Política': 'icon-pol',
        'Tipo de Vivienda': 'icon-home',
        'Previsión de Salud': 'icon-health'
    };
    
    if (map[title]) return map[title];

    // Keyword matching for longer titles
    const t = title.toLowerCase();
    if (t.includes('capacitacion') || t.includes('curso') || t.includes('taller')) return 'icon-edu';
    if (t.includes('trabajo') || t.includes('empleo')) return 'icon-work';
    
    return 'icon-default';
};

const getAnswerText = (question) => {
    if (question.question_type === 'open' || question.question_type === 'slider' || question.question_type === 'date') {
        let answer = dynamicAnswers[question.id]?.text_answer || question.current_user_answer?.text_answer;
        
        if (question.question_type === 'slider' && answer) {
             const lowerTitle = question.title.toLowerCase();
             if (lowerTitle.includes('estatura')) answer += ' cm';
             else if (lowerTitle.includes('peso')) answer += ' kg';
        }

        if (question.question_type === 'date' && answer) {
             // Basic formatting YYYY-MM-DD -> DD/MM/YYYY
             try {
                const [y, m, d] = answer.split('-');
                if (d && m && y) return `${d}/${m}/${y}`;
                return answer;
             } catch (e) { return answer; }
        }
        
        return answer;
    } else if (question.question_type === 'dropdown') {
        const optionId = dynamicAnswers[question.id]?.option_id || question.current_user_answer?.option_id;
        if (!optionId) return null;
        const opt = question.options.find(o => o.id === optionId);
        return opt ? opt.title : null;
    }
    return null;
};

// Reactive state for the new questions (Deprecated/Legacy - kept for safely removing references if any)
const questionValues = reactive({});

// State for filtering
const selectedCategory = ref('');
const sortBy = ref('recent');

// Generate years for datalist (1900 - Current Year)
const currentYear = new Date().getFullYear();
const availableYears = Array.from({ length: currentYear - 1900 + 1 }, (_, i) => currentYear - i);

const filteredPreguntas = computed(() => {
    console.log('=== FILTER DEBUG ===');
    console.log('Raw preguntas:', preguntas.value);
    console.log('Total preguntas:', preguntas.value?.length);
    console.log('showHiddenVotes:', showHiddenVotes.value);
    
    
    let filtered = [];
    if (activeTab.value === 'votaciones') {
        filtered = [...(store.state.userPreguntas || [])];
    } else {
        filtered = [...(store.state.preguntas || [])];
    }
    
    // Explicitly filter out unvoted questions if we are in "Votaciones" tab
    if (activeTab.value === 'votaciones') {
        // Only hide if explicitly marked as hidden (deleted locally)
        // Trust the backend list otherwise.
        filtered = filtered.filter(p => !p.hidden);
    }

    console.log('After spread:', filtered.length);

    // Log first item to see structure
    if (filtered.length > 0) {
        console.log('First pregunta sample:', filtered[0]);
        console.log('user_vote_is_public value:', filtered[0]?.user_vote_is_public);
    }

    // Only filter by privacy if explicitly showing hidden votes AND NOT IN VOTACIONES TAB
    // In Votaciones tab, we want to see ALL votes (User request)
    if (activeTab.value !== 'votaciones') {
        if (showHiddenVotes.value) {
            // Show only private votes
            const beforeFilter = filtered.length;
            filtered = filtered.filter(p => p.user_vote_is_public === false);
            console.log(`Filter for HIDDEN: ${beforeFilter} -> ${filtered.length}`);
        } else {
            // Show public votes AND votes without privacy status (includes all by default)
            // This ensures backward compatibility and shows all votes when filter is off
            const beforeFilter = filtered.length;
            filtered = filtered.filter(p => p.user_vote_is_public !== false);
            console.log(`Filter for PUBLIC: ${beforeFilter} -> ${filtered.length}`);
        }
    }

    if (selectedCategory.value) {
        const beforeFilter = filtered.length;
        filtered = filtered.filter(p => p.category === selectedCategory.value);
        console.log(`Filter by category '${selectedCategory.value}': ${beforeFilter} -> ${filtered.length}`);
    }

    if (sortBy.value === 'recent') {
        // Assuming creation_date exists and is string
         filtered.sort((a, b) => new Date(b.creation_date) - new Date(a.creation_date));
    } else if (sortBy.value === 'most_voted') {
        filtered.sort((a, b) => b.cantidad_votos - a.cantidad_votos);
    }

    console.log('Final filtered count:', filtered.length);
    console.log('===================');
    return filtered;
});

// Icon logic for compatibility matches
const iconosPorCategoria = {
  deporte: 'fa fa-futbol',
  tecnologia: 'fa fa-laptop',
  entretenimiento: 'fa fa-film',
  politica: 'fa fa-balance-scale',
  sociedad: 'fa fa-users',
  mundial: 'fa fa-plane',
  educacion: 'fa fa-graduation-cap',
  salud: 'fa fa-heartbeat',
  masVotadas: 'fa fa-star',
  masNuevo: 'fa fa-clock',
};

const getCategoryIcon = (categoryName) => {
    if (!categoryName) return 'fas fa-check';
    const key = categoryName.toLowerCase();
    return iconosPorCategoria[key] || 'fas fa-hashtag';
};

const startEditing = () => {
    isEditingPersonal.value = true;
    if (user.value) {
        editForm.birth_year = user.value.birth_year;
        editForm.gender = user.value.gender;
        editForm.nickname = user.value.nickname;
    }
    
    // Re-sync dynamic answers just in case
    personalQuestions.value.forEach(q => {
        if (!dynamicAnswers[q.id]) {
            dynamicAnswers[q.id] = {
                 option_id: q.current_user_answer?.option_id || null,
                 text_answer: q.current_user_answer?.text_answer || ''
            };
        }
    });
};

const cancelEditing = () => {
    isEditingPersonal.value = false;
    // Reset form? Optional.
};

const savePersonal = async () => {
    try {
        // 1. Save Legacy Profile Fields (Birth Year, Gender, Nickname)
        const profilePayload = { ...editForm };
        await store.dispatch('updateProfile', profilePayload);

        // 2. Save Dynamic Questions
        const promises = [];
        personalQuestions.value.forEach(q => {
            const ans = dynamicAnswers[q.id];
            
            // Check if there is data to submit
            const hasOption = ans.option_id !== null && ans.option_id !== undefined;
            const hasText = ans.text_answer !== null && ans.text_answer !== undefined && String(ans.text_answer).trim() !== '';
            
            // For now, only submit if we have a value. 
            // TODO: Handle un-answering (clearing vote) if needed later.
            if (hasOption || hasText) {
                promises.push(store.dispatch('submitAnswer', {
                    questionId: q.id,
                    optionId: ans.option_id,
                    textAnswer: ans.text_answer
                }));
            }
        });

        await Promise.all(promises);
        
        // Refresh Questions to update view state
        await fetchPersonalQuestions();

        isEditingPersonal.value = false;
        toast.success("Perfil actualizado");
    } catch (error) {
        console.error(error);
        toast.error("Error al guardar perfil");
    }
};

const togglePrivacy = async (fieldOrQuestion) => {
    if (!user.value) return;
    
    // Handle Question Object (Dynamic Questions)
    if (typeof fieldOrQuestion === 'object' && fieldOrQuestion.id) {
        const q = fieldOrQuestion;
        try {
            await store.dispatch('toggleQuestionPrivacy', q.id);
            // Toggle local state
            // user_vote_is_public can be null (default public) or boolean
            const current = q.user_vote_is_public !== false; 
            q.user_vote_is_public = !current;
            toast.success(`Privacidad: ${!current ? 'Público' : 'Privado'}`);
        } catch (e) {
            console.error(e);
            toast.error("Error al cambiar privacidad");
        }
        return;
    }

    // Handle Legacy Fields (Strings)
    const field = fieldOrQuestion;
    const update = {};
    if (field === 'birth_year') {
        update.is_birth_year_public = !user.value.is_birth_year_public;
    } else if (field === 'gender') {
        update.is_gender_public = !user.value.is_gender_public;
    } else if (field === 'email') {
        update.is_email_public = !user.value.is_email_public;
    }
    await store.dispatch('updateProfile', update);
};


const activeTab = ref('personal');

const loadData = () => {
  if (activeTab.value === 'personal') {
    if (store.state.user && store.state.user.id) {
        // User is already in store/watched (triggers loadData), don't re-fetch profile causing loop
        fetchPersonalQuestions();
    }
  } else if (activeTab.value === 'votaciones') {
    store.dispatch('fetchPreguntasForUser');
  } else if (activeTab.value === 'compatibilidad') {
    store.dispatch('fetchCompatibility');
  } else if (activeTab.value === 'comunidad') {
    store.dispatch('fetchProfiles');
  }
};

onMounted(() => {
  if (user.value && user.value.id) {
    loadData();
  }
});

watch(user, (newUser) => {
    if (newUser && newUser.id) {
        loadData();
    }
}, { immediate: true });

watch(activeTab, () => {
  loadData();
});

const showHiddenVotes = ref(false);
</script>

<style scoped>
.user-profile {
  grid-column: 1 / -1;
  padding: 20px;
  max-width: 100%;
  margin: 0;
  background: linear-gradient(135deg, var(--colortertiary), var(--colordark));
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.section-divider {
    margin-top: 30px;
    border-top: 1px solid rgba(255,255,255,0.1);
    padding-top: 20px;
}

.section-divider h3 {
    margin-bottom: 20px;
    font-size: 1.2rem;
    color: #60A5FA;
    padding-left: 10px;
    color: #6B7280;
    font-style: italic;
    font-weight: normal;
    font-size: 0.9rem;
}

.pq-input {
    width: 100%;
}

/* Custom icon colors */
.icon-civil { background: rgba(239, 68, 68, 0.2); color: #F87171; }
.icon-nation { background: rgba(59, 130, 246, 0.2); color: #60A5FA; }
.icon-birth { background: rgba(245, 158, 11, 0.2); color: #FBBF24; }
.icon-job { background: rgba(16, 185, 129, 0.2); color: #34D399; }
.icon-edu { background: rgba(139, 92, 246, 0.2); color: #A78BFA; }
.icon-work { background: rgba(236, 72, 153, 0.2); color: #F472B6; }
.icon-rel { background: rgba(107, 114, 128, 0.2); color: #D1D5DB; }
.icon-pol { background: rgba(220, 38, 38, 0.2); color: #EF4444; }
.icon-home { background: rgba(20, 184, 166, 0.2); color: #2DD4BF; }
.icon-health { background: rgba(99, 102, 241, 0.2); color: #818CF8; }

.tabs {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 30px;
  gap: 15px;
  padding-left: 5px;
}

button {
  padding: 12px 30px;
  cursor: pointer;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ccc;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

button.active {
  background: var(--gradient-primary);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}

button:hover:not(.active) {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

/* Personal Tab Styles */
.personal-wrapper {
  display: flex;
  flex-direction: column;
  gap: 30px;
  animation: fadeIn 0.5s ease-out;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.profile-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.1), transparent);
  z-index: 0;
}

.avatar-container {
  height: 60px;
  background: linear-gradient(135deg, #65BCF6, #3B82F6);
  border-radius: 50%;
  overflow: hidden; /* Ensure image stays circular */
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.1);
  z-index: 1;
}

.avatar-container i {
  font-size: 1.8rem;
  color: white;
}

.user-email {
  font-size: 0.95rem;
  color: white;
  margin: 0 0 6px 0;
  font-weight: 500;
  z-index: 1;
  max-width: 90%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 10px;
}

.user-badge {
  background: rgba(16, 185, 129, 0.2);
  color: #34D399;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 600;
  border: 1px solid rgba(16, 185, 129, 0.3);
  z-index: 1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  width: 100%;
  margin-top: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 15px;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.3s ease, background 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.1);
}

.stat-card.clickable {
    cursor: pointer;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon.votes {
  background: rgba(245, 158, 11, 0.2);
  color: #FBBF24;
}

.stat-icon.year {
  background: rgba(236, 72, 153, 0.2);
  color: #F472B6;
}

.stat-icon.gender {
  background: rgba(139, 92, 246, 0.2);
  color: #A78BFA;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: white;
  line-height: 1.2;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.value-row {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    min-width: 0;
    flex: 1;
}

.value-row .stat-value {
    flex: 1;
    min-width: 0;
}

.privacy-btn {
    background: none;
    border: none;
    color: #6B7280;
    cursor: pointer;
    font-size: 0.9rem;
    padding: 0;
    transition: all 0.2s;
}

.privacy-btn:hover {
    color: #65BCF6;
    transform: scale(1.1);
}

.stat-label {
  font-size: 0.85rem;
  color: #9CA3AF;
  font-weight: 500;
}

.votaciones-info {
  margin-top: 10px;
}

.votaciones-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid rgba(255,255,255,0.1);
    margin-bottom: 20px;
    padding-bottom: 15px;
    flex-wrap: wrap;
    gap: 15px;
}

.votaciones-info h2 {
  font-size: 1.5rem;
  color: white;
  margin: 0;
  border-bottom: none;
  padding-bottom: 0;
}

.filters {
    display: flex;
    gap: 10px;
}

.filter-select {
    height: 40px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    padding: 0 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    backdrop-filter: blur(5px);
    outline: none;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
}

.filter-select:focus {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(67, 180, 255, 0.5);
    box-shadow: 0 0 10px rgba(67, 180, 255, 0.2);
}

.filter-select option {
    background: #1a1a1a; /* Dark background for options */
    color: white;
    padding: 10px;
}

.personal-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

.edit-input {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 6px 10px; /* Reduced padding */
    border-radius: 6px; /* Slightly smaller radius */
    font-size: 0.95rem; /* Slightly smaller font */
    width: 100%;
    outline: none;
    transition: all 0.3s ease;
}

.small-input {
    width: 100px; /* Specific width for short inputs like Year */
}

.nickname-input {
    max-width: 180px; /* Limit nickname width */
}

.edit-input:focus {
    background: rgba(255, 255, 255, 0.15);
    border-color: #3B82F6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

/* Fix for Select Options Visibility */
select.edit-input option {
    background-color: #1f2937; /* Dark gray */
    color: white;
    padding: 10px;
}

/* Remove Arrows/Spinners from Number Input */
input[type=number].edit-input::-webkit-inner-spin-button, 
input[type=number].edit-input::-webkit-outer-spin-button { 
  -webkit-appearance: none; 
  margin: 0; 
}
input[type=number].edit-input {
  -moz-appearance: textfield;
}

.btn-edit-personal, .btn-save-personal, .btn-cancel-personal {
    padding: 8px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
    border: none;
    display: flex;
    align-items: center;
    gap: 5px;
}

.btn-edit-personal {
    background: rgba(59, 130, 246, 0.5);
    color: white;
}

.btn-save-personal {
    background: rgba(16, 185, 129, 0.5);
    color: white;
}

.btn-cancel-personal {
    background: rgba(239, 68, 68, 0.5);
    color: white;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .profile-header {
    padding: 30px 20px;
  }
}

/* Fix for unified card layout */
.profile-header {
    display: flex;
    flex-direction: column;
    align-items: stretch; /* Change from center to stretch to fill width */
    padding: 20px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}

/* Ensure avatar and name are still centered */
.avatar-container, .user-email, .user-badge {
    align-self: center;
}

.section-divider {
    margin-top: 30px;
    border-top: 1px solid rgba(255,255,255,0.1);
    padding-top: 20px;
    width: 100%;
}

.questions-grid-profile {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
    width: 100%;
}

/* Remove background from profile-question-item to avoid double background look if desired, 
   OR keep it but ensure spacing is right. User said "hay 2 fondos".
   If the card has a background and the question items have a background, that's 2 layers.
   If consistent with stats (which have backgrounds), it should be fine.
   Maybe the issue was the width making it look box-in-box.
   I'll keep the background but fix the width. */
/* Compatibility Styles */
.compatibility-wrapper h2 {
    color: white;
    border-bottom: 2px solid rgba(255,255,255,0.1);
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.compatibility-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
}

.match-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 15px;
    display: flex;
    align-items: center;
    gap: 15px;
    transition: transform 0.2s;
    cursor: pointer;
}

.match-card:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.15); /* More visible hover */
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.match-avatar i {
    font-size: 2.5rem;
    color: #65BCF6;
}

.match-info {
    flex-grow: 1;
}

.match-email {
    color: white;
    font-weight: bold;
    font-size: 0.95rem;
    margin-bottom: 5px;
}

.match-score-bar {
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    margin-bottom: 5px;
    overflow: hidden;
}

.score-fill {
    height: 100%;
    background: linear-gradient(90deg, #F472B6, #8B5CF6);
    border-radius: 3px;
}

.match-details {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
}

.score-text {
    color: var(--colorprimary);
    font-weight: bold;
}

.common-text {
    color: #9CA3AF;
}

.loading, .no-data {
    color: white;
    text-align: center;
    padding: 20px;
}

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(5px);
}

.modal-content {
    background: #1a1a1a;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    animation: fadeIn 0.3s ease-out;
}

.modal-header {
    background: var(--gradient-primary);
    padding: 15px 20px;
    border-radius: 15px 15px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    color: white;
    font-size: 1.2rem;
}

.close-btn {
    background: transparent;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
}

.modal-body {
    padding: 20px;
    overflow-y: auto;
}

.details-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.detail-item {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.detail-category {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #65BCF6;
    font-weight: bold;
    letter-spacing: 0.5px;
}

.detail-question {
    font-size: 1rem;
    font-weight: 600;
    color: white;
    margin-bottom: 5px;
    display: block;
}

.detail-answer {
    font-size: 0.9rem;
    color: #10B981; /* Green */
    display: flex;
    align-items: center;
    gap: 8px;
}
/* Community Styles */
.community-wrapper { animation: fadeIn 0.5s ease-out; }
.community-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
.community-header h2 { color: white; margin: 0; }
.member-count { color: #9CA3AF; font-size: 0.9rem; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 10px; }
.community-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
.community-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 15px; display: flex; align-items: center; gap: 15px; cursor: pointer; transition: all 0.3s ease; }
.community-card:hover { background: rgba(255, 255, 255, 0.1); transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); border-color: rgba(59, 130, 246, 0.4); }
.c-avatar { width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #60A5FA, #3B82F6); display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; flex-shrink: 0; }
.c-info { flex-grow: 1; overflow: hidden; }
.c-name { color: white; font-weight: bold; font-size: 1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.c-email { color: #9CA3AF; font-size: 0.8rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.c-stats { display: flex; align-items: center; }
.c-votes { color: #FBBF24; font-size: 0.9rem; display: flex; align-items: center; gap: 5px; font-weight: 600; }

/* User Profile Modal */
.user-profile-modal { background: #1e1e1e; max-width: 400px; width: 90%; padding: 30px; border-radius: 20px; position: relative; text-align: center; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); display: flex; flex-direction: column; }
.close-modal-btn { position: absolute; top: 15px; right: 15px; background: transparent; border: none; color: #9CA3AF; font-size: 1.2rem; cursor: pointer; }
.close-modal-btn:hover { color: white; }
.up-header { display: flex; flex-direction: column; align-items: center; margin-bottom: 25px; }
.up-avatar { width: 90px; height: 90px; background: linear-gradient(135deg, #8B5CF6, #3B82F6); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; color: white; margin-bottom: 15px; box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3); border: 3px solid rgba(255,255,255,0.1); }
.up-name { color: white; font-size: 1.5rem; margin: 0 0 5px 0; }
.up-email { color: #9CA3AF; font-size: 0.9rem; margin-bottom: 10px; }
.up-badge { background: rgba(16, 185, 129, 0.2); color: #34D399; padding: 4px 12px; border-radius: 15px; font-size: 0.75rem; font-weight: 600; }
.up-stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px; }
.up-stat { background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; gap: 5px; }
.up-stat i { font-size: 1.2rem; color: #60A5FA; }
.up-stat-value { color: white; font-weight: bold; font-size: 1.1rem; }
.up-stat-label { color: #9CA3AF; font-size: 0.7rem; text-transform: uppercase; }
.up-extra-info { color: #6B7280; font-size: 0.85rem; font-style: italic; }
/* Friendship Styles */
.friend-actions { margin-top: 15px; display: flex; gap: 10px; width: 100%; justify-content: center; flex-wrap: wrap; }
.btn-friend-action { background: #3B82F6; color: white; border: none; padding: 8px 16px; border-radius: 20px; font-weight: 600; cursor: pointer; transition: 0.3s; font-size: 0.9rem; }
.btn-friend-action:hover { background: #2563EB; transform: scale(1.05); }
.btn-friend-action.disabled { background: #4B5563; cursor: not-allowed; opacity: 0.7; }
.friend-response-actions { display: flex; gap: 15px; }
.btn-friend-accept { background: #10B981; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s; }
.btn-friend-accept:hover { transform: scale(1.1); box-shadow: 0 0 15px rgba(16, 185, 129, 0.5); }
.btn-friend-reject { background: #EF4444; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s; }
.friend-indicator { color: #10B981; font-weight: bold; display: flex; gap: 5px; align-items: center; }
.friend-votes-section { margin-top: 20px; width: 100%; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; text-align: left; }
.friend-votes-section h4 { color: white; margin-bottom: 15px; text-align: center; }
.fv-list { 
    display: flex;
    overflow-x: auto;
    gap: 15px;
    padding: 10px 0 20px 0; /* padding bottom for scrollbar */
    max-width: 100%;
    scrollbar-width: thin; /* Firefox */
}
.fv-list::-webkit-scrollbar {
    height: 8px;
}
.fv-list::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
}
.fv-list::-webkit-scrollbar-thumb {
    background: #4B5563;
    border-radius: 4px;
}

.fv-item { 
    min-width: 280px; /* Base width before scale */
    width: 280px;
    flex-shrink: 0;
    /* Miniature effect: Scale down the whole card */
    transform: scale(0.85); 
    transform-origin: top left;
    /* Compensate for layout space left by scaling */
    margin-right: -42px; 
    margin-bottom: -20px; 
    
    box-shadow: 0 4px 6px rgba(0,0,0,0.2); 
    border-radius: 12px;
    background: rgba(255,255,255,0.02);
    height: fit-content;
}
.loading-votes, .no-votes { color: #9CA3AF; font-size: 0.9rem; margin: 20px 0; text-align: center; }

/* Privacy Toggle Styles - Compact version used now */


/* Switch Component */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input { 
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #4B5563;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

input:checked + .slider {
  background-color: #3B82F6; /* Primary Blue */
}

input:focus + .slider {
  box-shadow: 0 0 1px #3B82F6;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

.header-count {
    color: #9CA3AF;
    font-size: 0.8em;
    font-weight: 500;
    margin-left: 5px;
}

/* Compact Switch for Filters */
.filter-privacy {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.1);
    height: 40px;
    padding: 0 12px;
    border-radius: 8px;
    margin-left: auto; /* Push to right */
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.privacy-label-small {
    font-size: 0.8rem;
    color: #9CA3AF;
}

.privacy-status-text {
    font-size: 0.8rem;
    font-weight: 600;
    color: white;
    min-width: 45px;
}

.switch-compact {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
}

.switch-compact input { 
  opacity: 0;
  width: 0;
  height: 0;
}

.slider-compact {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #4B5563;
  transition: .4s;
  border-radius: 34px;
}

.slider-compact:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider-compact {
  background-color: #10B981;
}

input:checked + .slider-compact:before {
  transform: translateX(16px);
}

.filters {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
}

.anonymous-title {
    font-weight: 800;
    font-size: 1.8rem;
    color: white;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 20px;
}

/* Compatibility Modal Styles */
.compatibility-modal {
  max-width: 600px;
  width: 90%;
  background: #1a1b2e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  max-height: 85vh;
  border-radius: 16px;
}

.compatibility-modal .modal-header {
  background: rgba(255, 255, 255, 0.03);
  padding: 20px 25px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.compatibility-badge-large {
  background: linear-gradient(135deg, #10B981, #047857);
  color: white;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.5rem;
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
  border: 3px solid rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.modal-user-info h3 {
  margin: 0 0 4px 0;
  font-size: 0.85rem;
  color: #9CA3AF;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.match-name {
  font-size: 1.4rem;
  font-weight: 800;
  color: white;
  display: block;
}

.compatibility-modal .modal-body {
  padding: 0;
  overflow-y: auto;
  flex: 1;
  background: #13141f;
}

.details-list {
  list-style: none;
  padding: 25px;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.detail-item {
  background: #1e2030;
  border-radius: 12px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  gap: 18px;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.detail-item:hover {
  background: #25273c;
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 8px 15px rgba(0,0,0,0.2);
}

.detail-icon {
  width: 44px;
  height: 44px;
  background: rgba(59, 130, 246, 0.15);
  color: #60A5FA;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.detail-content {
  flex: 1;
  line-height: 1.4;
}

.detail-answer {
  margin-top: 8px;
  padding: 10px 12px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 8px;
  font-size: 0.95rem;
  color: #D1FAE5;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.detail-answer span {
    color: #9CA3AF;
    font-size: 0.85rem;
}

.detail-answer strong {
  color: #34D399;
  font-weight: 700;
  font-size: 1rem;
}

.loading, .no-matches {
  padding: 50px;
  text-align: center;
  color: #9CA3AF;
  font-size: 1.1rem;
}

.loading i {
  margin-right: 12px;
  color: #60A5FA;
}

.questions-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-top: 20px;
}

@media (max-width: 768px) {
    .questions-grid {
        grid-template-columns: 1fr;
    }
}

.questions-grid .grid-container {
    height: 100%;
    margin-bottom: 0;
}

.edit-slider-group {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
}

.edit-date-group {
    width: 100%;
}

.edit-date {
    width: auto;
    min-width: 140px;
    max-width: 160px;
    color-scheme: dark;
    padding: 6px 10px;
}

.slider-number {
    width: 70px !important; /* Force small width */
    padding: 8px 5px !important;
    text-align: center;
}

.edit-range {
    flex-grow: 1;
    cursor: pointer;
    accent-color: #60A5FA;
}

.privacy-btn-small {
    background: transparent;
    border: none;
    color: #9CA3AF;
    cursor: pointer;
    padding: 0 5px;
    margin-left: 10px;
    font-size: 0.9rem;
    transition: color 0.2s;
    opacity: 0.6;
}

.privacy-btn-small:hover {
    color: #60A5FA;
    opacity: 1;
}

.privacy-btn {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.1);
    color: #9CA3AF;
    cursor: pointer;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 8px;
    font-size: 0.8rem;
    transition: all 0.2s;
}

.privacy-btn:hover {
    color: white;
    background: rgba(255,255,255,0.1);
}

.questions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 60px; /* Increased separation */
    row-gap: 60px;
    margin-top: 40px;
}

/* Personal Profile Grid Styles */
.questions-grid-profile {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.profile-question-item {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 15px;
    display: flex;
    align-items: flex-start;
    gap: 15px;
    transition: transform 0.2s, background 0.2s;
}

.profile-question-item:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: translateY(-2px);
}

.pq-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    background: rgba(255, 255, 255, 0.1); /* Default fallback */
    flex-shrink: 0;
}

.pq-content {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 0; /* Prevent overflow */
}

.pq-content label {
    font-size: 0.85rem;
    color: #9CA3AF;
    font-weight: 500;
    line-height: 1.2;
}

.pq-value {
    color: white;
    font-weight: 600;
    font-size: 1.1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.placeholder {
    color: #6B7280;
    font-style: italic;
    font-size: 0.9rem;
}

.privacy-btn-small {
    background: none;
    border: none;
    color: #4B5563;
    cursor: pointer;
    font-size: 0.9rem;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;
}

.privacy-btn-small:hover {
    color: white;
    background: rgba(255,255,255,0.1);
}

.edit-date-group, .edit-slider-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
    width: 100%;
}

.slider-number {
    width: 60px !important;
    text-align: center;
}

/* Update for Avatar Images */
.up-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #A855F7, #6366F1);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    overflow: hidden; /* Ensure image stays circular */
}

.avatar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}

</style>
