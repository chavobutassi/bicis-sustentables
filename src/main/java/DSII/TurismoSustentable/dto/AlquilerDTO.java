package DSII.TurismoSustentable.dto;

import DSII.TurismoSustentable.models.Alquiler;
import java.math.BigDecimal;
import java.time.LocalDateTime;

public class AlquilerDTO {

    private int id;
    private LocalDateTime fechaInicio;
    private LocalDateTime fechaFin;
    private BigDecimal costoTotal;
    private BigDecimal costoTotalArs;
    private String estado;
    private int usuarioId;
    private int bicicletaId;
    private String codigoBicicleta;

    // Campos de ubicación
    private String ubicacionRetiro;
    private String ubicacionDevolucion;

    public AlquilerDTO() {
    }

    // CONSTRUCTOR
    public AlquilerDTO(Alquiler alquiler){
        this.id = alquiler.getId();
        this.fechaInicio = alquiler.getFechaInicio();
        this.fechaFin = alquiler.getFechaFin();
        this.costoTotal = alquiler.getCostoTotal();
        this.costoTotalArs = alquiler.getCostoTotalArs();
        this.estado = alquiler.getEstado().name();
        this.usuarioId = alquiler.getUsuario().getId();
        this.bicicletaId = alquiler.getBicicleta().getId();

        // Importante: Validar que la bici no sea null (por seguridad)
        if (alquiler.getBicicleta() != null) {
            this.codigoBicicleta = alquiler.getBicicleta().getCodigoBicicleta();
        }

        // Asignación de nombres de estaciones
        if (alquiler.getUbicacionRetiro() != null) {
            this.ubicacionRetiro = alquiler.getUbicacionRetiro().getNombre();
        }
        if (alquiler.getUbicacionDevolucion() != null) {
            this.ubicacionDevolucion = alquiler.getUbicacionDevolucion().getNombre();
        }
    }

    public int getId() { return id; }
    public LocalDateTime getFechaInicio() { return fechaInicio; }
    public LocalDateTime getFechaFin() { return fechaFin; }
    public BigDecimal getCostoTotal() { return costoTotal; }
    public String getEstado() { return estado; }
    public int getUsuarioId() { return usuarioId; }
    public int getBicicletaId() { return bicicletaId; }
    public String getCodigoBicicleta() { return codigoBicicleta; }

    public String getUbicacionRetiro() { return ubicacionRetiro; }
    public String getUbicacionDevolucion() { return ubicacionDevolucion; }
    public BigDecimal getCostoTotalArs() {
        return costoTotalArs;
    }
}