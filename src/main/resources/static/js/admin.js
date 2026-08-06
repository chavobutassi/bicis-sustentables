// Variables globales
let listaEstaciones = []; // Para llenar selects

document.addEventListener("DOMContentLoaded", async () => {
    await verificarAdmin();
    cargarTodo();
});

async function verificarAdmin() {
    try {
        // Intentamos acceder a un recurso protegido de ADMIN
        await axios.get('/api/admin/estadisticas/resumen');
    } catch (error) {
        window.location.href = 'index.html'; // Si falla (403), fuera
    }
}

function cargarTodo() {
    cargarUsuarios();
    cargarEstaciones(); // También llena la lista global para el select de bicis
    cargarBicicletas();
    cargarAlquileres();
}

// ==========================================
// 1. GESTIÓN DE USUARIOS
// ==========================================
async function cargarUsuarios() {
    try {
        const res = await axios.get('/api/usuarios');
        const tbody = document.getElementById('tabla-usuarios-body');
        tbody.innerHTML = '';
        res.data.forEach(u => {
            tbody.innerHTML += `
                <tr>
                    <td>${u.id}</td>
                    <td>${u.nombre} ${u.apellido}</td>
                    <td>${u.email}</td>
                    <td>${u.genero}</td>
                    <td>${u.fechaNacimiento}</td>
                    <td>${u.rol}</td>
                    <td>${u.activo ? '<span class="badge bg-success">Activo</span>' : '<span class="badge bg-danger">Inactivo</span>'}</td>
                    <td>
                        <button class="btn btn-sm btn-warning" onclick="editarUsuario(${u.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-sm btn-danger" onclick="borrarUsuario(${u.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>`;
        });
    } catch (e) { console.error(e); }
}

// DELETE Usuario
async function borrarUsuario(id) {
    if (await confirmar()) {
        try {
            await axios.delete(`/api/usuarios/${id}`);
            cargarUsuarios();
            Swal.fire('Eliminado', '', 'success');
        } catch (e) { Swal.fire('Error', 'No se pudo eliminar', 'error'); }
    }
}

// EDIT Usuario (Solo precarga el modal)
async function editarUsuario(id) {
    try {
        const res = await axios.get(`/api/usuarios/${id}`);
        const u = res.data; // El DTO con los datos completos

        // Carga de datos
        document.getElementById('user-id').value = u.id;
        document.getElementById('user-nombre').value = u.nombre;
        document.getElementById('user-apellido').value = u.apellido;
        document.getElementById('user-email').value = u.email;
        document.getElementById('user-genero').value = u.genero;
        document.getElementById('user-fecha').value = u.fechaNacimiento;

        new bootstrap.Modal(document.getElementById('modalUsuario')).show();

    } catch (error) {
        Swal.fire('Error', 'No se pudieron cargar los datos del usuario.', 'error');
    }
}

async function guardarUsuario() {
    const id = document.getElementById('user-id').value;

    // Construimos el objeto data con todos los campos
    const data = {
        nombre: document.getElementById('user-nombre').value,
        apellido: document.getElementById('user-apellido').value,
        email: document.getElementById('user-email').value,

        // --- ENVÍO DE DATOS NUEVOS ---
        genero: document.getElementById('user-genero').value,
        fechaNacimiento: document.getElementById('user-fecha').value
    };

    // IMPORTANTE: Si la fecha está vacía, no la enviamos (la borramos del objeto)
    // Esto evita que se envíe un string vacío ("") y falle en el backend
    if (!data.fechaNacimiento) {
        delete data.fechaNacimiento;
    }

    try {
        // El controlador actualizado aceptará estos campos parciales
        await axios.put(`/api/usuarios/${id}`, data);

        bootstrap.Modal.getInstance(document.getElementById('modalUsuario')).hide();
        cargarUsuarios(); // Recargar la tabla
        Swal.fire('Guardado', 'Usuario actualizado con éxito', 'success');
    } catch (e) {
        Swal.fire('Error', 'No se pudo guardar el usuario', 'error');
    }
}


// ==========================================
// 2. GESTIÓN DE ESTACIONES
// ==========================================
async function cargarEstaciones() {
    try {
        const res = await axios.get('/api/estaciones');
        listaEstaciones = res.data; // Guardamos para usar en Bicis
        const tbody = document.getElementById('tabla-estaciones-body');
        tbody.innerHTML = '';
        res.data.forEach(e => {
            tbody.innerHTML += `
                <tr>
                    <td>${e.id}</td>
                    <td>${e.nombre}</td>
                    <td>${e.direccion}</td>
                    <td>${e.capacidad}</td>
                    <td>${e.latitud ? e.latitud : '-'}</td>
                    <td>${e.longitud ? e.longitud : '-'}</td>
                    
                    <td>
                        <button class="btn btn-sm btn-warning" onclick="editarEstacion(${e.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-sm btn-danger" onclick="borrarEstacion(${e.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>`;
        });
    } catch (e) { console.error(e); }
}

function abrirModalEstacion() {
    document.getElementById('estacion-id').value = '';
    document.getElementById('estacion-nombre').value = '';
    document.getElementById('estacion-direccion').value = '';
    document.getElementById('estacion-capacidad').value = '';
    document.getElementById('estacion-latitud').value = '';
    document.getElementById('estacion-longitud').value = '';
    new bootstrap.Modal(document.getElementById('modalEstacion')).show();
}

async function editarEstacion(id) {
    // Buscamos en la lista local para ahorrar una petición
    const e = listaEstaciones.find(est => est.id === id);
    document.getElementById('estacion-id').value = e.id;
    document.getElementById('estacion-nombre').value = e.nombre;
    document.getElementById('estacion-direccion').value = e.direccion;
    document.getElementById('estacion-capacidad').value = e.capacidad;
    document.getElementById('estacion-latitud').value = e.latitud || '';
    document.getElementById('estacion-longitud').value = e.longitud || '';
    new bootstrap.Modal(document.getElementById('modalEstacion')).show();
}

async function guardarEstacion() {
    const id = document.getElementById('estacion-id').value;

    const data = {
        nombre: document.getElementById('estacion-nombre').value,
        direccion: document.getElementById('estacion-direccion').value,
        capacidad: parseInt(document.getElementById('estacion-capacidad').value),
        // Convertimos los valores a Float para que Java los reciba correctamente
        latitud: parseFloat(document.getElementById('estacion-latitud').value),
        longitud: parseFloat(document.getElementById('estacion-longitud').value)
    };
    try {
        if (id) await axios.put(`/api/estaciones/${id}`, data);
        else await axios.post('/api/estaciones', data);

        bootstrap.Modal.getInstance(document.getElementById('modalEstacion')).hide();
        cargarEstaciones();
        Swal.fire('Guardado', 'Estación guardada correctamente', 'success');
    } catch (e) {
        Swal.fire('Error', 'Datos inválidos, incompletos o nombre duplicado', 'error');
    }
}

async function borrarEstacion(id) {
    if (await confirmar()) {
        try {
            await axios.delete(`/api/estaciones/${id}`);
            cargarEstaciones();
            Swal.fire('Eliminado', '', 'success');
        } catch (e) { 
            // Aquí capturamos el 409 Conflict (bicis asignadas)
            Swal.fire('No se puede borrar', 'La estación tiene bicicletas asignadas.', 'warning'); 
        }
    }
}

// ==========================================
// 3. GESTIÓN DE BICICLETAS
// ==========================================
async function cargarBicicletas() {
    try {
        // Usamos el endpoint general (incluye Mantenimiento/Alquiladas)
        const res = await axios.get('/api/bicicletas');
        const tbody = document.getElementById('tabla-bicicletas-body');
        tbody.innerHTML = '';
        res.data.forEach(b => {
            tbody.innerHTML += `
                <tr>
                    <td>${b.id}</td>
                    <td>${b.codigoBicicleta}</td>
                    <td>${b.tipo}</td>
                    <td><span class="badge bg-${getColorEstado(b.estado)}">${b.estado}</span></td>
                    <td>$${b.precio}</td>
                    <td>${b.ubicacion}</td>
                    <td>
                        <button class="btn btn-sm btn-warning" onclick="editarBici(${b.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-sm btn-danger" onclick="borrarBici(${b.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>`;
        });
    } catch (e) { console.error(e); }
}

function llenarSelectEstaciones() {
    const select = document.getElementById('bici-estacion-select');
    select.innerHTML = '';
    listaEstaciones.forEach(e => {
        select.innerHTML += `<option value="${e.id}">${e.nombre}</option>`; // Enviamos ID, pero el backend espera OBJETO Estacion
    });
}

// ADAPTADOR ESPECIAL: El Backend espera un Objeto Estacion completo o un ID mapeado.
// Como hiciste el cambio a Entity, tu BicicletaController espera una "Estacion ubicacionActual".
// Axios enviará JSON. Si envías { "id": 1 }, Spring puede convertirlo si está configurado,
// PERO lo más seguro es enviar el objeto completo con el ID.
function getEstacionSeleccionada() {
    const id = parseInt(document.getElementById('bici-estacion-select').value);
    return { id: id }; // Spring interpretará esto como una Estacion con ese ID
}

function abrirModalBicicleta() {
    llenarSelectEstaciones();

    document.getElementById('bici-id').value = '';
    document.getElementById('bici-codigo').value = '';
    document.getElementById('bici-precio').value = '';
    document.getElementById('bici-estado').value = 'DISPONIBLE';

    // Habilitar todos los campos para una bicicleta nueva
    document.getElementById('bici-codigo').disabled = false;
    document.getElementById('bici-tipo').disabled = false;
    document.getElementById('bici-estado').disabled = false;
    document.getElementById('bici-estacion-select').disabled = false;

    document.getElementById('bici-alquiler-aviso')
        .classList.add('d-none');

    new bootstrap.Modal(
        document.getElementById('modalBicicleta')
    ).show();
}

async function editarBici(id) {
    llenarSelectEstaciones();

    const res = await axios.get(`/api/bicicletas/${id}`);
    const b = res.data;

    document.getElementById('bici-id').value = b.id;
    document.getElementById('bici-codigo').value = b.codigoBicicleta;
    document.getElementById('bici-tipo').value = b.tipo;
    document.getElementById('bici-estado').value = b.estado;
    document.getElementById('bici-precio').value = b.precio;

    const estaAlquilada = b.estado === 'ALQUILADA';

    // Durante un alquiler solamente se puede modificar el precio
    document.getElementById('bici-codigo').disabled = estaAlquilada;
    document.getElementById('bici-tipo').disabled = estaAlquilada;
    document.getElementById('bici-estado').disabled = estaAlquilada;
    document.getElementById('bici-estacion-select').disabled = estaAlquilada;

    document.getElementById('bici-alquiler-aviso')
        .classList.toggle('d-none', !estaAlquilada);

    new bootstrap.Modal(
        document.getElementById('modalBicicleta')
    ).show();
}

async function guardarBicicleta() {
    const id = document.getElementById('bici-id').value;

    const estaAlquilada =
        document.getElementById('bici-estado').value === 'ALQUILADA';

    let data;

    if (estaAlquilada) {
        // Durante el viaje solamente se envía el precio
        data = {
            precioPorHora:
            document.getElementById('bici-precio').value
        };
    } else {
        // Para las demás bicicletas se envían todos los datos
        data = {
            codigoBicicleta:
            document.getElementById('bici-codigo').value,

            tipo:
            document.getElementById('bici-tipo').value,

            estado:
            document.getElementById('bici-estado').value,

            precioPorHora:
            document.getElementById('bici-precio').value,

            ubicacionActual:
                getEstacionSeleccionada()
        };
    }

    try {
        if (id) {
            await axios.put(`/api/bicicletas/${id}`, data);
        } else {
            await axios.post('/api/bicicletas', data);
        }

        bootstrap.Modal.getInstance(
            document.getElementById('modalBicicleta')
        ).hide();

        cargarBicicletas();

        if (estaAlquilada) {
            Swal.fire(
                'Precio actualizado',
                'El nuevo precio se aplicará en los próximos alquileres.',
                'success'
            );
        } else {
            Swal.fire('Guardado', '', 'success');
        }

    } catch (e) {
        const mensaje =
            typeof e.response?.data === 'string'
                ? e.response.data
                : 'Verifica los datos';

        Swal.fire('Error', mensaje, 'error');
    }
}

async function borrarBici(id) {
    if (await confirmar()) {
        try {
            await axios.delete(`/api/bicicletas/${id}`);
            cargarBicicletas();
            Swal.fire('Eliminado', '', 'success');
        } catch (e) { Swal.fire('Error', 'No se pudo eliminar', 'error'); }
    }
}


// ==========================================
// 4. GESTIÓN DE ALQUILERES
// ==========================================
async function cargarAlquileres() {
    try {
        // Como ADMIN, este endpoint debería devolver TODOS
        // Si tu controlador filtra por usuario logueado, tendrás que crear un endpoint
        // nuevo en AdminController o modificar AlquilerController para que si es ADMIN devuelva todos.
        // ASUMO que por ahora devuelve los tuyos (admin).
        
        const res = await axios.get('/api/admin/estadisticas/alquileres-todos');
        const tbody = document.getElementById('tabla-alquileres-body');
        tbody.innerHTML = '';
        res.data.forEach(a => {
            tbody.innerHTML += `
                <tr>
                    <td>${a.id}</td>
                    <td>ID: ${a.usuarioId}</td>
                    <td>${a.codigoBicicleta}</td>
                    <td><span class="badge bg-${a.estado === 'INICIADO' ? 'success' : 'secondary'}">${a.estado}</span></td>
                    <td>${new Date(a.fechaInicio).toLocaleDateString()}</td>
                    <td>${a.fechaFin ? new Date(a.fechaFin).toLocaleDateString() : '-'}</td>
                    <td>$${a.costoTotal}</td>
                    <td>
                        ${a.estado === 'INICIADO' ? 
                        `<button class="btn btn-sm btn-danger" onclick="finalizarAlquilerAdmin(${a.id})">Finalizar</button>` : 
                        '<i class="fas fa-check text-success"></i>'}
                    </td>
                </tr>`;
        });
    } catch (e) { console.error(e); }
}

async function finalizarAlquilerAdmin(id) {
    try {
        // Obtener información actualizada de las estaciones
        const respuesta = await axios.get('/api/estaciones');

        // Mostrar solamente estaciones que tengan lugar
        const estacionesDisponibles = respuesta.data.filter(
            estacion => estacion.espaciosLibres > 0
        );

        if (estacionesDisponibles.length === 0) {
            Swal.fire(
                'Sin estaciones disponibles',
                'No hay estaciones con espacios libres para devolver la bicicleta.',
                'warning'
            );
            return;
        }

        // Opciones para el selector de SweetAlert
        const opciones = {};

        estacionesDisponibles.forEach(estacion => {
            opciones[estacion.nombre] =
                `${estacion.nombre} - ${estacion.espaciosLibres} espacios libres`;
        });

        const resultado = await Swal.fire({
            title: 'Finalizar alquiler',
            text: 'Seleccione la estación de devolución',
            input: 'select',
            inputOptions: opciones,
            inputPlaceholder: 'Seleccione una estación',
            showCancelButton: true,
            confirmButtonText: 'Finalizar viaje',
            cancelButtonText: 'Cancelar',
            icon: 'question',

            inputValidator: valor => {
                if (!valor) {
                    return 'Debe seleccionar una estación.';
                }
            }
        });

        if (!resultado.isConfirmed) {
            return;
        }

        // El backend espera: { ubicacionDestino: "Nombre estación" }
        await axios.patch(
            `/api/alquileres/finalizar/${id}`,
            {
                ubicacionDestino: resultado.value
            }
        );

        await Promise.all([
            cargarAlquileres(),
            cargarBicicletas(),
            cargarEstaciones()
        ]);

        Swal.fire(
            'Alquiler finalizado',
            'La bicicleta fue devuelta correctamente.',
            'success'
        );

    } catch (e) {
        const mensaje =
            typeof e.response?.data === 'string'
                ? e.response.data
                : 'No se pudo finalizar el alquiler.';

        Swal.fire(
            'No se pudo finalizar',
            mensaje,
            'error'
        );
    }
}


// UTILIDADES
function getColorEstado(estado) {
    if (estado === 'DISPONIBLE') return 'success';
    if (estado === 'ALQUILADA') return 'warning';
    return 'secondary'; // Mantenimiento/Inactiva
}

async function confirmar(msg = "¿Estás seguro?") {
    const res = await Swal.fire({
        title: msg, icon: 'warning', showCancelButton: true, confirmButtonColor: '#d33'
    });
    return res.isConfirmed;
}