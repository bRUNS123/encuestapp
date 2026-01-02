<template>
  <div class="admin-questions">
    <div class="header">
      <h1>Gestión de Preguntas</h1>
    </div>

    <div v-if="loading" class="loading">Cargando preguntas...</div>

    <div v-else class="table-container">
      <table class="q-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Categoría</th>
            <th>Creador</th>
            <th>Votos</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="q in questions" :key="q.id">
            <td>#{{ q.id }}</td>
            <td class="title-cell" :title="q.title">{{ truncate(q.title) }}</td>
            <td>
                <span class="badge-cat">{{ q.category || 'Sin Categoría' }}</span>
            </td>
             <td>
              <span v-if="q.owner">{{ q.owner_nickname || 'Usuario #' + q.owner }}</span>
              <span v-else class="anon">Anónimo</span>
            </td>
            <td>{{ q.cantidad_votos }}</td>
            <td>{{ formatDate(q.creation_date) }}</td>
            <td class="actions-cell">
              <button 
                @click="openQuestion(q)" 
                class="btn-action btn-view"
                title="Ver encuesta"
              >
                <i class="fas fa-external-link-alt"></i>
              </button>
              
               <button 
                @click="openEditModal(q)" 
                class="btn-action btn-edit"
                title="Editar encuesta"
              >
                <i class="fas fa-edit"></i>
              </button>
              
              <button 
                @click="deleteQuestion(q)" 
                class="btn-action btn-delete"
                title="Eliminar pregunta"
              >
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Pagination Controls (Simple) -->
      <div v-if="nextUrl || prevUrl" class="pagination">
        <button :disabled="!prevUrl" @click="fetchQuestions(prevUrl)" class="btn-page">Anterior</button>
        <button :disabled="!nextUrl" @click="fetchQuestions(nextUrl)" class="btn-page">Siguiente</button>
      </div>


    </div>
    
    <!-- Modal para ver encuesta -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
            <button class="close-btn" @click="closeModal">&times;</button>
            <div class="modal-body">
                <Pregunta 
                    v-if="selectedQuestion"
                    :key="selectedQuestion.id"
                    :questionId="selectedQuestion.id"
                    :pregunta="selectedQuestion.title"
                    :questionType="selectedQuestion.question_type || 'binary'"
                    :allOptions="selectedQuestion.options || []"
                    :respuesta1="selectedQuestion.options[0] || { title: 'Sin respuesta', votes: 0 }"
                    :respuesta2="selectedQuestion.options[1] || { title: 'Sin respuesta', votes: 0 }"
                    :respuesta1Id="selectedQuestion.options[0] ? selectedQuestion.options[0].id : null"
                    :respuesta2Id="selectedQuestion.options[1] ? selectedQuestion.options[1].id : null"
                    :categoria="selectedQuestion.category"
                    :fecha="selectedQuestion.creation_date"
                    :expirationDate="selectedQuestion.expiration_date"
                    :votos="selectedQuestion.cantidad_votos"
                    :profileId="0" 
                    :isPublic="true"
                />
            </div>
        </div>
    </div>

    <!-- Modal para EDITAR encuesta -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-content edit-modal">
            <button class="close-btn" @click="closeEditModal">&times;</button>
            <div class="modal-header-edit">
                <h2>Editar Pregunta</h2>
            </div>
            <div class="modal-body-form" v-if="editingQuestion">
                <div class="form-group">
                    <label>Título:</label>
                    <input type="text" v-model="editingQuestion.title" class="admin-input" />
                </div>
                
                <div class="form-group">
                     <label>Categoría:</label>
                     <select v-model="editingQuestion.category" class="admin-select">
                        <option value="">Seleccionar Categoría</option>
                        <option v-for="cat in categories" :key="cat.id" :value="cat.name">
                            {{ cat.name }}
                        </option>
                     </select>
                </div>

                <!-- Options Editing -->
                <div class="form-group" v-if="editingQuestion.options && editingQuestion.options.length > 0">
                    <label>Opciones de Respuesta:</label>
                    <div v-for="(opt, index) in editingQuestion.options" :key="index" class="option-row">
                        <input 
                            type="text" 
                            v-model="opt.title" 
                            class="admin-input option-input"
                            :placeholder="'Opción ' + (index + 1)"
                        />
                    </div>
                </div>

                <div class="form-actions">
                    <button @click="closeEditModal" class="btn-cancel">Cancelar</button>
                    <button @click="saveQuestionChanges" class="btn-save">Guardar Cambios</button>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/store/axiosInstance';
import Swal from 'sweetalert2';
import { useRouter } from 'vue-router';
import Pregunta from '/src/components/preguntas/Pregunta.vue';

const router = useRouter();
const questions = ref([]);
const categories = ref([]); // Store categories for dropdown
const loading = ref(true);
const nextUrl = ref(null);
const prevUrl = ref(null);

// Modal state
const showModal = ref(false);
const selectedQuestion = ref(null);

// Edit Modal state
const showEditModal = ref(false);
const editingQuestion = ref(null);

const fetchQuestions = async (url = 'questions/') => {
  loading.value = true;
  try {
    const response = await axios.get(url);
    if (response.data.results) {
        questions.value = response.data.results;
        nextUrl.value = response.data.next;
        prevUrl.value = response.data.previous;
    } else {
        questions.value = response.data;
        nextUrl.value = null;
        prevUrl.value = null;
    }
  } catch (error) {
    console.error("Error fetching questions:", error);
    Swal.fire('Error', 'No se pudieron cargar las preguntas', 'error');
  } finally {
    loading.value = false;
  }
};

const fetchCategories = async () => {
    try {
        const response = await axios.get('categories/');
        if (response.data.results) {
             categories.value = response.data.results;
        } else {
             categories.value = response.data;
        }
    } catch (error) {
        console.error("Error fetching categories:", error);
    }
};

const deleteQuestion = async (q) => {
    const result = await Swal.fire({
        title: '¿Eliminar encuesta?',
        text: `"${q.title}" será eliminada permanentemente con todos sus votos.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
        try {
            await axios.delete(`questions/${q.id}/`);
            questions.value = questions.value.filter(item => item.id !== q.id);
            Swal.fire('Eliminada', 'La encuesta ha sido eliminada', 'success');
        } catch (error) {
            console.error(error);
            Swal.fire('Error', 'No se pudo eliminar la encuesta', 'error');
        }
    }
};

const openQuestion = (q) => {
    selectedQuestion.value = q;
    showModal.value = true;
};

const closeModal = () => {
    showModal.value = false;
    selectedQuestion.value = null;
};

// --- Edit Logic ---

const openEditModal = (q) => {
    // Clone to avoid reactive updates before saving
    // Deep clone options array to avoid binding issues
    const optionsClone = q.options ? q.options.map(o => ({...o})) : [];
    
    editingQuestion.value = { 
        ...q,
        // Using 'category' field directly as it comes from serializer (name string)
        category: q.category, 
        options: optionsClone
    };
    showEditModal.value = true;
    if (categories.value.length === 0) {
        fetchCategories();
    }
};

const closeEditModal = () => {
    showEditModal.value = false;
    editingQuestion.value = null;
};

const saveQuestionChanges = async () => {
    if (!editingQuestion.value || !editingQuestion.value.title) {
        Swal.fire('Error', 'El título es obligatorio', 'error');
        return;
    }

    try {
        const payload = {
            title: editingQuestion.value.title,
            category: editingQuestion.value.category,
            options: editingQuestion.value.options // Send updated options
        };
        
        const response = await axios.patch(`questions/${editingQuestion.value.id}/`, payload);
        const updatedQ = response.data;
        
        // Update local list
        const index = questions.value.findIndex(q => q.id === editingQuestion.value.id);
        if (index !== -1) {
            // Update all fields from response to ensure consistency
            questions.value[index] = updatedQ;
        }

        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: 'success',
            title: 'Pregunta actualizada',
            showConfirmButton: false,
            timer: 2000
        });
        closeEditModal();

    } catch (error) {
        console.error(error);
        Swal.fire('Error', 'No se pudieron guardar los cambios', 'error');
    }
};


const truncate = (str) => {
    if (!str) return '';
    return str.length > 50 ? str.substring(0, 50) + '...' : str;
};

const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
};

onMounted(() => {
  fetchQuestions();
});
</script>

<style scoped>
.header {
  margin-bottom: 20px;
  border-bottom: 2px solid var(--colortertiary);
  padding-bottom: 10px;
}

.header h1 {
    color: white;
    font-size: 1.8rem;
    margin: 0;
}

.table-container {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow-x: auto;
  padding-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.q-table {
  width: 100%;
  border-collapse: collapse;
}

.q-table th, .q-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.q-table th {
  background-color: rgba(0,0,0,0.2);
  color: #aaa;
  font-weight: 600;
}

.title-cell {
    font-weight: bold;
    max-width: 300px;
}

.badge-cat {
    padding: 2px 8px;
    background-color: rgba(59, 130, 246, 0.2);
    color: #60a5fa;
    border-radius: 4px;
    font-size: 0.8rem;
}

.anon { opacity: 0.5; font-style: italic; }

.actions-cell {
    display: flex;
    gap: 10px;
}

.btn-action {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    color: white;
}

.btn-view { background-color: #3b82f6; }
.btn-delete { background-color: #ef4444; }

.pagination {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 20px;
}

.btn-page {
    padding: 8px 16px;
    background: var(--colortertiary);
    border: 1px solid var(--border-color);
    color: white;
    cursor: pointer;
    border-radius: 6px;
}

.btn-page:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: var(--colorsecondary);
    padding: 30px;
    border-radius: 12px;
    width: 90%;
    max-width: 600px;
    position: relative;
    max-height: 90vh;
    overflow-y: auto;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.close-btn {
    position: absolute;
    top: 10px;
    right: 15px;
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    z-index: 10;
}

.modal-body {
    margin-top: 10px;
}

/* Edit Modal Styles */
.modal-overlay {
    background: rgba(0, 0, 0, 0.85); /* Darker overlay */
    backdrop-filter: blur(5px);
}

.edit-modal {
    background: #111827; /* Solid dark background or very dark grey */
    background: linear-gradient(135deg, #1f2937, #111827); /* Nice gradient */
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header-edit h2 {
    margin-top: 0;
    color: white;
    font-size: 1.5rem;
    margin-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding-bottom: 15px;
}

.form-group {
    margin-bottom: 25px;
}

.form-group label {
    display: block;
    margin-bottom: 10px;
    color: #9ca3af; /* Light grey text */
    font-weight: 500;
    font-size: 0.95rem;
}

.admin-input, .admin-select {
    width: 100%;
    padding: 12px 15px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    font-size: 1rem;
    box-sizing: border-box;
    transition: all 0.3s ease;
}

.admin-input:focus, .admin-select:focus {
    outline: none;
    border-color: #3b82f6; /* Blue focus */
    background: rgba(0, 0, 0, 0.5);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.admin-select option {
    background: #1f2937;
    color: white;
    padding: 10px;
}

.option-row {
    margin-bottom: 12px;
}

.option-input {
    border-left: 3px solid #f59e0b; /* Amber accent */
    background: rgba(245, 158, 11, 0.05); /* Very subtle amber tint */
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.05);
}
.btn-save, .btn-cancel {
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-weight: bold;
    font-size: 1rem;
}

.btn-save {
    background: var(--colorprimary);
    color: white; /* Contrast? Primary might be yellow/gold */
    /* Check var --colorprimary definition, assuming it might be bright. 
       If it is yellow (#FBBF24), use black text. If blue/purple, white. 
       Let's stick to white or adjust if needed. */
     color: #111; /* Assuming primary is bright yellow/gold from context */
}

.btn-cancel {
    background: transparent;
    color: #aaa;
    border: 1px solid #555;
}

.btn-edit { background-color: #f59e0b; } /* Amber/Orange for edit */
</style>
