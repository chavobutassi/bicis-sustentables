package DSII.TurismoSustentable;

import DSII.TurismoSustentable.models.*; // Importamos todos los modelos
import DSII.TurismoSustentable.repositories.*; // Importamos todos los repositorios
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import org.springframework.security.crypto.password.PasswordEncoder;

@SpringBootApplication
public class TurismoSustentableApplication {

	@Autowired
	private PasswordEncoder passwordEncoder;

	@Autowired
	private UsuarioRepository usuarioRepository;

	// MAIN
	public static void main(String[] args) {
		SpringApplication.run(TurismoSustentableApplication.class, args);
	}

	// CommandLineRunner para ejecutar codigo al inicio
	@Bean
	public CommandLineRunner initData(EstacionRepository estacionRepository,
									  UsuarioRepository usuarioRepository,
									  BicicletaRepository bicicletaRepository,
									  AlquilerRepository alquilerRepository,
									  TarjetaRepository tarjetaRepository) {

		// Clave en texto plano para pruebas
		String claveHernan = "admin123";
		String claveBelen = "clave456";
		String claveKarim = "clave789";

		return args -> {

			// --- 0. ESTACIONES ---
			Estacion estacionPlaza, estacionPunta, estacionMision;

			// Verificamos si ya existen para no duplicarlas al reiniciar
			if (estacionRepository.count() == 0) {
				// Se agregan las coordenadas reales (Latitud, Longitud) de Río Grande

				// Plaza Cien Años (Centro, zona Av. San Martín)
				estacionPlaza = new Estacion("Plaza Cien Años", "Sebastián Elcano, Río Grande, Tierra del Fuego", 20, -53.773389631284616, -67.70135546614691);

				// Reserva Punta Popper (Margen sur de la desembocadura del río)
				estacionPunta = new Estacion("Reserva Punta Popper", "Río Grande, Tierra del Fuego", 15, -53.79183646859147, -67.67227667681732);

				// Misión Salesiana (Al norte de la ciudad, por la Ruta 3)
				estacionMision = new Estacion("Misión Salesiana", "RN3 Km. 2.835, V9420 Río Grande, Tierra del Fuego", 10, -53.72376827208061, -67.7981224590526);

				estacionRepository.save(estacionPlaza);
				estacionRepository.save(estacionPunta);
				estacionRepository.save(estacionMision);
			} else {
				// Si ya existen, las buscamos para usarlas en las bicis (evita NullPointerException)
				estacionPlaza = estacionRepository.findByNombre("Plaza Cien Años").orElse(null);
				estacionPunta = estacionRepository.findByNombre("Reserva Punta Popper").orElse(null);
				estacionMision = estacionRepository.findByNombre("Misión Salesiana").orElse(null);
			}

			// --- 1. USUARIOS ---
			if (usuarioRepository.findAll().isEmpty()) {

				// Usuario 1: ADMIN
				Usuario usuario1 = new Usuario("Hernan", "Montiel", "hernanm@gmail.com",
						passwordEncoder.encode(claveHernan),
						LocalDate.of(1985, 5, 20),GeneroUsuario.MASCULINO, true, Rol.ADMIN);

				// Usuario 2 y 3: CLIENTE
				Usuario usuario2 = new Usuario("Belen", "Ruiz", "belenr@gmail.com",
						passwordEncoder.encode(claveBelen),
						LocalDate.of(1992, 11, 15), GeneroUsuario.FEMENINO, true);

				Usuario usuario3 = new Usuario("Karim", "Homsi", "karimh@gmail.com",
						passwordEncoder.encode(claveKarim),
						LocalDate.of(1997, 9, 5), GeneroUsuario.OTRO, true);

				usuarioRepository.save(usuario1);
				usuarioRepository.save(usuario2);
				usuarioRepository.save(usuario3);
			}

            // --- 2. BICICLETAS
            if (bicicletaRepository.findAll().isEmpty() && estacionPlaza != null && estacionPunta != null && estacionMision != null) {

                Bicicleta bicicleta1 = new Bicicleta("BM-01", TipoBicicleta.MONTANA,
                        EstadoBicicleta.DISPONIBLE, new BigDecimal("9.00"), estacionPlaza);

                Bicicleta bicicleta2 = new Bicicleta("BP-02", TipoBicicleta.PASEO,
                        EstadoBicicleta.MANTENIMIENTO, new BigDecimal("7.50"), estacionPlaza);

                Bicicleta bicicleta3 = new Bicicleta("BEL-03", TipoBicicleta.ELECTRICA,
                        EstadoBicicleta.DISPONIBLE, new BigDecimal("12.00"), estacionMision);

                Bicicleta bicicleta4 = new Bicicleta("BM-04", TipoBicicleta.MONTANA,
                        EstadoBicicleta.DISPONIBLE, new BigDecimal("9.00"), estacionPlaza);

                Bicicleta bicicleta5 = new Bicicleta("BP-05", TipoBicicleta.PASEO,
                        EstadoBicicleta.DISPONIBLE, new BigDecimal("7.50"), estacionPlaza);

                Bicicleta bicicleta6 = new Bicicleta("BEL-06", TipoBicicleta.ELECTRICA,
                        EstadoBicicleta.DISPONIBLE, new BigDecimal("12.00"), estacionPlaza);

                Bicicleta bicicleta7 = new Bicicleta("BM-07", TipoBicicleta.MONTANA,
                        EstadoBicicleta.DISPONIBLE, new BigDecimal("9.00"), estacionPlaza);

                Bicicleta bicicleta8 = new Bicicleta("BP-08", TipoBicicleta.PASEO,
                        EstadoBicicleta.DISPONIBLE, new BigDecimal("7.50"), estacionMision);

                Bicicleta bicicleta9 = new Bicicleta("BM-09", TipoBicicleta.MONTANA,
                        EstadoBicicleta.DISPONIBLE, new BigDecimal("9.00"), estacionMision);

                Bicicleta bicicleta10 = new Bicicleta("BP-10", TipoBicicleta.PASEO,
                        EstadoBicicleta.INACTIVA, new BigDecimal("7.00"), // <-- Bici Inactiva
                        estacionMision);

				Bicicleta bicicleta11 = new Bicicleta("BM-11", TipoBicicleta.MONTANA,
						EstadoBicicleta.DISPONIBLE, new BigDecimal("9.00"), estacionPlaza);

				Bicicleta bicicleta12 = new Bicicleta("BP-12", TipoBicicleta.PASEO,
						EstadoBicicleta.DISPONIBLE, new BigDecimal("7.50"), estacionPlaza);

                bicicletaRepository.save(bicicleta1);
                bicicletaRepository.save(bicicleta2);
                bicicletaRepository.save(bicicleta3);
                bicicletaRepository.save(bicicleta4);
                bicicletaRepository.save(bicicleta5);
                bicicletaRepository.save(bicicleta6);
                bicicletaRepository.save(bicicleta7);
                bicicletaRepository.save(bicicleta8);
                bicicletaRepository.save(bicicleta9);
                bicicletaRepository.save(bicicleta10);
				bicicletaRepository.save(bicicleta11);
				bicicletaRepository.save(bicicleta12);
            }

			// --- 3. TARJETAS ---
			if (tarjetaRepository.findAll().isEmpty()) {
				Usuario usuario = usuarioRepository.findByEmail("octavio@gmail.com").orElse(null);
				Usuario usuario2 = usuarioRepository.findByEmail("elchasqui@gmail.com").orElse(null);

				if (usuario != null) {
					Tarjeta tarjeta1 = new Tarjeta("Hernan Montiel", "12/25", "VISA", "123", "tok123");
					Tarjeta tarjeta2 = new Tarjeta("Hernan Montiel", "10/24", "MASTERCARD", "456", "tok456");

					usuario.addTarjeta(tarjeta1);
					usuario.addTarjeta(tarjeta2);

					tarjetaRepository.save(tarjeta1);
					tarjetaRepository.save(tarjeta2);
					usuarioRepository.save(usuario);
				}
				if (usuario2 != null) {
					Tarjeta tarjeta3 = new Tarjeta("Belen Ruiz", "01/26", "VISA", "321", "tok987");
					usuario2.addTarjeta(tarjeta3);
					tarjetaRepository.save(tarjeta3);
					usuarioRepository.save(usuario2);
				}
			}

			// --- 4. ALQUILERES (CORRECCIÓN: Usamos los objetos Estacion) ---
			if (alquilerRepository.findAll().isEmpty()) {
				Usuario usuario = usuarioRepository.findByEmail("octavio@gmail.com").orElse(null);
				Bicicleta bici1 = bicicletaRepository.findByCodigoBicicleta("BM-01").orElse(null);
				Bicicleta bici3 = bicicletaRepository.findByCodigoBicicleta("BEL-03").orElse(null);

				// Aseguramos que usuario, bicis Y estaciones existan
				if (usuario != null && bici1 != null && bici3 != null && estacionPlaza != null) {
					LocalDateTime inicio = LocalDateTime.now().minusDays(1);
					LocalDateTime fin = inicio.plusHours(4);

					BigDecimal costo = bici1.getPrecioPorHora().multiply(new BigDecimal("4"));

					// Alquiler ACTIVO / INICIADO
					// Usamos el constructor: Alquiler(usuario, bicicleta, ubicacionRetiro)
					Alquiler alquilerActivo = new Alquiler(usuario, bici3, estacionMision); // <-- Objeto Estacion

					// Alquiler FINALIZADO
					// Usamos el constructor completo pasando las Estaciones
					Alquiler alquilerFinalizado = new Alquiler(usuario, bici1, inicio, fin, costo,
							EstadoAlquiler.FINALIZADO,
							estacionPlaza,  // <-- Retiro: Plaza
							estacionPunta); // <-- Devolución: Punta Popper

					// El estado de la bici3 debe ser ALQUILADA (coherencia de datos)
					bici3.setEstado(EstadoBicicleta.ALQUILADA);

					usuario.addAlquiler(alquilerActivo);
					usuario.addAlquiler(alquilerFinalizado);

					alquilerRepository.save(alquilerActivo);
					alquilerRepository.save(alquilerFinalizado);
					usuarioRepository.save(usuario);
					bicicletaRepository.save(bici3);
					bicicletaRepository.save(bici1);
				}
			}
		};
	}
}