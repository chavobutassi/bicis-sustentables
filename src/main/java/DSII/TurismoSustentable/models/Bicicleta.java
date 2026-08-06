package DSII.TurismoSustentable.models;

import javax.persistence.*;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.util.Set;

@Entity
public class Bicicleta {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @NotBlank(message = "El código es obligatorio.")
    @Column(unique = true)
    private String codigoBicicleta;

    @NotNull(message = "El tipo de bicicleta es obligatorio.")
    @Enumerated(EnumType.STRING)
    private TipoBicicleta tipo;

    @NotNull(message = "El estado es obligatorio.")
    @Enumerated(EnumType.STRING)
    private EstadoBicicleta estado;

    // --- CAMPOS ADICIONALES REQUERIDOS ---

    @NotNull(message = "El precio por hora es obligatorio.")
    private BigDecimal precioPorHora; // Para calcular el costo del alquiler

    @ManyToOne(fetch = FetchType.LAZY, optional = true)
    @JoinColumn(name = "estacion_id", nullable = true)
    private Estacion ubicacionActual;

    private boolean borradoBici = false; // Para el borrado lógico
    // ------------------------------------

    @OneToMany(mappedBy = "bicicleta", fetch = FetchType.LAZY)
    private Set<Alquiler> alquileres;

    // CONSTRUCTORES
    public Bicicleta() {
    }

    public Bicicleta(String codigoBicicleta, TipoBicicleta tipo, EstadoBicicleta estado, BigDecimal precioPorHora, Estacion ubicacionActual) {
        this.codigoBicicleta = codigoBicicleta;
        this.tipo = tipo;
        this.estado = estado;
        this.precioPorHora = precioPorHora;
        this.ubicacionActual = ubicacionActual;
        this.borradoBici = false;
    }

    // GETTERS Y SETTERS

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getCodigoBicicleta() {
        return codigoBicicleta;
    }

    public void setCodigoBicicleta(String codigoBicicleta) {
        this.codigoBicicleta = codigoBicicleta;
    }

    public TipoBicicleta getTipo() {
        return tipo;
    }

    public void setTipo(TipoBicicleta tipo) {
        this.tipo = tipo;
    }

    public EstadoBicicleta getEstado() {
        return estado;
    }

    public void setEstado(EstadoBicicleta estado) {
        this.estado = estado;
    }

    // Getters y Setters de los campos adicionales

    public BigDecimal getPrecioPorHora() {
        return precioPorHora;
    }

    public void setPrecioPorHora(BigDecimal precioPorHora) {
        this.precioPorHora = precioPorHora;
    }

    public Estacion getUbicacionActual() {
        return ubicacionActual;
    }

    public void setUbicacionActual(Estacion ubicacionActual) {
        this.ubicacionActual = ubicacionActual;
    }

    public boolean isBorradoBici() {
        return borradoBici;
    }

    public void setBorradoBici(boolean borradoBici) {
        this.borradoBici = borradoBici;
    }

    // Getters y Setters de la relación

    public Set<Alquiler> getAlquileres() {
        return alquileres;
    }

    public void setAlquileres(Set<Alquiler> alquileres) {
        this.alquileres = alquileres;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Bicicleta bicicleta = (Bicicleta) o;

        // Comparamos usando el identificador único de negocio
        return codigoBicicleta != null ? codigoBicicleta.equals(bicicleta.codigoBicicleta) : bicicleta.codigoBicicleta == null;
    }

    @Override
    public int hashCode() {
        // Usamos el mismo campo para el hashCode
        return codigoBicicleta != null ? codigoBicicleta.hashCode() : 0;
    }

}