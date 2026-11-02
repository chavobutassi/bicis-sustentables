package DSII.TurismoSustentable.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import DSII.TurismoSustentable.models.Usuario;
import java.util.List;
import java.util.Optional;

public interface UsuarioRepository extends JpaRepository<Usuario, Integer> {

    List<Usuario> findByActivoTrue();
    Optional<Usuario> findByEmail(String email);

    // Para comprobar duplicados durante el registro
    boolean existsByEmailIgnoreCase(String email);

    // Para comprobar duplicados al editar,
    // excluyendo al mismo usuario
    boolean existsByEmailIgnoreCaseAndIdNot(
            String email,
            Integer id
    );

    Optional<Usuario> findByTokenRecuperacion(
            String tokenRecuperacion
    );

    Optional<Usuario> findByNicknameIgnoreCase(String nickname);

    boolean existsByNicknameIgnoreCase(String nickname);

    boolean existsByNicknameIgnoreCaseAndIdNot(
            String nickname,
            Integer id
    );

}
