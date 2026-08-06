package DSII.TurismoSustentable.controllers;

import DSII.TurismoSustentable.dto.BicicletaDTO;
import DSII.TurismoSustentable.models.Bicicleta;
import DSII.TurismoSustentable.models.EstadoBicicleta;
import DSII.TurismoSustentable.models.TipoBicicleta;
import DSII.TurismoSustentable.models.Estacion;
import org.springframework.transaction.annotation.Transactional;
import DSII.TurismoSustentable.repositories.EstacionRepository;
import DSII.TurismoSustentable.repositories.BicicletaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api")
public class BicicletaController {

    @Autowired
    private BicicletaRepository bicicletaRepository;

    @Autowired
    private EstacionRepository estacionRepository;

    // OBTENER TODAS LAS BICIS DE LA BD (Solo las no borradas)
    @GetMapping("/bicicletas")
    public List<BicicletaDTO> getBicicletas(){
        // Filtra solo por borrado lógico (muestra MANTENIMIENTO, ALQUILADA, etc.)
        return bicicletaRepository.findByBorradoBiciFalse()
                .stream()
                .map(BicicletaDTO:: new)
                .collect(Collectors.toList());
    }

    // OBTIENE LAS BICIS DISPONIBLES PARA ALQUILAR
    @GetMapping("/bicicletas/disponibles")
    public List<BicicletaDTO> getBicicletasDisponibles(){
        // Filtra por no borrada (borradoBici=false) Y estado = DISPONIBLE (Enum)
        return bicicletaRepository.findByBorradoBiciFalseAndEstado(EstadoBicicleta.DISPONIBLE)
                .stream()
                .map(BicicletaDTO:: new)
                .collect(Collectors.toList());
    }

    // OBTENER BICICLETAS FILTRADAS POR TIPO (Montaña, Paseo, Eléctrica)
    @GetMapping("/bicicletas/tipo/{tipo}")
    public List<BicicletaDTO> getBicicletasPorTipo(@PathVariable TipoBicicleta tipo){
        return bicicletaRepository.findByBorradoBiciFalseAndTipo(tipo)
                .stream()
                .map(BicicletaDTO::new)
                .collect(Collectors.toList());
    }

    // GET por ID
    @GetMapping("/bicicletas/{id}")
    public ResponseEntity<BicicletaDTO> getBicicletaPorId(@PathVariable Integer id) {

        Optional<Bicicleta> bicicletaOpt = bicicletaRepository.findById(id);

        if (bicicletaOpt.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }

        Bicicleta bicicleta = bicicletaOpt.get();

        // Filtro de seguridad. Si la bici está borrada lógicamente, devuelve 404
        if (bicicleta.isBorradoBici()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }

        return ResponseEntity.ok(new BicicletaDTO(bicicleta));
    }

    // POST /api/bicicletas: Crear nueva bicicleta (Solo ADMIN)
    @PostMapping("/bicicletas")
    @Transactional
    public ResponseEntity<Object> crearBicicleta(
            @Valid @RequestBody Bicicleta bicicleta
    ) {

        // La nueva bicicleta debe tener una estación
        if (bicicleta.getUbicacionActual() == null
                || bicicleta.getUbicacionActual().getId() <= 0) {

            return new ResponseEntity<>(
                    "Debe seleccionar una estación válida.",
                    HttpStatus.BAD_REQUEST
            );
        }

        Integer estacionId =
                bicicleta.getUbicacionActual().getId();

        // Buscar y bloquear la estación durante la creación
        Estacion estacion = estacionRepository
                .buscarActivaPorIdConBloqueo(estacionId)
                .orElse(null);

        if (estacion == null) {
            return new ResponseEntity<>(
                    "La estación seleccionada no existe o está inactiva.",
                    HttpStatus.BAD_REQUEST
            );
        }

        // Consultar la ocupación real
        long espaciosOcupados = bicicletaRepository
                .countByUbicacionActualAndBorradoBiciFalse(
                        estacion
                );

        if (espaciosOcupados >= estacion.getCapacidad()) {
            return new ResponseEntity<>(
                    "No se puede agregar la bicicleta: " +
                            "la estación no tiene espacios libres.",
                    HttpStatus.CONFLICT
            );
        }

        // Usar la estación administrada y bloqueada por JPA
        bicicleta.setUbicacionActual(estacion);

        // Una bicicleta nueva no puede nacer alquilada ni borrada
        bicicleta.setEstado(EstadoBicicleta.DISPONIBLE);
        bicicleta.setBorradoBici(false);

        Bicicleta nuevaBicicleta = bicicletaRepository.save(bicicleta);

        return new ResponseEntity<>(
                new BicicletaDTO(nuevaBicicleta),
                HttpStatus.CREATED
        );
    }

    // DELETE /api/bicicletas/{id}: Borrado Lógico (Solo ADMIN)
    @DeleteMapping("/bicicletas/{id}")
    public ResponseEntity<Object> eliminarBicicletaLogico(@PathVariable Integer id) {

        Optional<Bicicleta> bicicletaOptional = bicicletaRepository.findById(id);

        if (bicicletaOptional.isEmpty()) {
            return new ResponseEntity<>("La bicicleta no existe.", HttpStatus.NOT_FOUND);
        }

        Bicicleta bicicleta = bicicletaOptional.get();

        if (bicicleta.getEstado() == EstadoBicicleta.ALQUILADA) {
            return new ResponseEntity<>(
                    "No se puede eliminar una bicicleta que está actualmente alquilada.",
                    HttpStatus.CONFLICT // 409 Conflict es el código correcto
            );
        }
        // ---------------------------------

        // Borrado lógico
        bicicleta.setBorradoBici(true);
        bicicleta.setEstado(EstadoBicicleta.INACTIVA);

        bicicletaRepository.save(bicicleta);

        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    // PUT /api/bicicletas/{id}: Actualizar bicicleta (Solo ADMIN)
    @PutMapping("/bicicletas/{id}")
    @Transactional
    public ResponseEntity<Object> actualizarBicicleta(
            @PathVariable Integer id,
            @RequestBody Bicicleta bicicletaDetalles
    ) {

        Optional<Bicicleta> bicicletaOpt =
                bicicletaRepository.findById(id);

        if (bicicletaOpt.isEmpty()
                || bicicletaOpt.get().isBorradoBici()) {

            return new ResponseEntity<>(
                    "La bicicleta no existe o está inactiva.",
                    HttpStatus.NOT_FOUND
            );
        }

        Bicicleta bicicletaExistente = bicicletaOpt.get();

        boolean estabaAlquilada =
                bicicletaExistente.getEstado()
                        == EstadoBicicleta.ALQUILADA;

        // El código no puede modificarse durante un alquiler
        if (!estabaAlquilada && bicicletaDetalles.getCodigoBicicleta() != null) {
            bicicletaExistente.setCodigoBicicleta(
                    bicicletaDetalles.getCodigoBicicleta()
            );
        }

        /*
         * El estado solamente puede modificarse si la bicicleta
         * no está actualmente alquilada.
         */
        if (!estabaAlquilada
                && bicicletaDetalles.getEstado() != null) {

            if (bicicletaDetalles.getEstado()
                    == EstadoBicicleta.ALQUILADA) {

                return new ResponseEntity<>(
                        "No se puede marcar manualmente una bicicleta " +
                                "como alquilada. Debe iniciarse un alquiler.",
                        HttpStatus.CONFLICT
                );
            }

            bicicletaExistente.setEstado(
                    bicicletaDetalles.getEstado()
            );
        }

        /*
         * La estación solamente puede modificarse si la bicicleta
         * no está actualmente alquilada.
         */
        if (!estabaAlquilada
                && bicicletaDetalles.getUbicacionActual() != null) {

            int estacionDestinoId =
                    bicicletaDetalles.getUbicacionActual().getId();

            if (estacionDestinoId <= 0) {
                return new ResponseEntity<>(
                        "Debe seleccionar una estación válida.",
                        HttpStatus.BAD_REQUEST
                );
            }

            Estacion estacionActual =
                    bicicletaExistente.getUbicacionActual();

            boolean cambiaDeEstacion =
                    estacionActual == null
                            || estacionActual.getId()
                            != estacionDestinoId;

            /*
             * Si permanece en la misma estación,
             * no ocupa un espacio adicional.
             */
            if (cambiaDeEstacion) {

                Estacion estacionDestino = estacionRepository
                        .buscarActivaPorIdConBloqueo(
                                estacionDestinoId
                        )
                        .orElse(null);

                if (estacionDestino == null) {
                    return new ResponseEntity<>(
                            "La estación seleccionada no existe " +
                                    "o está inactiva.",
                            HttpStatus.BAD_REQUEST
                    );
                }

                long espaciosOcupados = bicicletaRepository
                        .countByUbicacionActualAndBorradoBiciFalse(
                                estacionDestino
                        );

                if (espaciosOcupados
                        >= estacionDestino.getCapacidad()) {

                    return new ResponseEntity<>(
                            "No se puede mover la bicicleta: " +
                                    "la estación de destino está llena.",
                            HttpStatus.CONFLICT
                    );
                }

                bicicletaExistente.setUbicacionActual(
                        estacionDestino
                );
            }
        }

        // El tipo no puede modificarse durante un alquiler
        if (!estabaAlquilada
                && bicicletaDetalles.getTipo() != null) {
            bicicletaExistente.setTipo(
                    bicicletaDetalles.getTipo()
            );
        }

        // Se puede modificar el precio aunque esté alquilada
        if (bicicletaDetalles.getPrecioPorHora() != null) {
            bicicletaExistente.setPrecioPorHora(
                    bicicletaDetalles.getPrecioPorHora()
            );
        }

        /*
         * Si estaba alquilada, se conservan obligatoriamente
         * su estado ALQUILADA y su ubicación vacía.
         */
        if (estabaAlquilada) {
            bicicletaExistente.setEstado(
                    EstadoBicicleta.ALQUILADA
            );
            bicicletaExistente.setUbicacionActual(null);
        }

        Bicicleta bicicletaActualizada =
                bicicletaRepository.save(bicicletaExistente);

        return ResponseEntity.ok(
                new BicicletaDTO(bicicletaActualizada)
        );
    }
}
