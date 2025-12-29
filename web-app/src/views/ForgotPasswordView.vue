<template>
  <div class="forgot-password-container">
    <div class="card glass-effect">
      <h2>Recuperar Contraseña</h2>
      
      <div v-if="step === 1" class="step-content">
        <p class="instruction">Ingresa tu email para recibir un código de recuperación.</p>
        
        <div class="form-group">
          <label>Email</label>
          <input 
            v-model="email" 
            type="email" 
            placeholder="tu@email.com" 
            @keyup.enter="requestReset"
          />
        </div>
        
        <button class="btn-primary" @click="requestReset" :disabled="loading">
          <span v-if="loading">Enviando...</span>
          <span v-else>Enviar Código</span>
        </button>
      </div>

      <div v-else class="step-content">
        <p class="instruction">Revisa la consola del servidor para ver el código.</p>
        
        <div class="form-group">
          <label>Código de Verificación (6 dígitos)</label>
          <input v-model="code" type="text" placeholder="123456" />
        </div>
        
        <div class="form-group">
          <label>Nueva Contraseña</label>
          <div class="input-wrapper">
             <input :type="showPassword ? 'text' : 'password'" v-model="password" placeholder="Nueva contraseña" />
             <span class="password-toggle" @click="showPassword = !showPassword">
                <i :class="['fas', showPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
             </span>
          </div>
        </div>

        <button class="btn-primary" @click="confirmReset" :disabled="loading">
          <span v-if="loading">Actualizando...</span>
          <span v-else>Cambiar Contraseña</span>
        </button>
      </div>

      <p v-if="error" class="error-msg">{{ error }}</p>
      
      <div class="actions">
        <router-link to="/auth" class="back-link">Volver al Login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useToast } from 'vue-toastification';

const router = useRouter();
const toast = useToast();

const step = ref(1);
const email = ref('');
const code = ref('');
const password = ref('');
const showPassword = ref(false);
const loading = ref(false);
const error = ref('');

// Use direct axios import or the instance if available globally, but we can assume axiosInstance pattern
// For simplicity in this standalone view, importing axios and using base URL
// Better to use the store or axiosInstance from utils
import axiosInstance from '@/store/axiosInstance';

const requestReset = async () => {
  if (!email.value) { error.value = "Ingresa tu email"; return; }
  loading.value = true;
  error.value = "";
  
  try {
    await axiosInstance.post('/password-reset/request_reset/', { email: email.value });
    step.value = 2;
    toast.success("Código enviado. Revisa la consola.");
  } catch (err) {
    console.error(err);
    error.value = err.response?.data?.error || "Error al solicitar código";
    toast.error("Error al solicitar código");
  } finally {
    loading.value = false;
  }
};

const confirmReset = async () => {
  if (!code.value || !password.value) { error.value = "Completa todos los campos"; return; }
  loading.value = true;
  error.value = "";
  
  try {
    await axiosInstance.post('/password-reset/confirm_reset/', { 
      email: email.value,
      code: code.value,
      password: password.value 
    });
    toast.success("Contraseña actualizada exitosamente");
    router.push('/auth');
  } catch (err) {
    console.error(err);
    error.value = err.response?.data?.error || "Error al restablecer contraseña";
    toast.error(error.value);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.forgot-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.card {
  background: var(--colorbase);
  padding: 2rem;
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

h2 {
  margin-bottom: 1.5rem;
  color: var(--colortext);
  font-weight: 700;
}

.instruction {
  color: var(--colortext);
  opacity: 0.8;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.2rem;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: var(--colortext);
  font-weight: 600;
}

input {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--colorsecondary);
  background: rgba(255, 255, 255, 0.05);
  color: var(--colortext);
  font-size: 1rem;
  transition: all 0.3s ease;
}

input:focus {
  border-color: var(--colorprimary);
  outline: none;
  background: rgba(255, 255, 255, 0.1);
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: var(--colorprimary);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 1rem;
  transition: transform 0.2s;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-msg {
  color: #ef4444;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.actions {
  margin-top: 1.5rem;
}

.back-link {
  color: var(--colortext);
  text-decoration: underline;
  font-size: 0.9rem;
  cursor: pointer;
}

.input-wrapper {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--colortext);
  cursor: pointer;
  opacity: 0.7;
}

/* Mobile Adjustments */
@media (max-width: 480px) {
  .card {
    padding: 1.5rem;
  }
}
</style>
