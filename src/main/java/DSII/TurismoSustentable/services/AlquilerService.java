package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.dto.AlquilerDTO;
import DSII.TurismoSustentable.dto.AlquilerRequestDTO;
import DSII.TurismoSustentable.models.*;
import DSII.TurismoSustentable.repositories.AlquilerRepository;
import DSII.TurismoSustentable.repositories.BicicletaRepository;
import DSII.TurismoSustentable.repositories.EstacionRepository;
import DSII.TurismoSustentable.repositories.UsuarioRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Map;

@Service
public class AlquilerService {

    @Autowired
    private AlquilerRepository alquilerRepository;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private BicicletaRepository bicicletaRepository;

    @Autowired
    private EstacionRepository estacionRepository;

    @Autowired
    private CorreoService correoService;

    private static final BigDecimal SEGUNDOS_EN_HORA =
            new BigDecimal("3600");


    // OBTIENE EL USUARIO AUTENTICADO
    private Usuario obtenerUsuarioAutenticado() {
        Authentication auth =
                SecurityContextHolder.getContext().getAuthentication();

        if (auth == null || !auth.isAuthenticated()) {
            throw new AccessDeniedException("Debe iniciar sesión.");
        }

        return usuarioRepository.findByEmail(auth.getName())
                .filter(Usuario::isActivo)
                .orElseThrow(() ->
                        new AccessDeniedException(
                                "El usuario autenticado no existe o está inactivo."
                        )
                );
    }


    // COMPRUEBA SI EL USUARIO ACTUAL ES ADMINISTRADOR
    private boolean usuarioActualEsAdmin() {
        Authentication auth =
                SecurityContextHolder.getContext().getAuthentication();

        if (auth == null) {
            return false;
        }

        return auth.getAuthorities().stream()
                .anyMatch(autoridad ->
                        "ADMIN".equals(autoridad.getAuthority())
                );
    }

    // CREAR UN ALQUILER
    @Transactional
    public AlquilerDTO crearAlquiler(
            AlquilerRequestDTO alquilerRequest
    ) throws Exception {

        // 1. Obtener el usuario de la sesión
        Usuario usuario = obtenerUsuarioAutenticado();

        // 2. Buscar y bloquear la bicicleta durante el alquiler
        Bicicleta bicicleta = bicicletaRepository
                .buscarActivaPorIdConBloqueo(
                        alquilerRequest.getBicicletaId()
                )
                .orElseThrow(() ->
                        new Exception("Bicicleta no encontrada.")
                );

        // 3. Verificar disponibilidad
        if (bicicleta.getEstado() != EstadoBicicleta.DISPONIBLE) {
            throw new IllegalStateException(
                    "La bicicleta no está disponible."
            );
        }

        // Guardamos la estación antes de sacar la bicicleta
        Estacion estacionRetiro = bicicleta.getUbicacionActual();

        if (estacionRetiro == null) {
            throw new IllegalStateException(
                    "La bicicleta no tiene una estación de retiro asignada."
            );
        }

        // 4. Verificar duración
        if (alquilerRequest.getDuracionEnHoras() <= 0) {
            throw new IllegalArgumentException(
                    "La duración debe ser mayor que cero."
            );
        }

        // También se valida en el backend el máximo mostrado en el frontend
        if (alquilerRequest.getDuracionEnHoras() > 24) {
            throw new IllegalArgumentException(
                    "La duración máxima del alquiler es de 24 horas."
            );
        }

        // 5. Calcular fechas
        LocalDateTime fechaInicio = LocalDateTime.now();

        LocalDateTime fechaFinEstimada = fechaInicio.plusHours(
                alquilerRequest.getDuracionEnHoras()
        );

        // 6. Calcular precio estimado
        BigDecimal precioPorHora = bicicleta.getPrecioPorHora();

        BigDecimal duracion = BigDecimal.valueOf(
                alquilerRequest.getDuracionEnHoras()
        );

        BigDecimal costoEstimado = precioPorHora
                .multiply(duracion)
                .setScale(2, RoundingMode.HALF_UP);

        // 7. Crear alquiler
        Alquiler nuevoAlquiler = new Alquiler(
                usuario,
                bicicleta,
                fechaInicio,
                fechaFinEstimada,
                costoEstimado,
                EstadoAlquiler.INICIADO,
                estacionRetiro,
                null
        );

        // se guardan tanto la tarifa congelada como el costo estimado inicial
        nuevoAlquiler.setPrecioPorHoraAplicado(precioPorHora);
        nuevoAlquiler.setCostoTotal(costoEstimado);

        // 8. Cambiar estado y sacar físicamente la bicicleta de la estación
        bicicleta.setEstado(EstadoBicicleta.ALQUILADA);
        bicicleta.setUbicacionActual(null);
        bicicletaRepository.save(bicicleta);

        // 9. Guardar alquiler
        Alquiler alquilerGuardado = alquilerRepository.save(nuevoAlquiler);
        correoService.enviarComprobanteInicio(alquilerGuardado);
        return new AlquilerDTO(alquilerGuardado);
    }

    /*
     * BORRAR LÓGICAMENTE UN ALQUILER
     *
     * Actualmente este metodo está protegido para ADMIN desde
     * WebAuthorization.
     */
    @Transactional
    public void borrarAlquilerLogico(Integer id) throws Exception {

        Alquiler alquiler = alquilerRepository.findById(id)
                .filter(a -> !a.isBorradoAlquiler())
                .orElseThrow(() ->
                        new Exception(
                                "El alquiler con ID "
                                        + id
                                        + " no existe."
                        )
                );

        // Un viaje activo debe devolverse físicamente antes de borrarse
        if (alquiler.getEstado() == EstadoAlquiler.INICIADO) {
            throw new IllegalStateException(
                    "No se puede eliminar un alquiler en curso. " +
                            "Primero debe finalizarse indicando una estación de devolución."
            );
        }

        // Solo se borran lógicamente alquileres terminados o cancelados
        alquiler.setBorradoAlquiler(true);
        alquilerRepository.save(alquiler);
    }

    /*
     * FINALIZAR UN ALQUILER
     */
    @Transactional
    public AlquilerDTO finalizarAlquiler(
            Integer id,
            String nombreEstacionDestino
    ) throws Exception {

        // 1. Obtener el usuario autenticado
        Usuario usuarioAutenticado = obtenerUsuarioAutenticado();

        // 2. Buscar el alquiler
        Alquiler alquiler = alquilerRepository.findById(id)
                .filter(a -> !a.isBorradoAlquiler())
                .orElseThrow(() ->
                        new Exception("El alquiler no existe.")
                );

        // 3. Prevenir IDOR
        boolean esAdmin = usuarioActualEsAdmin();

        boolean esPropietario =
                alquiler.getUsuario().getId()
                        == usuarioAutenticado.getId();

        if (!esAdmin && !esPropietario) {
            throw new AccessDeniedException(
                    "No tiene permiso para finalizar este alquiler."
            );
        }

        // 4. Comprobar el estado
        if (alquiler.getEstado() != EstadoAlquiler.INICIADO) {
            throw new IllegalStateException(
                    "El alquiler ya fue finalizado o cancelado."
            );
        }

        // 5. Validar el nombre de la estación
        if (nombreEstacionDestino == null
                || nombreEstacionDestino.trim().isEmpty()) {

            throw new IllegalArgumentException(
                    "Debe especificar una estación de destino."
            );
        }

        // 6. Buscar la estación de destino

        // Buscar y bloquear la estación durante esta devolución
        Estacion nuevaEstacion = estacionRepository
                .buscarActivaPorNombreConBloqueo(
                        nombreEstacionDestino.trim()
                )
                .orElseThrow(() ->
                        new IllegalArgumentException(
                                "La estación de destino no existe."
                        )
                );

        // Contar las bicicletas realmente ubicadas en la estación
        long espaciosOcupados = bicicletaRepository
                .countByUbicacionActualAndBorradoBiciFalse(
                        nuevaEstacion
                );

        // Impedir que la devolución supere la capacidad
        if (espaciosOcupados >= nuevaEstacion.getCapacidad()) {
            throw new IllegalStateException(
                    "La estación seleccionada no tiene espacios libres."
            );
        }

        // 7. Registrar la hora real de devolución
        LocalDateTime fechaDevolucion = LocalDateTime.now();

        alquiler.setFechaFin(fechaDevolucion);
        alquiler.setEstado(EstadoAlquiler.FINALIZADO);
        alquiler.setUbicacionDevolucion(nuevaEstacion);

        // 8. Calcular duración real
        long segundosReales = ChronoUnit.SECONDS.between(
                alquiler.getFechaInicio(),
                fechaDevolucion
        );

        if (segundosReales < 0) {
            segundosReales = 0;
        }

        // 9. Calcular costo final en USD
        BigDecimal precioPorHora = alquiler.getPrecioPorHoraAplicado();

        if (precioPorHora == null) {
            precioPorHora = alquiler.getBicicleta().getPrecioPorHora();
        }

        BigDecimal precioPorSegundo = precioPorHora.divide(
                SEGUNDOS_EN_HORA,
                10,
                RoundingMode.HALF_UP
        );

        BigDecimal costoFinal = precioPorSegundo
                .multiply(BigDecimal.valueOf(segundosReales))
                .setScale(2, RoundingMode.HALF_UP);

        alquiler.setCostoTotal(costoFinal);

        // 10. Obtener y congelar costo en ARS
        BigDecimal tasaCambio = obtenerCotizacionDolar();

        BigDecimal costoArs = costoFinal
                .multiply(tasaCambio)
                .setScale(0, RoundingMode.HALF_UP);

        alquiler.setCostoTotalArs(costoArs);

        // 11. Liberar y trasladar la bicicleta
        Bicicleta bicicleta = alquiler.getBicicleta();

        bicicleta.setEstado(EstadoBicicleta.DISPONIBLE);
        bicicleta.setUbicacionActual(nuevaEstacion);

        bicicletaRepository.save(bicicleta);

        // 12. Guardar alquiler finalizado
        Alquiler alquilerFinalizado = alquilerRepository.save(alquiler);
        correoService.enviarComprobanteFinalizacion(alquilerFinalizado);
        return new AlquilerDTO(alquilerFinalizado);
    }

    /*
     * OBTENER COTIZACIÓN DEL DÓLAR
     */
    public BigDecimal obtenerCotizacionDolar() {

        try {
            RestTemplate restTemplate = new RestTemplate();

            String url =
                    "https://dolarapi.com/v1/dolares/tarjeta";

            Map<?, ?> response =
                    restTemplate.getForObject(url, Map.class);

            if (response != null && response.get("venta") != null) {
                return new BigDecimal(
                        response.get("venta").toString()
                );
            }

        } catch (Exception e) {
            System.err.println(
                    "Error al obtener la cotización: "
                            + e.getMessage()
            );
        }

        // Valor de respaldo
        return new BigDecimal("1400");
    }
}