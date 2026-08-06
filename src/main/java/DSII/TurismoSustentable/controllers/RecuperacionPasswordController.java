package DSII.TurismoSustentable.controllers;

import DSII.TurismoSustentable.services.RecuperacionPasswordService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/password")
public class RecuperacionPasswordController {

    private final RecuperacionPasswordService
            recuperacionPasswordService;

    public RecuperacionPasswordController(
            RecuperacionPasswordService
                    recuperacionPasswordService
    ) {
        this.recuperacionPasswordService =
                recuperacionPasswordService;
    }

    @PostMapping("/solicitar")
    public ResponseEntity<String> solicitarRecuperacion(
            @RequestBody(required = false)
            Map<String, String> datos
    ) {

        String email = datos != null
                ? datos.get("email")
                : null;

        recuperacionPasswordService
                .solicitarRecuperacion(email);

        /*
         * Siempre se devuelve el mismo mensaje para no revelar
         * si una dirección está registrada.
         */
        return ResponseEntity.ok(
                "Si el correo está registrado, "
                        + "recibirás las instrucciones."
        );
    }

    @PostMapping("/restablecer")
    public ResponseEntity<String> restablecerPassword(
            @RequestBody(required = false)
            Map<String, String> datos
    ) {

        if (datos == null) {
            return new ResponseEntity<>(
                    "Debe proporcionar el token y la nueva clave.",
                    HttpStatus.BAD_REQUEST
            );
        }

        try {
            recuperacionPasswordService
                    .restablecerPassword(
                            datos.get("token"),
                            datos.get("password")
                    );

            return ResponseEntity.ok(
                    "La contraseña fue actualizada correctamente."
            );

        } catch (IllegalArgumentException e) {
            return new ResponseEntity<>(
                    e.getMessage(),
                    HttpStatus.BAD_REQUEST
            );
        }
    }
}