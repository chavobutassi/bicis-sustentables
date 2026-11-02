package DSII.TurismoSustentable.controllers;

import DSII.TurismoSustentable.dto.UsuarioDTO;
import DSII.TurismoSustentable.models.Rol;
import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;
import org.springframework.dao.DataIntegrityViolationException;
import java.security.Principal;
import DSII.TurismoSustentable.services.CorreoService;
import DSII.TurismoSustentable.dto.ActualizarUsuarioDTO;
import DSII.TurismoSustentable.services.UsuarioService;
import org.springframework.dao.OptimisticLockingFailureException;

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
    private final PasswordEncoder passwordEncoder;
    private final CorreoService correoService;
    private final UsuarioService usuarioService;

    public UsuarioController(
            UsuarioRepository usuarioRepository,
            PasswordEncoder passwordEncoder,
            CorreoService correoService,
            UsuarioService usuarioService
    ) {
        this.usuarioRepository = usuarioRepository;
        this.passwordEncoder = passwordEncoder;
        this.correoService = correoService;
        this.usuarioService = usuarioService;
    }

    @GetMapping("/usuarios")
    public List<UsuarioDTO> getUsuarios(){
        // metodo que filtra por activo
        return usuarioRepository.findByActivoTrue()
                .stream()
                .map(UsuarioDTO:: new)
                .collect(Collectors.toList());
    }

    @GetMapping("/usuarios/{id}")
    public ResponseEntity<UsuarioDTO> getUsuarioPorId(@PathVariable Integer id) {
        Optional<Usuario> usuarioOpt = usuarioRepository.findById(id);

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

        Usuario usuario = usuarioRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("Usuario no encontrado."));

        return ResponseEntity.ok(new UsuarioDTO(usuario));
    }

    @PostMapping("/usuarios")
    public ResponseEntity<Object> createUsuario(
            @Valid @RequestBody Usuario usuario
    ) {

        String emailNormalizado = usuario.getEmail();

        // Comprobación antes de guardar
        if (usuarioRepository.existsByEmailIgnoreCase(
                emailNormalizado
        )) {
            return new ResponseEntity<>(
                    "Ya existe un usuario registrado con ese email.",
                    HttpStatus.CONFLICT
            );
        }

        // Cifrar la contraseña
        String rawPassword = usuario.getPassword();
        String encodedPassword = passwordEncoder.encode(rawPassword);
        usuario.setPassword(encodedPassword);

        // El registro público siempre crea clientes
        usuario.setRol(Rol.CLIENTE);
        usuario.setActivo(true);

        try {
            /*
             * saveAndFlush fuerza la inserción inmediatamente.
             * Esto permite capturar aquí una colisión simultánea.
             */
            Usuario nuevoUsuario =
                    usuarioRepository.saveAndFlush(usuario);

            correoService.enviarBienvenida(
                    nuevoUsuario.getEmail(),
                    nuevoUsuario.getPersona().getNombre()
            );

            return new ResponseEntity<>(
                    new UsuarioDTO(nuevoUsuario),
                    HttpStatus.CREATED
            );

        } catch (DataIntegrityViolationException e) {
            /*
             * Protección para dos registros simultáneos:
             * ambos podrían superar existsByEmailIgnoreCase(),
             * pero la restricción UNIQUE rechazará al segundo.
             */
            return new ResponseEntity<>(
                    "Ya existe un usuario registrado con ese email.",
                    HttpStatus.CONFLICT
            );
        }
    }

    @DeleteMapping("/usuarios/{id}")
    public ResponseEntity<Object> eliminarUsuarioLogico(@PathVariable Integer id) {

        Optional<Usuario> usuarioOptional = usuarioRepository.findById(id); // Buscar el usuario

        if (usuarioOptional.isEmpty()) { // Verificar existencia
            // Si no existe devuelve 404
            return new ResponseEntity<>("El usuario con ID " + id + " no existe.", HttpStatus.NOT_FOUND);
        }

        Usuario usuario = usuarioOptional.get();

        // --- VALIDACIÓN DE ROL ---
        if (usuario.getRol() == Rol.ADMIN) {
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
