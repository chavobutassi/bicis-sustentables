package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.dto.RegistroUsuarioDTO;
import DSII.TurismoSustentable.dto.UsuarioDTO;
import DSII.TurismoSustentable.models.*;
import DSII.TurismoSustentable.repositories.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDate;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class RegistroUsuarioServiceTest {

    private static final String HASH_SIMULADO = "hash-simulado-para-test";

    @Mock
    private UsuarioRepository usuarioRepository;

    @Mock
    private PersonaRepository personaRepository;

    @Mock
    private GeneroRepository generoRepository;

    @Mock
    private TipoDocumentoRepository tipoDocumentoRepository;

    @Mock
    private PaisRepository paisRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private RegistroUsuarioService registroUsuarioService;

    private RegistroUsuarioDTO datos;
    private Genero genero;
    private TipoDocumento tipoDocumento;
    private Pais pais;

    @BeforeEach
    void prepararDatos() {
        genero = new Genero("FEMENINO");
        tipoDocumento = new TipoDocumento(
                "DNI",
                "Documento Nacional de Identidad"
        );
        pais = new Pais("AR", "Argentina");

        datos = new RegistroUsuarioDTO();
        datos.setNombre(" Ana ");
        datos.setApellido(" Perez ");
        datos.setFechaNacimiento(LocalDate.of(1995, 5, 20));
        datos.setGeneroId(1);
        datos.setTipoDocumentoId(1);
        datos.setNumeroDocumento(" 00123456 ");
        datos.setPaisEmisorId(1);
        datos.setNickname(" Ana.Perez ");
        datos.setEmail(" ANA@EXAMPLE.COM ");
        datos.setPassword("Clave#123");
    }

    @Test
    void registraPersonaYCuentaConPasswordHasheada() {
        prepararGuardadoDePersona();

        when(usuarioRepository.saveAndFlush(any(Usuario.class)))
                .thenAnswer(invocacion -> {
                    Usuario usuario = invocacion.getArgument(0);
                    usuario.setId(17);
                    return usuario;
                });

        UsuarioDTO resultado = registroUsuarioService.registrarUsuario(datos);

        ArgumentCaptor<Persona> personaCaptor =
                ArgumentCaptor.forClass(Persona.class);

        ArgumentCaptor<Usuario> usuarioCaptor =
                ArgumentCaptor.forClass(Usuario.class);

        verify(personaRepository).save(personaCaptor.capture());
        verify(usuarioRepository).saveAndFlush(usuarioCaptor.capture());

        Persona persona = personaCaptor.getValue();
        Usuario usuario = usuarioCaptor.getValue();

        assertEquals("Ana", persona.getNombre());
        assertEquals("Perez", persona.getApellido());
        assertEquals(datos.getFechaNacimiento(), persona.getFechaNacimiento());
        assertEquals("00123456", persona.getNumeroDocumento());
        assertSame(genero, persona.getGenero());
        assertSame(tipoDocumento, persona.getTipoDocumento());
        assertSame(pais, persona.getPaisEmisor());

        assertSame(persona, usuario.getPersona());
        assertEquals("ana@example.com", usuario.getEmail());
        assertEquals("ana.perez", usuario.getNickname());
        assertEquals(HASH_SIMULADO, usuario.getPassword());
        assertNotEquals(datos.getPassword(), usuario.getPassword());
        assertEquals(Rol.CLIENTE, usuario.getRol());
        assertTrue(usuario.isActivo());

        assertEquals(17, resultado.getId());
        assertEquals("Ana", resultado.getNombre());
        assertEquals("ana@example.com", resultado.getEmail());
        assertEquals("ana.perez", resultado.getNickname());
        assertEquals("CLIENTE", resultado.getRol());

        verify(passwordEncoder).encode("Clave#123");
        verify(usuarioRepository).existsByEmailIgnoreCase("ana@example.com");
        verify(usuarioRepository).existsByNicknameIgnoreCase("ana.perez");

        verify(personaRepository)
                .existsByTipoDocumento_IdAndPaisEmisor_IdAndNumeroDocumento(
                        1, 1, "00123456"
                );
    }

    @Test
    void rechazaEmailOcupadoSinGuardar() {
        when(usuarioRepository.existsByEmailIgnoreCase("ana@example.com"))
                .thenReturn(true);

        IllegalStateException error = assertThrows(
                IllegalStateException.class,
                () -> registroUsuarioService.registrarUsuario(datos)
        );

        assertEquals(
                "Ya existe un usuario registrado con ese email.",
                error.getMessage()
        );

        comprobarQueNoSeGuardoNada();
    }

    @Test
    void rechazaNicknameOcupadoSinGuardar() {
        when(usuarioRepository.existsByNicknameIgnoreCase("ana.perez"))
                .thenReturn(true);

        IllegalStateException error = assertThrows(
                IllegalStateException.class,
                () -> registroUsuarioService.registrarUsuario(datos)
        );

        assertEquals("El nickname ya está en uso.", error.getMessage());

        comprobarQueNoSeGuardoNada();
    }

    @Test
    void rechazaDocumentoRepetidoSinGuardar() {
        prepararCatalogos();

        when(personaRepository
                .existsByTipoDocumento_IdAndPaisEmisor_IdAndNumeroDocumento(
                        1, 1, "00123456"
                ))
                .thenReturn(true);

        assertThrows(
                IllegalStateException.class,
                () -> registroUsuarioService.registrarUsuario(datos)
        );

        comprobarQueNoSeGuardoNada();
    }

    @Test
    void rechazaGeneroInexistenteSinGuardar() {
        when(generoRepository.findById(1)).thenReturn(Optional.empty());

        IllegalArgumentException error = assertThrows(
                IllegalArgumentException.class,
                () -> registroUsuarioService.registrarUsuario(datos)
        );

        assertEquals("El género seleccionado no existe.", error.getMessage());

        comprobarQueNoSeGuardoNada();
    }

    @Test
    void rechazaTipoDocumentoInexistenteSinGuardar() {
        when(generoRepository.findById(1)).thenReturn(Optional.of(genero));
        when(tipoDocumentoRepository.findById(1)).thenReturn(Optional.empty());

        IllegalArgumentException error = assertThrows(
                IllegalArgumentException.class,
                () -> registroUsuarioService.registrarUsuario(datos)
        );

        assertEquals(
                "El tipo de documento seleccionado no existe.",
                error.getMessage()
        );

        comprobarQueNoSeGuardoNada();
    }

    @Test
    void rechazaPaisInexistenteSinGuardar() {
        when(generoRepository.findById(1)).thenReturn(Optional.of(genero));
        when(tipoDocumentoRepository.findById(1))
                .thenReturn(Optional.of(tipoDocumento));
        when(paisRepository.findById(1)).thenReturn(Optional.empty());

        IllegalArgumentException error = assertThrows(
                IllegalArgumentException.class,
                () -> registroUsuarioService.registrarUsuario(datos)
        );

        assertEquals(
                "El país emisor seleccionado no existe.",
                error.getMessage()
        );

        comprobarQueNoSeGuardoNada();
    }

    @Test
    void propagaConflictoAlGuardarLaCuenta() {
        prepararGuardadoDePersona();

        DataIntegrityViolationException conflicto =
                new DataIntegrityViolationException("Conflicto simulado");

        when(usuarioRepository.saveAndFlush(any(Usuario.class)))
                .thenThrow(conflicto);

        DataIntegrityViolationException resultado = assertThrows(
                DataIntegrityViolationException.class,
                () -> registroUsuarioService.registrarUsuario(datos)
        );

        assertSame(conflicto, resultado);
        verify(personaRepository).save(any(Persona.class));
    }

    private void prepararCatalogos() {
        when(generoRepository.findById(1)).thenReturn(Optional.of(genero));
        when(tipoDocumentoRepository.findById(1))
                .thenReturn(Optional.of(tipoDocumento));
        when(paisRepository.findById(1)).thenReturn(Optional.of(pais));
    }

    private void prepararGuardadoDePersona() {
        prepararCatalogos();

        when(passwordEncoder.encode("Clave#123"))
                .thenReturn(HASH_SIMULADO);

        when(personaRepository.save(any(Persona.class)))
                .thenAnswer(invocacion -> invocacion.getArgument(0));
    }

    private void comprobarQueNoSeGuardoNada() {
        verify(personaRepository, never()).save(any(Persona.class));
        verify(usuarioRepository, never()).saveAndFlush(any(Usuario.class));
        verifyNoInteractions(passwordEncoder);
    }
}
