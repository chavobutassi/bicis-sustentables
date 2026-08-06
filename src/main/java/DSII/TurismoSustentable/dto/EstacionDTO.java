package DSII.TurismoSustentable.dto;

import DSII.TurismoSustentable.models.Estacion;
import DSII.TurismoSustentable.models.EstadoBicicleta;

public class EstacionDTO {

    private int id;
    private String nombre;
    private String direccion;
    private int capacidad;
    private Double latitud;
    private Double longitud;
    private int bicicletasDisponibles;
    private int espaciosLibres;

    public EstacionDTO(Estacion estacion) {
        this.id = estacion.getId();
        this.nombre = estacion.getNombre();
        this.direccion = estacion.getDireccion();
        this.capacidad = estacion.getCapacidad();

        // Mapeamos las coordenadas
        this.latitud = estacion.getLatitud();
        this.longitud = estacion.getLongitud();

        if (estacion.getBicicletasEnEstacion() != null) {

            // Bicicletas no eliminadas que pueden alquilarse
            this.bicicletasDisponibles =
                    (int) estacion.getBicicletasEnEstacion()
                            .stream()
                            .filter(b -> !b.isBorradoBici())
                            .filter(b ->
                                    b.getEstado()
                                            == EstadoBicicleta.DISPONIBLE
                            )
                            .count();

            // Todas las bicicletas físicas no eliminadas ocupan espacio, incluyendo mantenimiento e inactivas.
            long bicicletasFisicas =
                    estacion.getBicicletasEnEstacion()
                            .stream()
                            .filter(b -> !b.isBorradoBici())
                            .count();

            this.espaciosLibres = Math.max(
                    0,
                    this.capacidad - (int) bicicletasFisicas
            );

        } else {
            this.bicicletasDisponibles = 0;
            this.espaciosLibres = this.capacidad;
        }
    }

    // GETTERS
    public int getId() {
        return id;
    }

    public String getNombre() {
        return nombre;
    }

    public String getDireccion() {
        return direccion;
    }

    public int getCapacidad() {
        return capacidad;
    }

    public Double getLatitud() {
        return latitud;
    }

    public Double getLongitud() {
        return longitud;
    }

    public int getBicicletasDisponibles() {
        return bicicletasDisponibles;
    }

    public int getEspaciosLibres() {
        return espaciosLibres;
    }
}