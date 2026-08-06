package DSII.TurismoSustentable.models;

import javax.persistence.*;
import java.time.LocalDate;
@Entity
public class Suscripcion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @OneToOne
    @JoinColumn(name = "usuario_id")
    private Usuario usuario;

    private LocalDate fechaInicio;
    private LocalDate fechaFin;



}
