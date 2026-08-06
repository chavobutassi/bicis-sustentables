// Variables Globales
let listaAlquileres = [];
let monedaActual = 'USD';

document.addEventListener("DOMContentLoaded", async function() {

    /*
     * Evita mostrar una copia almacenada por el navegador
     * después de cerrar sesión.
     * La seguridad real sigue estando en Spring Security.
     */
    const estaLogueado =
        sessionStorage.getItem("usuarioLogueado") === "true";

    if (!estaLogueado) {
        window.location.replace(
            "index.html#login-anchor"
        );
        return;
    }

    // Cargar los alquileres y nombre de usuario logueado
    await Promise.all([
        cargarNombreUsuario(),
        cargarAlquileres()
    ]);

    // Listener del Switch de Moneda
    const switchMoneda = document.getElementById('switch-moneda');
    if (switchMoneda) {
        switchMoneda.addEventListener('change', function(e) {
            monedaActual = e.target.checked ? 'ARS' : 'USD';
            document.getElementById('label-moneda').textContent = monedaActual === 'ARS' ? 'AR$' : 'US$';

            // Re-renderizamos para aplicar la nueva moneda en la tabla visualmente
            renderizarAlquileres();
        });
    }
});

// Formateador de moneda para el historial
function formatearPrecioHistorial(precioUSD, precioARS) {
    if (precioUSD == null) return "0.00";

    if (monedaActual === 'ARS') {
        // Trae directamente el valor congelado en pesos.
        return 'AR$ ' + (precioARS || 0).toLocaleString('es-AR', { maximumFractionDigits: 0 });
    } else {
        // Trae directamente el valor original en dólares.
        return 'US$ ' + parseFloat(precioUSD).toFixed(2);
    }
}

// CARGA Y RENDERIZADO DE ALQUILERES
async function cargarAlquileres() {
    try {
        const response = await axios.get('/api/alquileres');
        listaAlquileres = response.data;
        renderizarAlquileres();
    } catch (error) {
        console.error(error);
        // Si no está logueado, redirige al inicio
        window.location.href = 'index.html';
    }
}

function renderizarAlquileres() {
    const containerActivos = document.getElementById('container-activos');
    const tbodyHistorial = document.getElementById('tbody-historial');

    if (!containerActivos || !tbodyHistorial) return;

    containerActivos.innerHTML = '';
    tbodyHistorial.innerHTML = '';
    let hayActivos = false;

    listaAlquileres.forEach(alq => {
        if (alq.estado === 'INICIADO') {
            hayActivos = true;
            containerActivos.innerHTML += `
                <div class="alert alert-success d-flex flex-column flex-md-row justify-content-between align-items-md-center shadow-sm" role="alert">
                    <div class="mb-3 mb-md-0">
                        <h4 class="alert-heading fw-bold"><i class="fas fa-bicycle"></i> ${alq.codigoBicicleta}</h4>
                        <p class="mb-1"><i class="fas fa-play-circle"></i> Iniciado el: ${new Date(alq.fechaInicio).toLocaleString('es-AR')}</p>
                        <p class="mb-0 small text-muted"><i class="fas fa-map-marker-alt"></i> Retirada en: ${alq.ubicacionRetiro}</p>
                    </div>
                    <button class="btn btn-danger fw-bold shadow px-4 py-2 rounded-pill" onclick="abrirModalDevolucion(${alq.id}, '${alq.codigoBicicleta}', '${alq.fechaInicio}')">
                        <i class="fas fa-stop-circle"></i> DEVOLVER AHORA
                    </button>
                </div>
            `;
        } else {
            // Historial con moneda dinámica
            const precioMostrado = formatearPrecioHistorial(alq.costoTotal, alq.costoTotalArs);
            tbodyHistorial.innerHTML += `
                <tr>
                    <td><span class="badge bg-light text-dark border"> ${alq.codigoBicicleta}</span></td>
                    <td class="small">${new Date(alq.fechaInicio).toLocaleString('es-AR')}</td>
                    <td class="small">${new Date(alq.fechaFin).toLocaleString('es-AR')}</td>
                    <td class="fw-bold text-success">${precioMostrado}</td>
                    <td><span class="badge bg-secondary">${alq.estado}</span></td>
                </tr>
            `;
        }
    });

    if (!hayActivos) {
        containerActivos.innerHTML = '<p class="text-muted mb-0">No tenés viajes en curso.</p>';
    }

    const mensajeHistorial = document.getElementById('mensaje-historial');
    if (tbodyHistorial.innerHTML === '') {
        mensajeHistorial.textContent = 'Aun no tenés historial de viajes.';
    } else {
        mensajeHistorial.textContent = '';
    }
}

// LÓGICA DEL MODAL DE DEVOLUCIÓN
async function abrirModalDevolucion(idAlquiler, codigoBici, fechaInicioISO) {
    // 1. Setear datos básicos visuales
    document.getElementById('modal-dev-id').value = idAlquiler;
    document.getElementById('modal-dev-bici').textContent = `Bicicleta ${codigoBici}`;

    // 2. Calcular tiempo exacto transcurrido
    const fechaInicio = new Date(fechaInicioISO);
    const ahora = new Date();
    const difMilisegundos = ahora - fechaInicio;
    const minutosUso = Math.max(1, Math.floor(difMilisegundos / 60000)); // Para que como mínimo cobre 1 minuto

    // Mostrar horas y minutos si es más de 60
    let textoTiempo = `${minutosUso} minutos`;
    if (minutosUso >= 60) {
        const horas = Math.floor(minutosUso / 60);
        const minsRestantes = minutosUso % 60;
        textoTiempo = `${horas}h ${minsRestantes}m`;
    }
    document.getElementById('modal-dev-tiempo').textContent = textoTiempo;

    // 3. Cargar estaciones disponibles (Consumiendo el DTO de Spring Boot)
    const select = document.getElementById('select-estacion-destino');
    select.innerHTML = '<option value="">Cargando estaciones...</option>';

    try {
        const response = await axios.get('/api/estaciones');
        select.innerHTML = '<option value="" disabled selected>Seleccioná una estación con lugar...</option>';

        let hayLugares = false;

        response.data.forEach(est => {
            // USAMOS LA PROPIEDAD espaciosLibres
            const lugaresLibres = est.espaciosLibres;

            const option = document.createElement('option');
            option.value = est.nombre; // Guardamos el nombre para enviarlo al backend

            if (lugaresLibres > 0) {
                option.textContent = `${est.nombre} (${lugaresLibres} lugares libres)`;
                hayLugares = true;
            } else {
                option.textContent = `${est.nombre} (LLENA - Sin lugar)`;
                option.disabled = true;
            }
            select.appendChild(option);
        });

        if (!hayLugares) {
            Swal.fire('Atención', 'Actualmente no hay estaciones con lugares disponibles.', 'warning');
        }

    } catch (error) {
        select.innerHTML = '<option value="">Error al cargar estaciones</option>';
        console.error(error);
    }

    // 4. Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById('modalDevolucion'));
    modal.show();
}

// CONFIRMAR DEVOLUCIÓN (PATCH AL BACKEND)
async function confirmarDevolucion() {
    const id = document.getElementById('modal-dev-id').value;
    const estacionDestino = document.getElementById('select-estacion-destino').value;

    if (!estacionDestino) {
        Swal.fire('Atención', 'Por favor, seleccioná en qué estación vas a dejar la bicicleta.', 'warning');
        return;
    }

    try {
        Swal.fire({ title: 'Procesando devolución...', didOpen: () => Swal.showLoading() });

        // Enviamos al backend dónde la dejó el usuario.
        const payload = {
            ubicacionDestino: estacionDestino
        };

        const response = await axios.patch(`/api/alquileres/finalizar/${id}`, payload);

        // Cerrar modal
        const modalEl = document.getElementById('modalDevolucion');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();

        // Mostrar éxito calculando la moneda que tenga elegida
        const precioFinal = formatearPrecioHistorial(response.data.costoTotal, response.data.costoTotalArs);

        await Swal.fire({
            icon: 'success',
            title: '¡Bici devuelta con éxito!',
            text: `Tu viaje finalizó correctamente. Costo final exacto: ${precioFinal}`,
            confirmButtonColor: '#198754'
        });

        cargarAlquileres(); // Recargar historial para que pase a Finalizados

    } catch (error) {
        console.error(error);
        Swal.fire('Error', 'No se pudo finalizar el viaje. Intentá nuevamente.', 'error');
    }
}