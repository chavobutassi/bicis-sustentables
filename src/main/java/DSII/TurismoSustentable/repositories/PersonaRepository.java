package DSII.TurismoSustentable.repositories;

import DSII.TurismoSustentable.models.Persona;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PersonaRepository extends JpaRepository<Persona, Integer> {

    boolean existsByTipoDocumento_IdAndPaisEmisor_IdAndNumeroDocumento(
            Integer tipoDocumentoId,
            Integer paisEmisorId,
            String numeroDocumento
    );

}
