package DSII.TurismoSustentable.repositories;

import DSII.TurismoSustentable.models.Alquiler;
import DSII.TurismoSustentable.models.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface AlquilerRepository extends JpaRepository<Alquiler, Integer> {

    /**
     * 1. PREFERENCIAS DE BICICLETA POR GÉNERO
     * * Consulta que agrupa y cuenta los alquileres por el tipo de bicicleta (a.bicicleta.tipo)
     * y el género del usuario (a.usuario.genero).
     * * Resultado: List<Object[]> donde cada Object[] contiene [TipoBicicleta, String Genero, Long Cantidad].
     */
    @Query("SELECT a.bicicleta.tipo, a.usuario.genero, COUNT(a.id) " +
            "FROM Alquiler a " +
            // CORRECCIÓN: Usar el nombre completo del Enum para 'FINALIZADO'
            "WHERE a.estado = DSII.TurismoSustentable.models.EstadoAlquiler.FINALIZADO " +
            "GROUP BY a.bicicleta.tipo, a.usuario.genero " +
            "ORDER BY a.usuario.genero, COUNT(a.id) DESC")
    List<Object[]> contarPreferenciasBicicletaPorGenero();

    // ----------------------------------------------------------------------------------------------------

    /**
     * 2. CANTIDAD DE BICICLETAS ALQUILADAS
     * * Devuelve la cantidad de alquileres que están actualmente en curso (estado INICIADO).
     */
    @Query("SELECT COUNT(a) FROM Alquiler a WHERE a.estado = DSII.TurismoSustentable.models.EstadoAlquiler.INICIADO")
    Long contarBicicletasAlquiladasActuales();

    // ----------------------------------------------------------------------------------------------------

    // MÉTODOS DE BÚSQUEDA PERSONALIZADOS
    List<Alquiler> findByBorradoAlquilerFalse();
    List<Alquiler> findByUsuarioAndBorradoAlquilerFalse(Usuario usuario);
}