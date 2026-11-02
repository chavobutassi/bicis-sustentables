package DSII.TurismoSustentable.repositories;

import DSII.TurismoSustentable.models.TipoDocumento;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface TipoDocumentoRepository
        extends JpaRepository<TipoDocumento, Integer> {

    Optional<TipoDocumento> findByCodigo(String codigo);

}