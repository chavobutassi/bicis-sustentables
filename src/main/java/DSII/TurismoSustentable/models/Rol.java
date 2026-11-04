package DSII.TurismoSustentable.models;

import javax.persistence.*;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Pattern;
import javax.validation.constraints.Size;
import java.util.Locale;

@Entity
@Table(name = "rol")
public class Rol {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @NotBlank(message = "El código del rol es obligatorio.")
    @Size(
            max = 20,
            message = "El código del rol no puede superar los 20 caracteres."
    )
    @Pattern(
            regexp = "^$|^(CLIENTE|ADMIN|TECNICO)$",
            message = "El rol debe ser CLIENTE, ADMIN o TECNICO."
    )
    @Column(nullable = false, unique = true, length = 20)
    private String codigo;

    public Rol() {
    }

    public Rol(String codigo) {
        setCodigo(codigo);
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
}
