package DSII.TurismoSustentable.models;

import org.hibernate.annotations.GenericGenerator;

import javax.persistence.*;

@Entity
public class Tarjeta {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO, generator = "native")
    @GenericGenerator(name = "native", strategy = "native")
    private int id;

    private String titular;
    private String fechaVencimiento;
    private String tipoTarjeta;
    private String codigoCVV;
    private String tokenPago;

    @ManyToOne
    @JoinColumn(name = "usuario_id")
    private Usuario usuario;

    public Tarjeta() {
    }

    public Tarjeta(String titular, String fechaVencimiento, String tipoTarjeta, String codigoCVV, String tokenPago) {
        this.titular = titular;
        this.fechaVencimiento = fechaVencimiento;
        this.tipoTarjeta = tipoTarjeta;
        this.codigoCVV = codigoCVV;
        this.tokenPago = tokenPago;
    }

    public int getId() {
        return id;
    }

    public String getTitular() {
        return titular;
    }

    public void setTitular(String titular) {
        this.titular = titular;
    }

    public String getFechaVencimiento() {
        return fechaVencimiento;
    }

    public void setFechaVencimiento(String fechaVencimiento) {
        this.fechaVencimiento = fechaVencimiento;
    }

    public String getTipoTarjeta() {
        return tipoTarjeta;
    }

    public void setTipoTarjeta(String tipoTarjeta) {
        this.tipoTarjeta = tipoTarjeta;
    }

    public String getCodigoCVV() {
        return codigoCVV;
    }

    public void setCodigoCVV(String codigoCVV) {
        this.codigoCVV = codigoCVV;
    }

    public String getTokenPago() {
        return tokenPago;
    }

    public void setTokenPago(String tokenPago) {
        this.tokenPago = tokenPago;
    }

    public Usuario getUsuario() {
        return usuario;
    }

    public void setUsuario(Usuario usuario) {
        this.usuario = usuario;
    }
}
