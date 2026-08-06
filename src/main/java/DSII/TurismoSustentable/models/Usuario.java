package DSII.TurismoSustentable.models;

import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.GenericGenerator;

import javax.persistence.*;
import javax.validation.constraints.*;
import java.time.LocalDate;
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

    @NotBlank(message = "El nombre no puede estar vacío.")
    @Size(max = 50, message = "El nombre no puede superar los 50 caracteres.")
    @Pattern(
            regexp = "^$|^[\\p{L}]+(?:[ '\\-][\\p{L}]+)*$",
            message = "El nombre solo puede contener letras, espacios, apóstrofes o guiones."
    )
    @Column(nullable = false, length = 50)
    private String nombre;

    @NotBlank(message = "El apellido no puede estar vacío.")
    @Size(max = 50, message = "El apellido no puede superar los 50 caracteres.")
    @Pattern(
            regexp = "^$|^[\\p{L}]+(?:[ '\\-][\\p{L}]+)*$",
            message = "El apellido solo puede contener letras, espacios, apóstrofes o guiones."
    )
    @Column(nullable = false, length = 50)
    private String apellido;

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

    @NotBlank(message = "La clave es obligatoria.")
    @Size(min = 6, max = 64, message = "La clave debe tener entre 6 y 64 caracteres.")
    // Contraseña: entre 6 y 64 caracteres, con minúscula, mayúscula, carácter especial y sin espacios.
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$&*])(?=\\S+$).+$",
            message = "La clave debe contener una minúscula, una mayúscula, un carácter especial y no debe tener espacios.")
    @Column(nullable = false, length = 255)
    private String password;

    @NotNull(message = "La fecha de nacimiento es obligatoria.")
    @Past(message = "La fecha de nacimiento debe estar en el pasado.")
    @Column(nullable = false)
    private LocalDate fechaNacimiento;

    @NotNull(message = "El género es obligatorio.")
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private GeneroUsuario genero;

    // --- CAMPO ROL MODIFICADO ---
    @Enumerated(EnumType.STRING) // Almacena el Enum como String en la BD
    private Rol rol = Rol.CLIENTE; // Valor por defecto: CLIENTE
    // ----------------------------

    @CreationTimestamp
    private LocalDate fechaRegistro;
    private boolean activo = true;

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

    // Constructor actualizado con los campos y el rol
    public Usuario(String nombre, String apellido, String email, String password, LocalDate fechaNacimiento, GeneroUsuario genero, boolean activo, Rol rol) {
        this.setNombre(nombre);
        this.setApellido(apellido);
        this.setEmail(email);
        this.password = password;
        this.fechaNacimiento = fechaNacimiento;
        this.genero = genero;
        this.fechaRegistro = LocalDate.now();
        this.activo = true;
        this.rol = rol; // Asignación del rol
        this.alquileres = new HashSet<>();
        this.tarjetas = new HashSet<>();
    }

    // Constructor de conveniencia para CLIENTE
    public Usuario(String nombre, String apellido, String email, String password, LocalDate fechaNacimiento, GeneroUsuario genero, boolean activo) {
        this(nombre, apellido, email, password, fechaNacimiento, genero, activo, Rol.CLIENTE);
    }

    // Metodo para normalizar mail
    @PrePersist
    @PreUpdate
    private void normalizarEmailAntesDeGuardar() {
        setEmail(this.email);
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

    public Rol getRol() {
        return rol;
    }

    public void setRol(Rol rol) {
        this.rol = rol;
    }

    // **METODO DE CONVENIENCIA PARA SABER SI ES ADMINISTRADOR**
    public boolean esAdministrador() {
        return this.rol == Rol.ADMIN;
    }

    // **METODO DE CONVENIENCIA PARA SABER SI PUEDE ALQUILAR**
    public boolean puedeAlquilar() {
        return this.rol == Rol.CLIENTE || this.rol == Rol.ADMIN;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre == null
                ? null
                : nombre.trim();
    }

    public String getApellido() {
        return apellido;
    }

    public void setApellido(String apellido) {
        this.apellido = apellido == null
                ? null
                : apellido.trim();
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

    public LocalDate getFechaNacimiento() {
        return fechaNacimiento;
    }

    public void setFechaNacimiento(LocalDate fechaNacimiento) {
        this.fechaNacimiento = fechaNacimiento;
    }

    public GeneroUsuario getGenero() {
        return genero;
    }

    public void setGenero(GeneroUsuario genero) {
        this.genero = genero;
    }

    public LocalDate getFechaRegistro() {
        return fechaRegistro;
    }

    public void setFechaRegistro(LocalDate fechaRegistro) {
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