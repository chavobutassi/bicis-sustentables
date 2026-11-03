package DSII.TurismoSustentable.dto;

import DSII.TurismoSustentable.models.Genero;
import DSII.TurismoSustentable.models.Pais;
import DSII.TurismoSustentable.models.Persona;
import DSII.TurismoSustentable.models.TipoDocumento;
import DSII.TurismoSustentable.models.Usuario;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;

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
}
