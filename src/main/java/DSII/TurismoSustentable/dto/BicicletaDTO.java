package DSII.TurismoSustentable.dto;

import DSII.TurismoSustentable.models.Bicicleta;

import java.math.BigDecimal;
import java.util.List;

public class BicicletaDTO {

    private int id;
    private String codigoBicicleta;

    private String estado;

    private String ubicacion;

    private String tipo;

    private BigDecimal precio;

    private List<AlquilerDTO> alquileres;

    public BicicletaDTO() {
    }

    public BicicletaDTO(Bicicleta bicicleta) {
        this.id = bicicleta.getId();
        this.codigoBicicleta = bicicleta.getCodigoBicicleta();
        this.estado = bicicleta.getEstado().name();
        this.tipo = bicicleta.getTipo().name();
        this.precio = bicicleta.getPrecioPorHora();

        if (bicicleta.getUbicacionActual() != null) {
            this.ubicacion = bicicleta.getUbicacionActual().getNombre();
        } else {
            this.ubicacion = "Sin Asignar";
        }

        //ALQUILERES
        /*this.alquileres = bicicleta.getAlquileres().stream().map(alquiler ->
                new AlquilerDTO(alquiler)).collect(Collectors.toList());*/
    }

    public int getId() {
        return id;
    }

    public String getCodigoBicicleta() {
        return codigoBicicleta;
    }

    public String getEstado() {
        return estado;
    }

    public String getUbicacion() {
        return ubicacion;
    }
    public String getTipo() {
        return tipo;
    }

    public BigDecimal getPrecio() {
        return precio;
    }

    public List<AlquilerDTO>getAlquileres(){
        return alquileres;
    }
}
