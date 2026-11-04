package DSII.TurismoSustentable.dto;

import DSII.TurismoSustentable.models.Persona;
import DSII.TurismoSustentable.models.Tarjeta;
import DSII.TurismoSustentable.models.Usuario;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

public class UsuarioDTO {

    private int id;
    private String nombre;
    private String apellido;
    private String email;
    private String nickname;
    private LocalDateTime fechaRegistro;
    private boolean activo;
    private String genero;
    private String rol;
    private List<String> roles;
    private LocalDate fechaNacimiento;

    private List<AlquilerDTO> alquileres;
    private List<TarjetaDTO> tarjetas;

    // Constructor
    public UsuarioDTO(Usuario usuario) {
        Persona persona = usuario.getPersona();

        if (persona == null) {
            throw new IllegalStateException(
                    "El usuario no tiene una persona asociada."
            );
        }

        this.id = usuario.getId();
        this.email = usuario.getEmail();
        this.nickname = usuario.getNickname();
        this.fechaRegistro = usuario.getFechaRegistro();
        this.activo = usuario.isActivo();

        this.nombre = persona.getNombre();
        this.apellido = persona.getApellido();
        this.fechaNacimiento = persona.getFechaNacimiento();
        this.genero = persona.getGenero().getCodigo();

        this.roles = usuario.getUsuarioRoles().stream()
                .map(asignacion -> asignacion.getRol().getCodigo())
                .distinct()
                .sorted()
                .collect(Collectors.toList());

        // Compatibilidad temporal con el frontend que todavía lee "rol".
        // Los permisos reales utilizan todos los roles asignados.
        if (this.roles.contains("ADMIN")) {
            this.rol = "ADMIN";
        } else if (this.roles.contains("CLIENTE")) {
            this.rol = "CLIENTE";
        } else if (this.roles.contains("TECNICO")) {
            this.rol = "TECNICO";
        } else {
            this.rol = null;
        }
    }

    // Getters
    public int getId() { return id; }

    public String getNombre() { return nombre; }
    public String getApellido() { return apellido; }

    public String getNickname() {
        return nickname;
    }

    public String getEmail() { return email; }
    public LocalDateTime getFechaRegistro() {
        return fechaRegistro;
    }
    public boolean isActivo() { return activo; }
    public String getGenero() { return genero; }
    public String getRol() { return rol; }

    public List<String> getRoles() {
        return roles;
    }

    public LocalDate getFechaNacimiento() { return fechaNacimiento; }

    public List<AlquilerDTO> getAlquileres() { return alquileres; }
    public List<TarjetaDTO> getTarjetas() { return tarjetas; }

}
