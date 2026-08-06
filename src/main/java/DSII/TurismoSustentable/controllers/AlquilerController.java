package DSII.TurismoSustentable.controllers;

import DSII.TurismoSustentable.dto.AlquilerDTO;
import DSII.TurismoSustentable.dto.AlquilerRequestDTO;
import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.repositories.AlquilerRepository;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import DSII.TurismoSustentable.services.AlquilerService; // <-- 1. IMPORTA EL SERVICIO
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.AccessDeniedException;

import java.math.BigDecimal;
import java.security.Principal;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api")
public class AlquilerController {

    // --- Inyectamos el Servicio ---
    @Autowired
    private AlquilerService alquilerService;
    @Autowired
    private AlquilerRepository alquilerRepository;
    @Autowired
    private UsuarioRepository usuarioRepository;

    @GetMapping("/alquileres")
    public List<AlquilerDTO> getAlquiler(Principal principal) {
        Usuario usuario = usuarioRepository.findByEmail(principal.getName())
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado o sesión expirada"));
        return alquilerRepository.findByUsuarioAndBorradoAlquilerFalse(usuario)
                .stream()
                .map(AlquilerDTO:: new)
                .collect(Collectors.toList());
    }

    /**
     * CREAR ALQUILER
     * Ahora solo llama al servicio y maneja la respuesta.
     */
    @PostMapping("/alquileres")
    public ResponseEntity<Object> crearAlquiler(@RequestBody AlquilerRequestDTO alquilerRequest) {
        try {
            // 2. Llama al servicio (que es transaccional)
            AlquilerDTO alquilerGuardado = alquilerService.crearAlquiler(alquilerRequest);

            // 3. Devuelve la respuesta OK
            return new ResponseEntity<>(alquilerGuardado, HttpStatus.CREATED);

        } catch (Exception e) {
            // 4. Si el servicio lanzó un error, devuélvelo como 400 Bad Request
            return new ResponseEntity<>(e.getMessage(), HttpStatus.BAD_REQUEST);
        }
    }

    // BORRAR ALQUILER
    @DeleteMapping("/alquileres/{id}")
    public ResponseEntity<Object> borrarAlquilerLogico(
            @PathVariable Integer id
    ) {
        try {
            alquilerService.borrarAlquilerLogico(id);

            return new ResponseEntity<>(HttpStatus.NO_CONTENT);

        } catch (IllegalStateException e) {
            // El alquiler todavía está en curso
            return new ResponseEntity<>(
                    e.getMessage(),
                    HttpStatus.CONFLICT
            );

        } catch (Exception e) {
            // El alquiler no existe
            return new ResponseEntity<>(
                    e.getMessage(),
                    HttpStatus.NOT_FOUND
            );
        }
    }

    // FINALIZAR ALQUILER
    @PatchMapping("/alquileres/finalizar/{id}")
    public ResponseEntity<Object> finalizarAlquiler(
            @PathVariable Integer id,
            @RequestBody Map<String, String> payload) {

        try {
            String ubicacionDestino = payload.get("ubicacionDestino");

            if (ubicacionDestino == null
                    || ubicacionDestino.trim().isEmpty()) {

                return new ResponseEntity<>(
                        "Debe especificar la estación de destino.",
                        HttpStatus.BAD_REQUEST
                );
            }

            AlquilerDTO alquilerFinalizado =
                    alquilerService.finalizarAlquiler(
                            id,
                            ubicacionDestino
                    );

            return ResponseEntity.ok(alquilerFinalizado);

        } catch (AccessDeniedException e) {
            // Intentó finalizar el alquiler de otro usuario
            return new ResponseEntity<>(
                    e.getMessage(),
                    HttpStatus.FORBIDDEN
            );

        } catch (IllegalStateException e) {
            // Alquiler finalizado, cancelado o estación llena
            return new ResponseEntity<>(
                    e.getMessage(),
                    HttpStatus.CONFLICT
            );

        } catch (IllegalArgumentException e) {
            // Estación inexistente o datos inválidos
            return new ResponseEntity<>(
                    e.getMessage(),
                    HttpStatus.BAD_REQUEST
            );

        } catch (Exception e) {
            // Cualquier otro error no previsto
            return new ResponseEntity<>(
                    e.getMessage(),
                    HttpStatus.BAD_REQUEST
            );
        }
    }

    /**
     * OBTENER COTIZACIÓN DEL DÓLAR
     * El frontend llama a este endpoint para mostrar precios estimativos,
     * evitando consumir APIs externas desde el navegador.
     */
    @GetMapping("/cotizacion")
    public ResponseEntity<BigDecimal> getCotizacion() {
        // Llama al servicio centralizado y devuelve el número
        BigDecimal cotizacion = alquilerService.obtenerCotizacionDolar();
        return ResponseEntity.ok(cotizacion);
    }

}