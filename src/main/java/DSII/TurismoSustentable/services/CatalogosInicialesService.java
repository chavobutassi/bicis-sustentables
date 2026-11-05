package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.models.Genero;
import DSII.TurismoSustentable.models.Pais;
import DSII.TurismoSustentable.models.Rol;
import DSII.TurismoSustentable.models.TipoDocumento;
import DSII.TurismoSustentable.repositories.GeneroRepository;
import DSII.TurismoSustentable.repositories.PaisRepository;
import DSII.TurismoSustentable.repositories.RolRepository;
import DSII.TurismoSustentable.repositories.TipoDocumentoRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Locale;

/**
 * Carga los valores iniciales aprobados de los catálogos del DER v5.
 * Es idempotente: solo inserta los códigos que todavía no existen y
 * nunca modifica ni elimina registros ya presentes.
 */
@Service
public class CatalogosInicialesService {

    private static final String[] GENEROS = {
            "FEMENINO", "MASCULINO", "NO_BINARIO", "OTRO", "PREFIERO_NO_DECIR"
    };

    private static final String[][] TIPOS_DOCUMENTO = {
            {"DNI", "Documento Nacional de Identidad"},
            {"PASAPORTE", "Pasaporte"}
    };

    private static final String[] ROLES = {"CLIENTE", "ADMIN", "TECNICO"};

    private static final Locale IDIOMA_NOMBRES = new Locale("es", "AR");

    private final GeneroRepository generoRepository;
    private final TipoDocumentoRepository tipoDocumentoRepository;
    private final PaisRepository paisRepository;
    private final RolRepository rolRepository;

    public CatalogosInicialesService(
            GeneroRepository generoRepository,
            TipoDocumentoRepository tipoDocumentoRepository,
            PaisRepository paisRepository,
            RolRepository rolRepository
    ) {
        this.generoRepository = generoRepository;
        this.tipoDocumentoRepository = tipoDocumentoRepository;
        this.paisRepository = paisRepository;
        this.rolRepository = rolRepository;
    }

    @Transactional
    public void cargar() {
        for (String codigo : GENEROS) {
            if (generoRepository.findByCodigo(codigo).isEmpty()) {
                generoRepository.save(new Genero(codigo));
            }
        }

        for (String[] tipo : TIPOS_DOCUMENTO) {
            if (tipoDocumentoRepository.findByCodigo(tipo[0]).isEmpty()) {
                tipoDocumentoRepository.save(
                        new TipoDocumento(tipo[0], tipo[1])
                );
            }
        }

        for (String codigo : ROLES) {
            if (rolRepository.findByCodigo(codigo).isEmpty()) {
                rolRepository.save(new Rol(codigo));
            }
        }

        // Códigos ISO 3166-1 alfa-2 reales, con nombre en español.
        for (String codigo : Locale.getISOCountries()) {
            if (paisRepository.findByCodigo(codigo).isEmpty()) {
                String nombre = new Locale("", codigo)
                        .getDisplayCountry(IDIOMA_NOMBRES);
                paisRepository.save(new Pais(codigo, nombre));
            }
        }
    }
}
