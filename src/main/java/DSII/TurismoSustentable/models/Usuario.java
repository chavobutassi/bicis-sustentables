package DSII.TurismoSustentable.models;

import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.GenericGenerator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnore;

import javax.persistence.*;
import javax.validation.constraints.*;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;
import java.util.Locale;

@Entity
public class    Usuario {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO, generator = "native")
    @GenericGenerator(name = "native", strategy = "native")
    private int id;

    @NotNull(message = "Los datos personales son obligatorios.")
    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
            name = "persona_id",
            nullable = false,
            unique = true
    )
    private Persona persona;

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
    @Column(name = "nickname", nullable = false, unique = true, length = 30)
    private String nickname;

    @NotBlank(message = "El email no puede estar vacío.")
    @Email(
            regexp = "^$|^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$",
            message = "Debe ser una dirección de correo válida, por ejemplo usuario@correo.com."
    )
    @Size(
            max = 254,
            message = "El email no puede superar los 254 caracteres."
    )
    @Pattern(
            regexp = "^(?![0-9]).*$",
            message = "El email no puede comenzar con un número."
    )
    @Column(
            name = "email",
            nullable = false,
            unique = true,
            length = 254
    )
    private String email;

    // Almacena la contraseña ya hasheada por el servicio.
    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
    @NotBlank(message = "El hash de la contraseña es obligatorio.")
    @Size(
            max = 255,
            message = "El hash de la contraseña no puede superar los 255 caracteres."
    )
    @Column(nullable = false, length = 255)
    private String password;

    @OneToMany(mappedBy = "usuario", fetch = FetchType.LAZY)
    @JsonIgnore
    private Set<UsuarioRol> usuarioRoles = new HashSet<>();

    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    @CreationTimestamp
    @Column(
            name = "fecha_registro",
            nullable = false,
            updatable = false
    )
    private LocalDateTime fechaRegistro;
    private boolean activo = true;

    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    @Version
    @Column(name = "version", nullable = false)
    private Integer version;

    @Column(
            name = "token_recuperacion",
            length = 64,
            unique = true
    )
    private String tokenRecuperacion;

    @Column(name = "vencimiento_token_recuperacion")
    private LocalDateTime vencimientoTokenRecuperacion;

    @OneToMany(mappedBy = "usuario", fetch = FetchType.EAGER)
    Set<Alquiler> alquileres = new HashSet<>();

    @OneToMany(mappedBy = "usuario", fetch = FetchType.EAGER)
    Set<Tarjeta> tarjetas = new HashSet<>();

    // CONSTRUCTORES
    public Usuario() {
    }

    // El servicio debe entregar la contraseña ya hasheada.
    public Usuario(
            Persona persona,
            String nickname,
            String email,
            String passwordHasheada
    ) {
        setPersona(persona);
        setNickname(nickname);
        setEmail(email);
        setPassword(passwordHasheada);
    }

    // Metodo para normalizar mail
    @PrePersist
    @PreUpdate
    private void normalizarIdentificadoresAntesDeGuardar() {
        setEmail(this.email);
        setNickname(this.nickname);
    }

    // Metodo para añadir un Alquiler
    public void addAlquiler(Alquiler alquiler){
        alquiler.setUsuario(this);
        this.alquileres.add(alquiler);
    }

    // Metodo para añadir una Tarjeta
    public void addTarjeta(Tarjeta tarjeta){
        tarjeta.setUsuario(this);
        this.tarjetas.add(tarjeta);
    }

    // GETTERS Y SETTERS
    public int getId() {
        return id;
    }

    public Persona getPersona() {
        return persona;
    }

    public void setPersona(Persona persona) {
        this.persona = persona;
    }

    public String getNickname() {
        return nickname;
    }

    public void setNickname(String nickname) {
        this.nickname = nickname == null
                ? null
                : nickname.trim().toLowerCase(Locale.ROOT);
    }

    public Integer getVersion() {
        return version;
    }

    public Set<UsuarioRol> getUsuarioRoles() {
        return usuarioRoles;
    }

    public void setId(int id) {
        this.id = id;
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

    public LocalDateTime getFechaRegistro() {
        return fechaRegistro;
    }

    public void setFechaRegistro(LocalDateTime fechaRegistro) {
        this.fechaRegistro = fechaRegistro;
    }

    public boolean isActivo() {
        return activo;
    }

    public void setActivo(boolean activo) {
        this.activo = activo;
    }

    public Set<Alquiler> getAlquileres() {
        return alquileres;
    }

    public Set<Tarjeta> getTarjetas() {
        return tarjetas;
    }

    public void setAlquileres(Set<Alquiler> alquileres) {
        this.alquileres = alquileres;
    }

    public void setTarjetas(Set<Tarjeta> tarjetas) {
        this.tarjetas = tarjetas;
    }

    public String getTokenRecuperacion() {
        return tokenRecuperacion;
    }

    public void setTokenRecuperacion(
            String tokenRecuperacion
    ) {
        this.tokenRecuperacion = tokenRecuperacion;
    }

    public LocalDateTime getVencimientoTokenRecuperacion() {
        return vencimientoTokenRecuperacion;
    }

    public void setVencimientoTokenRecuperacion(
            LocalDateTime vencimientoTokenRecuperacion
    ) {
        this.vencimientoTokenRecuperacion =
                vencimientoTokenRecuperacion;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Usuario usuario = (Usuario) o;

        // Usamos el email como identificador único de negocio.
        return email != null ? email.equals(usuario.email) : usuario.email == null;
    }

    @Override
    public int hashCode() {
        // Usamos el email para generar el hashCode.
        return email != null ? email.hashCode() : 0;
    }

}
