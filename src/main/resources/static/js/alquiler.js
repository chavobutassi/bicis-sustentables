// Variables globales para guardar datos
let todasLasBicis = [];
let precioActualBici = 0;

let tasaCambio = 1; // Por defecto 1 (para dólares)
let monedaActual = 'USD'; // USD o ARS

document.addEventListener("DOMContentLoaded", async function() {
    // 1. Verificar si hay sesión (básico)
    if (!sessionStorage.getItem("usuarioLogueado")) {
        window.location.href = "index.html#login-anchor";
        return;
    }

    // Ejecutamos las 4 cargas en paralelo (nombre, estaciones, bicis y cotización)
    await Promise.all([
        cargarNombreUsuario(),
        cargarEstaciones(),
        cargarBicicletas(),
        cargarCotizacion() // Llamada a la API del dólar
    ]);

    // Listeners para ambos filtros (Estación y Tipo)
    document.getElementById('filtro-estacion').addEventListener('change', filtrarBicicletas);
    document.getElementById('filtro-tipo').addEventListener('change', filtrarBicicletas);

    // Listener para calcular precio en tiempo real en el modal
    document.getElementById('duracion').addEventListener('input', actualizarTotalModal);
});

// --- 1. CARGAR ESTACIONES (Para el select) ---
async function cargarEstaciones() {
    try {
        const response = await axios.get('/api/estaciones');
        const select = document.getElementById('filtro-estacion');

        response.data.forEach(est => {
            const option = document.createElement('option');
            option.value = est.nombre; // Filtramos por nombre de estación
            option.textContent = est.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Error cargando estaciones", error);
    }
}

// --- 2. CARGAR BICICLETAS DISPONIBLES ---
async function cargarBicicletas() {
    const container = document.getElementById('bicicletas-container');

    try {
        const response = await axios.get('/api/bicicletas/disponibles');
        todasLasBicis = response.data;

        renderizarBicicletas(todasLasBicis);

    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger text-center">No se pudieron cargar las bicicletas. ¿Has iniciado sesión?</div>`;
        console.error(error);
    }
}

// --- 3. RENDERIZAR TARJETAS (HTML Dinámico) ---
function renderizarBicicletas(listaBicis) {
    const container = document.getElementById('bicicletas-container');
    container.innerHTML = ''; // Limpiar loader

    if (listaBicis.length === 0) {
        container.innerHTML = `<div class="col-12 text-center text-muted py-5"><h4><i class="fas fa-bicycle"></i> No hay bicicletas disponibles con estos filtros.</h4></div>`;
        return;
    }

    listaBicis.forEach(bici => {
        // Asignar imagen según tipo
        let imagenUrl = '';
        switch(bici.tipo) {
            case 'MONTANA':
                imagenUrl = 'img/montana.jpg';
                break;
            case 'ELECTRICA':
                imagenUrl = 'img/electrica.jpg';
                break;
            case 'PASEO':
                imagenUrl = 'img/paseo.jpg';
                break;
            default:
                imagenUrl = 'img/paseo.jpg';
                break;
        }

        // Traducción del tipo de bici para el usuario
        let tipoBonito = bici.tipo;
        if (bici.tipo === 'MONTANA') tipoBonito = 'Montaña';
        if (bici.tipo === 'ELECTRICA') tipoBonito = 'Eléctrica';
        if (bici.tipo === 'PASEO') tipoBonito = 'Paseo';

        // LÓGICA DE PRECIO Y MONEDA
        let precioMostrar = bici.precio;
        let simbolo = 'US$';

        if (monedaActual === 'ARS') {
            precioMostrar = (bici.precio * tasaCambio).toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
            simbolo = 'AR$';
        } else {
            precioMostrar = bici.precio.toFixed(2);
        }

        const html = `
    <div class="col-md-6 col-lg-4 fade-in">
        <div class="card h-100 shadow-sm border-0 bike-card">
            <div class="position-relative">
                <img src="${imagenUrl}" class="card-img-top" alt="Bicicleta" style="height: 200px; object-fit: cover;">
                <span class="position-absolute top-0 end-0 badge bg-success m-2 shadow">
                    <i class="fas fa-check-circle"></i> Disponible
                </span>
            </div>
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="card-title fw-bold mb-0">${tipoBonito}</h5>
                    <span class="text-success fw-bold h5">${simbolo} ${precioMostrar} <small class="text-muted fs-6">/h</small></span>
                </div>
                <p class="card-text text-muted small">
                    <i class="fas fa-map-marker-alt text-danger"></i> ${bici.ubicacion}
                    <br>
                    <i class="fas fa-barcode"></i> Código: ${bici.codigoBicicleta}
                </p>
            </div>
            <div class="card-footer bg-white border-0 pb-3 text-center">
                <button class="btn btn-outline-success w-100 rounded-pill fw-bold"
                    onclick="abrirModalAlquiler(${bici.id}, '${bici.codigoBicicleta}', '${bici.ubicacion}', ${bici.precio}, '${tipoBonito}')">
                    Alquilar Ahora
                </button>
            </div>
        </div>
    </div>
    `;
        container.innerHTML += html;
    });
}

// --- 4. FILTRADO COMBINADO (Estación + Tipo) ---
function filtrarBicicletas() {
    const filtroEstacion = document.getElementById('filtro-estacion').value;
    const filtroTipo = document.getElementById('filtro-tipo').value;

    let bicisFiltradas = todasLasBicis;

    // Filtrar por estación si no está en "todas"
    if (filtroEstacion !== 'todas') {
        bicisFiltradas = bicisFiltradas.filter(b => b.ubicacion === filtroEstacion);
    }

    // Filtrar por tipo si no está en "todos"
    if (filtroTipo !== 'todos') {
        bicisFiltradas = bicisFiltradas.filter(b => b.tipo === filtroTipo);
    }

    renderizarBicicletas(bicisFiltradas);
}

// --- 5. LÓGICA DEL MODAL DE DOS PASOS ---

// Reinicia siempre el modal al Paso 1 cuando se abre
function volverAPaso1() {
    document.getElementById('modal-paso-2').classList.add('d-none');
    document.getElementById('footer-paso-2').classList.remove('d-flex');
    document.getElementById('footer-paso-2').classList.add('d-none');

    document.getElementById('modal-paso-1').classList.remove('d-none');
    document.getElementById('footer-paso-1').classList.remove('d-none');
    document.getElementById('footer-paso-1').classList.add('d-flex');
}

function abrirModalAlquiler(id, codigo, ubicacion, precio, tipo) {
    volverAPaso1(); // Forzamos reset de la vista

    document.getElementById('modal-bici-id').value = id;
    document.getElementById('modal-bici-codigo').textContent = `${tipo} ${codigo}`;
    document.getElementById('modal-bici-ubicacion').textContent = ubicacion;

    // Configurar precio en el modal según moneda actual
    let simbolo = monedaActual === 'ARS' ? 'AR$' : 'US$';
    let precioModal = monedaActual === 'ARS' ? (precio * tasaCambio).toLocaleString('es-AR', {maximumFractionDigits: 0}) : precio.toFixed(2);

    document.getElementById('modal-bici-precio').textContent = `${simbolo} ${precioModal} / hora`;

    precioActualBici = precio;
    document.getElementById('duracion').value = 1;
    actualizarTotalModal();

    const modal = new bootstrap.Modal(document.getElementById('modalAlquiler'));
    modal.show();
}

function actualizarTotalModal() {
    const horas = document.getElementById('duracion').value || 0;
    const totalDolares = horas * precioActualBici;

    if (monedaActual === 'ARS') {
        const totalPesos = (totalDolares * tasaCambio).toLocaleString('es-AR', { maximumFractionDigits: 0 });
        document.getElementById('calculo-total').textContent = `AR$ ${totalPesos}`;
    } else {
        document.getElementById('calculo-total').textContent = `US$ ${totalDolares.toFixed(2)}`;
    }
}

// Lógica de transición y cálculo de fechas para el ticket
function pasarAPaso2() {
    const horasInput = document.getElementById('duracion').value;
    const horas = parseInt(horasInput);

    if (isNaN(horas) || horas < 1 || horas > 24) {
        Swal.fire({
            icon: 'error',
            title: 'Cantidad inválida',
            text: 'Debes seleccionar entre 1 y 24 horas para alquilar.',
            confirmButtonColor: '#198754'
        });
        return;
    }

    // Calcular Fechas (Hora actual vs Hora de devolución)
    const fechaInicio = new Date();
    const fechaFin = new Date(fechaInicio.getTime() + (horas * 60 * 60 * 1000));

    // Formatear las fechas
    const opcionesFecha = { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false };
    const formatoInicio = fechaInicio.toLocaleString('es-AR', opcionesFecha);
    const formatoFin = fechaFin.toLocaleString('es-AR', opcionesFecha);

    // Llenar los datos del Ticket (Paso 2)
    document.getElementById('ticket-bici').textContent = document.getElementById('modal-bici-codigo').textContent;
    document.getElementById('ticket-ubicacion').textContent = document.getElementById('modal-bici-ubicacion').textContent;
    document.getElementById('ticket-inicio').textContent = formatoInicio;
    document.getElementById('ticket-fin').textContent = formatoFin + ` (${horas}h)`;
    document.getElementById('ticket-total').textContent = document.getElementById('calculo-total').textContent;

    // Cambiar la vista (Ocultar Paso 1, Mostrar Paso 2)
    document.getElementById('modal-paso-1').classList.add('d-none');
    document.getElementById('footer-paso-1').classList.remove('d-flex');
    document.getElementById('footer-paso-1').classList.add('d-none');

    document.getElementById('modal-paso-2').classList.remove('d-none');
    document.getElementById('footer-paso-2').classList.remove('d-none');
    document.getElementById('footer-paso-2').classList.add('d-flex');
}

// --- 6. ACCIÓN: ALQUILAR (POST) ---
async function confirmarAlquiler() {
    const biciId = document.getElementById('modal-bici-id').value;
    const horas = document.getElementById('duracion').value;

    if (horas <= 0) {
        Swal.fire('Error', 'La duración debe ser al menos 1 hora', 'error');
        return;
    }

    try {
        // Mostrar cargando
        Swal.fire({ title: 'Procesando...', didOpen: () => Swal.showLoading() });

        const payload = {
            bicicletaId: parseInt(biciId),
            duracionEnHoras: parseInt(horas)
        };

        // Petición al backend
        const response = await axios.post('/api/alquileres', payload);

        if (response.status === 201) {
            // Cerrar modal
            const modalEl = document.getElementById('modalAlquiler');
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();

            // Éxito (SweetAlert)
            await Swal.fire({
                icon: 'success',
                title: '¡Alquiler Iniciado!',
                text: 'Tu bicicleta ha sido desbloqueada. ¡Disfrutá el viaje!',
                confirmButtonColor: '#198754'
            });

            // Recargar la lista para quitar la bici alquilada
            cargarBicicletas();
        }

    } catch (error) {
        console.error(error);
        let mensaje = 'No se pudo procesar el alquiler.';
        if (error.response && error.response.data) {
            mensaje = error.response.data; // Mensaje del backend ("Bicicleta ocupada")
        }
        Swal.fire('Oops...', mensaje, 'error');
    }
}

// --- 7. LÓGICA DE MONEDA Y DOLARAPI ---
async function cargarCotizacion() {
    try {
        // Apuntamos al Dólar Tarjeta
        const response = await axios.get('/api/cotizacion');
        tasaCambio = response.data;
        console.log("Cotización Dólar Tarjeta cargada: AR$", tasaCambio);
    } catch (error) {
        console.error("Error al cargar la cotización de DolarAPI", error);
        // Respaldo por si falla la API
        tasaCambio = 1400;
    }
}

// Escuchar cambios en el Switch de Moneda
document.getElementById('switch-moneda').addEventListener('change', function(e) {
    monedaActual = e.target.checked ? 'ARS' : 'USD';

    // Cambiar la etiqueta junto al switch
    document.getElementById('label-moneda').textContent = monedaActual === 'ARS' ? 'AR$' : 'US$';

    // Volver a renderizar las tarjetas y el modal con la nueva moneda
    filtrarBicicletas();

    // Si el modal está abierto, actualiza su total también
    actualizarTotalModal();
});