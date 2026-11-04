package DSII.TurismoSustentable.models;

import javax.persistence.Column;
import javax.persistence.Embeddable;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;
import java.io.Serializable;
import java.util.Objects;

@Embeddable
public class UsuarioRolId implements Serializable {

    private static final long serialVersionUID = 1L;

    @NotNull(message = "El identificador del usuario es obligatorio.")
    @Positive(message = "El identificador del usuario debe ser positivo.")
    @Column(name = "usuario_id", nullable = false)
    private Integer usuarioId;

    @NotNull(message = "El identificador del rol es obligatorio.")
    @Positive(message = "El identificador del rol debe ser positivo.")
    @Column(name = "rol_id", nullable = false)
    private Integer rolId;

    public UsuarioRolId() {
    }

    public UsuarioRolId(Integer usuarioId, Integer rolId) {
        this.usuarioId = usuarioId;
        this.rolId = rolId;
    }

    public Integer getUsuarioId() {
        return usuarioId;
    }

    public Integer getRolId() {
        return rolId;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }

        if (o == null || getClass() != o.getClass()) {
            return false;
        }

        UsuarioRolId otro = (UsuarioRolId) o;

        return Objects.equals(usuarioId, otro.usuarioId)
                && Objects.equals(rolId, otro.rolId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(usuarioId, rolId);
    }
}
