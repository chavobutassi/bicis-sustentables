document.addEventListener("DOMContentLoaded", function() {
    checkSession();
});

// Función para verificar la sesión al cargar la página
function checkSession() {
    const isLogueado = sessionStorage.getItem("usuarioLogueado") === "true";
    const userRol = sessionStorage.getItem("usuarioRol"); // Leer el rol guardado

    if (isLogueado) {
        // Ocultar botones de Visitante
        document.querySelectorAll('.nav-visitante, .btn-visitante').forEach(el => el.classList.add('d-none'));

        // Mostrar botones de Usuario Logueado (Mi Cuenta, Salir)
        document.querySelectorAll('.nav-usuario, .btn-usuario').forEach(el => el.classList.remove('d-none'));

        // --- LÓGICA DE ADMIN ---
        if (userRol === "ADMIN") {
            // Si es Admin, mostrar también el botón de Panel Admin
            document.querySelectorAll('.nav-admin').forEach(el => el.classList.remove('d-none'));
        }
        // -----------------------

        // Reemplazar el formulario de login en el footer
        const loginFormContainer = document.getElementById('login-form');
        if(loginFormContainer) {
            loginFormContainer.innerHTML = `
                <div class="text-center py-4">
                    <h4 class="text-success mb-3"><i class="fas fa-check-circle"></i> Sesión Activa</h4>
                    <p class="text-muted">Ya has iniciado sesión.</p>
                    <a href="mis_alquileres.html" class="btn btn-success w-100 mb-2 rounded-pill">Ir a Mi Cuenta</a>
                    ${userRol === "ADMIN" ? '<a href="admin.html" class="btn btn-primary w-100 mb-2 rounded-pill">Ir al Panel Admin</a>' : ''}

                    <button onclick="logout()" class="btn btn-outline-danger w-100 rounded-pill">Cerrar Sesión</button>

                </div>
            `;
            const inputs = loginFormContainer.parentElement.querySelectorAll('input');
            inputs.forEach(i => i.remove());
        }
    }
}

// Lógica del Formulario de Login
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const emailInput = document.getElementById('login-email');
        const passwordInput = document.getElementById('login-password');

        if(!emailInput || !passwordInput) return;

        const email = emailInput.value;
        const password = passwordInput.value;
        const statusDiv = document.getElementById('status-message');

        const params = new URLSearchParams();
        params.append('email', email);
        params.append('password', password);

        statusDiv.classList.remove('d-none', 'alert-danger', 'alert-success');
        statusDiv.classList.add('alert-info');
        statusDiv.textContent = 'Verificando credenciales...';

        try {
            // --- PASO 1: Intentar hacer Login ---
            const response = await axios.post('/api/login', params.toString(), {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            if (response.status === 200) {
                // --- PASO 2: Login exitoso, ahora preguntar "¿Quién soy?" ---
                statusDiv.textContent = '¡Bienvenido! Obteniendo datos...';

                const userResponse = await axios.get('/api/usuarios/actual');
                const userRol = userResponse.data.rol; // "ADMIN" o "CLIENTE"

                // --- PASO 3: Guardar estado, rol y nombre de usuario---
                sessionStorage.setItem("usuarioLogueado", "true");
                sessionStorage.setItem("usuarioRol", userRol);
                sessionStorage.setItem('usuarioNombre', userResponse.data.nombre);

                statusDiv.classList.remove('alert-info');
                statusDiv.classList.add('alert-success');
                statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> ¡Acceso concedido!';

                // Redirigir (el checkSession hará el resto)
                setTimeout(() => {
                    // Si es admin, lo mandamos al panel, si es cliente, a alquilar
                    if (userRol === "ADMIN") {
                        window.location.href = '/admin.html';
                    } else {
                        window.location.href = '/alquiler.html';
                    }
                }, 1000);
            }

        } catch (error) {
            // Error de Login (401)
            statusDiv.classList.remove('alert-info');
            statusDiv.classList.add('alert-danger');

            if (error.response && error.response.status === 401) {
                statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Email o contraseña incorrectos.';
            } else {
                statusDiv.innerHTML = '<i class="fas fa-wifi"></i> Error de conexión.';
            }
            passwordInput.value = '';
        }
    });
}