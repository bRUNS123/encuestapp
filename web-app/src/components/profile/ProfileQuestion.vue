<template>
  <div class="stat-card">
    <div class="stat-icon" :class="iconClass">
      <i :class="icon"></i>
    </div>
    <div class="stat-info">
        <!-- Header / Label -->
        <span class="stat-label">{{ label }}</span>

        <!-- View Mode -->
        <div class="value-row" v-if="!isEditing">
            <span class="stat-value" :class="{ 'not-specified': !modelValue }">{{ displayValue }}</span>
            <button v-if="allowPrivacy" @click.stop="$emit('togglePrivacy')" class="privacy-btn" :title="isPublic ? 'Público (Visible para miembros)' : 'Privado (Solo tú)'">
                <i :class="isPublic ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
            </button>
        </div>

        <!-- Edit Mode -->
        <div v-else class="edit-wrapper">
            <!-- Dropdown -->
            <select v-if="type === 'select'" v-model="internalSelect" class="edit-input select-input" @change="handleSelectChange">
                <option value="" disabled>Seleccionar</option>
                <option v-for="opt in options" :key="opt" :value="opt">{{ opt }}</option>
                <option value="OTRO_CUSTOM">Otro / Escribir...</option>
            </select>
            
            <!-- Date Input -->
            <input v-else-if="type === 'date'" type="date" v-model="internalText" class="edit-input date-input" @input="handleDateInput">

            <!-- Text Input (Direct or via 'Other') -->
            <input 
                v-if="showTextInput" 
                v-model="internalText" 
                type="text" 
                class="edit-input text-input" 
                :placeholder="type === 'select' ? 'Especifique...' : label"
                @input="handleTextInput"
            >
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
    modelValue: [String, Number], // The actual value stored
    isPublic: Boolean,
    label: String,
    icon: String,
    iconClass: { type: String, default: 'default-icon-bg' }, // Class for background color
    isEditing: Boolean,
    type: { type: String, default: 'text' }, // 'text', 'select', 'date'
    options: { type: Array, default: () => [] },
    allowPrivacy: { type: Boolean, default: true }
});

const emit = defineEmits(['update:modelValue', 'togglePrivacy']);

const internalSelect = ref('');
const internalText = ref('');
const showTextInput = ref(false);

const displayValue = computed(() => {
    if (!props.modelValue) return 'No especificado';
    return props.modelValue;
});

// Initialize logic
const init = () => {
    if (props.type === 'select') {
        if (!props.modelValue) {
            internalSelect.value = '';
            internalText.value = '';
            showTextInput.value = false;
        } else if (props.options.includes(props.modelValue)) {
            internalSelect.value = props.modelValue;
            internalText.value = '';
            showTextInput.value = false;
        } else {
            // Custom value
            internalSelect.value = 'OTRO_CUSTOM';
            internalText.value = props.modelValue;
            showTextInput.value = true;
        }
    } else {
        internalText.value = props.modelValue || '';
        showTextInput.value = props.type === 'text'; // Always show for text
    }
};

watch(() => props.isEditing, (newVal) => {
    if (newVal) init(); 
});

watch(() => props.modelValue, () => {
    if (props.isEditing) init();
});

const handleSelectChange = () => {
    if (internalSelect.value === 'OTRO_CUSTOM') {
        showTextInput.value = true;
        internalText.value = ''; // Reset text on switch to Other
        emit('update:modelValue', ''); // Clear value until typed
    } else {
        showTextInput.value = false;
        emit('update:modelValue', internalSelect.value);
    }
};

const handleTextInput = () => {
    emit('update:modelValue', internalText.value);
};

const handleDateInput = () => {
     emit('update:modelValue', internalText.value);
};

// Initial setup
init();

</script>

<style scoped>
/* Reusing/Adapting styles from ProfileView */
.stat-card {
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 15px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  min-height: 80px;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 45px;
  height: 45px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

/* Default colors if no class provided */
.default-icon-bg {
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

/* Custom icon background classes can be defined in parent or here */

.stat-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0; /* Prevent overflow */
}

.stat-label {
  font-size: 0.75rem;
  color: #9CA3AF;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.value-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
}

.stat-value {
    font-size: 1rem;
    color: white;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.stat-value.not-specified {
    color: rgba(255, 255, 255, 0.4);
    font-style: italic;
    font-size: 0.9rem;
}

.privacy-btn {
    background: none;
    border: none;
    color: #6B7280;
    cursor: pointer;
    font-size: 0.9rem;
    padding: 5px;
    margin-left: 8px;
    transition: all 0.2s;
    opacity: 0.7;
}

.privacy-btn:hover {
    color: #60A5FA;
    opacity: 1;
    transform: scale(1.1);
}

/* Edit Mode Styles */
.edit-wrapper {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
}

.edit-input {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
    padding: 8px 12px;
    border-radius: 8px;
    width: 100%;
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.2s;
}

.edit-input:focus {
    border-color: #60A5FA;
    background: rgba(0, 0, 0, 0.3);
}

.select-input {
    cursor: pointer;
}

.select-input option {
    background: #1F2937; /* Dark background for options */
    color: white;
}
</style>
