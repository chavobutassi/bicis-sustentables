package DSII.TurismoSustentable.repositories;

import DSII.TurismoSustentable.models.UsuarioRol;
import DSII.TurismoSustentable.models.UsuarioRolId;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UsuarioRolRepository
        extends JpaRepository<UsuarioRol, UsuarioRolId> {

    List<UsuarioRol> findByUsuario_Id(Integer usuarioId);
}