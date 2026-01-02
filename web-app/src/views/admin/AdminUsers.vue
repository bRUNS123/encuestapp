<template>
  <div class="admin-users">
    <div class="header">
      <h1>Gestión de Usuarios</h1>
      <div class="actions">
        <!-- Search bar could go here -->
      </div>
    </div>

    <div v-if="loading" class="loading">Cargando usuarios...</div>

    <div v-else class="table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nickname</th>
            <th>Email</th>
            <th>Año Nac.</th>
            <th>Estado</th>
            <th>Staff</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>#{{ user.id }}</td>
            <td class="nickname">
                <img v-if="user.photo_url" :src="user.photo_url" class="avatar-mini" />
                {{ user.nickname }}
            </td>
            <td>{{ user.email || 'Oculto (Admin debe ver)' }}</td>
            <td>{{ user.birth_year }}</td>
            <td>
              <span :class="['badge', user.is_active ? 'active' : 'banned']">
                {{ user.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
             <td>
              <span v-if="user.is_staff" class="badge staff">Staff</span>
              <span v-else>-</span>
            </td>
            <td class="actions-cell">
              <button 
                @click="toggleActive(user)" 
                :class="['btn-action', user.is_active ? 'btn-ban' : 'btn-activate']"
                :title="user.is_active ? 'Desactivar Usuario' : 'Activar Usuario'"
              >
                <i :class="['fas', user.is_active ? 'fa-ban' : 'fa-check']"></i>
              </button>
              
              <button 
                @click="deleteUser(user)" 
                class="btn-action btn-delete"
                title="Eliminar permanentemente"
                v-if="!user.is_staff" 
              >
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/store/axiosInstance';
import Swal from 'sweetalert2';

const users = ref([]);
const loading = ref(true);

const fetchUsers = async () => {
  try {
    const response = await axios.get('profiles/');
    // If pagination is used, check response.data.results
    if (response.data.results) {
        users.value = response.data.results;
    } else {
        users.value = response.data;
    }
  } catch (error) {
    console.error("Error fetching users:", error);
    Swal.fire('Error', 'No se pudieron cargar los usuarios', 'error');
  } finally {
    loading.value = false;
  }
};

const toggleActive = async (user) => {
    try {
        const response = await axios.post(`profiles/${user.id}/toggle-active/`);
        user.is_active = response.data.is_active;
        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: 'success',
            title: response.data.message,
            showConfirmButton: false,
            timer: 2000
        });
    } catch (error) {
        Swal.fire('Error', 'No se pudo cambiar el estado', 'error');
    }
};

const deleteUser = async (user) => {
    const result = await Swal.fire({
        title: '¿Estás seguro?',
        text: `Vas a eliminar a ${user.nickname}. Esta acción no se puede deshacer.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
        try {
            await axios.delete(`profiles/${user.id}/`);
            users.value = users.value.filter(u => u.id !== user.id);
            Swal.fire('Eliminado', 'El usuario ha sido eliminado', 'success');
        } catch (error) {
            console.error(error);
            Swal.fire('Error', 'No se pudo eliminar el usuario', 'error');
        }
    }
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-container {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th, .users-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.users-table th {
  background-color: rgba(0,0,0,0.2);
  color: #aaa;
  font-weight: 600;
}

.nickname {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: bold;
}

.avatar-mini {
    width: 24px;
    height: 24px;
    border-radius: 50%;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.badge.active { background-color: rgba(16, 185, 129, 0.2); color: #34d399; }
.badge.banned { background-color: rgba(239, 68, 68, 0.2); color: #f87171; }
.badge.staff { background-color: rgba(139, 92, 246, 0.2); color: #a78bfa; border: 1px solid #a78bfa; }

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

.btn-ban { background-color: #ef4444; }
.btn-activate { background-color: #10b981; }
.btn-delete { background-color: #333; border: 1px solid #555; }
.btn-delete:hover { background-color: #b91c1c; border-color: #b91c1c; }

</style>
