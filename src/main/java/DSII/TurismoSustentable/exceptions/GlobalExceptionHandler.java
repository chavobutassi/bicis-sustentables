package DSII.TurismoSustentable.exceptions;

import org.springframework.http.HttpStatus;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors; // <-- Asegúrate de tener esta importación

// Esta anotación hace que esta clase escuche errores en todos los @Controllers
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ResponseStatus(HttpStatus.BAD_REQUEST)
    @ExceptionHandler(MethodArgumentNotValidException.class)
    // Cambiamos el tipo de retorno para incluir más información del error
    public Map<String, Object> handleValidationExceptions(
            MethodArgumentNotValidException ex) {

        Map<String, Object> response = new HashMap<>();
        List<String> errors = new ArrayList<>();

        // Iteramos sobre todos los errores que Spring encontró en los campos
        ex.getBindingResult().getAllErrors().forEach((error) -> {

            // Obtenemos el nombre del campo (ej: "email")
            String fieldName = ((FieldError) error).getField();

            // Obtenemos el mensaje de la anotación (@Email, @Size, @Pattern, etc.)
            String errorMessage = error.getDefaultMessage();

            // Formateamos el mensaje para el cliente (ej: "email: Debe ser una dirección...")
            errors.add(fieldName + ": " + errorMessage);
        });

        // Añadimos información general del error
        response.put("timestamp", LocalDateTime.now().toString());
        response.put("status", HttpStatus.BAD_REQUEST.value());
        response.put("error", "Validation Error");
        response.put("validationErrors", errors); // <-- CLAVE: Lista de todos los errores

        return response; // Spring convertirá este Map en un JSON
    }
}