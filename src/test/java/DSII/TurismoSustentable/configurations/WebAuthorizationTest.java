package DSII.TurismoSustentable.configurations;

import DSII.TurismoSustentable.controllers.UsuarioController;
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
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = UsuarioController.class)
@ContextConfiguration(classes = {
        UsuarioController.class,
        WebAuthorization.class
})
class WebAuthorizationTest {

    private static final String EMAIL = "ana@example.com";

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UsuarioRepository usuarioRepository;

    @MockBean
    private CorreoService correoService;

    @MockBean
    private UsuarioService usuarioService;

    @MockBean
    private RegistroUsuarioService registroUsuarioService;

    // El login se prueba aparte; aquí simulamos usuarios autenticados.
    @MockBean
    private UserDetailsService userDetailsService;

    @Test
    @WithMockUser(username = EMAIL, authorities = "TECNICO")
    void tecnicoPuedeConsultarSusDatos() throws Exception {
        comprobarPerfilPropio("TECNICO");
    }

    @Test
    @WithMockUser(username = EMAIL, authorities = "CLIENTE")
    void clientePuedeConsultarSusDatos() throws Exception {
        comprobarPerfilPropio("CLIENTE");
    }

    @Test
    @WithMockUser(username = EMAIL, authorities = "ADMIN")
    void administradorPuedeConsultarSusDatos() throws Exception {
        comprobarPerfilPropio("ADMIN");
    }

    @Test
    void exigeSesionParaConsultarDatosPropios() throws Exception {
        mockMvc.perform(get("/api/usuarios/actual"))
                .andExpect(status().isUnauthorized());

        verifyNoInteractions(usuarioRepository);
    }

    @Test
    @WithMockUser(username = EMAIL, authorities = "TECNICO")
    void tecnicoNoPuedeConsultarUsuariosAjenosNiAdministracion()
            throws Exception {

        comprobarRutasAdministrativasBloqueadas();
    }

    @Test
    @WithMockUser(username = EMAIL, authorities = "CLIENTE")
    void clienteNoPuedeConsultarUsuariosAjenosNiAdministracion()
            throws Exception {

        comprobarRutasAdministrativasBloqueadas();
    }

    @Test
    @WithMockUser(
            username = "admin@example.com",
            authorities = "ADMIN"
    )
    void administradorPuedeListarYConsultarUsuariosPorId()
            throws Exception {

        Usuario cliente = crearUsuario("CLIENTE");

        when(usuarioRepository.buscarActivosConDatosYRoles())
                .thenReturn(List.of(cliente));

        when(usuarioRepository.buscarPorIdConDatosYRoles(17))
                .thenReturn(Optional.of(cliente));

        mockMvc.perform(get("/api/usuarios"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value(17))
                .andExpect(jsonPath("$[0].email").value(EMAIL));

        mockMvc.perform(get("/api/usuarios/17"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(17))
                .andExpect(jsonPath("$.email").value(EMAIL));

        verify(usuarioRepository).buscarActivosConDatosYRoles();
        verify(usuarioRepository).buscarPorIdConDatosYRoles(17);
        verifyNoMoreInteractions(usuarioRepository);
    }

    private void comprobarPerfilPropio(String codigoRol)
            throws Exception {

        when(usuarioRepository.buscarPorEmailConDatosYRoles(EMAIL))
                .thenReturn(Optional.of(crearUsuario(codigoRol)));

        mockMvc.perform(
                        get("/api/usuarios/actual")
                                .param("email", "otra@example.com")
                )
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(17))
                .andExpect(jsonPath("$.email").value(EMAIL))
                .andExpect(jsonPath("$.roles[0]").value(codigoRol));

        // Se utiliza la identidad autenticada, no el parámetro recibido.
        verify(usuarioRepository).buscarPorEmailConDatosYRoles(EMAIL);
        verifyNoMoreInteractions(usuarioRepository);
    }

    private void comprobarRutasAdministrativasBloqueadas()
            throws Exception {

        String[] rutas = {
                "/api/usuarios",
                "/api/usuarios/99",
                "/api/admin/estadisticas/resumen"
        };

        for (String ruta : rutas) {
            mockMvc.perform(get(ruta))
                    .andExpect(status().isForbidden());
        }

        verifyNoInteractions(usuarioRepository);
    }

    private Usuario crearUsuario(String codigoRol) {
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
                "hash-simulado-para-test"
        );

        usuario.setId(17);

        Rol rol = new Rol(codigoRol);
        ReflectionTestUtils.setField(rol, "id", 1);

        usuario.getUsuarioRoles().add(
                new UsuarioRol(usuario, rol)
        );

        return usuario;
    }
}