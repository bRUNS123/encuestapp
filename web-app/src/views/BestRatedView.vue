<template>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-else-if="preguntas.length === 0 && !loading">No hay preguntas disponibles</div>
    <Pregunta 
      v-for="pregunta in preguntas"
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
      :ratingAverage="pregunta.rating_average"
      :ratingCount="pregunta.rating_count"
      :userRating="pregunta.user_rating"
      @respuesta-seleccionada="mostrarRespuesta"
    />
  </template>
  
  <script setup>
  import { computed, onMounted } from 'vue';
  import { useStore } from 'vuex';
  import { useToast } from 'vue-toastification';
  import Pregunta from '/src/components/preguntas/Pregunta.vue';
  
  const store = useStore();
  const toast = useToast();
  
  const profileId = computed(() => store.state.user ? store.state.user.id : null);
  
  const preguntas = computed(() => {
    const sorted = store.getters.preguntas.slice().sort((a, b) => (b.rating_average || 0) - (a.rating_average || 0));
    
    // Reorder for vertical filling (column by column)
    const half = Math.ceil(sorted.length / 2);
    const reordered = [];
    
    for (let i = 0; i < half; i++) {
      reordered.push(sorted[i]);
      if (i + half < sorted.length) {
        reordered.push(sorted[i + half]);
      }
    }
    
    return reordered;
  });
  
  const loading = computed(() => store.getters.loading);
  const error = computed(() => store.getters.error);
  
  onMounted(() => {
    // We fetch all questions and sort locally as per existing pattern
    // Alternatively call store action with ordering param if implemented
    store.dispatch('fetchPreguntas');
  });
  
  const mostrarRespuesta = (respuesta) => {
    toast.success("Respuesta seleccionada: " + respuesta);
  };
  
  </script>
  
  <style scoped>
  .error {
    color: red;
  }
  </style>
