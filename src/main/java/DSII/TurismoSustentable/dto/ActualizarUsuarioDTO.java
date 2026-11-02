package DSII.TurismoSustentable.dto;

import javax.validation.constraints.*;
import java.time.LocalDate;
import java.util.Locale;

public class ActualizarUsuarioDTO {

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

    @NotNull(message = "La fecha de nacimiento es obligatoria.")
    @Past(message = "La fecha de nacimiento debe estar en el pasado.")
    private LocalDate fechaNacimiento;

    @NotNull(message = "El género es obligatorio.")
    @Positive(message = "Debe seleccionar un género válido.")
    private Integer generoId;

    public ActualizarUsuarioDTO() {
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

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email == null
                ? null
                : email.trim().toLowerCase(Locale.ROOT);
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
}