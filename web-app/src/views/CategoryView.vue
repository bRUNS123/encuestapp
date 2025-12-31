<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'vue-toastification';
import Pregunta from '/src/components/preguntas/Pregunta.vue';
import { useRoute } from 'vue-router';
import { categorias } from '/src/utils/categoriaUtils.js';

const store = useStore();
const toast = useToast();
const route = useRoute();

const profileId = computed(() => store.state.user ? store.state.user.id : null);
const routeCategory = computed(() => route.params.categoria);
const categoria = computed(() => {
    // Find matching category in utils to get the correct backend name (case-sensitive)
    if (!routeCategory.value) return '';
    const match = categorias.value.find(c => c.enlace === '/' + routeCategory.value);
    return match ? match.nombre : routeCategory.value;
});
const questions = ref([]);
const loading = ref(false);
const error = computed(() => store.getters.error);


const loadQuestions = async () => {
    // Force cache bust - v1.2.2
    console.log("🚀 loadQuestions START. Categoria computed:", categoria.value);
    if (!categoria.value) {
        console.warn("❌ Categoria value is empty/null");
        return;
    }
    
    questions.value = [];
    loading.value = true;
    
    try {
        // Use server-side filtering action
        console.log("📞 Dispatching fetchQuestionsByCategory with:", categoria.value);
        const result = await store.dispatch('fetchQuestionsByCategory', categoria.value);
        console.log("📦 Result from dispatch:", result);
        
        // Reorder for vertical filling (column by column)
        const half = Math.ceil(result.length / 2);
        const reordered = [];
        
        for (let i = 0; i < half; i++) {
            reordered.push(result[i]);
            if (i + half < result.length) {
                reordered.push(result[i + half]);
            }
        }

        questions.value = reordered;
        // Commit to store so Pregunta.vue can find data (e.g. for answers)
        // Store keeps original order or reordered? It mostly matters for finding by ID.
        store.commit('SET_PREGUNTAS', result);
    } catch (err) {
        toast.error("Error al cargar preguntas: " + err.message);
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
  loadQuestions();
});

watch(() => route.params.categoria, () => {
  loadQuestions();
});

const mostrarRespuesta = (respuesta) => {
  toast.success("Respuesta seleccionada: " + respuesta);
};
</script>

<template>
  <div v-if="error" class="error">{{ error }}</div>
  <div v-else-if="loading" class="loading-state">
      Cargando...
  </div>
  <div v-else-if="questions.length === 0" class="empty-state">No hay preguntas disponibles para {{ categoria }}</div>
  <template v-else>
      <Pregunta 
        v-for="pregunta in questions"
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
        @respuesta-seleccionada="mostrarRespuesta"
        :isPublic="true" 
      />
  </template>
</template>

<style scoped>
.error {
  color: #EF4444;
  text-align: center;
  padding: 20px;
}
.loading-state, .empty-state {
    text-align: center;
    padding: 40px;
    color: #9CA3AF;
    font-size: 1.1rem;
}
.questions-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}
</style>
