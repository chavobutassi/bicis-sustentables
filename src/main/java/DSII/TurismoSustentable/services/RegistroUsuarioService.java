package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.dto.RegistroUsuarioDTO;
import DSII.TurismoSustentable.dto.UsuarioDTO;
import DSII.TurismoSustentable.models.Genero;
import DSII.TurismoSustentable.models.Pais;
import DSII.TurismoSustentable.models.Persona;
import DSII.TurismoSustentable.models.Rol;
import DSII.TurismoSustentable.models.TipoDocumento;
import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.repositories.GeneroRepository;
import DSII.TurismoSustentable.repositories.PaisRepository;
import DSII.TurismoSustentable.repositories.PersonaRepository;
import DSII.TurismoSustentable.repositories.TipoDocumentoRepository;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.validation.annotation.Validated;

import javax.validation.Valid;
import javax.validation.constraints.NotNull;

@Service
@Validated
public class RegistroUsuarioService {

    private final UsuarioRepository usuarioRepository;
    private final PersonaRepository personaRepository;
    private final GeneroRepository generoRepository;
    private final TipoDocumentoRepository tipoDocumentoRepository;
    private final PaisRepository paisRepository;
    private final PasswordEncoder passwordEncoder;

    public RegistroUsuarioService(
            UsuarioRepository usuarioRepository,
            PersonaRepository personaRepository,
            GeneroRepository generoRepository,
            TipoDocumentoRepository tipoDocumentoRepository,
            PaisRepository paisRepository,
            PasswordEncoder passwordEncoder
    ) {
        this.usuarioRepository = usuarioRepository;
        this.personaRepository = personaRepository;
        this.generoRepository = generoRepository;
        this.tipoDocumentoRepository = tipoDocumentoRepository;
        this.paisRepository = paisRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional
    public UsuarioDTO registrarUsuario(
            @NotNull(message = "Los datos de registro son obligatorios.")
            @Valid RegistroUsuarioDTO datos
    ) {

        // Comprobar identificadores, incluyendo cuentas inactivas.
        if (usuarioRepository.existsByEmailIgnoreCase(datos.getEmail())) {
            throw new IllegalStateException(
                    "Ya existe un usuario registrado con ese email."
            );
        }

        if (usuarioRepository.existsByNicknameIgnoreCase(datos.getNickname())) {
            throw new IllegalStateException(
                    "El nickname ya está en uso."
            );
        }

        // Buscar los catálogos reales, no aceptar objetos del formulario.
        Genero genero = generoRepository.findById(datos.getGeneroId())
                .orElseThrow(() -> new IllegalArgumentException(
                        "El género seleccionado no existe."
                ));

        TipoDocumento tipoDocumento = tipoDocumentoRepository
                .findById(datos.getTipoDocumentoId())
                .orElseThrow(() -> new IllegalArgumentException(
                        "El tipo de documento seleccionado no existe."
                ));

        Pais paisEmisor = paisRepository.findById(datos.getPaisEmisorId())
                .orElseThrow(() -> new IllegalArgumentException(
                        "El país emisor seleccionado no existe."
                ));

        boolean documentoOcupado = personaRepository
                .existsByTipoDocumento_IdAndPaisEmisor_IdAndNumeroDocumento(
                        datos.getTipoDocumentoId(),
                        datos.getPaisEmisorId(),
                        datos.getNumeroDocumento()
                );

        if (documentoOcupado) {
            throw new IllegalStateException(
                    "Ya existe una persona registrada con ese tipo, " +
                            "país emisor y número de documento."
            );
        }

        // La contraseña se hashea antes de asignarla a Usuario.
        String passwordHasheada = passwordEncoder.encode(
                datos.getPassword()
        );

        Persona persona = new Persona(
                datos.getNombre(),
                datos.getApellido(),
                datos.getFechaNacimiento(),
                genero,
                tipoDocumento,
                datos.getNumeroDocumento(),
                paisEmisor
        );

        Persona personaGuardada = personaRepository.save(persona);

        Usuario usuario = new Usuario(
                personaGuardada,
                datos.getNickname(),
                datos.getEmail(),
                passwordHasheada
        );

        // El registro público nunca permite elegir privilegios.
        usuario.setRol(Rol.CLIENTE);
        usuario.setActivo(true);

        Usuario usuarioGuardado = usuarioRepository.saveAndFlush(usuario);

        return new UsuarioDTO(usuarioGuardado);
    }
}