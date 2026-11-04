package DSII.TurismoSustentable.controllers;

import DSII.TurismoSustentable.models.Genero;
import DSII.TurismoSustentable.models.Pais;
import DSII.TurismoSustentable.models.Persona;
import DSII.TurismoSustentable.models.Rol;
import DSII.TurismoSustentable.models.TipoDocumento;
import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.models.UsuarioRol;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import DSII.TurismoSustentable.services.CorreoService;
import DSII.TurismoSustentable.services.RegistroUsuarioService;
import DSII.TurismoSustentable.services.UsuarioService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDate;
import java.util.HashSet;
import java.util.Optional;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UsuarioControllerTest {

    private static final int ID = 17;

    @Mock
    private UsuarioRepository usuarioRepository;

    @Mock
    private CorreoService correoService;

    @Mock
    private UsuarioService usuarioService;

    @Mock
    private RegistroUsuarioService registroUsuarioService;

    @InjectMocks
    private UsuarioController usuarioController;

    @Test
    void protegeUsuarioConRolAdministrador() {
        comprobarAdministradorProtegido(
                crearUsuario("ADMIN")
        );
    }

    @Test
    void protegeAdministradorAunqueTambienSeaTecnico() {
        comprobarAdministradorProtegido(
                crearUsuario("TECNICO", "ADMIN")
        );
    }

    @Test
    void inactivaClienteSinBorrarSusDatos() {
        comprobarBajaLogica(
                crearUsuario("CLIENTE")
        );
    }

    @Test
    void inactivaTecnicoSinBorrarSusDatos() {
        comprobarBajaLogica(
                crearUsuario("TECNICO")
        );
    }

    @Test
    void rechazaUsuarioInexistente() {
        when(usuarioRepository.buscarPorIdConDatosYRoles(ID))
                .thenReturn(Optional.empty());

        ResponseEntity<Object> respuesta =
                usuarioController.eliminarUsuarioLogico(ID);

        assertEquals(HttpStatus.NOT_FOUND, respuesta.getStatusCode());
        assertEquals(
                "El usuario con ID " + ID + " no existe.",
                respuesta.getBody()
        );

        verify(usuarioRepository).buscarPorIdConDatosYRoles(ID);
        verifyNoMoreInteractions(usuarioRepository);
    }

    @Test
    void rechazaUsuarioYaInactivo() {
        Usuario usuario = crearUsuario("CLIENTE");
        usuario.setActivo(false);
        prepararBusqueda(usuario);

        ResponseEntity<Object> respuesta =
                usuarioController.eliminarUsuarioLogico(ID);

        assertEquals(HttpStatus.BAD_REQUEST, respuesta.getStatusCode());
        assertEquals(
                "El usuario ya se encuentra inactivo.",
                respuesta.getBody()
        );
        assertFalse(usuario.isActivo());

        verify(usuarioRepository).buscarPorIdConDatosYRoles(ID);
        verifyNoMoreInteractions(usuarioRepository);
    }

    private void comprobarAdministradorProtegido(Usuario usuario) {
        prepararBusqueda(usuario);

        ResponseEntity<Object> respuesta =
                usuarioController.eliminarUsuarioLogico(ID);

        assertEquals(HttpStatus.FORBIDDEN, respuesta.getStatusCode());
        assertEquals(
                "No se puede eliminar a un usuario Administrador.",
                respuesta.getBody()
        );
        assertTrue(usuario.isActivo());

        verify(usuarioRepository).buscarPorIdConDatosYRoles(ID);
        verifyNoMoreInteractions(usuarioRepository);
    }

    private void comprobarBajaLogica(Usuario usuario) {
        Persona personaAnterior = usuario.getPersona();

        Set<UsuarioRol> rolesAnteriores =
                new HashSet<>(usuario.getUsuarioRoles());

        prepararBusqueda(usuario);

        ResponseEntity<Object> respuesta =
                usuarioController.eliminarUsuarioLogico(ID);

        assertEquals(HttpStatus.NO_CONTENT, respuesta.getStatusCode());
        assertNull(respuesta.getBody());
        assertFalse(usuario.isActivo());

        // La baja no elimina estos datos ni sus relaciones.
        assertEquals(ID, usuario.getId());
        assertEquals("ana.perez", usuario.getNickname());
        assertEquals("ana@example.com", usuario.getEmail());
        assertEquals("hash-simulado-para-test", usuario.getPassword());

        assertSame(personaAnterior, usuario.getPersona());
        assertEquals("Ana", usuario.getPersona().getNombre());
        assertEquals("Perez", usuario.getPersona().getApellido());
        assertEquals(
                "00123456",
                usuario.getPersona().getNumeroDocumento()
        );
        assertEquals(rolesAnteriores, usuario.getUsuarioRoles());

        verify(usuarioRepository).buscarPorIdConDatosYRoles(ID);
        verify(usuarioRepository).save(same(usuario));

        // Cualquier llamada adicional, incluido delete, haría fallar.
        verifyNoMoreInteractions(usuarioRepository);
    }

    private void prepararBusqueda(Usuario usuario) {
        when(usuarioRepository.buscarPorIdConDatosYRoles(ID))
                .thenReturn(Optional.of(usuario));
    }

    private Usuario crearUsuario(String... codigosRol) {
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
                "ana@example.com",
                "hash-simulado-para-test"
        );

        usuario.setId(ID);

        // Las decisiones deben usar UsuarioRol, no el enum legado.
        for (int i = 0; i < codigosRol.length; i++) {
            Rol rol = new Rol(codigosRol[i]);
            ReflectionTestUtils.setField(rol, "id", i + 1);

            usuario.getUsuarioRoles().add(
                    new UsuarioRol(usuario, rol)
            );
        }

        return usuario;
    }
}
