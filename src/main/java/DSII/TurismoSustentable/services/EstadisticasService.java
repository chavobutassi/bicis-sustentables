package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.models.EstadoBicicleta;
import DSII.TurismoSustentable.models.TipoBicicleta;
import DSII.TurismoSustentable.repositories.AlquilerRepository;
import DSII.TurismoSustentable.repositories.BicicletaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class EstadisticasService {

    @Autowired
    private AlquilerRepository alquilerRepository;
    @Autowired
    private BicicletaRepository bicicletaRepository;

    public List<Object[]> getPreferenciasBicicletaPorGenero() {
        // Llama al método del repositorio para obtener las preferencias por género y tipo.
        return alquilerRepository.contarPreferenciasBicicletaPorGenero();
    }

    public Long getBicicletasAlquiladasActuales() {
        // Llama al método del repositorio para contar alquileres en estado INICIADO.
        return alquilerRepository.contarBicicletasAlquiladasActuales();
    }

    public List<Object[]> getBicicletasPorEstado() {
        // Llama al método del repositorio para contar bicicletas por su estado actual.
        return bicicletaRepository.contarBicicletasPorEstado();
    }
}