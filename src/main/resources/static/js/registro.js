document.getElementById('registro-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const statusDiv = document.getElementById('status-message');
    statusDiv.classList.add('d-none');
    statusDiv.innerHTML = '';

    // 1. Recolectar datos del formulario
    const payload = {
        nombre: document.getElementById('reg-nombre').value,
        apellido: document.getElementById('reg-apellido').value,
        email: document.getElementById('reg-email').value,
        fechaNacimiento: document.getElementById('reg-nacimiento').value,
        genero: document.getElementById('reg-genero').value,
        password: document.getElementById('reg-password').value
    };

    // Si la fecha está vacía, la convertimos en 'null'.
    if (payload.fechaNacimiento === "") {
        payload.fechaNacimiento = null;
    }

    // Si el género está vacío (opción "Selecciona..."), lo volvemos 'null'.
    if (payload.genero === "") {
        payload.genero = null;
    }
    // -------------------------

    try {
        // 3. Mostrar estado de carga
        Swal.fire({
            title: 'Registrando...',
            text: 'Estamos creando tu cuenta.',
            didOpen: () => { Swal.showLoading() },
            allowOutsideClick: false
        });

        // 4. Enviar Petición POST (Ahora con payload "limpio")
        const response = await axios.post('/api/usuarios', payload);

        // 5. Éxito
        Swal.fire({
            icon: 'success',
            title: '¡Registro Exitoso!',
            text: 'Tu cuenta ha sido creada. Ahora podés iniciar sesión.',
            confirmButtonColor: '#198754'
        }).then(() => {
            window.location.href = 'index.html#login-anchor';
        });

        // MANEJO DE ERRORES EN EL REGISTRO
    } catch (error) {
        Swal.close();

        if (error.response?.status === 400) {
            if (error.response.data?.validationErrors) {
                mostrarErrores(
                    error.response.data.validationErrors
                );
            } else {
                mostrarErrores([
                    'Revisá el formato de los datos ingresados.'
                ]);
            }

        } else if (error.response?.status === 409) {
            const mensaje =
                typeof error.response.data === 'string'
                    ? error.response.data
                    : 'El correo electrónico ya está registrado.';

            mostrarErrores([mensaje]);

        } else if (error.response?.status >= 500) {
            mostrarErrores([
                'Ocurrió un error en el servidor. Intentá nuevamente.'
            ]);

        } else {
            mostrarErrores([
                'No se pudo conectar con el servidor. Intentá nuevamente.'
            ]);
        }

        console.error('Error de registro:', error);
    }
});

/**
 * Muestra una lista de errores de validación en el div de estado.
 * @param {string[]} errors - Lista de mensajes de error
 */
function mostrarErrores(errors) {
    const statusDiv = document.getElementById('status-message');
    let html = '<strong>Por favor, corrige los siguientes errores:</strong><ul>';

    errors.sort();

    errors.forEach(err => {
        html += `<li>${err}</li>`;

    });

    html += '</ul>';
    statusDiv.innerHTML = html;
    statusDiv.classList.remove('d-none');

    statusDiv.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });

}