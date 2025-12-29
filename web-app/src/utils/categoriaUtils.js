// src/utils/categoriaUtils.js
import { reactive, toRefs } from "vue";

const state = reactive({
  categorias: [
    {
      id: 13,
      nombre: "PERSONAL",
      icono: "fas fa-user-circle", // Updated icon to match profile feel
      enlace: "/personal",
      isActive: false,
      auth: true,
    },
    {
      id: 1,
      nombre: "MÁS VOTADAS",
      icono: "fas fa-star",
      enlace: "/",
      isActive: false,
    },
    {
      id: 2,
      nombre: "MÁS NUEVO",
      icono: "fas fa-clock",
      enlace: "/newest",
      isActive: false,
    },
    {
      id: 12,
      nombre: "MEJORES",
      icono: "fas fa-trophy",
      enlace: "/best-rated",
      isActive: false,
    },
    {
      id: 3,
      nombre: "POLÍTICA",
      icono: "fas fa-balance-scale",
      enlace: "/politica",
      isActive: false,
    },
    {
      id: 4,
      nombre: "SOCIEDAD",
      icono: "fas fa-users",
      enlace: "/sociedad",
      isActive: false,
    },
    {
      id: 5,
      nombre: "DEPORTE",
      icono: "fas fa-futbol",
      enlace: "/deporte",
      isActive: false,
    },
    {
      id: 6,
      nombre: "TECNOLOGÍA",
      icono: "fas fa-laptop",
      enlace: "/tecnologia",
      isActive: false,
    },
    {
      id: 7,
      nombre: "ENTRETENIMIENTO",
      icono: "fas fa-film",
      enlace: "/entretenimiento",
      isActive: false,
    },
    {
      id: 8,
      nombre: "INTERNACIONAL",
      icono: "fas fa-globe",
      enlace: "/internacional",
      isActive: false,
    },
    {
      id: 9,
      nombre: "EDUCACIÓN",
      icono: "fas fa-graduation-cap",
      enlace: "/educacion",
      isActive: false,
    },
    {
      id: 10,
      nombre: "SALUD",
      icono: "fas fa-medkit",
      enlace: "/salud",
      isActive: false,
    },
    {
      id: 11,
      nombre: "CREA ENCUESTA",
      icono: "fas fa-brain",
      enlace: "/crear-encuesta",
      isActive: false,
      auth: true,
    },
  ],
});

const seleccionarCategoria = (id) => {
  if (id === null) {
    state.categorias.forEach((categoria) => (categoria.isActive = false));
  } else {
    state.categorias.forEach(
      (categoria) => (categoria.isActive = categoria.id === id)
    );
  }
};

const { categorias } = toRefs(state);

export { categorias, seleccionarCategoria };
