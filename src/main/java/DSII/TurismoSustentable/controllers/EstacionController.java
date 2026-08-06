package DSII.TurismoSustentable.controllers;

import DSII.TurismoSustentable.dto.EstacionDTO;
import DSII.TurismoSustentable.models.Estacion;
import DSII.TurismoSustentable.repositories.EstacionRepository;
import DSII.TurismoSustentable.repositories.BicicletaRepository;
import org.springframework.transaction.annotation.Transactional;
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
public class EstacionController {

    @Autowired
    private EstacionRepository estacionRepository;

    @Autowired
    private BicicletaRepository bicicletaRepository;

    // OBTENER TODAS LAS ESTACIONES (Solo las no borradas)
    @GetMapping("/estaciones")
    public List<EstacionDTO> getEstaciones() {
        // Filtra solo por borrado lógico
        return estacionRepository.findByBorradoEstacionFalse()
                .stream()
                .map(EstacionDTO::new)
                .collect(Collectors.toList());
    }

    // GET por ID
    @GetMapping("/estaciones/{id}")
    public ResponseEntity<EstacionDTO> getEstacionPorId(@PathVariable Integer id) {

        Optional<Estacion> estacionOpt = estacionRepository.findById(id);

        if (estacionOpt.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }

        Estacion estacion = estacionOpt.get();

        // Filtro de seguridad: Si está borrada lógicamente, devuelve 404
        if (estacion.isBorradoEstacion()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }

        return ResponseEntity.ok(new EstacionDTO(estacion));
    }

    // POST /api/estaciones: Crear nueva estación (Solo ADMIN)
    @PostMapping("/estaciones")
    public ResponseEntity<Object> crearEstacion(@Valid @RequestBody Estacion estacion) {

        // Validación extra: Nombre único
        if (estacionRepository.findByNombre(estacion.getNombre()).isPresent()) {
            return new ResponseEntity<>("Ya existe una estación con ese nombre.", HttpStatus.BAD_REQUEST);
        }

        Estacion nuevaEstacion = estacionRepository.save(estacion);
        // Devuelve un DTO
        return new ResponseEntity<>(new EstacionDTO(nuevaEstacion), HttpStatus.CREATED);
    }

    // DELETE /api/estaciones/{id}: Borrado Lógico (Solo ADMIN)
    @DeleteMapping("/estaciones/{id}")
    @Transactional
    public ResponseEntity<Object> eliminarEstacionLogico(
            @PathVariable Integer id
    ) {

        /*
         * Bloquear la estación para que ninguna bicicleta pueda
         * ingresar mientras se está comprobando y eliminando.
         */
        Optional<Estacion> estacionOptional = estacionRepository
                .buscarActivaPorIdConBloqueo(id);

        if (estacionOptional.isEmpty()) {
            return new ResponseEntity<>(
                    "La estación con ID "
                            + id
                            + " no existe o está inactiva.",
                    HttpStatus.NOT_FOUND
            );
        }

        Estacion estacion = estacionOptional.get();

        // Contar únicamente bicicletas físicas no eliminadas
        long bicicletasFisicas = bicicletaRepository
                .countByUbicacionActualAndBorradoBiciFalse(
                        estacion
                );

        if (bicicletasFisicas > 0) {
            return new ResponseEntity<>(
                    "No se puede eliminar la estación porque contiene "
                            + bicicletasFisicas
                            + " bicicletas. "
                            + "Primero debe moverlas a otra estación.",
                    HttpStatus.CONFLICT
            );
        }

        estacion.setBorradoEstacion(true);
        estacionRepository.save(estacion);

        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    // PUT /api/estaciones/{id}: Actualizar estación (Solo ADMIN)
    @PutMapping("/estaciones/{id}")
    @Transactional
    public ResponseEntity<Object> actualizarEstacion(
            @PathVariable Integer id,
            @Valid @RequestBody Estacion estacionDetalles
    ) {

        // Buscar y bloquear la estación durante la modificación
        Optional<Estacion> estacionOpt = estacionRepository
                .buscarActivaPorIdConBloqueo(id);

        if (estacionOpt.isEmpty()) {
            return new ResponseEntity<>(
                    "La estación no existe o está inactiva.",
                    HttpStatus.NOT_FOUND
            );
        }

        Estacion estacionExistente = estacionOpt.get();

        // Contar las bicicletas físicas actuales
        long bicicletasFisicas = bicicletaRepository
                .countByUbicacionActualAndBorradoBiciFalse(
                        estacionExistente
                );

        int nuevaCapacidad =
                estacionDetalles.getCapacidad();

        /*
         * No permitir que la capacidad quede por debajo
         * de la ocupación actual.
         */
        if (nuevaCapacidad < bicicletasFisicas) {
            return new ResponseEntity<>(
                    "No se puede reducir la capacidad a "
                            + nuevaCapacidad
                            + ". La estación contiene actualmente "
                            + bicicletasFisicas
                            + " bicicletas.",
                    HttpStatus.CONFLICT
            );
        }

        if (estacionDetalles.getNombre() != null) {
            estacionExistente.setNombre(
                    estacionDetalles.getNombre()
            );
        }

        if (estacionDetalles.getDireccion() != null) {
            estacionExistente.setDireccion(
                    estacionDetalles.getDireccion()
            );
        }

        estacionExistente.setCapacidad(nuevaCapacidad);

        if (estacionDetalles.getLatitud() != null) {
            estacionExistente.setLatitud(
                    estacionDetalles.getLatitud()
            );
        }

        if (estacionDetalles.getLongitud() != null) {
            estacionExistente.setLongitud(
                    estacionDetalles.getLongitud()
            );
        }

        Estacion estacionActualizada =
                estacionRepository.save(estacionExistente);

        return ResponseEntity.ok(
                new EstacionDTO(estacionActualizada)
        );
    }
}
