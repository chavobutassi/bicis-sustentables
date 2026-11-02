package DSII.TurismoSustentable.dto;

import DSII.TurismoSustentable.models.Persona;
import DSII.TurismoSustentable.models.Tarjeta;
import DSII.TurismoSustentable.models.Usuario;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

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

        if (usuario.getRol() != null) {
            this.rol = usuario.getRol().name();
        } else {
            this.rol = "CLIENTE";
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

    public LocalDate getFechaNacimiento() { return fechaNacimiento; }

    public List<AlquilerDTO> getAlquileres() { return alquileres; }
    public List<TarjetaDTO> getTarjetas() { return tarjetas; }

}
