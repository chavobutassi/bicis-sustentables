package DSII.TurismoSustentable.models;

import javax.persistence.*;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import java.util.Locale;

@Entity
@Table(name = "tipo_documento")
public class TipoDocumento {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @NotBlank(message = "El código del tipo de documento es obligatorio.")
    @Size(max = 10, message = "El código no puede superar los 10 caracteres.")
    @Column(nullable = false, unique = true, length = 10)
    private String codigo;

    @NotBlank(message = "El nombre del tipo de documento es obligatorio.")
    @Size(max = 50, message = "El nombre no puede superar los 50 caracteres.")
    @Column(nullable = false, length = 50)
    private String nombre;

    public TipoDocumento() {
    }

    public TipoDocumento(String codigo, String nombre) {
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
