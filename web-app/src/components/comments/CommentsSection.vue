<template>
  <div class="comments-section">
    <div class="comments-header">
      <h3>Comentarios ({{ comments.length }})</h3>
    </div>

    <div class="comments-list" v-if="comments.length > 0">
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-avatar">
          <i class="fas fa-user-circle"></i>
        </div>
        <div class="comment-content">
          <div class="comment-meta">
            <span class="comment-author">{{ comment.nickname || comment.username || 'Usuario' }}</span>
            <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
          </div>
          <p class="comment-text">{{ comment.text }}</p>
        </div>
      </div>
    </div>
    <div v-else class="no-comments">
      Sé el primero en comentar.
    </div>

    <div class="add-comment" v-if="isAuthenticated">
      <div class="comment-input-wrapper">
        <textarea 
          v-model="newComment" 
          placeholder="Escribe un comentario..." 
          rows="2"
          @keydown.enter.prevent="submitComment"
        ></textarea>
        <button @click="submitComment" :disabled="!newComment.trim() || isSubmitting">
          <i class="fas fa-paper-plane"></i>
        </button>
      </div>
    </div>
    <div v-else class="login-prompt">
      <router-link to="/login">Inicia sesión</router-link> para comentar.
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

const props = defineProps({
  questionId: {
    type: Number,
    required: true
  }
});

const store = useStore();
const newComment = ref('');
const isSubmitting = ref(false);

const comments = computed(() => store.state.comments[props.questionId] || []);
const isAuthenticated = computed(() => store.getters.isAuthenticated);

const formatDate = (dateString) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true, locale: es });
  } catch (e) {
    return '';
  }
};

const submitComment = async () => {
  if (!newComment.value.trim()) return;
  
  isSubmitting.value = true;
  try {
    await store.dispatch('postComment', {
      questionId: props.questionId,
      text: newComment.value
    });
    newComment.value = '';
  } catch (error) {
    console.error('Error posting comment:', error);
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  store.dispatch('fetchComments', props.questionId);
});
</script>

<style scoped>
.comments-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  animation: fadeIn 0.3s ease;
}

.comments-header h3 {
  font-size: 0.9rem;
  color: var(--colorsecondary);
  margin-bottom: 10px;
  text-transform: uppercase;
  font-weight: 700;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 15px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 5px;
}

/* Custom Scrollbar for comments */
.comments-list::-webkit-scrollbar {
  width: 4px;
}
.comments-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}
.comments-list::-webkit-scrollbar-thumb {
  background: var(--colorsecondary);
  border-radius: 4px;
}

.comment-item {
  display: flex;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  padding: 8px 12px;
  border-radius: 8px;
}

.comment-avatar i {
  font-size: 1.5rem;
  color: var(--colorsecondary);
  margin-top: 4px;
}

.comment-content {
  flex: 1;
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 0.75rem;
}

.comment-author {
  font-weight: 700;
  color: var(--colortext);
}

.comment-date {
  color: var(--colorsecondary);
}

.comment-text {
  font-size: 0.9rem;
  color: var(--colortext);
  margin: 0;
  line-height: 1.4;
  word-break: break-word;
}

.no-comments {
  text-align: center;
  color: var(--colorsecondary);
  font-size: 0.9rem;
  font-style: italic;
  margin: 15px 0;
}

.comment-input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  background: rgba(0, 0, 0, 0.2);
  padding: 8px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.comment-input-wrapper textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--colortext);
  font-family: inherit;
  font-size: 0.9rem;
  resize: none;
  outline: none;
}

.comment-input-wrapper button {
  background: var(--colorprimary);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.comment-input-wrapper button:disabled {
  background: var(--colorsecondary);
  opacity: 0.5;
  cursor: not-allowed;
}

.comment-input-wrapper button:hover:not(:disabled) {
  transform: scale(1.05);
  background: var(--colortertiary);
}

.login-prompt {
  text-align: center;
  font-size: 0.9rem;
  color: var(--colorsecondary);
  margin-top: 10px;
}

.login-prompt a {
  color: var(--colorprimary);
  text-decoration: none;
  font-weight: 600;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
