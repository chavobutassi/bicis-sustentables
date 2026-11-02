package DSII.TurismoSustentable.models;

import javax.persistence.*;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import javax.validation.constraints.Pattern;
import java.util.Locale;

@Entity
@Table(name = "pais")
public class Pais {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @NotBlank(message = "El código del país es obligatorio.")
    @Pattern(
            regexp = "^$|^[A-Z]{2}$",
            message = "El código del país debe tener dos letras mayúsculas, por ejemplo AR."
    )
    @Column(nullable = false, unique = true, length = 2)
    private String codigo;

    @NotBlank(message = "El nombre del país es obligatorio.")
    @Size(max = 100, message = "El nombre no puede superar los 100 caracteres.")
    @Column(nullable = false, length = 100)
    private String nombre;

    public Pais() {
    }

    public Pais(String codigo, String nombre) {
        setCodigo(codigo);
        setNombre(nombre);
    }

    public Integer getId() {
        return id;
    }

    public String getCodigo() {
        return codigo;
    }

    public void setCodigo(String codigo) {
        this.codigo = codigo == null
                ? null
                : codigo.trim().toUpperCase(Locale.ROOT);
    }

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre == null ? null : nombre.trim();
    }
}