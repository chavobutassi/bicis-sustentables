package DSII.TurismoSustentable.repositories;

import DSII.TurismoSustentable.models.Genero;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface GeneroRepository extends JpaRepository<Genero, Integer> {

    Optional<Genero> findByCodigo(String codigo);

}