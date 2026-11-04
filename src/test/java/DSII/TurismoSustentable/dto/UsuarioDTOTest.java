package DSII.TurismoSustentable.dto;

import DSII.TurismoSustentable.models.Genero;
import DSII.TurismoSustentable.models.Pais;
import DSII.TurismoSustentable.models.Persona;
import DSII.TurismoSustentable.models.Rol;
import DSII.TurismoSustentable.models.TipoDocumento;
import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.models.UsuarioRol;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDate;
import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

class UsuarioDTOTest {

    @Test
    void tomaDatosPersonalesDesdePersona() {
        LocalDate nacimiento = LocalDate.of(1995, 5, 20);

        Persona persona = new Persona(
                "Ana",
                "Perez",
                nacimiento,
                new Genero("FEMENINO"),
                new TipoDocumento("DNI", "Documento Nacional de Identidad"),
                "00123456",
                new Pais("AR", "Argentina")
        );

        Usuario usuario = new Usuario(
                persona,
                " Ana.Perez ",
                " ANA@EXAMPLE.COM ",
                "hash-simulado-para-test"
        );

        UsuarioDTO dto = new UsuarioDTO(usuario);

        assertEquals("Ana", dto.getNombre());
        assertEquals("Perez", dto.getApellido());
        assertEquals(nacimiento, dto.getFechaNacimiento());
        assertEquals("FEMENINO", dto.getGenero());
        assertEquals("ana.perez", dto.getNickname());
        assertEquals("ana@example.com", dto.getEmail());
    }

    @Test
    void rechazaUsuarioSinPersona() {
        Usuario usuario = new Usuario();

        assertThrows(
                IllegalStateException.class,
                () -> new UsuarioDTO(usuario)
        );
    }

    @Test
    void incluyeTodosLosRolesSinUsarElEnum() {
        Usuario usuario = crearUsuarioConPersona();

        agregarRol(usuario, 2, "TECNICO");
        agregarRol(usuario, 1, "ADMIN");

        UsuarioDTO dto = new UsuarioDTO(usuario);

        assertEquals(
                Arrays.asList("ADMIN", "TECNICO"),
                dto.getRoles()
        );
        assertEquals("ADMIN", dto.getRol());
    }

    @Test
    void noInventaRolesCuandoNoHayAsignaciones() {
        Usuario usuario = crearUsuarioConPersona();

        UsuarioDTO dto = new UsuarioDTO(usuario);

        assertNotNull(dto.getRoles());
        assertTrue(dto.getRoles().isEmpty());
        assertNull(dto.getRol());
    }

    @Test
    void muestraClienteCuandoEsSuUnicoRol() {
        Usuario usuario = crearUsuarioConPersona();
        agregarRol(usuario, 1, "CLIENTE");

        UsuarioDTO dto = new UsuarioDTO(usuario);

        assertEquals("CLIENTE", dto.getRol());
        assertEquals(Arrays.asList("CLIENTE"), dto.getRoles());
    }

    @Test
    void muestraTecnicoCuandoEsSuUnicoRol() {
        Usuario usuario = crearUsuarioConPersona();
        agregarRol(usuario, 1, "TECNICO");

        UsuarioDTO dto = new UsuarioDTO(usuario);

        assertEquals("TECNICO", dto.getRol());
        assertEquals(Arrays.asList("TECNICO"), dto.getRoles());
    }

    @Test
    void conservaAmbosRolesAunqueElSingularMuestreCliente() {
        Usuario usuario = crearUsuarioConPersona();
        agregarRol(usuario, 1, "TECNICO");
        agregarRol(usuario, 2, "CLIENTE");

        UsuarioDTO dto = new UsuarioDTO(usuario);

        assertEquals("CLIENTE", dto.getRol());
        assertEquals(
                Arrays.asList("CLIENTE", "TECNICO"),
                dto.getRoles()
        );
    }

    private Usuario crearUsuarioConPersona() {
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
}
