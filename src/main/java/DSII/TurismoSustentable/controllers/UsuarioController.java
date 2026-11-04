package DSII.TurismoSustentable.controllers;

import DSII.TurismoSustentable.dto.UsuarioDTO;
import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.*;
import org.springframework.dao.DataIntegrityViolationException;
import java.security.Principal;
import DSII.TurismoSustentable.services.CorreoService;
import DSII.TurismoSustentable.dto.ActualizarUsuarioDTO;
import DSII.TurismoSustentable.services.UsuarioService;
import org.springframework.dao.OptimisticLockingFailureException;
import DSII.TurismoSustentable.dto.RegistroUsuarioDTO;
import DSII.TurismoSustentable.services.RegistroUsuarioService;

import javax.persistence.EntityNotFoundException;
import javax.persistence.OptimisticLockException;
import javax.validation.ConstraintViolationException;

import javax.validation.Valid;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api")
public class UsuarioController {

    private final UsuarioRepository usuarioRepository;
    private final CorreoService correoService;
    private final UsuarioService usuarioService;
    private final RegistroUsuarioService registroUsuarioService;

    public UsuarioController(
            UsuarioRepository usuarioRepository,
            CorreoService correoService,
            UsuarioService usuarioService,
            RegistroUsuarioService registroUsuarioService
    ) {
        this.usuarioRepository = usuarioRepository;
        this.correoService = correoService;
        this.usuarioService = usuarioService;
        this.registroUsuarioService = registroUsuarioService;
    }

    @GetMapping("/usuarios")
    public List<UsuarioDTO> getUsuarios(){
        // metodo que filtra por activo
        return usuarioRepository.buscarActivosConDatosYRoles()
                .stream()
                .map(UsuarioDTO:: new)
                .collect(Collectors.toList());
    }

    @GetMapping("/usuarios/{id}")
    public ResponseEntity<UsuarioDTO> getUsuarioPorId(@PathVariable Integer id) {
        Optional<Usuario> usuarioOpt = usuarioRepository.buscarPorIdConDatosYRoles(id);

        // Verificar el ID y devolver 404
        if (usuarioOpt.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        Usuario usuario = usuarioOpt.get();

        // Filtrado por activo/inactivo
        if (!usuario.isActivo()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }

        // Devolver si está activo
        return ResponseEntity.ok(new UsuarioDTO(usuario)); // Devuelve 200 OK con el DTO
    }

    // DEVUELVE EL NOMBRE DEL USUARIO ACTUAL
    @GetMapping("/usuarios/actual")
    public ResponseEntity<UsuarioDTO> getUsuarioActual(Principal principal) {

        // Spring Security inyecta el objeto Principal (que contiene el email)
        String email = principal.getName();

        Usuario usuario = usuarioRepository.buscarPorEmailConDatosYRoles(email)
                .orElseThrow(() -> new UsernameNotFoundException("Usuario no encontrado."));

        return ResponseEntity.ok(new UsuarioDTO(usuario));
    }

    @PostMapping("/usuarios")
    public ResponseEntity<Object> createUsuario(
            @Valid @RequestBody RegistroUsuarioDTO datos
    ) {
        UsuarioDTO nuevoUsuario;

        try {
            nuevoUsuario = registroUsuarioService.registrarUsuario(datos);

        } catch (ConstraintViolationException e) {
            String mensaje = e.getConstraintViolations().stream()
                    .map(v -> v.getMessage())
                    .distinct()
                    .sorted()
                    .collect(Collectors.joining(" "));

            return ResponseEntity.badRequest().body(mensaje);

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());

        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(e.getMessage());

        } catch (DataIntegrityViolationException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(
                            "Los datos entran en conflicto con otro registro. " +
                                    "Revisá el email, el nickname y el documento."
                    );
        }

        // El servicio ya confirmó el registro antes de solicitar el correo.
        correoService.enviarBienvenida(
                nuevoUsuario.getEmail(),
                nuevoUsuario.getNombre()
        );

        return ResponseEntity.status(HttpStatus.CREATED)
                .body(nuevoUsuario);
    }

    @DeleteMapping("/usuarios/{id}")
    public ResponseEntity<Object> eliminarUsuarioLogico(@PathVariable Integer id) {

        Optional<Usuario> usuarioOptional = usuarioRepository.buscarPorIdConDatosYRoles(id); // Buscar el usuario

        if (usuarioOptional.isEmpty()) { // Verificar existencia
            // Si no existe devuelve 404
            return new ResponseEntity<>("El usuario con ID " + id + " no existe.", HttpStatus.NOT_FOUND);
        }

        Usuario usuario = usuarioOptional.get();

        // --- VALIDACIÓN DE ROL ---
        boolean esAdministrador = usuario.getUsuarioRoles().stream()
                .anyMatch(asignacion ->
                        "ADMIN".equals(asignacion.getRol().getCodigo())
                );

        if (esAdministrador) {
            return new ResponseEntity<>(
                    "No se puede eliminar a un usuario Administrador.",
                    HttpStatus.FORBIDDEN // 403 Prohibido
            );
        }

        // borrado logico
        if (!usuario.isActivo()) {
            // si ya estaba inactivo, devuelve un error 400
            return new ResponseEntity<>("El usuario ya se encuentra inactivo.", HttpStatus.BAD_REQUEST);
        }
        usuario.setActivo(false);
        usuarioRepository.save(usuario);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    @PutMapping("/usuarios/{id}")
    public ResponseEntity<Object> actualizarUsuario(
            @PathVariable Integer id,
            @Valid @RequestBody ActualizarUsuarioDTO datos
    ) {
        try {
            return ResponseEntity.ok(
                    usuarioService.actualizarUsuario(id, datos)
            );

        } catch (ConstraintViolationException e) {
            String mensaje = e.getConstraintViolations().stream()
                    .map(v -> v.getMessage())
                    .distinct()
                    .sorted()
                    .collect(Collectors.joining(" "));

            return ResponseEntity.badRequest().body(mensaje);

        } catch (EntityNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(e.getMessage());

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(e.getMessage());

        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(e.getMessage());

        } catch (OptimisticLockingFailureException
                 | OptimisticLockException e) {

            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(
                            "El usuario fue modificado por otra operación. " +
                                    "Volvé a cargar sus datos e intentá nuevamente."
                    );

        } catch (DataIntegrityViolationException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(
                            "Los datos entran en conflicto con otro registro. " +
                                    "Revisá el email."
                    );
        }
    }
}
