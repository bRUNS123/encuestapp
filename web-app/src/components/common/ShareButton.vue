<template>
  <button 
    @click.stop="share" 
    class="share-button" 
    :class="{ 'copied': copied }"
    :title="copied ? '¡Copiado!' : 'Compartir'"
  >
    <i v-if="copied" class="fas fa-check"></i>
    <i v-else class="fas fa-share-alt"></i>
    <span v-if="showLabel" class="share-label">{{ copied ? 'Copiado' : 'Compartir' }}</span>
  </button>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  text: {
    type: String,
    default: ''
  },
  url: {
    type: String,
    default: () => window.location.href
  },
  showLabel: {
    type: Boolean,
    default: false
  }
});

const copied = ref(false);

const share = async () => {
  const shareData = {
    title: props.title,
    text: props.text,
    url: props.url
  };

  // Try native share first (Mobile/Safari)
  if (navigator.share) {
    try {
      await navigator.share(shareData);
      return;
    } catch (err) {
      console.log('Error sharing:', err);
    }
  }

  // Fallback to clipboard
  try {
    await navigator.clipboard.writeText(`${props.title} ${props.url}`);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (err) {
    console.error('Failed to copy:', err);
  }
};
</script>

<style scoped>
.share-button {
  background: transparent;
  border: none;
  color: var(--colortext);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.7;
}

.share-button:hover {
  background: rgba(255, 255, 255, 0.1);
  opacity: 1;
  transform: translateY(-2px);
  color: var(--colorprimary);
}

.share-button.copied {
  color: #10b981; /* Green success */
}

.share-label {
  font-size: 0.85rem;
  font-weight: 600;
}
</style>
