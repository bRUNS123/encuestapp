# 🚀 Guía de Deployment - DecideLibre

Esta guía te llevará paso a paso para subir tu aplicación DecideLibre a la web **totalmente GRATIS**.

## 📋 Tabla de Contenidos

1. [Preparación](#preparación)
2. [Deploy del Backend (Render)](#deploy-del-backend-render)
3. [Deploy del Frontend (Vercel)](#deploy-del-frontend-vercel)
4. [Configurar Google OAuth](#configurar-google-oauth)
5. [Verificación Final](#verificación-final)
6. [Troubleshooting](#troubleshooting)

---

## Preparación

### 1. Subir el Código a GitHub

Si aún no tienes tu código en GitHub:

```bash
# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Preparar para deployment en producción"

# Crear repositorio en GitHub y conectarlo
git remote add origin https://github.com/TU_USUARIO/decidelibre.git
git branch -M main
git push -u origin main
```

### 2. Generar una SECRET_KEY nueva

Por seguridad, genera una nueva SECRET_KEY para producción:

**Opción 1: Python**
```bash
cd backend
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Opción 2: Online**
Visita: https://djecrety.ir/

**Guarda esta clave**, la necesitarás más adelante.

---

## Deploy del Backend (Render)

### 1. Crear Cuenta en Render

1. Ve a [render.com](https://render.com)
2. Crea una cuenta (puedes usar GitHub para login rápido)

### 2. Crear Base de Datos PostgreSQL

1. En el dashboard de Render, haz clic en **"New +"** → **"PostgreSQL"**
2. Configuración:
   - **Name**: `decidelibre-db`
   - **Database**: `decidelibre`
   - **User**: (se genera automáticamente)
   - **Region**: `Oregon (US West)` (gratis)
   - **Plan**: **Free** ✅
3. Haz clic en **"Create Database"**
4. **Espera** 2-3 minutos a que se cree
5. Una vez creada, copia la **"Internal Database URL"** (la necesitarás en el siguiente paso)

### 3. Crear Web Service para Django

1. En Render, haz clic en **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub
3. Configuración:
   - **Name**: `decidelibre-backend`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn core.wsgi:application`
   - **Plan**: **Free** ✅

4. **Variables de Entorno** (haz clic en "Add Environment Variable"):

   ```
   SECRET_KEY=<la-clave-que-generaste-antes>
   DEBUG=False
   ALLOWED_HOSTS=decidelibre-backend.onrender.com
   DATABASE_URL=<internal-database-url-de-render>
   RENDER=True
   FRONTEND_URL=https://decidelibre.vercel.app
   CORS_ALLOWED_ORIGINS=https://decidelibre.vercel.app,http://localhost:5173
   GOOGLE_CLIENT_ID=419930149880-325o4917akvnt56j11f87aklik25grje.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=<tu-google-secret>
   EMAIL_HOST_USER=encuestappcl@gmail.com
   EMAIL_HOST_PASSWORD=<tu-contraseña-de-aplicación>
   ```

   > **Nota**: Reemplaza:
   > - `decidelibre-backend` con el nombre que elegiste
   > - `decidelibre.vercel.app` con tu dominio de Vercel (lo obtendrás después)
   > - Las credenciales de Google y Email con las tuyas

5. Haz clic en **"Create Web Service"**

### 4. Esperar el Deploy

- El primer deploy toma 5-10 minutos
- Verás los logs en tiempo real
- Cuando aparezca "Your service is live 🎉", ¡está listo!

### 5. Verificar el Backend

Visita: `https://decidelibre-backend.onrender.com/api/`

Deberías ver un JSON o una lista de endpoints disponibles.

---

## Deploy del Frontend (Vercel)

### 1. Crear Cuenta en Vercel

1. Ve a [vercel.com](https://vercel.com)
2. Regístrate con GitHub (recomendado)

### 2. Importar Proyecto

1. Haz clic en **"Add New..." → "Project"**
2. **Import** tu repositorio de GitHub `decidelibre`
3. Configuración:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `web-app` ✅ (muy importante)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3. Variables de Entorno

Antes de hacer deploy, agrega la variable de entorno:

- **Key**: `VITE_API_URL`
- **Value**: `https://decidelibre-backend.onrender.com`

  (Reemplaza con la URL real de tu backend en Render)

### 4. Deploy

1. Haz clic en **"Deploy"**
2. Espera 2-3 minutos
3. ¡Listo! Vercel te dará una URL como: `https://decidelibre.vercel.app`

### 5. Actualizar Backend con la URL del Frontend

Ahora que tienes la URL de Vercel, **vuelve a Render** y actualiza las variables:

1. Ve a tu Web Service en Render
2. En la pestaña "Environment", actualiza:
   ```
   FRONTEND_URL=https://decidelibre.vercel.app
   CORS_ALLOWED_ORIGINS=https://decidelibre.vercel.app,http://localhost:5173
   ```
3. Guarda y espera a que Render redeploy automáticamente

---

## Configurar Google OAuth

Para que el login con Google funcione en producción:

### 1. Google Cloud Console

1. Ve a [console.cloud.google.com](https://console.cloud.google.com/)
2. Selecciona tu proyecto existente (el que ya tienes configurado)
3. Ve a **"APIs & Services" → "Credentials"**
4. Busca tu OAuth 2.0 Client ID existente
5. Haz clic para editarlo

### 2. Agregar URLs Autorizadas

**Authorized JavaScript origins:**
- Agrega: `https://decidelibre.vercel.app`
- Agrega: `https://decidelibre-backend.onrender.com`

**Authorized redirect URIs:**
- Agrega: `https://decidelibre-backend.onrender.com/auth/google/callback/`
- Agrega: `https://decidelibre.vercel.app`

### 3. Guardar

Haz clic en **"Save"** y espera unos segundos a que se propague.

---

## Verificación Final

### Checklist de Funcionalidad

Visita tu aplicación en: `https://decidelibre.vercel.app`

- [ ] ✅ La página carga sin errores
- [ ] ✅ Puedo hacer clic en "Iniciar Sesión con Google"
- [ ] ✅ El login con Google funciona correctamente
- [ ] ✅ Puedo ver las preguntas
- [ ] ✅ Puedo votar en una pregunta
- [ ] ✅ Al recargar la página, mi voto sigue ahí
- [ ] ✅ Puedo ver mi perfil
- [ ] ✅ No hay errores en la consola del navegador (F12)

### Comandos Útiles

**Ver logs del backend:**
- Ve a Render → Tu Web Service → Pestaña "Logs"

**Redeployar manualmente:**
- Render: Botón "Manual Deploy" → "Deploy latest commit"
- Vercel: Pestaña "Deployments" → Botón con tres puntos → "Redeploy"

---

## Troubleshooting

### Error: "CORS policy" en consola

**Problema**: El frontend no puede comunicarse con el backend.

**Solución**:
1. Verifica que `CORS_ALLOWED_ORIGINS` en Render incluya tu URL de Vercel
2. Asegúrate de que `VITE_API_URL` en Vercel esté correctamente configurada
3. Redeploy ambos servicios

### Error: "Server Error 500" en el backend

**Problema**: Error interno del servidor.

**Solución**:
1. Ve a los logs en Render
2. Busca el traceback del error
3. Usualmente es una variable de entorno faltante o mal configurada

### Login con Google no funciona

**Problema**: Redirect error o "redirect_uri_mismatch"

**Solución**:
1. Verifica que las URLs en Google Cloud Console coincidan EXACTAMENTE
2. No olvides el `/` al final en las redirect URIs
3. Espera 1-2 minutos después de guardar cambios en Google

### Base de datos vacía

**Problema**: No hay preguntas después del deploy.

**Solución**:
En Render, abre la **Shell**:
```bash
python manage.py shell
```
Y ejecuta tu script de carga de datos, o importa fixtures.

### El servicio free de Render "se duerme"

**Comportamiento normal**: Los servicios gratuitos de Render se duermen después de 15 minutos de inactividad.

**Resultado**: La primera petición puede tardar 30-60 segundos en "despertar".

**Soluciones**:
- **Opción 1**: Acepta esta limitación (normal para free tier)
- **Opción 2**: Usa un servicio de "ping" como [cron-job.org](https://cron-job.org) para hacer ping cada 10 minutos
- **Opción 3**: Upgrade a plan pagado ($7/mes)

---

## 🎉 ¡Felicidades!

Tu aplicación DecideLibre ahora está en la web y accesible desde cualquier lugar.

**URLs importantes:**
- Frontend: `https://decidelibre.vercel.app`
- Backend API: `https://decidelibre-backend.onrender.com/api/`

### Próximos Pasos

- **Dominio personalizado**: Tanto Vercel como Render permiten dominios custom
- **Monitoreo**: Configura alertas en Render y Vercel
- **Analytics**: Agrega Google Analytics o similar
- **CI/CD**: Los deploys son automáticos cuando hagas `git push`

---

## Soporte

Si tienes problemas, puedes:
1. Revisar los logs en Render y Vercel
2. Verificar la consola del navegador (F12)
3. Consultar documentación oficial:
   - [Render Docs](https://render.com/docs)
   - [Vercel Docs](https://vercel.com/docs)
