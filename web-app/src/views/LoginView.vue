<template>
  <div class="auth-wrapper">
    <div class="auth-container">
      <h1 v-if="isLogin">{{ loginTitle }}</h1>
      <h1 v-else>{{ registerTitle }}</h1>


      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="email">Email:</label>
          <input type="email" id="email" v-model="email" placeholder="usuario@ejemplo.com" required>
        </div>
        <div class="form-group">
          <label for="password">Password:</label>
          <div class="input-wrapper">
            <input :type="showPassword ? 'text' : 'password'" id="password" v-model="password" placeholder="Ingresa tu contraseña" required>
            <span @click="togglePasswordVisibility" class="password-toggle">
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </span>
          </div>
        </div>
        <div v-if="!isLogin" class="form-group">
          <label for="confirm-password">Confirm Password:</label>
          <div class="input-wrapper">
            <input :type="showConfirmPassword ? 'text' : 'password'" id="confirm-password" v-model="confirmPassword" placeholder="Confirma tu contraseña" required>
            <span @click="toggleConfirmPasswordVisibility" class="password-toggle">
              <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </span>
          </div>
        </div>
        <div v-if="!isLogin" class="form-row">
          <div class="form-group half-width">
            <label for="birth-year">Año:</label>
            <select id="birth-year" v-model="birthYear" required>
              <option value="" disabled selected>Año</option>
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
          <div class="form-group half-width">
            <label for="gender">Género:</label>
            <select id="gender" v-model="gender" required>
              <option value="" disabled selected>Género</option>
              <option value="Masculino">Masculino</option>
              <option value="Femenino">Femenino</option>
              <option value="Otro">Otro</option>
            </select>
          </div>
        </div>
        <div v-if="isLogin" class="form-group options-row">
          <label class="checkbox-label" for="rememberMe">
              <input type="checkbox" v-model="rememberMe" id="rememberMe">
              <span class="checkbox-text">Recordar usuario</span>
          </label>
          <router-link to="/forgot-password" class="forgot-password">¿Olvidaste la contraseña?</router-link>
        </div>
        <button type="submit" class="auth-button">{{ isLogin ? 'Acceder' : 'Registrarse' }}</button>
      </form>
      <div class="social-login" v-if="isLogin">
        <p>O Continua Con</p>
        <div class="social-buttons">
          <button @click="loginWithFacebook" class="facebook-button">Facebook</button>
          <button @click="loginWithGoogle" class="google-button">Google</button>
        </div>
      </div>
      <div class="toggle-link">
        <a href="#" @click.prevent="toggleAuthMode">
            {{ isLogin ? 'CREA UNA CUENTA' : 'INICIAR SESIÓN' }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'vue-toastification';
import { seleccionarCategoria } from '/src/utils/categoriaUtils.js';

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const birthYear = ref('');
const gender = ref('');
const isLogin = ref(true);
const rememberMe = ref(false); // New state
const loginTitle = ref('Bienvenid@');
const registerTitle = ref('Registro');
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const toast = useToast();

const store = useStore();

const currentYear = new Date().getFullYear();
const years = Array.from({ length: 100 }, (_, i) => currentYear - i);

const errorMessages = {
  "profile with this email already exists.": "Ya existe un perfil con este email."
};

onMounted(() => {
    const savedEmail = localStorage.getItem('userEmail');
    if (savedEmail) {
        email.value = savedEmail;
        rememberMe.value = true;
    }
});

const handleSubmit = async () => {
  if (isLogin.value) {
    try {
      await store.dispatch('login', { email: email.value, password: password.value });
      
      // Handle Remember Me
      if (rememberMe.value) {
          localStorage.setItem('userEmail', email.value);
      } else {
          localStorage.removeItem('userEmail');
      }

      toast.success('¡Inicio de sesión exitoso!');
      seleccionarCategoria(1); // ID del elemento "/" en el menú de categorías
    } catch (error) {
      console.error("Login catch error:", error);
      let errorMessage = 'Error al iniciar sesión. Verifique sus credenciales.';
      
      if (error && error.detail) {
          errorMessage = 'Credenciales incorrectas.'; // Overwrite standard Django/JWT detail
      } else if (error && error.data && error.data.detail) {
           errorMessage = 'Credenciales incorrectas.';
      } else if (error && error.email) {
          errorMessage = error.email[0];
      }

      toast.error(errorMessages[errorMessage] || errorMessage);
    }
  } else {
    if (password.value !== confirmPassword.value) {
      toast.error('Las contraseñas no coinciden.');
      return;
    }
    try {
      await store.dispatch('register', { email: email.value, password: password.value, birth_year: birthYear.value, gender: gender.value });
      toast.success('¡Registro exitoso! Iniciando sesión...');
      
      // Auto login
      await store.dispatch('login', { email: email.value, password: password.value });
      toast.success('¡Inicio de sesión exitoso!');
      seleccionarCategoria(1);
    } catch (error) {
       let errorMessage = 'Error en el registro. Inténtalo de nuevo.';
       if (error && error.email) {
          errorMessage = error.email[0];
       }
      toast.error(errorMessages[errorMessage] || errorMessage);
    }
  }
};
const toggleAuthMode = () => {
  isLogin.value = !isLogin.value;
};

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

const toggleConfirmPasswordVisibility = () => {
  showConfirmPassword.value = !showConfirmPassword.value;
};

// Watcher to clear error state on mode toggle
watch(isLogin, () => {
  store.commit('CLEAR_ERROR');
});

import { googleTokenLogin } from 'vue3-google-login';

const loginWithGoogle = () => {
  googleTokenLogin().then(async (response) => {
    console.log("Google OAuth response:", response);
    try {
      // response.access_token contains the Google OAuth token
      await store.dispatch('socialLogin', {
        provider: 'google',
        accessToken: response.access_token
      });
      toast.success("¡Inicio de sesión exitoso con Google!");
    } catch (error) {
      console.error("Error during Google login:", error);
      toast.error("Error al iniciar sesión con Google. Intenta nuevamente.");
    }
  }).catch((error) => {
    console.error("Google popup error:", error);
    toast.error("Login cancelado o error de Google");
  });
};

const loginWithFacebook = () => {
   toast.info("Facebook Login: Not implemented yet");
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.auth-wrapper {
  font-family: 'Inter', sans-serif;
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem 0.5rem;
  grid-column: 1 / -1; /* Force span across all columns of parent grid */
}

@keyframes borderGlow {
  0% { border-color: rgba(59, 130, 246, 0.3); box-shadow: 0 0 15px rgba(59, 130, 246, 0.1); }
  50% { border-color: rgba(139, 92, 246, 0.5); box-shadow: 0 0 25px rgba(139, 92, 246, 0.25); }
  100% { border-color: rgba(59, 130, 246, 0.3); box-shadow: 0 0 15px rgba(59, 130, 246, 0.1); }
}

.auth-container {
  position: relative;
  background: var(--glass-bg);
  backdrop-filter: var(--backdrop-blur);
  -webkit-backdrop-filter: var(--backdrop-blur);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: var(--colortext);
  text-align: center;
  margin: auto;
  max-width: 800px; /* Increased from 380px for standard layout */
  width: 100%;
  padding: 25px 30px;
  animation: fadeInUp 0.6s ease-out, borderGlow 4s infinite;
  overflow: hidden;
}

.auth-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.15), transparent 60%),
              radial-gradient(circle at bottom left, rgba(236, 72, 153, 0.15), transparent 60%);
  z-index: -1;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

h1 {
  margin-bottom: 25px;
  font-size: 1.8em;
  background: linear-gradient(135deg, #60A5FA, #A78BFA);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  letter-spacing: -0.5px;
  text-transform: uppercase;
}

p {
  font-size: 0.85em;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 20px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.form-group {
  margin-bottom: 10px;
  text-align: left;
}

.form-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.half-width {
  flex: 1;
  margin-bottom: 0;
}

label {
  display: block;
  margin-bottom: 3px;
  font-size: 0.7em;
  font-weight: 500;
  color: var(--colortext);
  opacity: 0.9;
  letter-spacing: 0.3px;
}

/* Inputs are handled in the main block now to ensure precedence */
/* Actually restoring them because the previous main block update failed */
input[type="email"],
input[type="password"],
input[type="text"],
select {
  width: 100%;
  padding: 10px 40px 10px 15px; /* Increased padding-right for icon space */
  border: 2px solid var(--glass-border);
  border-radius: 8px;
  background-color: var(--colorquaternary);
  color: var(--colortext);
  font-size: 0.9em;
  font-weight: 400;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  box-sizing: border-box;
}

/* Hide native password toggle in Edge/IE */
input[type="password"]::-ms-reveal,
input[type="password"]::-ms-clear {
  display: none;
}

input::placeholder,
select option {
  color: var(--colorcomplementary);
}

input:focus,
select:focus {
  outline: none;
  border: 2px solid transparent;
  background: var(--colorbase) padding-box,
              var(--gradient-primary) border-box;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
  transform: translateY(-2px);
}

select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748b' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  padding-right: 40px;
}

select option {
  background-color: var(--colorbase);
  color: var(--colortext);
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: var(--colorsecondary);
  transition: all 0.3s ease;
  font-size: 0.9em;
  z-index: 10;
  display: flex;
  align-items: center;
}

.password-toggle:hover {
  color: var(--colorprimary);
  transform: scale(1.1);
}

.forgot-password {
  display: block;
  text-align: center;
  color: var(--colorprimary);
  text-decoration: none;
  font-size: 0.8em;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-top: 4px;
}

.forgot-password:hover {
  color: var(--colorhover);
  text-decoration: underline;
}

.auth-button {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: var(--gradient-primary);
  color: white;
  cursor: pointer;
  margin-bottom: 12px;
  font-size: 0.85em;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  position: relative;
  overflow: hidden;
}

.auth-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.auth-button:hover::before {
  left: 100%;
}

.auth-button:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
}

.auth-button:active {
  transform: translateY(0) scale(0.98);
}

.social-login {
  margin: 15px 0 15px 0;
}

.social-login p {
  font-size: 0.8em;
  color: var(--colorsecondary);
  margin-bottom: 10px;
  font-weight: 400;
  position: relative;
}

.social-login p::before,
.social-login p::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 35%;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--colorquaternary), transparent);
}

.social-login p::before {
  left: 0;
}

.social-login p::after {
  right: 0;
}

.social-buttons {
  display: flex;
  gap: 10px;
}

.facebook-button,
.google-button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.facebook-button {
  background: linear-gradient(135deg, #4267B2 0%, #365899 100%);
  box-shadow: 0 4px 15px rgba(66, 103, 178, 0.3);
}

.google-button {
  background: linear-gradient(135deg, #DB4437 0%, #C23321 100%);
  box-shadow: 0 4px 15px rgba(219, 68, 55, 0.3);
}

.facebook-button:hover:not(:disabled),
.google-button:hover:not(:disabled) {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

.options-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
  margin-bottom: 0; /* Override default label margin */
}

.checkbox-label input[type="checkbox"] {
    appearance: none;
    -webkit-appearance: none;
    background-color: var(--colorquaternary);
    border: 1px solid rgba(255,255,255,0.3);
    width: 16px;
    height: 16px;
    border-radius: 4px;
    display: grid;
    place-content: center;
    transition: all 0.2s;
    padding: 0;
    margin: 0;
    cursor: pointer;
}

.checkbox-label input[type="checkbox"]:checked {
    background-color: var(--colorprimary);
    border-color: var(--colorprimary);
}

.checkbox-label input[type="checkbox"]:checked::after {
    content: '✓';
    color: white;
    font-size: 10px;
    font-weight: bold;
}

.checkbox-text {
    font-size: 0.85em;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 500;
}

.toggle-link {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.toggle-link a {
  color: white;
  text-decoration: none;
  font-weight: 700;
  border: none;
  padding: 12px 15px; /* Slightly reduced padding */
  border-radius: 12px;
  width: 100%;
  box-sizing: border-box; /* Fixes overflow */
  text-align: center;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #3B82F6, #6366F1); /* Softer Blue-Indigo */
  display: block;
  text-transform: uppercase;
  font-size: 0.95rem;
  letter-spacing: 1px;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4); /* Softer glow */
}

.toggle-link a:hover {
  background: linear-gradient(135deg, #60A5FA, #818CF8);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .auth-container {
    padding: 20px 15px; /* Comfortable but compact */
    margin: 10px; /* Ensure edge spacing */
    max-width: 100%;
  }
  
  h1 {
    font-size: 1.5em; /* Smaller header */
    margin-bottom: 20px;
  }
  
  .auth-button {
    padding: 12px; /* Touch friendly */
  }

  .social-buttons {
    flex-direction: column; /* Stack social buttons if needed, or keep row */
  }
}
</style>
