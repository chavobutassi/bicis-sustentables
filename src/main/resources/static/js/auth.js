/**
 * Función Universal de Logout.
 * Cierra la sesión del backend (POST), limpia el frontend (sessionStorage),
 * muestra un "Toast" de éxito y redirige al index.
 */
async function logout() {

    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 1500,
        timerProgressBar: true
    });

    try {
        /*
         * Cerrar la sesión real del servidor.
         * withCredentials asegura el envío de JSESSIONID.
         */
        await axios.post(
            '/api/logout',
            null,
            {
                withCredentials: true
            }
        );

        /*
         * Verificar que la sesión realmente haya dejado
         * de ser válida antes de informar éxito.
         */
        try {
            await axios.get(
                '/api/usuarios/actual',
                {
                    withCredentials: true
                }
            );

            /*
             * Si esta petición devuelve 200, la sesión
             * continúa activa y el logout no funcionó.
             */
            throw new Error(
                'La sesión continúa activa después del logout.'
            );

        } catch (verificacionError) {

            const estado =
                verificacionError.response?.status;

            /*
             * 401 o 403 confirman que ya no existe
             * una sesión autenticada válida.
             */
            if (estado !== 401 && estado !== 403) {
                throw verificacionError;
            }
        }

        /*
         * Limpiar toda la información local solamente
         * después de confirmar el cierre del backend.
         */
        sessionStorage.clear();

        await Toast.fire({
            icon: 'success',
            title: '¡Sesión cerrada con éxito!'
        });

        /*
         * replace impide volver a la página privada
         * mediante el botón Atrás del navegador.
         */
        window.location.replace(
            'index.html'
        );

    } catch (error) {

        console.error(
            'No se pudo cerrar la sesión correctamente:',
            error
        );

        await Swal.fire({
            icon: 'error',
            title: 'No se pudo cerrar la sesión',
            text: 'La sesión continúa activa. Intentá nuevamente.',
            confirmButtonColor: '#198754'
        });
    }
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