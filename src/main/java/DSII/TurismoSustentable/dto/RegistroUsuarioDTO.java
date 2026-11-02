package DSII.TurismoSustentable.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import javax.validation.constraints.*;
import java.time.LocalDate;
import java.util.Locale;

public class RegistroUsuarioDTO {

    @NotBlank(message = "El nombre no puede estar vacío.")
    @Size(max = 50, message = "El nombre no puede superar los 50 caracteres.")
    @Pattern(
            regexp = "^$|^[\\p{L}]+(?:[ '\\-][\\p{L}]+)*$",
            message = "El nombre solo puede contener letras, espacios, apóstrofes o guiones."
    )
    private String nombre;

    @NotBlank(message = "El apellido no puede estar vacío.")
    @Size(max = 50, message = "El apellido no puede superar los 50 caracteres.")
    @Pattern(
            regexp = "^$|^[\\p{L}]+(?:[ '\\-][\\p{L}]+)*$",
            message = "El apellido solo puede contener letras, espacios, apóstrofes o guiones."
    )
    private String apellido;

    @NotNull(message = "La fecha de nacimiento es obligatoria.")
    @Past(message = "La fecha de nacimiento debe estar en el pasado.")
    private LocalDate fechaNacimiento;

    @NotNull(message = "El género es obligatorio.")
    @Positive(message = "Debe seleccionar un género válido.")
    private Integer generoId;

    @NotNull(message = "El tipo de documento es obligatorio.")
    @Positive(message = "Debe seleccionar un tipo de documento válido.")
    private Integer tipoDocumentoId;

    @NotBlank(message = "El número de documento es obligatorio.")
    @Size(
            max = 50,
            message = "El número de documento no puede superar los 50 caracteres."
    )
    private String numeroDocumento;

    @NotNull(message = "El país emisor del documento es obligatorio.")
    @Positive(message = "Debe seleccionar un país emisor válido.")
    private Integer paisEmisorId;

    @NotBlank(message = "El nickname es obligatorio.")
    @Size(
            min = 3,
            max = 30,
            message = "El nickname debe tener entre 3 y 30 caracteres."
    )
    @Pattern(
            regexp = "^$|^[a-z][a-z0-9._-]*$",
            message = "El nickname debe comenzar con una letra de a a z y solo puede contener letras, números, punto, guion y guion bajo."
    )
    private String nickname;

    @NotBlank(message = "El email no puede estar vacío.")
    @Size(max = 254, message = "El email no puede superar los 254 caracteres.")
    @Email(
            regexp = "^$|^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$",
            message = "Debe ser una dirección de correo válida, por ejemplo usuario@correo.com."
    )
    @Pattern(
            regexp = "^(?![0-9]).*$",
            message = "El email no puede comenzar con un número."
    )
    private String email;

    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
    @NotBlank(message = "La clave es obligatoria.")
    @Size(
            min = 6,
            max = 64,
            message = "La clave debe tener entre 6 y 64 caracteres."
    )
    @Pattern(
            regexp = "^$|^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$&*])(?=\\S+$).+$",
            message = "La clave debe contener una minúscula, una mayúscula, al menos uno de !@#$&* y no debe tener espacios."
    )
    private String password;

    public RegistroUsuarioDTO() {
    }

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre == null ? null : nombre.trim();
    }

    public String getApellido() {
        return apellido;
    }

    public void setApellido(String apellido) {
        this.apellido = apellido == null ? null : apellido.trim();
    }

    public LocalDate getFechaNacimiento() {
        return fechaNacimiento;
    }

    public void setFechaNacimiento(LocalDate fechaNacimiento) {
        this.fechaNacimiento = fechaNacimiento;
    }

    public Integer getGeneroId() {
        return generoId;
    }

    public void setGeneroId(Integer generoId) {
        this.generoId = generoId;
    }

    public Integer getTipoDocumentoId() {
        return tipoDocumentoId;
    }

    public void setTipoDocumentoId(Integer tipoDocumentoId) {
        this.tipoDocumentoId = tipoDocumentoId;
    }

    public String getNumeroDocumento() {
        return numeroDocumento;
    }

    public void setNumeroDocumento(String numeroDocumento) {
        this.numeroDocumento = numeroDocumento == null
                ? null
                : numeroDocumento.trim().toUpperCase(Locale.ROOT);
    }

    public Integer getPaisEmisorId() {
        return paisEmisorId;
    }

    public void setPaisEmisorId(Integer paisEmisorId) {
        this.paisEmisorId = paisEmisorId;
    }

    public String getNickname() {
        return nickname;
    }

    public void setNickname(String nickname) {
        this.nickname = nickname == null
                ? null
                : nickname.trim().toLowerCase(Locale.ROOT);
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email == null
                ? null
                : email.trim().toLowerCase(Locale.ROOT);
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}