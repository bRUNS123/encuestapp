<template>
  <div class="grid-container">
    <div class="icono-container">
      <router-link :to="calcularURL(categoria)">
        <div class="icono-wrapper">
          <i :class="calcularIcono(categoria)"></i>
          <span class="categoria-nombre">{{ categoria ? categoria.toUpperCase() : '' }}</span>
        </div>
      </router-link>
      <div class="fecha">
        <i v-if="allowPrivacy && !readOnly" 
           :class="isVotePublic ? 'fas fa-eye' : 'fas fa-eye-slash'" 
           class="privacy-icon"
           :title="isVotePublic ? 'Público' : 'Privado'"
           @click.stop="toggleVisibility">
        </i>
        {{ formatFecha(fecha) }}
        <i v-if="canEditVote && !readOnly && !isEditingVote" class="fas fa-pencil-alt edit-icon" @click.stop="enableVoteEditing" title="Editar voto"></i>
        <div v-if="isEditingVote" class="edit-actions">
            <i class="fas fa-trash-alt delete-icon" @click.stop="deleteVote" title="Eliminar voto"></i>
            <i class="fas fa-times cancel-icon" @click.stop="cancelEditing" title="Cancelar"></i>
        </div>
      </div>
    </div>
    

    <div class="pregunta">{{ preguntaTextClean }}</div>
    
    <!-- TIPO: BINARY (Si/No o 2 opciones) -->
    <div v-if="questionType === 'binary'" class="respuestas">
      <div v-if="(!userHasVoted && !respuestaSeleccionada) || isEditingVote" class="respuesta" @click="seleccionarRespuesta(allOptions[0]?.id)">
        {{ allOptions[0]?.title || 'Opción 1' }}
      </div>
      <div v-if="(!userHasVoted && !respuestaSeleccionada) || isEditingVote" class="respuesta" @click="seleccionarRespuesta(allOptions[1]?.id)">
        {{ allOptions[1]?.title || 'Opción 2' }}
      </div>
      
      <!-- Resultados Binary -->
      <div v-if="(respuestaSeleccionada || userHasVoted) && !isEditingVote" class="resultados scrollable-results">
        <div v-for="(option, index) in allOptions" :key="option.id" 
             class="resultado-item" 
             :class="{'voted-option': respuestaSeleccionada === option.id}">
          <div class="respuesta-label">
            {{ option.title }}
            <i v-if="respuestaSeleccionada === option.id" class="fas fa-check-circle" style="color: #4ADE80; margin-left: 5px;"></i>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: getOptionPercentage(option) + '%' }"></div>
            <span class="progress-text">{{ getOptionPercentage(option) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- TIPO: SCALE (Escala 1-5) -->
    <div v-else-if="questionType === 'scale'" class="scale-container">
      <div v-if="(!userHasVoted && !respuestaSeleccionada) || isEditingVote" class="scale-buttons">
        <button 
          v-for="option in allOptions" 
          :key="option.id"
          @click="seleccionarRespuesta(option.id)"
          class="scale-button"
        >
          {{ option.title }}
        </button>
      </div>
      
      <!-- Resultados Scale -->
      <div v-if="(respuestaSeleccionada || userHasVoted) && !isEditingVote" class="scale-results scrollable-results">
        <div class="scale-result-item" v-for="option in allOptions" :key="option.id">
          <div class="scale-label" :class="{'selected-scale': respuestaSeleccionada === option.id}">
            {{ option.title }}
            <i v-if="respuestaSeleccionada === option.id" class="fas fa-star"></i>
          </div>
          <div class="scale-bar">
            <div class="scale-fill" :style="{ width: getOptionPercentage(option) + '%' }"></div>
            <span class="scale-percent">{{ getOptionPercentage(option) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- TIPO: DROPDOWN (Lista desplegable) -->
    <div v-else-if="questionType === 'dropdown'" class="dropdown-container">
      <select 
        v-if="(!userHasVoted && !respuestaSeleccionada) || isEditingVote"
        v-model="selectedDropdownOption"
        @change="handleDropdownChange"
        class="dropdown-select"
      >
        <option value="">-- Selecciona una opción --</option>
        <option v-for="option in allOptions" :key="option.id" :value="option.id">
          {{ option.title }}
        </option>
      </select>
      
      <!-- Resultados Dropdown -->
      <div v-if="(respuestaSeleccionada || userHasVoted) && !isEditingVote" class="dropdown-results scrollable-results">
        <div class="selected-answer">
          <i class="fas fa-check-circle"></i>
          Tu respuesta: <strong>{{ getSelectedOptionTitle() }}</strong>
        </div>
        <div class="dropdown-result-item" v-for="option in allOptions" :key="option.id">
          <div class="option-info">
            <span class="option-title" :class="{'voted-option-text': respuestaSeleccionada === option.id}">
              {{ option.title }}
            </span>
            <span class="option-votes">{{ option.votes }} votos</span>
          </div>
          <div class="option-bar">
            <div class="option-fill" :style="{ width: getOptionPercentage(option) + '%' }"></div>
            <span class="option-percent">{{ getOptionPercentage(option) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- TIPO: OPEN (Texto) -->
    <div v-else-if="questionType === 'open'" class="open-container">
       <div v-if="(!userHasVoted && !respuestaSeleccionada) || isEditingVote" class="open-input-wrapper">
           <input type="text" v-model="textAnswerValue" placeholder="Escribe tu respuesta..." class="open-input" @keyup.enter="enviarTexto">
           <button @click="enviarTexto" class="btn-enviar" :disabled="!textAnswerValue.trim()">
               <i class="fas fa-paper-plane"></i>
           </button>
       </div>
       <div v-else class="open-result">
           <div class="selected-answer">
             <i class="fas fa-check-circle"></i> Tu respuesta: <strong>{{ currentTextAnswerDisplay }}</strong>
           </div>
       </div>
    </div>

    <!-- TIPO: SLIDER (Rango) -->
    <div v-else-if="questionType === 'slider'" class="slider-container">
       <div v-if="(!userHasVoted && !respuestaSeleccionada) || isEditingVote" class="slider-wrapper">
         <div class="slider-value-wrapper">
            <input 
                type="number" 
                v-model="sliderValue" 
                class="slider-number-input" 
                :min="sliderMin" 
                :max="sliderMax"
                @blur="validateSliderValue"
                @keyup.enter="validateSliderValue"
            >
            <span class="unit">{{ unitLabel }}</span>
         </div>
         <input 
            type="range" 
            :min="sliderMin" 
            :max="sliderMax" 
            :step="sliderStep" 
            v-model="sliderValue"
            class="slider-input"
            list="tickmarks"
         >
         <div class="slider-labels">
            <span>{{ sliderMin }}{{ unitLabel }}</span>
            <span>{{ sliderMax }}{{ unitLabel }}</span>
         </div>
         <button 
           class="votar-btn" 
           @click="submitSliderVote"
           :disabled="!isAuthenticated && !isAnonymousAllowed"
         >
           Votar
         </button>
       </div>
       
       <!-- Result View for Slider -->
       <div v-else class="slider-result">
          <div class="user-vote-display">
             Tu respuesta: <strong>{{ currentTextAnswerDisplay || '...' }} {{ unitLabel }}</strong>
          </div>
       </div>
    </div>
    
    <div class="votos">{{ totalVotos }} Votos</div>
    <div v-if="expirationDate" class="countdown">
      <i class="far fa-clock"></i>
      <span v-if="!isExpired">{{ timeRemaining }}</span>
      <span v-else class="expired">Expirada</span>
    </div>



    <!-- Rating Section -->
    <div class="rating-container" :class="{ 'disabled': !isAuthenticated }">
       <div class="stars">
         <i v-for="star in 5" :key="star" 
            class="fa-star"
            :class="[
              (hoverRating >= star || (!hoverRating && (usuarioRating >= star))) ? 'fas' : 'far',
              {'interactive': isAuthenticated}
            ]"
            @mouseenter="isAuthenticated ? hoverRating = star : null"
            @mouseleave="isAuthenticated ? hoverRating = 0 : null"
            @click="submitRating(star)"
         ></i>
       </div>
       <div class="rating-info-line" v-if="promedioRating > 0">
         <span class="rating-avg">{{ Number(promedioRating || 0).toFixed(1) }}</span>
         <span class="rating-count">({{ totalRatings }})</span>
       </div>
    </div>
    
    <!-- Report Button - Bottom Right Corner -->
    <button v-if="!readOnly" @click.stop="openReportModal" class="report-btn" title="Reportar pregunta">
      <i class="fas fa-flag"></i>
    </button>
    
    <ConfirmationModal 
      v-if="showDeleteModal" 
      message="¿Estás seguro que deseas eliminar tu voto? Esta acción no se puede deshacer."
      @confirm="confirmDeleteVote"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useStore } from 'vuex';
import { format, parseISO } from 'date-fns';
import { getCookie, setCookie } from '@/store/cookies';
import { useToast } from 'vue-toastification';
import { v4 as uuidv4 } from 'uuid';
import axios from '/src/store/axiosInstance.js';
import ConfirmationModal from '/src/components/ui/ConfirmationModal.vue';

const emit = defineEmits(['respuesta-seleccionada']);

const props = defineProps({
  questionId: Number,
  pregunta: String,
  questionType: {
    type: String,
    default: 'binary',
    validator: (value) => ['binary', 'scale', 'dropdown', 'open', 'slider'].includes(value)
  },
  allOptions: {
    type: Array,
    default: () => []
  },
  // Backwards compatibility props (needed if parent components pass them)
  respuesta1Id: Number,
  respuesta2Id: Number,
  respuesta1: {
    type: Object,
    default: () => ({ title: 'Sin respuesta', votes: 0 })
  },
  respuesta2: {
    type: Object,
    default: () => ({ title: 'Sin respuesta', votes: 0 })
  },
  categoria: String,
  fecha: String,
  votos: Number,
  profileId: {
    type: [String, Number],
    default: null
  },
  allowPrivacy: {
    type: Boolean,
    default: false
  },
  isPublic: {
    type: Boolean,
    default: true
  },
  expirationDate: {
    type: String,
    default: null
  },
  readOnly: {
    type: Boolean,
    default: false
  },
  forcedVoteId: {
    type: Number,
    default: null
  },
  ratingAverage: {
    type: Number,
    default: 0
  },
  ratingCount: {
    type: Number,
    default: 0
  },
  userRating: {
    type: Number,
    default: 0
  }
});

const store = useStore();
const respuestaSeleccionada = ref(props.forcedVoteId || null);
const totalVotos = ref(props.votos);


const isVotePublic = ref(props.isPublic);
const timeRemaining = ref('');
const isExpired = ref(false);
const selectedDropdownOption = ref('');
const isEditingVote = ref(false);
const showDeleteModal = ref(false);
const textAnswerValue = ref('');

// ... (other refs)

const preguntaData = computed(() => {
    // Check userPreguntas first (profile/votes context - mostly up to date)
    const inUserList = store.state.userPreguntas?.find(p => p.id === props.questionId);
    if (inUserList) return inUserList;
    
    // Check main feed
    return store.state.preguntas?.find(p => p.id === props.questionId);
});

const currentTextAnswerDisplay = computed(() => {
    // Priority: Local state (if user just voted) -> Store (preguntaData) -> Prop override?
    if (preguntaData.value && preguntaData.value.current_user_answer) {
        return preguntaData.value.current_user_answer.text_answer || '';
    }
    // Fallback if not updated in store yet but we know user voted? 
    // Usually updateVote updates the store, so preguntaData should be fresh.
    return '';
});

// Helper function must be declared before use in computed
function hasUserVoted(questionId) {
  if (store.getters.isAuthenticated) {
    const userVotes = store.state.preguntas.filter(p => p.user_has_voted);
    return userVotes.some(vote => vote.id === questionId);
  } else {
    return !!getCookie(`${COOKIE_NAME}_vote_${questionId}`);
  }
}

const userHasVoted = computed(() => {
    if (props.forcedVoteId) return true;
    // Direct check on the data object is more reliable than filtering the list again
    if (preguntaData.value && preguntaData.value.user_has_voted) return true;
    
    return hasUserVoted(props.questionId);
});

// Initialize text answer and selected option if available
watch(() => preguntaData.value, (newPregunta) => {
    if (newPregunta && newPregunta.current_user_answer) {
        if (newPregunta.current_user_answer.text_answer) {
            textAnswerValue.value = newPregunta.current_user_answer.text_answer;
        } else {
            textAnswerValue.value = '';
        }
        
        // Check for both option_id (current backend) and chosen_option (legacy/optimistic)
        const val = newPregunta.current_user_answer.option_id || newPregunta.current_user_answer.chosen_option;
        
        if (val) {
             const id = typeof val === 'object' ? val.id : val;
             
             respuestaSeleccionada.value = Number(id);
             selectedDropdownOption.value = respuestaSeleccionada.value;
        } else {
             respuestaSeleccionada.value = null;
             selectedDropdownOption.value = '';
        }
    } else {
        // Only reset if we truly have no vote data AND we don't think the user has voted.
        // If userHasVoted is true (e.g. from cookie or props) but store data is temporarily missing/stale,
        // we should NOT wipe the local selection immediately.
        if (!userHasVoted.value) {
            textAnswerValue.value = '';
            respuestaSeleccionada.value = null;
            selectedDropdownOption.value = '';
        }
    }
}, { immediate: true });

// Ensure options are ready or re-eval if needed?
// The logic above relies on optionsMap being used in getSelectedOptionTitle template, which is reactive.
// Just setting the ID is enough.

// ...

const enviarTexto = async () => {
  if (!textAnswerValue.value.trim()) return;
  if (!store.getters.isAuthenticated) {
      toast.warning("Debes iniciar sesión para responder");
      return; 
  }
  
  const payload = {
    question_id: props.questionId,
    option_id: null, // No option for text
    text_answer: textAnswerValue.value,
    is_anonymous: false, // Text answers usually not anonymous or use same logic
    user_token: null,
    profile_id: Number(props.profileId) || 0
  };

  try {
    // No optimistic update for text (visual feedback is input value)
    await store.dispatch('voteForOption', payload);
    toast.success('¡Respuesta enviada!');
    isEditingVote.value = false;
  } catch (error) {
    console.error('Error al responder:', error);
    toast.error('Error al responder.');
  }
};

    const confirmDeleteVote = async () => {
        showDeleteModal.value = false;
        
        try {
            await store.dispatch('deleteVote', { questionId: props.questionId });
            toast.success("Voto eliminado");
            
             // Manually decrement total votes locally
             totalVotos.value = Math.max(0, totalVotos.value - 1);
             
             // Decrement specific option count if we know what was selected
             if (respuestaSeleccionada.value) {
                 const optId = Number(respuestaSeleccionada.value);
                 const opt = optionsMap.value.get(optId);
                 if (opt) {
                     opt.votes = Math.max(0, opt.votes - 1);
                     optionsMap.value.set(optId, opt);
                 }
             }

             // Reset local state AFTER updating counts
             respuestaSeleccionada.value = null;
             selectedDropdownOption.value = '';
             textAnswerValue.value = ''; 
             isEditingVote.value = false;
             
             // Do NOT call initializeOptions() here as it would overwrite our local optimistic update 
             // with potentially stale props until the parent refectches.
             // initializeOptions();

        } catch (error) {
            toast.error("Error al eliminar voto");
        }
    };

    const deleteVote = () => {
        showDeleteModal.value = true;
    };

    const unitLabel = computed(() => {
        return props.pregunta?.toLowerCase().includes('estatura') ? 'cm' : 'kg';
    });

    const enableVoteEditing = () => {
        isEditingVote.value = true;
        
        // Initialize slider with previous value if available
        if (props.questionType === 'slider' && currentTextAnswerDisplay.value) {
            const val = Number(currentTextAnswerDisplay.value);
            if (!isNaN(val)) {
                sliderValue.value = val;
            }
        }
    };

    const cancelEditing = () => {
        isEditingVote.value = false;
    };

// ...

const calcularURL = (categoria) => {
    if (!categoria) return '#';
    const cat = categoria.toLowerCase();
  switch (cat) {
    case 'deporte': return '/deporte';
    case 'politica': return '/politica';
    case 'sociedad': return '/sociedad';
    case 'tecnologia': return '/tecnologia';
    case 'entretenimiento': return '/entretenimiento';
    case 'internacional': return '/internacional';
    case 'educacion': return '/educacion';
    case 'salud': return '/salud';
    case 'personal': return '/profile?tab=personal'; /* Map Personal to Profile Tab */
    default: return '#';
  }
};
const hoverRating = ref(0);
const isAuthenticated = computed(() => store.getters.isAuthenticated);
const usuarioRating = computed(() => {
    // If we have prop data, use it, otherwise check store
    return props.userRating || (preguntaData.value ? preguntaData.value.user_rating : 0);
});
const promedioRating = computed(() => props.ratingAverage || (preguntaData.value ? preguntaData.value.rating_average : 0));
const totalRatings = computed(() => props.ratingCount || (preguntaData.value ? preguntaData.value.rating_count : 0));

const submitRating = async (score) => {
    if (!isAuthenticated.value) {
        toast.warning("Debes iniciar sesión para calificar");
        return;
    }
    try {
        await store.dispatch('rateQuestion', { questionId: props.questionId, score });
        toast.success(`¡Calificado con ${score} estrellas!`);
    } catch (e) {
        toast.error("Error al enviar calificación");
    }
};

const optionsMap = ref(new Map());

// --- SLIDER LOGIC ---
const sliderValue = ref(0);
const sliderMin = computed(() => {
    if (props.allOptions && props.allOptions.length >= 1) return Number(props.allOptions[0].title) || 0;
    return 0;
});
const sliderMax = computed(() => {
    if (props.allOptions && props.allOptions.length >= 2) return Number(props.allOptions[1].title) || 100;
    return 100;
});
const sliderStep = computed(() => {
    if (props.allOptions && props.allOptions.length >= 3) return Number(props.allOptions[2].title) || 1;
    return 1;
});

watch(() => sliderMin.value, (newMin) => {
    // Only reset if current value is out of bounds or uninitialized
    if (sliderValue.value < newMin) sliderValue.value = newMin;
}, { immediate: true });

const validateSliderValue = () => {
    let val = Number(sliderValue.value);
    if (isNaN(val)) val = sliderMin.value;
    if (val < sliderMin.value) val = sliderMin.value;
    if (val > sliderMax.value) val = sliderMax.value;
    sliderValue.value = val;
};

const submitSliderVote = async () => {
    if (!store.getters.isAuthenticated && !props.isAnonymousAllowed) {
         toast.warning("Debes iniciar sesión para votar");
         return;
    }
    
    // Construct payload
    const isAnonymous = !store.getters.isAuthenticated;
    const payload = {
        question_id: props.questionId,
        text_answer: String(sliderValue.value),
        is_anonymous: isAnonymous,
        user_token: userToken,
        profile_id: isAnonymous ? 0 : Number(props.profileId)
    };
    
    try {
        await store.dispatch('voteForOption', payload);
        
        if (isAnonymous) {
             setCookie(`${COOKIE_NAME}_vote_${props.questionId}`, true, 30);
        }

        const unit = props.pregunta.toLowerCase().includes('estatura') ? 'cm' : 'kg';
        toast.success(`Voto registrado: ${sliderValue.value}${unit}`);
        
        // Optimistic update?
        // Reuse logic? Maybe just rely on fetch?
        // Text answers usually don't have optimistic counts unless we track them separately.
    } catch (e) {
        console.error(e);
        toast.error("Error al enviar voto");
    }
};
// --------------------

// Initialize votes from default props if allOptions is empty (fallback)
const initializeOptions = () => {
    optionsMap.value.clear(); // Ensure clean slate
    if (props.allOptions && props.allOptions.length > 0) {
        // console.log(`[Q${props.questionId}] Initializing options:`, props.allOptions.map(o => o.id));
        props.allOptions.forEach(opt => {
            optionsMap.value.set(opt.id, { ...opt });
            // Handle string ID fallback just in case
            if (typeof opt.id === 'string' || typeof opt.id === 'number') {
                optionsMap.value.set(Number(opt.id), { ...opt });
            }
        });
    } else {
        // Fallback for binary view if allOptions not provided
        if (props.respuesta1Id) optionsMap.value.set(props.respuesta1Id, { ...props.respuesta1, id: props.respuesta1Id });
        if (props.respuesta2Id) optionsMap.value.set(props.respuesta2Id, { ...props.respuesta2, id: props.respuesta2Id });
    }
};

// Re-initialize when props change
watch(() => [props.allOptions, props.votos], () => {
    initializeOptions();
    totalVotos.value = props.votos;
}, { deep: true, immediate: true });

watch(() => props.isPublic, (val) => isVotePublic.value = val);


const preguntaText = computed(() => props.pregunta || (preguntaData.value ? preguntaData.value.title : ''));
const preguntaTextClean = computed(() => {
  let text = preguntaText.value;
  // Patterns to remove
  const patterns = [
    /^En una escala de 1 a 5,? :? ?/i,
    /^En una escala del 1 al 5,? :? ?/i,
    /^Del 1 al 5,? :? ?/i,
    /^De 1 a 5,? :? ?/i
  ];
  
  patterns.forEach(pattern => {
    text = text.replace(pattern, '');
  });

  // Remove scale suffix like ( 1= Malo, 5 = Bueno )
  // Matches: ( space* 1 space* = space* anything , space* 5 space* = space* anything )
  text = text.replace(/\(\s*1\s*=.*5\s*=.*\)/gi, '');
  text = text.replace(/\(\s*1\s*=.*5\s*=.*\)/gi, ''); // Run twice just in case? No, global flag 'g' handles it.
  
  // Clean up any double spaces or trailing punctuation often left behind
  text = text.replace(/\s+/g, ' ').trim();
  text = text.replace(/^:\s*/, ''); // Remove leading colon if left
  
  // Capitalize first letter after cleaning
  return text.charAt(0).toUpperCase() + text.slice(1);
});
const toast = useToast();

const COOKIE_NAME = "user_token";
if (!getCookie(COOKIE_NAME)) {
  const token = uuidv4();
  setCookie(COOKIE_NAME, token, 30);
}
const userToken = getCookie(COOKIE_NAME);

watch(() => props.forcedVoteId, (val) => {
    if (val) respuestaSeleccionada.value = val;
});

const canEditVote = computed(() => {
    const canEdit = userHasVoted.value && store.getters.isAuthenticated;
    // console.log(`Debugging canEditVote for Q${props.questionId}:`, canEdit, `(Voted: ${userHasVoted.value}, Auth: ${store.getters.isAuthenticated})`);
    return canEdit;
});

const getOptionPercentage = (option) => {
  if (!option) return 0;
  const opt = optionsMap.value.get(option.id);
  const currentVotes = opt ? opt.votes : option.votes;
  
  // Calculate total from current map state to reflect immediate changes
  const total = Array.from(optionsMap.value.values()).reduce((sum, o) => sum + o.votes, 0);
  return total > 0 ? Math.round((currentVotes / total) * 100) : 0;
};

// Removed duplicate optionsMap computed

// ...

const getSelectedOptionTitle = () => {
  if (!respuestaSeleccionada.value) return '';

  // Ensure we depend on optionsMap size to trigger re-eval
  if (optionsMap.value.size === 0) {
      // Fallback: Try searching props directly if map is empty
      if (props.allOptions && props.allOptions.length > 0) {
          const foundProp = props.allOptions.find(o => o.id == respuestaSeleccionada.value);
          if (foundProp) return foundProp.title;
      }
      return 'Cargando...';
  }
  
  const id = Number(respuestaSeleccionada.value);
  const option = optionsMap.value.get(id);
  
  if (!option) {
       // Deep search in map values
       const found = Array.from(optionsMap.value.values()).find(o => o.id == respuestaSeleccionada.value);
       if (found) return found.title;

       // FINAL FALLBACK: Search props directly (in case map is stale)
       if (props.allOptions) {
            const foundProp = props.allOptions.find(o => o.id == respuestaSeleccionada.value);
            if (foundProp) {
                // Self-repair the map
                optionsMap.value.set(Number(foundProp.id), foundProp);
                return foundProp.title;
            }
       }
       
       console.warn(`[Q${props.questionId}] OPTION NOT FOUND. ID: ${id}. Available:`, Array.from(optionsMap.value.keys()));
       return 'Opción no encontrada';
  }
  return option.title;
};

const seleccionarRespuesta = async (respuestaId) => {
  if (!respuestaId) return;
  if (props.readOnly) return;
  if ((respuestaSeleccionada.value || userHasVoted.value) && !isEditingVote.value) return;

  // Capture previous vote ID for optimistic update logic (if editing)
  const previousVoteId = isEditingVote.value ? Number(respuestaSeleccionada.value) : null;

  respuestaSeleccionada.value = respuestaId;

  const isAnonymous = !store.getters.isAuthenticated;
  const profileId = isAnonymous ? 0 : Number(props.profileId);
  const payload = {
    question_id: props.questionId,
    option_id: respuestaId,
    is_anonymous: isAnonymous,
    user_token: isAnonymous ? userToken : null,
    profile_id: profileId
  };

  try {
    // Optimistic Update
    
    // If editing, decrement the previous vote first
    if (isEditingVote.value && previousVoteId) {
        const prevOption = optionsMap.value.get(previousVoteId);
        if (prevOption) {
            prevOption.votes = Math.max(0, prevOption.votes - 1);
            optionsMap.value.set(previousVoteId, prevOption);
        }
        totalVotos.value = Math.max(0, totalVotos.value - 1);
    }

    const option = optionsMap.value.get(respuestaId);
    if (option) {
        option.votes++;
        optionsMap.value.set(respuestaId, option); // Trigger reactivity
    }
    totalVotos.value++;

    await store.dispatch('voteForOption', payload);

    if (isAnonymous) {
      setCookie(`${COOKIE_NAME}_vote_${props.questionId}`, true, 30);
    }

    toast.success('¡Votación exitosa!');
    isEditingVote.value = false;
    
    emit('respuesta-seleccionada', respuestaId);
  } catch (error) {
    // Revert optimistic update
    const option = optionsMap.value.get(respuestaId);
    if (option) {
        option.votes--;
        optionsMap.value.set(respuestaId, option);
    }
    totalVotos.value--;
    
    // Revert previous vote decrement if we failed
    if (isEditingVote.value && previousVoteId) {
         const prevOption = optionsMap.value.get(previousVoteId);
         if (prevOption) {
             prevOption.votes++;
             optionsMap.value.set(previousVoteId, prevOption);
         }
         totalVotos.value++;
    }
    
    respuestaSeleccionada.value = previousVoteId || null;
    console.error('Error al votar:', error);
    toast.error('Error al votar. Por favor, intenta de nuevo.');
  }
};

const handleDropdownChange = () => {
  if (selectedDropdownOption.value) {
    seleccionarRespuesta(selectedDropdownOption.value);
  }
};

const toggleVisibility = async () => {
    try {
        const response = await axios.post('answers/toggle-privacy/', { question_id: props.questionId });
        isVotePublic.value = response.data.is_public;
        toast.info(isVotePublic.value ? "Voto visible" : "Voto privado");
    } catch (e) {
        console.error(e);
        toast.error("Error al cambiar privacidad");
    }
};



const iconosPorCategoria = {
  salud: 'fa fa-medkit',
  deporte: 'fa fa-futbol',
  tecnologia: 'fa fa-laptop',
  salud: 'fa fa-medkit',
  deporte: 'fa fa-futbol',
  tecnologia: 'fa fa-laptop',
  entretenimiento: 'fa fa-film',
  politica: 'fa fa-balance-scale',
  sociedad: 'fa fa-users',
  internacional: 'fas fa-globe',
  educacion: 'fa fa-graduation-cap',
  masVotadas: 'fa fa-star',
  masNuevo: 'fa fa-clock',
};

const calcularIcono = (categoria) => iconosPorCategoria[categoria?.toLowerCase()] || 'fa fa-question-circle';



const formatFecha = (fecha) => {
  if (!fecha) return 'Fecha no disponible';
  try {
    const date = parseISO(fecha);
    return format(date, "dd-MM-yyyy");
  } catch (error) {
    console.error('Error formateando la fecha:', error);
    return 'Fecha no válida';
  }
};

const updateCountdown = () => {
  if (!props.expirationDate) return;
  
  const now = new Date();
  const expDate = new Date(props.expirationDate);
  const timeDiff = expDate - now;
  
  if (timeDiff <= 0) {
    isExpired.value = true;
    timeRemaining.value = 'Expired';
    return;
  }
  
  const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);
  
  if (days > 0) {
    timeRemaining.value = `${days}d ${hours}h`;
  } else if (hours > 0) {
    timeRemaining.value = `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    timeRemaining.value = `${minutes}m ${seconds}s`;
  } else {
    timeRemaining.value = `${seconds}s`;
  }
};

let countdownInterval = null;

onMounted(() => {
  if (props.expirationDate) {
    updateCountdown();
    countdownInterval = setInterval(updateCountdown, 1000);
  }
});

onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval);
  }
});
</script>

<style scoped>
/* Scrollbar Styles */
.scrollable-results {
  max-height: 220px;
  overflow-y: auto;
  padding-right: 5px; /* Space for scrollbar */
}

/* Custom Scrollbar */
.scrollable-results::-webkit-scrollbar {
  width: 6px;
}

.scrollable-results::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.scrollable-results::-webkit-scrollbar-thumb {
  background: var(--colorprimary); 
  border-radius: 3px;
}

.scrollable-results::-webkit-scrollbar-thumb:hover {
  background: var(--colorsecondary);
}

/* Estilos base mantenidos */
.grid-container {
  display: flex;
  flex-direction: column;
  background: var(--gradient-card);
  backdrop-filter: var(--backdrop-blur);
  -webkit-backdrop-filter: var(--backdrop-blur);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 10px;
  min-height: auto;
  height: auto;
  overflow: visible; /* Restored to visible for shadows */
  position: relative; /* Removed !important, relative is standard */
  justify-content: space-between;
}

.grid-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-primary);
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 10px 10px 0 0;
}

.grid-container:hover::before {
  opacity: 1;
}

.grid-container:hover {
  transform: translateY(-2px) scale(1.005);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.2);
}

.icono-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--colortext);
  font-size: 0.85rem;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 8px;
}

.icono-container a {
  text-decoration: none;
}

.icono-container i {
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1rem;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.icono-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.categoria-nombre {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--colortext);
  letter-spacing: 0.5px;
}

.pregunta {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--colortext);
  margin-bottom: 10px;
  line-height: 1.3;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  padding: 8px 12px;
  transition: all 0.3s ease;
  border: 1px solid rgba(128, 128, 128, 0.1);
  text-align: left;
  position: relative;
  overflow: hidden;
}

.respuesta:hover {
  background: var(--gradient-hover);
  color: white;
  transform: translateX(3px);
  box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
  border-color: rgba(255,255,255,0.2);
}

.resultados {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 0;
}

.resultado-item {
  width: 100%;
}

.respuesta-label {
  font-weight: 600;
  font-size: 0.8rem;
  color: var(--colortext);
  margin-bottom: 3px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.voted-option .respuesta-label {
    color: #4ADE80;
    font-weight: 700;
}

.progress-track {
  width: 100%;
  height: 20px;
  background: var(--colorquaternary);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-fill {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: 10px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

.voted-option .progress-fill {
    background: linear-gradient(90deg, #34D399, #10B981) !important;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: 700;
  font-size: 0.7rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* SCALE styles */
.scale-container {
  margin-bottom: 10px;
}

.scale-buttons {
  display: flex;
  gap: 8px;
  justify-content: space-between;
}

.scale-button {
  flex: 1;
  padding: 10px;
  background: var(--colorquaternary);
  color: var(--colortext);
  border: 2px solid var(--glass-border);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 1.1rem;
  transition: all 0.3s ease;
}

.scale-button:hover {
  background: var(--gradient-primary);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.scale-results {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.scale-result-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.scale-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--colorsecondary);
  display: flex;
  align-items: center;
  gap: 5px;
}

.selected-scale {
  color: #4ADE80;
  font-weight: 700;
}

.scale-bar {
  height: 16px;
  background: var(--colorquaternary);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.scale-fill {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: 8px;
  transition: width 1s ease;
}

.scale-percent {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.7rem;
  color: white;
  font-weight: 700;
}

/* OPEN styles */
.open-container {
    margin-bottom: 10px;
    width: 100%;
}

.open-input-wrapper {
    display: flex;
    gap: 10px;
}

.open-input {
    flex-grow: 1;
    background: var(--colorquaternary);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    padding: 10px;
    font-size: 0.95rem;
    outline: none;
    transition: all 0.3s ease;
}

.open-input:focus {
    background: rgba(255, 255, 255, 0.1);
    border-color: #3B82F6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.btn-enviar {
    background: var(--gradient-primary);
    border: none;
    border-radius: 8px;
    color: white;
    padding: 0 15px;
    cursor: pointer;
    transition: transform 0.2s;
}

.btn-enviar:hover {
    transform: scale(1.05);
}

.btn-enviar:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

.open-result {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 8px;
    padding: 10px;
    color: white;
    font-size: 0.95rem;
}

.selected-answer i {
    color: #4ADE80;
    margin-right: 5px;
}
.dropdown-container {
  margin-bottom: 10px;
}

.dropdown-select {
  width: 100%;
  padding: 12px;
  background: var(--colorquaternary);
  color: var(--colortext);
  border: 2px solid var(--glass-border);
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dropdown-select:focus {
  outline: none;
  border-color: var(--colorprimary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.dropdown-select option {
  background: var(--colorbase);
  color: var(--colortext);
}

.dropdown-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selected-answer {
  background: rgba(74, 222, 128, 0.1);
  padding: 10px;
  border-radius: 8px;
  border-left: 3px solid #4ADE80;
  color: var(--colortext);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.selected-answer i {
  color: #4ADE80;
}

.dropdown-result-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-title {
  font-size: 0.85rem;
  color: var(--colortext);
  font-weight: 500;
}

.voted-option-text {
  color: #4ADE80;
  font-weight: 700;
}

.option-votes {
  font-size: 0.75rem;
  color: var(--colorsecondary);
}

.option-bar {
  height: 12px;
  background: var(--colorquaternary);
  border-radius: 6px;
  position: relative;
  overflow: hidden;
}

.option-fill {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: 6px;
  transition: width 1s ease;
}

.option-percent {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.65rem;
  color: white;
  font-weight: 700;
}

/* Common styles */
.votos {
  text-align: right;
  font-size: 0.7rem;
  color: var(--colorsecondary);
  margin-top: 6px;
  padding-top: 6px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 5px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  white-space: nowrap;
}

.votos::before {
  content: '\f080';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
}

.countdown {
  font-size: 0.75rem;
  color: var(--colorsecondary);
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.countdown i {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 0.85rem;
}

.countdown .expired {
  color: #EF4444;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.edit-icon {
  margin-left: 6px;
  font-size: 0.8rem;
}

.privacy-icon {
    margin-right: 8px;
    cursor: pointer;
    font-size: 0.8rem;
    color: #9CA3AF;
    transition: color 0.3s;
}

.privacy-icon:hover {
    color: var(--colorprimary);
}

.privacy-icon.fa-eye-slash {
    color: #EF4444;
}

.fecha {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
}

.rating-container {
    display: flex;
    flex-direction: row; /* 1 sola línea */
    align-items: center;
    justify-content: flex-start; /* Lado izquierdo */
    gap: 10px;
    margin-top: 8px;
    width: 100%;
}

.rating-info-line {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.9rem;
    color: var(--colortext);
    font-weight: 600;
}

.stars {
    display: flex;
    gap: 5px;
    font-size: 1.1rem;
    cursor: pointer;
}

.stars .fas {
    color: #FFD700; /* Amarillo más intenso (Gold) */
    filter: drop-shadow(0 0 2px rgba(0,0,0,0.5));
}

.stars .far {
    color: #4B5563; /* Gris para estrellas vacías */
}

.stars i.interactive:hover {
    transform: scale(1.1);
}

.edit-actions {
    display: flex;
    gap: 8px;
    margin-left: 8px;
}

.delete-icon {
    color: #EF4444;
    cursor: pointer;
    font-size: 0.9rem;
}

.cancel-icon {
    color: #9CA3AF;
    cursor: pointer;
    font-size: 0.9rem;
}

.delete-icon:hover {
    color: #DC2626;
    transform: scale(1.1);
}

.cancel-icon:hover {
    color: white;
}

/* Report Button */
.report-btn {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.25);
  cursor: pointer;
  padding: 6px 8px;
  font-size: 0.85em;
  transition: all 0.3s ease;
  z-index: 5;
  border-radius: 4px;
}

.report-btn:hover {
  color: #EF4444;
  background: rgba(239, 68, 68, 0.1);
  transform: scale(1.1);
}

.report-btn i {
  pointer-events: none;
}

/* SLIDER styles */
.slider-container {
  margin-bottom: 12px;
  width: 100%;
}

.slider-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.slider-value-wrapper {
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 5px;
  margin-bottom: 5px;
}

.slider-number-input {
  background: transparent;
  border: none;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  color: var(--colorprimary);
  font-size: 1.5rem;
  font-weight: 700;
  width: 80px;
  text-align: right;
  outline: none;
  padding-bottom: 2px;
  text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
  -moz-appearance: textfield;
}

.slider-number-input::-webkit-outer-spin-button,
.slider-number-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.slider-number-input:focus {
  border-bottom-color: var(--colorprimary);
}

.unit {
  font-size: 1rem;
  font-weight: 600;
  color: var(--colorsecondary);
}

.slider-input {
  -webkit-appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: var(--colorquaternary);
  outline: none;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--colorprimary); /* Blue Thumb */
  cursor: pointer;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.6);
  border: 2px solid white;
  margin-top: -8px; /* Center thumb on track */
}

.slider-input::-webkit-slider-runnable-track {
  width: 100%;
  height: 6px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.slider-input:hover::-webkit-slider-thumb {
  transform: scale(1.1);
  background: white;
  border-color: var(--colorprimary);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--colorsecondary);
  font-weight: 600;
  padding: 0 2px;
}

.votar-btn {
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 10px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.9rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.votar-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(59, 130, 246, 0.4);
}

.votar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #374151; /* Gray for disabled */
  box-shadow: none;
}

.slider-result {
    background: rgba(59, 130, 246, 0.1);
    padding: 15px;
    border-radius: 8px;
    border: 1px solid rgba(59, 130, 246, 0.3);
    text-align: center;
}

.user-vote-display {
    font-size: 1.1rem;
    color: var(--colortext);
}

.user-vote-display strong {
    color: #4ADE80;
    font-size: 1.3rem;
    margin-left: 5px;
}
</style>
