package DSII.TurismoSustentable.dto;


import DSII.TurismoSustentable.models.Tarjeta;

public class TarjetaDTO {

    private int id;
    private String titular;
    private String fechaVencimiento;
    private String tipoTarjeta;


    public TarjetaDTO(Tarjeta tarjeta) {
        this.id = tarjeta.getId();
        this.titular = tarjeta.getTitular();
        this.fechaVencimiento = tarjeta.getFechaVencimiento();
        this.tipoTarjeta = tarjeta.getTipoTarjeta();
    }

    public int getId() {
        return id;
    }

    public String getTitular() {
        return titular;
    }

    public String getFechaVencimiento() {
        return fechaVencimiento;
    }

    public String getTipoTarjeta() {
        return tipoTarjeta;
    }
}
