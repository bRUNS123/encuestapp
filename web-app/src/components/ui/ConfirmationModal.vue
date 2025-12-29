<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click="$emit('cancel')">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <i class="fas fa-exclamation-triangle warning-icon"></i>
          <h3>¿Estás seguro?</h3>
        </div>
        <div class="modal-body">
          <p>{{ message }}</p>
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="$emit('cancel')">Cancelar</button>
          <button class="btn-confirm" @click="$emit('confirm')">Eliminar</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: "¿Estás seguro de que deseas realizar esta acción?"
  }
});

defineEmits(['confirm', 'cancel']);
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85); /* Darker dim for better contrast */
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: #0f0f15; /* Much darker background */
  border: 1px solid rgba(255, 255, 255, 0.15); /* Slightly brighter border */
  padding: 25px 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7); /* Stronger shadow */
  animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  color: #ffffff; /* Pure white text */
  text-align: center;
}

.modal-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.warning-icon {
  font-size: 2rem;
  color: #EF4444;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4rem; /* Larger title */
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
  letter-spacing: 0.5px;
}

.modal-body p {
  color: #e5e7eb; /* Much brighter grey, almost white */
  font-size: 1rem;
  line-height: 1.6;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 5px;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-cancel {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--colortext, white);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-confirm {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.btn-confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
