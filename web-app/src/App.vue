<script setup>
import { RouterView, useRoute } from 'vue-router';
import { computed } from 'vue';

import LeftBar from './components/layout/LeftBar.vue';
import NavBar from './components/layout/Navbar.vue';
import RightBar from './components/layout/RightBar.vue';
import Footer from './components/layout/Footer.vue';

const route = useRoute();

const fullWidthContent = []; /* Sidebars enabled everywhere per user request */
const isLoginRoute = computed(() => fullWidthContent.includes(route.path));

</script>


<template>
  <div :class="['app', { 'login-layout': isLoginRoute }]">
    <header class="navbar">
      <NavBar/>
    </header>

    <div class="leftbar" v-if="!isLoginRoute">
      <LeftBar/>
    </div>

    <div class="rightbar" v-if="!isLoginRoute">

      <RightBar/>
    </div>

    <div :class="['content', { 'content-full-width': isLoginRoute }]">
      <router-view v-slot="{ Component }">
          <component :is="Component" :key="route.fullPath" />
      </router-view>
    </div>

    <div class="footer">
      <Footer/>
    </div>
  </div>
</template>
<script>
export default {
  name: 'App',
}
</script>

<style lang="css">
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

.app {
  display: grid;
  grid-template-areas:
    "navbar navbar navbar"
    "leftbar content rightbar"
    "footer footer  footer";
  grid-template-rows: auto 1fr auto; /* Use auto/1fr/auto instead of fixed % */
  grid-template-columns: 250px 1fr 450px; /* RightBar increased to 450px per user request */
  height: 100vh;
  overflow: hidden;
}

.app.login-layout {
  grid-template-areas:
    "navbar"
    "content"
    "footer";
  grid-template-columns: 1fr;
  grid-template-rows: auto 1fr auto;
}



/* Mobile Responsive */
@media (max-width: 900px) {
  .app {
    grid-template-columns: 200px 1fr 0px; /* Hide rightbar first? or stack? */
    /* Let's keep it simple for now, maybe hide rightbar on tablet? */
  }
  .rightbar { display: none; }
}

@media (max-width: 1024px) {
  .app {
    display: grid;
    grid-template-areas:
      "navbar navbar"
      "leftbar content"
      "footer footer";
    grid-template-columns: 50px 1fr; /* Ultra-compact Icon strip */
    grid-template-rows: auto 1fr auto;
    height: 100vh;
    width: 100vw;
    overflow-x: hidden;
  }
  
  .navbar {
    grid-area: navbar;
    width: 100%;
    z-index: 1000;
  }

  .content {
    grid-area: content;
    width: 100%;
    overflow-y: auto;
    padding: 10px;
  }

  .footer {
    grid-area: footer;
    width: 100%;
  }

  .leftbar {
    grid-area: leftbar;
    display: block !important; /* Show it */
    width: 100% !important;
    height: 100% !important;
    position: relative;
    opacity: 1;
    pointer-events: auto;
    border-right: 1px solid rgba(255,255,255,0.1);
    z-index: 90;
  }

  .rightbar {
    display: none !important; /* Still hide right bar */
    width: 0;
  }
}

.content {
  grid-area: content;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 20px;
  background-color: var(--colorbase);
  overflow: auto;
}

.content-full-width {
  grid-area: content;
  grid-template-columns: 1fr!important;
  overflow-y: auto!important;
  display: block;
}


.navbar {
  grid-area: navbar;
  background-color: var(--colortertiary);


}

.leftbar {
  grid-area: leftbar;
  background-color: var(--colorbase);
  overflow-y: auto;
  height: 100%; /* Ocupar toda la altura disponible */
  border-right: 1px solid var(--colorsecondary)

  ;
}

.rightbar {
  grid-area: rightbar;
  display: grid;
  grid-template-columns: 1fr;
  overflow-y: auto;
  background-color: var(--colorbase);

}

.footer {
  grid-area: footer;
  display: grid;
}

/* Page Transition Styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>