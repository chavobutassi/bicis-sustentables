package DSII.TurismoSustentable.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
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

    @EntityGraph(attributePaths = {
            "persona.genero",
            "usuarioRoles.rol"
    })
    @Query("select distinct u from Usuario u where u.activo = true")
    List<Usuario> buscarActivosConDatosYRoles();

    @EntityGraph(attributePaths = {
            "persona.genero",
            "usuarioRoles.rol"
    })
    @Query("select distinct u from Usuario u where u.id = :id")
    Optional<Usuario> buscarPorIdConDatosYRoles(
            @Param("id") Integer id
    );

    @EntityGraph(attributePaths = {
            "persona.genero",
            "usuarioRoles.rol"
    })
    @Query("select distinct u from Usuario u where u.email = :email")
    Optional<Usuario> buscarPorEmailConDatosYRoles(
            @Param("email") String email
    );

}
