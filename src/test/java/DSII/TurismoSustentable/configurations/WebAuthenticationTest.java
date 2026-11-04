package DSII.TurismoSustentable.configurations;

import DSII.TurismoSustentable.models.Genero;
import DSII.TurismoSustentable.models.Pais;
import DSII.TurismoSustentable.models.Persona;
import DSII.TurismoSustentable.models.Rol;
import DSII.TurismoSustentable.models.TipoDocumento;
import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.models.UsuarioRol;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import DSII.TurismoSustentable.services.UsuarioDetailsService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.DisabledException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.config.annotation.ObjectPostProcessor;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDate;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class WebAuthenticationTest {

    private static final String EMAIL = "ana@example.com";
    private static final String PASSWORD = "Clave#123";

    @Mock
    private UsuarioRepository usuarioRepository;

    private PasswordEncoder passwordEncoder;
    private AuthenticationManager authenticationManager;

    @BeforeEach
    void prepararAutenticacion() throws Exception {
        passwordEncoder = new SecurityConfig().passwordEncoder();

        UsuarioDetailsService detailsService =
                new UsuarioDetailsService(usuarioRepository);

        ObjectPostProcessor<Object> postProcessor =
                new ObjectPostProcessor<Object>() {
                    @Override
                    public <O> O postProcess(O object) {
                        return object;
                    }
                };

        AuthenticationManagerBuilder builder =
                new AuthenticationManagerBuilder(postProcessor);

        new WebAuthentication(detailsService, passwordEncoder)
                .init(builder);

        authenticationManager = builder.build();
    }

    @Test
    void autenticaConPasswordCorrectaYTodosLosRoles() {
        Usuario usuario = crearUsuario(true);

        agregarRol(usuario, 2, "ADMIN");
        agregarRol(usuario, 3, "TECNICO");
        prepararBusqueda(usuario);

        String hashGuardado = usuario.getPassword();

        Authentication resultado = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        " ANA@EXAMPLE.COM ",
                        PASSWORD
                )
        );

        assertTrue(resultado.isAuthenticated());
        assertEquals(EMAIL, resultado.getName());

        assertEquals(
                Set.of("ADMIN", "TECNICO"),
                resultado.getAuthorities().stream()
                        .map(GrantedAuthority::getAuthority)
                        .collect(Collectors.toSet())
        );
        assertEquals(2, resultado.getAuthorities().size());

        assertNull(resultado.getCredentials());
        assertEquals(hashGuardado, usuario.getPassword());
        assertNotEquals(PASSWORD, usuario.getPassword());

        verify(usuarioRepository)
                .buscarPorEmailConDatosYRoles(EMAIL);
    }

    @Test
    void rechazaPasswordIncorrecta() {
        Usuario usuario = crearUsuario(true);

        agregarRol(usuario, 1, "CLIENTE");
        prepararBusqueda(usuario);

        assertThrows(
                BadCredentialsException.class,
                () -> authenticationManager.authenticate(
                        new UsernamePasswordAuthenticationToken(
                                EMAIL,
                                "OtraClave#123"
                        )
                )
        );
    }

    @Test
    void rechazaCuentaInactivaConPasswordCorrecta() {
        Usuario usuario = crearUsuario(false);

        agregarRol(usuario, 1, "CLIENTE");
        prepararBusqueda(usuario);

        assertThrows(
                DisabledException.class,
                () -> authenticationManager.authenticate(
                        new UsernamePasswordAuthenticationToken(
                                EMAIL,
                                PASSWORD
                        )
                )
        );
    }

    private Usuario crearUsuario(boolean activo) {
        Persona persona = new Persona(
                "Ana",
                "Perez",
                LocalDate.of(1995, 5, 20),
                new Genero("FEMENINO"),
                new TipoDocumento(
                        "DNI",
                        "Documento Nacional de Identidad"
                ),
                "00123456",
                new Pais("AR", "Argentina")
        );

        Usuario usuario = new Usuario(
                persona,
                "ana.perez",
                EMAIL,
                passwordEncoder.encode(PASSWORD)
        );

        usuario.setId(17);
        usuario.setActivo(activo);

        return usuario;
    }

    private void agregarRol(
            Usuario usuario,
            int idRol,
            String codigo
    ) {
        Rol rol = new Rol(codigo);
        ReflectionTestUtils.setField(rol, "id", idRol);

        usuario.getUsuarioRoles().add(
                new UsuarioRol(usuario, rol)
        );
    }

    private void prepararBusqueda(Usuario usuario) {
        when(usuarioRepository.buscarPorEmailConDatosYRoles(EMAIL))
                .thenReturn(Optional.of(usuario));
    }
}
