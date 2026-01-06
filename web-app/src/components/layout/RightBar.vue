<template>
  <div>
    <div v-if="displayedQuestions.length === 0 && !loading">No hay preguntas disponibles</div>
    <transition-group name="fade-slide" tag="div" class="rightbar-list">
      <Pregunta 
        v-for="pregunta in displayedQuestions"
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
        :profileId="profileId"
        @respuesta-seleccionada="handleVote(pregunta.id)"
      />
    </transition-group>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'vue-toastification';
import Pregunta from '/src/components/preguntas/Pregunta.vue';

const store = useStore();
const toast = useToast();

const profileId = computed(() => store.state.user ? store.state.user.id : null);
const user = computed(() => store.state.user);

const votedQuestionIds = ref(new Set());
const pendingReplacements = ref(new Map()); // questionId -> timeoutId

const obtenerPreguntasAleatorias = (preguntas, cantidad) => {
  const preguntasAleatorias = [];
  const preguntasCopy = [...preguntas];
  while (preguntasAleatorias.length < cantidad && preguntasCopy.length > 0) {
    const randomIndex = Math.floor(Math.random() * preguntasCopy.length);
    preguntasAleatorias.push(preguntasCopy.splice(randomIndex, 1)[0]);
  }
  return preguntasAleatorias;
};

const displayedQuestions = ref([]);

const preguntas = computed(() => store.getters.rightBarPreguntas);

// Get available questions (not voted and not currently displayed)
const getAvailableQuestions = () => {
  return preguntas.value.filter(p => 
    !votedQuestionIds.value.has(p.id) && 
    !displayedQuestions.value.some(dq => dq.id === p.id)
  );
};

const randomizeQuestions = () => {
  if (preguntas.value && preguntas.value.length > 0) {
    const availableQuestions = preguntas.value.filter(p => !votedQuestionIds.value.has(p.id));
    displayedQuestions.value = obtenerPreguntasAleatorias(availableQuestions, 6);
  }
};

watch(preguntas, () => {
  randomizeQuestions();
}, { immediate: true });

const loading = computed(() => store.getters.loading);
const error = computed(() => store.getters.error);

const loadQuestions = () => {
  console.log('🔄 RightBar: Loading questions...');
  toast.info("Cargando preguntas...");
  store.dispatch('fetchRightBarPreguntas').then(() => {
    console.log('✅ RightBar: Questions loaded successfully');
    toast.clear();
    toast.success("Preguntas cargadas exitosamente");
  }).catch(err => {
    console.error('❌ RightBar: Error loading questions:', err);
    toast.clear();
    toast.error("Error al cargar preguntas: " + err.message);
  });
};

onMounted(() => {
  loadQuestions();
});

// Watch for user authentication changes
watch(user, (newUser, oldUser) => {
  console.log('👤 RightBar: User state changed', { 
    hadUser: !!oldUser, 
    hasUser: !!newUser,
    userId: newUser?.id 
  });
  
  // If user just logged in (went from no user to having a user)
  if (!oldUser && newUser) {
    console.log('🔐 RightBar: User just logged in, reloading questions');
    loadQuestions();
  }
}, { immediate: false });

const replaceQuestion = (questionId) => {
  const available = getAvailableQuestions();
  
  if (available.length > 0) {
    // Get a random new question
    const newQuestion = available[Math.floor(Math.random() * available.length)];
    
    // Find and replace the voted question
    const index = displayedQuestions.value.findIndex(q => q.id === questionId);
    if (index !== -1) {
      displayedQuestions.value.splice(index, 1, newQuestion);
    }
  } else {
    // No more questions available, just remove the voted one
    displayedQuestions.value = displayedQuestions.value.filter(q => q.id !== questionId);
  }
  
  // Clean up the pending replacement
  pendingReplacements.value.delete(questionId);
};

const handleVote = (questionId) => {
  // Mark as voted
  votedQuestionIds.value.add(questionId);
  
  // Cancel any existing timeout for this question
  if (pendingReplacements.value.has(questionId)) {
    clearTimeout(pendingReplacements.value.get(questionId));
  }
  
  // Random delay between 5-10 seconds
  const delay = 5000 + Math.random() * 5000;
  
  const timeoutId = setTimeout(() => {
    replaceQuestion(questionId);
  }, delay);
  
  // Store the timeout ID
  pendingReplacements.value.set(questionId, timeoutId);
};

</script>

<style scoped>
.error {
  color: red;
}

/* Fade and slide animations */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(30px) scale(0.95);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-30px) scale(0.95);
}

.fade-slide-move {
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.rightbar-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px; /* Spacing on all sides */
}
</style>
