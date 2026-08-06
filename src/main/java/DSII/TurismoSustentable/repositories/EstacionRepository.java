package DSII.TurismoSustentable.repositories;

import DSII.TurismoSustentable.models.Estacion;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import javax.persistence.LockModeType;
import java.util.List;
import java.util.Optional;

public interface EstacionRepository extends JpaRepository<Estacion, Integer> {

    // Útil para buscar una estación por su nombre
    Optional<Estacion> findByNombre(String nombre);
    List<Estacion> findByBorradoEstacionFalse();

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT e FROM Estacion e " +
            "WHERE e.nombre = :nombre " +
            "AND e.borradoEstacion = false")
    Optional<Estacion> buscarActivaPorNombreConBloqueo(
            @Param("nombre") String nombre
    );

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT e FROM Estacion e " +
            "WHERE e.id = :id " +
            "AND e.borradoEstacion = false")
    Optional<Estacion> buscarActivaPorIdConBloqueo(
            @Param("id") Integer id
    );

}