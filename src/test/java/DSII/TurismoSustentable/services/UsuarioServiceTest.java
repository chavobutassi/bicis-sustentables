package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.dto.ActualizarUsuarioDTO;
import DSII.TurismoSustentable.dto.UsuarioDTO;
import DSII.TurismoSustentable.models.*;
import DSII.TurismoSustentable.repositories.GeneroRepository;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.test.util.ReflectionTestUtils;

import javax.persistence.EntityManager;
import javax.persistence.EntityNotFoundException;
import javax.persistence.LockModeType;
import javax.persistence.OptimisticLockException;
import javax.validation.Validation;
import javax.validation.Validator;
import javax.validation.ValidatorFactory;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UsuarioServiceTest {

    @Mock
    private UsuarioRepository usuarioRepository;

    @Mock
    private GeneroRepository generoRepository;

    @Mock
    private EntityManager entityManager;

    @InjectMocks
    private UsuarioService usuarioService;

    private Usuario usuario;
    private ActualizarUsuarioDTO datos;
    private Genero generoNuevo;
    private LocalDateTime vencimientoOriginal;

    @BeforeEach
    void prepararDatos() {
        Persona persona = new Persona(
                "Ana",
                "Perez",
                LocalDate.of(1995, 5, 20),
                new Genero("FEMENINO"),
                new TipoDocumento("DNI", "Documento Nacional de Identidad"),
                "00123456",
                new Pais("AR", "Argentina")
        );

        vencimientoOriginal = LocalDateTime.of(2030, 1, 1, 0, 0);

        usuario = new Usuario();
        usuario.setId(1);
        usuario.setPersona(persona);
        usuario.setEmail("ana@example.com");
        usuario.setNickname("ana.perez");
        usuario.setPassword("hash-simulado-para-test");
        usuario.setTokenRecuperacion("a".repeat(64));
        usuario.setVencimientoTokenRecuperacion(vencimientoOriginal);

        Rol rolCliente = new Rol("CLIENTE");
        ReflectionTestUtils.setField(rolCliente, "id", 2);

        usuario.getUsuarioRoles().add(
                new UsuarioRol(usuario, rolCliente)
        );

        datos = new ActualizarUsuarioDTO();
        datos.setNombre(" Ana Maria ");
        datos.setApellido(" Lopez ");
        datos.setEmail(" ANA@EXAMPLE.COM ");
        datos.setFechaNacimiento(LocalDate.of(1994, 5, 20));
        datos.setGeneroId(2);

        generoNuevo = new Genero("OTRO");
    }

    @Test
    void actualizaPersonaSinAlterarOtrosDatosDeCuenta() {
        prepararBusquedasValidas();
        Persona personaOriginal = usuario.getPersona();

        UsuarioDTO resultado = usuarioService.actualizarUsuario(1, datos);

        assertSame(personaOriginal, usuario.getPersona());
        assertEquals("Ana Maria", personaOriginal.getNombre());
        assertEquals("Lopez", personaOriginal.getApellido());
        assertEquals(datos.getFechaNacimiento(), personaOriginal.getFechaNacimiento());
        assertSame(generoNuevo, personaOriginal.getGenero());

        assertEquals("00123456", personaOriginal.getNumeroDocumento());
        assertEquals("DNI", personaOriginal.getTipoDocumento().getCodigo());
        assertEquals("AR", personaOriginal.getPaisEmisor().getCodigo());
        assertEquals("ana.perez", usuario.getNickname());
        assertEquals(1, usuario.getUsuarioRoles().size());
        assertEquals(List.of("CLIENTE"), resultado.getRoles());
        assertEquals("hash-simulado-para-test", usuario.getPassword());
        assertEquals("a".repeat(64), usuario.getTokenRecuperacion());
        assertEquals(vencimientoOriginal, usuario.getVencimientoTokenRecuperacion());

        assertEquals("Ana Maria", resultado.getNombre());
        assertEquals("ana@example.com", resultado.getEmail());
        assertEquals("OTRO", resultado.getGenero());

        verify(usuarioRepository).existsByEmailIgnoreCaseAndIdNot(
                "ana@example.com", 1
        );
        verify(entityManager).lock(
                usuario, LockModeType.OPTIMISTIC_FORCE_INCREMENT
        );
        verify(usuarioRepository).flush();
    }

    @Test
    void cambiarEmailInvalidaLaRecuperacionAnterior() {
        prepararBusquedasValidas();
        datos.setEmail(" NUEVO@EXAMPLE.COM ");

        UsuarioDTO resultado = usuarioService.actualizarUsuario(1, datos);

        assertEquals("nuevo@example.com", usuario.getEmail());
        assertEquals("nuevo@example.com", resultado.getEmail());
        assertNull(usuario.getTokenRecuperacion());
        assertNull(usuario.getVencimientoTokenRecuperacion());
    }

    @Test
    void rechazaUsuarioInexistente() {
        when(usuarioRepository.findById(1)).thenReturn(Optional.empty());

        assertThrows(
                EntityNotFoundException.class,
                () -> usuarioService.actualizarUsuario(1, datos)
        );

        comprobarQueNoSeInicioEscritura();
        verifyNoInteractions(generoRepository);
    }

    @Test
    void rechazaUsuarioInactivo() {
        usuarioExiste();
        usuario.setActivo(false);

        assertThrows(
                EntityNotFoundException.class,
                () -> usuarioService.actualizarUsuario(1, datos)
        );

        comprobarQueNoSeInicioEscritura();
        verifyNoInteractions(generoRepository);
    }

    @Test
    void rechazaUsuarioSinPersona() {
        usuarioExiste();
        usuario.setPersona(null);

        assertThrows(
                IllegalStateException.class,
                () -> usuarioService.actualizarUsuario(1, datos)
        );

        comprobarQueNoSeInicioEscritura();
        verifyNoInteractions(generoRepository);
    }

    @Test
    void rechazaGeneroInexistente() {
        usuarioExiste();
        when(generoRepository.findById(2)).thenReturn(Optional.empty());

        assertThrows(
                IllegalArgumentException.class,
                () -> usuarioService.actualizarUsuario(1, datos)
        );

        comprobarQueNoSeInicioEscritura();
    }

    @Test
    void rechazaEmailOcupadoSinModificarDatos() {
        prepararBusquedasValidas();
        datos.setEmail("ocupado@example.com");

        when(usuarioRepository.existsByEmailIgnoreCaseAndIdNot(
                "ocupado@example.com", 1
        )).thenReturn(true);

        assertThrows(
                IllegalStateException.class,
                () -> usuarioService.actualizarUsuario(1, datos)
        );

        assertEquals("ana@example.com", usuario.getEmail());
        assertEquals("Ana", usuario.getPersona().getNombre());
        assertEquals("a".repeat(64), usuario.getTokenRecuperacion());
        comprobarQueNoSeInicioEscritura();
    }

    @Test
    void propagaConflictoDeVersionAntesDeModificarDatos() {
        prepararBusquedasValidas();
        datos.setEmail("nuevo@example.com");

        doThrow(new OptimisticLockException("Conflicto simulado"))
                .when(entityManager)
                .lock(usuario, LockModeType.OPTIMISTIC_FORCE_INCREMENT);

        assertThrows(
                OptimisticLockException.class,
                () -> usuarioService.actualizarUsuario(1, datos)
        );

        assertEquals("ana@example.com", usuario.getEmail());
        assertEquals("Ana", usuario.getPersona().getNombre());
        verify(usuarioRepository, never()).flush();
    }

    @Test
    void propagaConflictoDeIntegridadAlGuardar() {
        prepararBusquedasValidas();

        doThrow(new DataIntegrityViolationException("Conflicto simulado"))
                .when(usuarioRepository).flush();

        assertThrows(
                DataIntegrityViolationException.class,
                () -> usuarioService.actualizarUsuario(1, datos)
        );
    }

    @Test
    void validaLosCincoCamposDeActualizacion() {
        try (ValidatorFactory factory = Validation.buildDefaultValidatorFactory()) {
            Validator validator = factory.getValidator();

            assertTrue(validator.validate(datos).isEmpty());

            String[] campos = {
                    "nombre", "apellido", "email",
                    "fechaNacimiento", "generoId"
            };

            ActualizarUsuarioDTO vacio = new ActualizarUsuarioDTO();

            for (String campo : campos) {
                assertFalse(
                        validator.validateProperty(vacio, campo).isEmpty(),
                        "Debe exigir el campo: " + campo
                );
            }

            datos.setNombre("123");
            datos.setApellido("Lopez@");
            datos.setEmail("ana@ejemplo");
            datos.setFechaNacimiento(LocalDate.now().plusDays(1));
            datos.setGeneroId(0);

            for (String campo : campos) {
                assertFalse(
                        validator.validateProperty(datos, campo).isEmpty(),
                        "Debe rechazar el valor del campo: " + campo
                );
            }
        }
    }

    private void usuarioExiste() {
        when(usuarioRepository.findById(1))
                .thenReturn(Optional.of(usuario));
    }

    private void prepararBusquedasValidas() {
        usuarioExiste();
        when(generoRepository.findById(2))
                .thenReturn(Optional.of(generoNuevo));
    }

    private void comprobarQueNoSeInicioEscritura() {
        verify(usuarioRepository, never()).flush();
        verifyNoInteractions(entityManager);
    }
}
