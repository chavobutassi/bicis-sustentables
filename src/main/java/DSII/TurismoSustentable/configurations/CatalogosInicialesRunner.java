package DSII.TurismoSustentable.configurations;

import DSII.TurismoSustentable.services.CatalogosInicialesService;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

/** Ejecuta la carga idempotente de catálogos al iniciar la aplicación. */
@Component
public class CatalogosInicialesRunner implements ApplicationRunner {

    private final CatalogosInicialesService catalogosInicialesService;

    public CatalogosInicialesRunner(
            CatalogosInicialesService catalogosInicialesService
    ) {
        this.catalogosInicialesService = catalogosInicialesService;
    }

    @Override
    public void run(ApplicationArguments args) {
        catalogosInicialesService.cargar();
    }
}
