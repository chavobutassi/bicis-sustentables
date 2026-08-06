document.addEventListener("DOMContentLoaded", function() {

    // 1. Inicializar el mapa centrado en Río Grande (Ajustado)
    var map = L.map('map').setView([-53.7876, -67.7002], 14);

    // 2. Cargar capa de mapa (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // ---------------------------------------------------------
    // SITIOS TURÍSTICOS ESTÁTICOS
    // ---------------------------------------------------------
    const sitiosTuristicos = [
        { nombre: "Museo Virginia Choquintel", lat: -53.78788739688838, lng: -67.70383193191954, desc: "Conocé la historia local, flora, fauna y cultura." }, // Más al oeste
        { nombre: "Monumento Malvinas", lat: -53.77617824732636, lng: -67.69972785510566, desc: "Punto histórico emblemático." }, // Ajuste seguro
        { nombre: "Reserva Punta Popper", lat: -53.78926731524124, lng: -67.67435126484591, desc: "Recorrido para avistaje de aves y naturaleza." }, // Movido al inicio de la reserva
        { nombre: "Plaza Almirante Brown", lat: -53.78609592687204, lng: -67.69678982537542, desc: "Corazón céntrico de la ciudad." }
    ];

    // Icono violeta para distinguir turismo de estaciones
    var iconoTuristico = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    // Dibujar sitios turísticos en el mapa
    sitiosTuristicos.forEach(sitio => {
        L.marker([sitio.lat, sitio.lng], {icon: iconoTuristico}).addTo(map)
            .bindPopup(`
                <div class="text-center p-1">
                    <h6 class="fw-bold text-primary m-0 mb-1"><i class="fas fa-camera-retro"></i> ${sitio.nombre}</h6>
                    <p class="text-muted small m-0">${sitio.desc}</p>
                </div>
            `);
    });


    // ---------------------------------------------------------
    // CARGAR ESTACIONES DESDE EL BACKEND
    // ---------------------------------------------------------
    fetch('/api/estaciones')
        .then(response => response.json())
        .then(estaciones => {

            estaciones.forEach(estacion => {

                // Calculamos el límite del 30% basado en la capacidad total de la estación
                let limitePocasBicis = Math.ceil(estacion.capacidad * 0.30);

                // Definimos color según disponibilidad (Visibilidad del Estado)
                let colorIcon = 'blue'; // Fallback
                if (estacion.bicicletasDisponibles === 0) {
                    colorIcon = 'red'; // Sin bicis
                } else if (estacion.bicicletasDisponibles <= limitePocasBicis) {
                    colorIcon = 'gold'; // Pocas bicis (<= 30%)
                } else {
                    colorIcon = 'green'; // Muchas bicis (> 30%)
                }

                // Ícono personalizado de estación (con color dinámico)
                var icon = new L.Icon({
                    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${colorIcon}.png`,
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });

                // Validamos coordenadas de la BD
                let lat = estacion.latitud ? estacion.latitud : -53.7876;
                let lng = estacion.longitud ? estacion.longitud : -67.7002;

                // Crear marcador de la estación
                L.marker([lat, lng], {icon: icon}).addTo(map)
                    .bindPopup(`
                        <div class="text-center">
                            <h5>${estacion.nombre}</h5>
                            <p class="mb-1"><i class="fa-solid fa-location-dot"></i> ${estacion.direccion}</p>
                            <hr class="my-2">
                            <p class="mb-1"><strong>Disponibles:</strong> ${estacion.bicicletasDisponibles}</p>
                            <p class="text-muted mb-2"><small>Espacios libres: ${estacion.espaciosLibres}</small></p>
                            <button class="btn btn-sm btn-success w-100 fw-bold" onclick="alquilarBici(${estacion.id})">
                                <i class="fas fa-bicycle"></i> Ver Bicicletas
                            </button>
                        </div>
                    `);
            });
        })
        .catch(error => console.error('Error cargando estaciones:', error));
});

function alquilarBici(estacionId) {

    const estaLogueado =
        sessionStorage.getItem('usuarioLogueado') === 'true';

    if (!estaLogueado) {

        Swal.fire({
            title: 'Iniciá sesión',
            text: 'Necesitás iniciar sesión para consultar y alquilar bicicletas.',
            icon: 'info',
            confirmButtonText: 'Ir al ingreso',
            confirmButtonColor: '#198754'
        }).then(resultado => {

            if (resultado.isConfirmed) {

                document
                    .getElementById('login-anchor')
                    .scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });

                setTimeout(() => {
                    document
                        .getElementById('login-email')
                        ?.focus();
                }, 600);
            }
        });

        return;
    }

    sessionStorage.setItem('estacionSeleccionada', estacionId);
    window.location.href = `alquiler.html?estacionId=${estacionId}`;
}