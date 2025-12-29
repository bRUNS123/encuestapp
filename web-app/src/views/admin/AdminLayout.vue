<template>
  <div class="admin-container">
    <aside class="admin-sidebar">
      <div class="admin-header">
        <h3>Admin Panel</h3>
      </div>
      <nav class="admin-nav">
        <router-link to="/admin" class="nav-item">
          <i class="fas fa-chart-line"></i> Dashboard
        </router-link>
        <router-link to="/admin/users" class="nav-item">
          <i class="fas fa-users"></i> Usuarios
        </router-link>
        <router-link to="/admin/questions" class="nav-item">
          <i class="fas fa-question-circle"></i> Preguntas
        </router-link>
        <div class="nav-divider"></div>
        <router-link to="/" class="nav-item back-home">
          <i class="fas fa-arrow-left"></i> Volver a la App
        </router-link>
      </nav>
    </aside>

    <main class="admin-main">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
// Admin Layout Logic
</script>

<style scoped>
.admin-container {
  display: flex;
  height: 100vh;
  width: 100%;
  background-color: var(--colorbase);
  color: var(--colortext);
}

.admin-sidebar {
  width: 250px;
  background-color: var(--colortertiary);
  border-right: 1px solid var(--colorsecondary);
  display: flex;
  flex-direction: column;
}

.admin-header {
  padding: 20px;
  border-bottom: 1px solid var(--colorsecondary);
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: bold;
}

.admin-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.admin-nav {
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.nav-item {
  padding: 12px 20px;
  color: var(--colortext);
  text-decoration: none;
  font-size: 1rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-item:hover, .nav-item.router-link-exact-active {
  background-color: rgba(255, 255, 255, 0.1);
  color: #a78bfa; /* Primary purple-ish color */
  border-right: 3px solid #a78bfa;
}

.nav-divider {
  height: 1px;
  background-color: var(--colorsecondary);
  margin: 10px 20px;
}

.back-home {
  color: #888;
  font-size: 0.9rem;
}

.admin-main {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 60px;
  }
  .admin-header h3, .nav-item span {
    display: none;
  }
  .nav-item {
    justify-content: center;
    padding: 15px;
  }
}
</style>
