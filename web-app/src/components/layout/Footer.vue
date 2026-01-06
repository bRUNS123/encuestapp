<template>
	<div class="footer-container">
	  <div class="logo">
		<img :src="logo" alt="logo" class="img-logo">
	  </div>
	  <div class="text">
		ENCUESTAPP  2025 ©
	  </div>
	  <div class="icons">
		<div v-for="item in iconsFooter" :key="item.id" class="icon-container">
		  <a :href="item.enlace" class="menu">
			<i :class="['icono', item.icono]"></i>
		  </a>
		</div>
        <!-- Theme Toggle Moved to Navbar -->
	  </div>
	</div>
  </template>

  <script setup>
	import logo from '@/images/logo.png';
    import { ref, onMounted } from 'vue';

	const iconsFooter = [
	  { id: 2, nombre: 'Instagram', icono: 'fab fa-instagram', enlace: '#' },
	  { id: 3, nombre: 'Tiktok', icono: 'fab fa-tiktok', enlace: '#' },
	  { id: 1, nombre: 'X', icono: 'fas fa-x', enlace: '#' },
	];
  </script>

  <style scoped>
	.footer-container {
	  display: grid;
	  grid-template-areas: "logo text icons";
	  grid-template-columns: 1fr 1fr 1fr; /* Tres columnas de igual tamaño */
	  align-items: center; /* Centrar verticalmente los elementos */
	  background-color: var(--colortertiary);
	  padding: 0 30px; /* Añadir padding de 0 a 30px */
	}

	.logo {
	  grid-area: logo; /* Colocar en el área del logo */
	}

	.text {
	  grid-area: text; /* Colocar en el área del texto */
	  justify-self: center; /* Alinear al centro */
	  color: var(--colortext);
	  font-size: 1.2rem; /* Tamaño del texto */
	  font-weight: bold; /* Texto en negrita */
	}

	.icons {
	  grid-area: icons; /* Colocar en el área de los íconos */
	  justify-self: end; /* Alinear a la derecha */
	  display: flex;
	  gap: 15px; /* Espacio entre elementos */
	}

	.icon-container {
	  transition: transform 0.3s ease; /* Transición suave */
	}

    .icon-container:hover {
        transform: scale(1.2);
    }

	.icono {
	  color: var(--colortext);
	  font-size: 24px; /* Tamaño del ícono */
	}

	.img-logo {
	  max-height: 8vh; /* Establecer una altura máxima para el logo */
	  object-fit: contain; /* Ajustar la imagen dentro del contenedor manteniendo la relación de aspecto */
	}

	@media (max-width: 430px) and (max-height: 932px){
		.img-logo {
			max-height: 6vh; /* Establecer una altura máxima para el logo */
			object-fit: contain; /* Ajustar la imagen dentro del contenedor manteniendo la relación de aspecto */
		  }

		  .text {
			font-size: 1rem; /* Reducir el tamaño del texto */
			text-align: center; /* Centrar el texto */
		  }


		  .icono {
			font-size: 1.2em;

		}
		.footer-container {
			display: grid;
			grid-template-areas: "logo text icons";
			grid-template-columns: 1fr 1fr 1fr; /* Tres columnas de igual tamaño */
			align-items: center; /* Centrar verticalmente los elementos */
			background-color: black;
			padding: 0 20px; /* Añadir padding de 0 a 30px */

		  }
		  .icons {
			padding: 0px; /* Añadir padding de 0 a 20px */
		}



	}


	@media (max-width: 412px) {
		.footer-container {
			display: grid;
			grid-template-areas: "logo text icons";
			grid-template-columns: 1fr 1fr 1fr; /* Tres columnas de igual tamaño */
			align-items: center; /* Centrar verticalmente los elementos */
			background-color: black;
		  }

		  .logo {
			grid-area: logo; /* Colocar en el área del logo */
		  }

		  .text {
			grid-area: text; /* Colocar en el área del texto */
			justify-self: center; /* Alinear al centro */
			color: white;
			font-size: 1rem; /* Tamaño del texto */
			font-weight: bold; /* Texto en negrita */
		  }

		  .icons {
			grid-area: icons; /* Colocar en el área de los íconos */
			display: flex;
			gap: 15px; /* Espacio entre elementos */
			padding: 0px;
		  }

		  .icon-container {
			transition: transform 0.3s ease; /* Transición suave */
		  }

		  .icono {
			color: white;
			font-size: 1.5em; /* Tamaño del ícono */
		  }

		  .img-logo {
			max-height: 6vh; /* Establecer una altura máxima para el logo */
			object-fit: contain; /* Ajustar la imagen dentro del contenedor manteniendo la relación de aspecto */
		  }

		.img-logo {
			max-height: 6vh; /* Establecer una altura máxima para el logo */
			object-fit: contain; /* Ajustar la imagen dentro del contenedor manteniendo la relación de aspecto */
		  }

		  .text {
			font-size: 1rem; /* Reducir el tamaño del texto */
			text-align: center; /* Centrar el texto */
		  }


		  .icono {
			font-size: 1.5em;
		}


	}

	@media (max-width: 344px) and (max-height: 882px) {

		.img-logo {
			max-height: 6vh; /* Establecer una altura máxima para el logo */
			object-fit: contain; /* Ajustar la imagen dentro del contenedor manteniendo la relación de aspecto */
		  }

		  .text {
			font-size: 1rem; /* Reducir el tamaño del texto */
			text-align: center; /* Centrar el texto */
		  }


		  .icono {
			font-size: 1.2em;

		}
		.footer-container {
			display: grid;
			grid-template-areas: "logo text icons";
			grid-template-columns: 1fr 1fr 1fr; /* Tres columnas de igual tamaño */
			align-items: center; /* Centrar verticalmente los elementos */
			background-color: black;
			padding: 0 20px; /* Añadir padding de 0 a 30px */

		  }
		  .icons {
			padding: 0px; /* Añadir padding de 0 a 20px */
		}


		}


/* Compact Footer for All Mobile Devices */
@media (max-width: 768px) {
  .footer-container {
    padding: 18px 15px !important; /* More vertical padding for better height */
  }

  .img-logo {
    max-height: 4.5vh !important;
  }

  .text {
    font-size: 0.7rem !important;
  }

  .icono {
    font-size: 1rem !important;
  }
}

  </style>
