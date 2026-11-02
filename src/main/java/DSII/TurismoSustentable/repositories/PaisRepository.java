package DSII.TurismoSustentable.repositories;

import DSII.TurismoSustentable.models.Pais;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface PaisRepository extends JpaRepository<Pais, Integer> {

    Optional<Pais> findByCodigo(String codigo);

}
