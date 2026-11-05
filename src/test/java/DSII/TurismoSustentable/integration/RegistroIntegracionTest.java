package DSII.TurismoSustentable.integration;

import DSII.TurismoSustentable.dto.RegistroUsuarioDTO;
import DSII.TurismoSustentable.dto.UsuarioDTO;
import DSII.TurismoSustentable.models.UsuarioRol;
import DSII.TurismoSustentable.repositories.GeneroRepository;
import DSII.TurismoSustentable.repositories.PaisRepository;
import DSII.TurismoSustentable.repositories.PersonaRepository;
import DSII.TurismoSustentable.repositories.RolRepository;
import DSII.TurismoSustentable.repositories.TipoDocumentoRepository;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import DSII.TurismoSustentable.repositories.UsuarioRolRepository;
import DSII.TurismoSustentable.services.CatalogosInicialesService;
import DSII.TurismoSustentable.services.RegistroUsuarioService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.test.context.ActiveProfiles;

import java.time.LocalDate;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Prueba de integración sobre H2 en memoria: catálogos iniciales,
 * registro completo y restricciones reales de la base.
 */
@SpringBootTest
@ActiveProfiles("integracion")
@Transactional
class RegistroIntegracionTest {

    @Autowired private CatalogosInicialesService catalogos;
    @Autowired private RegistroUsuarioService registro;
    @Autowired private GeneroRepository generoRepository;
    @Autowired private TipoDocumentoRepository tipoDocumentoRepository;
    @Autowired private PaisRepository paisRepository;
    @Autowired private RolRepository rolRepository;
    @Autowired private PersonaRepository personaRepository;
    @Autowired private UsuarioRepository usuarioRepository;
    @Autowired private UsuarioRolRepository usuarioRolRepository;
    @Autowired private PasswordEncoder passwordEncoder;

    private RegistroUsuarioDTO datos(String nick, String email, String doc) {
        RegistroUsuarioDTO dto = new RegistroUsuarioDTO();
        dto.setNombre("Ana");
        dto.setApellido("Pérez");
        dto.setFechaNacimiento(LocalDate.of(1995, 5, 20));
        dto.setGeneroId(generoRepository.findByCodigo("FEMENINO").get().getId());
        dto.setTipoDocumentoId(
                tipoDocumentoRepository.findByCodigo("DNI").get().getId());
        dto.setPaisEmisorId(paisRepository.findByCodigo("AR").get().getId());
        dto.setNumeroDocumento(doc);
        dto.setNickname(nick);
        dto.setEmail(email);
        dto.setPassword("Clave$123");
        return dto;
    }

    @Test
    void catalogosSeCarganAlIniciar() {
        assertEquals(5, generoRepository.count());
        assertEquals(2, tipoDocumentoRepository.count());
        assertEquals(3, rolRepository.count());
        assertTrue(paisRepository.count() >= 240);
        assertEquals("Argentina",
                paisRepository.findByCodigo("AR").get().getNombre());
    }

    @Test
    void cargarDosVecesNoDuplica() {
        long paises = paisRepository.count();
        catalogos.cargar();
        assertEquals(paises, paisRepository.count());
        assertEquals(3, rolRepository.count());
    }

    @Test
    void registroCompletoPersisteTodoYAsignaCliente() {
        UsuarioDTO dto = registro.registrarUsuario(
                datos("ana.perez", "ana@correo.com", "30123456"));

        assertNotNull(dto);
        var usuario = usuarioRepository
                .findByEmail("ana@correo.com").orElseThrow();
        assertTrue(usuario.isActivo());
        assertNotEquals("Clave$123", usuario.getPassword());
        assertTrue(passwordEncoder.matches("Clave$123", usuario.getPassword()));

        List<UsuarioRol> roles = usuarioRolRepository.findAll();
        assertTrue(roles.stream().anyMatch(r ->
                r.getUsuario().getId().equals(usuario.getId())
                        && "CLIENTE".equals(r.getRol().getCodigo())));
        assertTrue(personaRepository.count() >= 1);
    }

    @Test
    void emailRepetidoSeRechaza() {
        registro.registrarUsuario(datos("luis.a", "luis@correo.com", "111"));
        assertThrows(IllegalStateException.class, () ->
                registro.registrarUsuario(
                        datos("luis.b", "LUIS@correo.com", "222")));
    }

    @Test
    void documentoRepetidoSeRechaza() {
        registro.registrarUsuario(datos("marta.a", "marta@correo.com", "999"));
        assertThrows(IllegalStateException.class, () ->
                registro.registrarUsuario(
                        datos("marta.b", "marta2@correo.com", "999")));
    }
}
