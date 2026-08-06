package DSII.TurismoSustentable.controllers;

import DSII.TurismoSustentable.services.EstadisticasService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize; // Importación clave
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import DSII.TurismoSustentable.dto.AlquilerDTO; // Importar DTO
import DSII.TurismoSustentable.repositories.AlquilerRepository; // Importar Repo

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/admin/estadisticas")
// --- CLAVE: Restringe el acceso a todo este controlador solo al rol ADMIN ---
@PreAuthorize("hasAuthority('ADMIN')")
public class AdminController {

    @Autowired
    private EstadisticasService estadisticasService;
    @Autowired
    private AlquilerRepository alquilerRepository;

    @GetMapping("/resumen")
    public ResponseEntity<Map<String, Object>> getResumenEstadistico() {

        Map<String, Object> resumen = new HashMap<>();

        // ... (Llamadas al servicio) ...
        List<Object[]> preferencias = estadisticasService.getPreferenciasBicicletaPorGenero();
        resumen.put("preferencias_por_genero_y_tipo", preferencias);

        Long alquiladas = estadisticasService.getBicicletasAlquiladasActuales();
        resumen.put("bicicletas_alquiladas_actualmente", alquiladas);

        List<Object[]> estados = estadisticasService.getBicicletasPorEstado();
        resumen.put("estados_de_bicicletas", estados);

        return ResponseEntity.ok(resumen);
    }

    //Metodo del admin para hacer GET a todos los alquileres
    @GetMapping("/alquileres-todos")
    public List<AlquilerDTO> getAllAlquileres() {
        // Llama al método del repositorio que trae TODOS (sin filtrar por usuario)
        return alquilerRepository.findByBorradoAlquilerFalse()
                .stream()
                .map(AlquilerDTO::new) // Convierte cada Alquiler a AlquilerDTO
                .collect(Collectors.toList());
    }

}