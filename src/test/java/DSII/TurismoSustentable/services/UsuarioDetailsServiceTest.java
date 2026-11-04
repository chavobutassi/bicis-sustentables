package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.models.Genero;
import DSII.TurismoSustentable.models.Pais;
import DSII.TurismoSustentable.models.Persona;
import DSII.TurismoSustentable.models.Rol;
import DSII.TurismoSustentable.models.TipoDocumento;
import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.models.UsuarioRol;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.CredentialsContainer;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDate;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UsuarioDetailsServiceTest {

    private static final String EMAIL = "ana@example.com";
    private static final String HASH = "hash-simulado-para-test";

    @Mock
    private UsuarioRepository usuarioRepository;

    @InjectMocks
    private UsuarioDetailsService usuarioDetailsService;

    @Test
    void cargaCredencialesYTodosLosRolesAsignados() {
        Usuario usuario = crearUsuario();

        agregarRol(usuario, 2, "ADMIN");
        agregarRol(usuario, 3, "TECNICO");
        prepararBusqueda(usuario);

        UserDetails resultado = usuarioDetailsService
                .loadUserByUsername(" ANA@EXAMPLE.COM ");

        assertEquals(EMAIL, resultado.getUsername());
        assertEquals(HASH, resultado.getPassword());
        assertTrue(resultado.isEnabled());
        assertTrue(resultado.isAccountNonExpired());
        assertTrue(resultado.isCredentialsNonExpired());
        assertTrue(resultado.isAccountNonLocked());

        assertEquals(
                Set.of("ADMIN", "TECNICO"),
                autoridades(resultado)
        );
        assertEquals(2, resultado.getAuthorities().size());

        verify(usuarioRepository)
                .buscarPorEmailConDatosYRoles(EMAIL);
        verifyNoMoreInteractions(usuarioRepository);
    }

    @Test
    void marcaComoDeshabilitadaLaCuentaInactiva() {
        Usuario usuario = crearUsuario();
        usuario.setActivo(false);

        agregarRol(usuario, 1, "CLIENTE");
        prepararBusqueda(usuario);

        UserDetails resultado =
                usuarioDetailsService.loadUserByUsername(EMAIL);

        assertFalse(resultado.isEnabled());
    }

    @Test
    void rechazaUsuarioInexistente() {
        when(usuarioRepository.buscarPorEmailConDatosYRoles(EMAIL))
                .thenReturn(Optional.empty());

        assertThrows(
                UsernameNotFoundException.class,
                () -> usuarioDetailsService.loadUserByUsername(EMAIL)
        );
    }

    @Test
    void rechazaUsuarioSinRoles() {
        Usuario usuario = crearUsuario();
        prepararBusqueda(usuario);

        UsernameNotFoundException error = assertThrows(
                UsernameNotFoundException.class,
                () -> usuarioDetailsService.loadUserByUsername(EMAIL)
        );

        assertEquals(
                "La cuenta no tiene roles asignados.",
                error.getMessage()
        );
    }

    @Test
    void rechazaEmailNuloOVacioSinConsultarLaBase() {
        String[] invalidos = {null, "", "   "};

        for (String email : invalidos) {
            assertThrows(
                    UsernameNotFoundException.class,
                    () -> usuarioDetailsService.loadUserByUsername(email)
            );
        }

        verifyNoInteractions(usuarioRepository);
    }

    @Test
    void creaUserDetailsNuevoSinBorrarElHashDelUsuario() {
        Usuario usuario = crearUsuario();

        agregarRol(usuario, 1, "CLIENTE");
        prepararBusqueda(usuario);

        UserDetails primero =
                usuarioDetailsService.loadUserByUsername(EMAIL);

        ((CredentialsContainer) primero).eraseCredentials();

        UserDetails segundo =
                usuarioDetailsService.loadUserByUsername(EMAIL);

        assertNotSame(primero, segundo);
        assertNull(primero.getPassword());
        assertEquals(HASH, usuario.getPassword());
        assertEquals(HASH, segundo.getPassword());
        assertEquals(Set.of("CLIENTE"), autoridades(segundo));

        verify(usuarioRepository, times(2))
                .buscarPorEmailConDatosYRoles(EMAIL);
    }

    private Usuario crearUsuario() {
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
                HASH
        );

        usuario.setId(17);
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

    private Set<String> autoridades(UserDetails usuario) {
        return usuario.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.toSet());
    }
}
