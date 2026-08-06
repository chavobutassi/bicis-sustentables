package DSII.TurismoSustentable.repositories;

import DSII.TurismoSustentable.models.Bicicleta;
import DSII.TurismoSustentable.models.EstadoBicicleta;
import DSII.TurismoSustentable.models.TipoBicicleta;
import DSII.TurismoSustentable.models.Estacion;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import javax.persistence.LockModeType;
import java.util.Optional;
import java.util.List;

public interface BicicletaRepository extends JpaRepository<Bicicleta, Integer> {

    /**
     * 3. ESTADOS DE LAS BICICLETAS (Preferencias/Estados de Bicis en general)
     * * Consulta que utiliza la tabla Bicicleta (no Alquiler) para contar cuántas bicicletas
     * están en cada EstadoBicicleta.
     * * Resultado: List<Object[]> donde cada Object[] contiene [EstadoBicicleta, Long Cantidad].
     */

    @Query("SELECT b.estado, COUNT(b.id) FROM Bicicleta b GROUP BY b.estado")
    List<Object[]> contarBicicletasPorEstado();

    Optional<Bicicleta> findByCodigoBicicleta(String codigoBicicleta);
    List<Bicicleta> findByBorradoBiciFalse();
    List<Bicicleta> findByBorradoBiciFalseAndEstado(EstadoBicicleta estado);
    List<Bicicleta> findByBorradoBiciFalseAndTipo(TipoBicicleta tipo);

    // Cuenta las bicicletas que están físicamente en una estación y que no fueron eliminadas lógicamente
    long countByUbicacionActualAndBorradoBiciFalse(
            Estacion ubicacionActual
    );

    // Bloqueo de la bici mientras se crea el alquiler
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query(
            "SELECT b FROM Bicicleta b " +
                    "WHERE b.id = :id " +
                    "AND b.borradoBici = false"
    )
    Optional<Bicicleta> buscarActivaPorIdConBloqueo(
            @Param("id") Integer id
    );
}
