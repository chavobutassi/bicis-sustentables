/**
 * Función Universal de Logout.
 * Cierra la sesión del backend (POST), limpia el frontend (sessionStorage),
 * muestra un "Toast" de éxito y redirige al index.
 */
async function logout() {
    
    // 1. Definir el "Toast"
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 1500, // Dura 1.5 segundos
        timerProgressBar: true
    });

    try {
        // 2. Llama al backend (POST)
        await axios.post('/api/logout'); 
    } catch (error) {
        console.error("La sesión del backend ya había expirado o falló el logout:", error);
    }

    // 3. Limpiar la sesión del frontend (SIEMPRE)
    sessionStorage.removeItem("usuarioLogueado");
    sessionStorage.removeItem("usuarioRol");
    sessionStorage.removeItem('usuarioNombre');

    // 4. Mostrar la notificación de éxito
    Toast.fire({
        icon: 'success',
        title: '¡Sesión cerrada con éxito!'
    });

    // 5. Esperar 1.5s y redirigir al index
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1500);
}

// --- FUNCIÓN PARA CARGAR EL NOMBRE DEL USUARIO ---
async function cargarNombreUsuario() {
    const elementoNombre =
        document.getElementById('navbar-username');

    if (!elementoNombre) {
        return;
    }


    // Mostrar inmediatamente el nombre guardado.
    const nombreGuardado =
        sessionStorage.getItem('usuarioNombre');

    if (nombreGuardado) {
        elementoNombre.textContent = nombreGuardado;
    }

    try {
        /*
         * Consultar igualmente el backend para validar la sesión
         * y actualizar el nombre si fue modificado.
         */
        const response =
            await axios.get('/api/usuarios/actual');

        const nombreActual = response.data.nombre;

        elementoNombre.textContent = nombreActual;

        sessionStorage.setItem(
            'usuarioNombre',
            nombreActual
        );

    } catch (error) {
        console.error(
            'Error cargando el nombre del usuario',
            error
        );

        if (error.response
            && (error.response.status === 401
                || error.response.status === 403)) {

            sessionStorage.removeItem('usuarioNombre');

            window.location.href =
                'index.html#login-anchor';
        }
    }
}