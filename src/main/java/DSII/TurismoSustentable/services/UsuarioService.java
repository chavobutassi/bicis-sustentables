package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.dto.ActualizarUsuarioDTO;
import DSII.TurismoSustentable.dto.UsuarioDTO;
import DSII.TurismoSustentable.models.Genero;
import DSII.TurismoSustentable.models.Persona;
import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.repositories.GeneroRepository;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.validation.annotation.Validated;

import javax.persistence.EntityManager;
import javax.persistence.EntityNotFoundException;
import javax.persistence.LockModeType;
import javax.validation.Valid;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;

@Service
@Validated
public class UsuarioService {

    private final UsuarioRepository usuarioRepository;
    private final GeneroRepository generoRepository;
    private final EntityManager entityManager;

    public UsuarioService(
            UsuarioRepository usuarioRepository,
            GeneroRepository generoRepository,
            EntityManager entityManager
    ) {
        this.usuarioRepository = usuarioRepository;
        this.generoRepository = generoRepository;
        this.entityManager = entityManager;
    }

    @Transactional
    @PreAuthorize("hasAuthority('ADMIN')")
    public UsuarioDTO actualizarUsuario(
            @NotNull(message = "El identificador del usuario es obligatorio.")
            @Positive(message = "El identificador del usuario debe ser positivo.")
            Integer id,

            @NotNull(message = "Los datos de actualización son obligatorios.")
            @Valid ActualizarUsuarioDTO datos
    ) {

        Usuario usuario = usuarioRepository.findById(id)
                .filter(Usuario::isActivo)
                .orElseThrow(() ->
                        new EntityNotFoundException(
                                "El usuario no existe o está inactivo."
                        )
                );

        Persona persona = usuario.getPersona();

        if (persona == null) {
            throw new IllegalStateException(
                    "El usuario no tiene una persona asociada."
            );
        }

        Genero genero = generoRepository.findById(datos.getGeneroId())
                .orElseThrow(() ->
                        new IllegalArgumentException(
                                "El género seleccionado no existe."
                        )
                );

        boolean emailOcupado =
                usuarioRepository.existsByEmailIgnoreCaseAndIdNot(
                        datos.getEmail(),
                        id
                );

        if (emailOcupado) {
            throw new IllegalStateException(
                    "Ya existe otro usuario registrado con ese email."
            );
        }

        // Controlar concurrencia incluso si solo cambia Persona.
        entityManager.lock(
                usuario,
                LockModeType.OPTIMISTIC_FORCE_INCREMENT
        );

        // El email pertenece a la cuenta.
        if (!usuario.getEmail().equals(datos.getEmail())) {
            usuario.setEmail(datos.getEmail());

            // Invalidar enlaces anteriores si cambia el email.
            usuario.setTokenRecuperacion(null);
            usuario.setVencimientoTokenRecuperacion(null);
        }

        // Los datos personales pertenecen a Persona.
        persona.setNombre(datos.getNombre());
        persona.setApellido(datos.getApellido());
        persona.setFechaNacimiento(datos.getFechaNacimiento());
        persona.setGenero(genero);

        // Persistir los cambios de las entidades administradas.
        usuarioRepository.flush();

        return new UsuarioDTO(usuario);
    }
}