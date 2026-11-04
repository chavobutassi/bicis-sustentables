package DSII.TurismoSustentable.models;

import javax.persistence.*;
import javax.validation.Valid;
import javax.validation.constraints.NotNull;

@Entity
@Table(name = "usuario_rol")
public class UsuarioRol {

    @EmbeddedId
    @NotNull(message = "La clave de la asignación es obligatoria.")
    @Valid
    private UsuarioRolId id;

    @MapsId("usuarioId")
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "usuario_id", nullable = false)
    @NotNull(message = "El usuario es obligatorio.")
    private Usuario usuario;

    @MapsId("rolId")
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "rol_id", nullable = false)
    @NotNull(message = "El rol es obligatorio.")
    private Rol rol;

    public UsuarioRol() {
    }

    public UsuarioRol(Usuario usuario, Rol rol) {
        if (usuario == null || usuario.getId() <= 0) {
            throw new IllegalArgumentException(
                    "El usuario debe tener un identificador válido."
            );
        }

        if (rol == null
                || rol.getId() == null
                || rol.getId() <= 0) {
            throw new IllegalArgumentException(
                    "El rol debe tener un identificador válido."
            );
        }

        this.usuario = usuario;
        this.rol = rol;
        this.id = new UsuarioRolId(
                usuario.getId(),
                rol.getId()
        );
    }

    public UsuarioRolId getId() {
        return id;
    }

    public Usuario getUsuario() {
        return usuario;
    }

    public Rol getRol() {
        return rol;
    }
}