package DSII.TurismoSustentable.dto;

import DSII.TurismoSustentable.models.Tarjeta;
import DSII.TurismoSustentable.models.Usuario;

import java.time.LocalDate;
import java.util.List;

public class UsuarioDTO {

    private int id;
    private String nombre;
    private String apellido;
    private String email;
    private LocalDate fechaRegistro;
    private boolean activo;
    private String genero;
    private String rol;
    private LocalDate fechaNacimiento;

    private List<AlquilerDTO> alquileres;
    private List<TarjetaDTO> tarjetas;

    // Constructor
    public UsuarioDTO (Usuario usuario) {
        this.id = usuario.getId();
        this.nombre = usuario.getNombre();
        this.apellido = usuario.getApellido();
        this.email = usuario.getEmail();
        this.fechaRegistro = usuario.getFechaRegistro();
        this.activo = usuario.isActivo();

        // --- 2. CAMBIO EN GENERO ---
        // Enviamos el valor ENUM original (ej: "NO_BINARIO")
        // en lugar del texto formateado ("No binario").
        // Esto es necesario para que el <select> del admin panel funcione.
        this.genero = usuario.getGenero().name();
        this.fechaNacimiento = usuario.getFechaNacimiento(); // <-- 3. ASIGNACIÓN AGREGADA

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

    public String getEmail() { return email; }
    public LocalDate getFechaRegistro() { return fechaRegistro; }
    public boolean isActivo() { return activo; }
    public String getGenero() { return genero; }
    public String getRol() { return rol; }

    public LocalDate getFechaNacimiento() { return fechaNacimiento; }

    public List<AlquilerDTO> getAlquileres() { return alquileres; }
    public List<TarjetaDTO> getTarjetas() { return tarjetas; }


    // (La función formatEnumText ya no se usa aquí, pero no molesta)
    /*private String formatEnumText(String text) {
        if (text == null || text.isEmpty()) return "";
        String result = text.replace("_", " ").toLowerCase();
        return result.substring(0, 1).toUpperCase() + result.substring(1);
    }*/
}
