package DSII.TurismoSustentable.dto;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import javax.validation.Validation;
import javax.validation.Validator;
import javax.validation.ValidatorFactory;
import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;

class RegistroUsuarioDTOTest {

    private static ValidatorFactory factory;
    private static Validator validator;

    @BeforeAll
    static void prepararValidaciones() {
        factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @AfterAll
    static void cerrarValidaciones() {
        if (factory != null) {
            factory.close();
        }
    }

    @Test
    void aceptaDatosValidos() {
        RegistroUsuarioDTO dto = datosValidos();

        // La política actual no exige números en la contraseña.
        dto.setPassword("Abcde!");

        assertTrue(validator.validate(dto).isEmpty());
    }

    @Test
    void normalizaDatosSinPerderCeros() {
        RegistroUsuarioDTO dto = datosValidos();
        dto.setNombre(" Ana ");
        dto.setApellido(" Perez ");
        dto.setNickname(" Juan.Perez ");
        dto.setEmail(" ANA@EXAMPLE.COM ");
        dto.setNumeroDocumento(" 00ab123 ");

        assertEquals("Ana", dto.getNombre());
        assertEquals("Perez", dto.getApellido());
        assertEquals("juan.perez", dto.getNickname());
        assertEquals("ana@example.com", dto.getEmail());
        assertEquals("00AB123", dto.getNumeroDocumento());
        assertTrue(validator.validate(dto).isEmpty());
    }

    @Test
    void aceptaNicknamesPermitidosYLimites() {
        String[] nicknames = {
                "ana",
                "a".repeat(30),
                "ana_23",
                "juan.perez",
                "maria-lopez",
                "ana..",
                "ana--",
                "ana_"
        };

        for (String nickname : nicknames) {
            RegistroUsuarioDTO dto = datosValidos();
            dto.setNickname(nickname);

            assertTrue(
                    validator.validate(dto).isEmpty(),
                    "Debería aceptar el nickname: " + nickname
            );
        }
    }

    @Test
    void rechazaNicknamesInvalidos() {
        String[] nicknames = {
                "",
                "ab",
                "1ana",
                ".ana",
                "_ana",
                "-ana",
                "an a",
                "aña",
                "ana@",
                "a".repeat(31)
        };

        for (String nickname : nicknames) {
            RegistroUsuarioDTO dto = datosValidos();
            dto.setNickname(nickname);

            assertCampoInvalido(dto, "nickname");
        }
    }

    @Test
    void rechazaEmailsInvalidos() {
        String[] emails = {
                "ana",
                "ana@ejemplo",
                "1ana@example.com",
                "@mail@gmail.com"
        };

        for (String email : emails) {
            RegistroUsuarioDTO dto = datosValidos();
            dto.setEmail(email);

            assertCampoInvalido(dto, "email");
        }
    }

    @Test
    void rechazaPasswordsInvalidasSinModificarlas() {
        String[] passwords = {
                "",
                "Ab#12",
                "abcdef!",
                "ABCDEF!",
                "Abcdefg",
                "Abc def#12",
                " Clave#123 ",
                "Aa#" + "a".repeat(62)
        };

        for (String password : passwords) {
            RegistroUsuarioDTO dto = datosValidos();
            dto.setPassword(password);

            assertEquals(password, dto.getPassword());
            assertCampoInvalido(dto, "password");
        }
    }

    @Test
    void rechazaIdsAusentesONoPositivos() {
        for (Integer id : new Integer[]{null, 0, -1}) {
            RegistroUsuarioDTO dto = datosValidos();
            dto.setGeneroId(id);
            dto.setTipoDocumentoId(id);
            dto.setPaisEmisorId(id);

            assertCampoInvalido(dto, "generoId");
            assertCampoInvalido(dto, "tipoDocumentoId");
            assertCampoInvalido(dto, "paisEmisorId");
        }
    }

    @Test
    void rechazaFechaDeNacimientoFutura() {
        RegistroUsuarioDTO dto = datosValidos();
        dto.setFechaNacimiento(LocalDate.now().plusDays(1));

        assertCampoInvalido(dto, "fechaNacimiento");
    }

    @Test
    void exigeTodosLosCamposObligatorios() {
        RegistroUsuarioDTO dto = new RegistroUsuarioDTO();

        String[] campos = {
                "nombre",
                "apellido",
                "fechaNacimiento",
                "generoId",
                "tipoDocumentoId",
                "numeroDocumento",
                "paisEmisorId",
                "nickname",
                "email",
                "password"
        };

        for (String campo : campos) {
            assertCampoInvalido(dto, campo);
        }
    }

    @Test
    void recibePasswordPeroNoLaSerializa() throws Exception {
        ObjectMapper mapper = new ObjectMapper()
                .registerModule(new JavaTimeModule());

        JsonNode json = mapper.valueToTree(datosValidos());

        assertEquals("ana_23", json.get("nickname").asText());
        assertFalse(json.has("password"));

        RegistroUsuarioDTO recibido = mapper.readValue(
                "{\"password\":\"Clave#123\"}",
                RegistroUsuarioDTO.class
        );

        assertEquals("Clave#123", recibido.getPassword());
    }

    private RegistroUsuarioDTO datosValidos() {
        RegistroUsuarioDTO dto = new RegistroUsuarioDTO();
        dto.setNombre("Ana");
        dto.setApellido("Perez");
        dto.setFechaNacimiento(LocalDate.of(1995, 5, 20));
        dto.setGeneroId(1);
        dto.setTipoDocumentoId(1);
        dto.setNumeroDocumento("AAA123456");
        dto.setPaisEmisorId(1);
        dto.setNickname("ana_23");
        dto.setEmail("ana@example.com");
        dto.setPassword("Clave#123");
        return dto;
    }

    private void assertCampoInvalido(
            RegistroUsuarioDTO dto,
            String campo
    ) {
        boolean tieneError = validator.validate(dto).stream()
                .anyMatch(error ->
                        error.getPropertyPath().toString().equals(campo)
                );

        assertTrue(tieneError, "Se esperaba un error en: " + campo);
    }
}
