package DSII.TurismoSustentable.services;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import DSII.TurismoSustentable.models.Alquiler;
import java.time.format.DateTimeFormatter;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

@Service
public class CorreoService {

    private static final Logger LOGGER =
            LoggerFactory.getLogger(CorreoService.class);

    private static final String BREVO_URL =
            "https://api.brevo.com/v3/smtp/email";

    private final RestTemplate restTemplate =
            new RestTemplate();

    @Value("${brevo.api-key:}")
    private String apiKey;

    @Value("${brevo.sender-email:}")
    private String senderEmail;

    @Value("${brevo.sender-name:Turismo Sustentable}")
    private String senderName;

    public boolean enviarCorreo(
            String destinatario,
            String nombreDestinatario,
            String asunto,
            String contenidoHtml
    ) {

        if (!StringUtils.hasText(apiKey)
                || !StringUtils.hasText(senderEmail)) {

            LOGGER.warn(
                    "Correo no enviado: Brevo todavía no está configurado."
            );

            return false;
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set(
                "api-key",
                apiKey
        );

        Map<String, String> remitente = new HashMap<>();
        remitente.put("name", senderName);
        remitente.put("email", senderEmail);

        Map<String, String> receptor = new HashMap<>();
        receptor.put("email", destinatario);
        receptor.put(
                "name",
                nombreDestinatario != null
                        ? nombreDestinatario
                        : ""
        );

        Map<String, Object> cuerpo = new HashMap<>();
        cuerpo.put("sender", remitente);
        cuerpo.put(
                "to",
                Collections.singletonList(receptor)
        );
        cuerpo.put("subject", asunto);
        cuerpo.put("htmlContent", contenidoHtml);

        HttpEntity<Map<String, Object>> peticion =
                new HttpEntity<>(cuerpo, headers);

        try {
            ResponseEntity<String> respuesta =
                    restTemplate.exchange(
                            BREVO_URL,
                            HttpMethod.POST,
                            peticion,
                            String.class
                    );

            boolean enviado =
                    respuesta.getStatusCode().is2xxSuccessful();

            if (enviado) {
                LOGGER.info(
                        "Correo enviado correctamente mediante Brevo."
                );
            }

            return enviado;

        } catch (RestClientException e) {
            /*
             * Un fallo del correo no debe cancelar un registro
             * o un alquiler que ya se realizó correctamente.
             */
            LOGGER.error(
                    "No se pudo enviar el correo mediante Brevo: {}",
                    e.getMessage()
            );

            return false;
        }
    }

    public boolean enviarBienvenida(
            String email,
            String nombre
    ) {

        String nombreSeguro = escaparHtml(nombre);

        String contenidoHtml =
                "<div style=\"font-family:Arial,sans-serif;"
                        + "max-width:600px;margin:auto;"
                        + "padding:24px;color:#24352b;\">"
                        + "<h1 style=\"color:#198754;\">"
                        + "¡Bienvenido a Turismo Sustentable!"
                        + "</h1>"
                        + "<p>Hola <strong>"
                        + nombreSeguro
                        + "</strong>,</p>"
                        + "<p>Tu cuenta fue registrada correctamente.</p>"
                        + "<p>Ya podés iniciar sesión, consultar las bicicletas "
                        + "disponibles y realizar tus viajes.</p>"
                        + "<hr>"
                        + "<small>Turismo Sustentable</small>"
                        + "</div>";

        return enviarCorreo(
                email,
                nombre,
                "Bienvenido a Turismo Sustentable",
                contenidoHtml
        );
    }

    public boolean enviarComprobanteInicio(
            Alquiler alquiler
    ) {

        DateTimeFormatter formatoFecha =
                DateTimeFormatter.ofPattern(
                        "dd/MM/yyyy HH:mm"
                );

        String nombre = escaparHtml(
                alquiler.getUsuario().getNombre()
        );

        String codigoBicicleta = escaparHtml(
                alquiler.getBicicleta().getCodigoBicicleta()
        );

        String estacionRetiro = escaparHtml(
                alquiler.getUbicacionRetiro().getNombre()
        );

        String contenidoHtml =
                "<div style=\"font-family:Arial,sans-serif;"
                        + "max-width:600px;margin:auto;"
                        + "padding:24px;color:#24352b;\">"
                        + "<h1 style=\"color:#198754;\">"
                        + "Comprobante de alquiler"
                        + "</h1>"
                        + "<p>Hola <strong>" + nombre + "</strong>,</p>"
                        + "<p>Tu alquiler comenzó correctamente.</p>"
                        + "<ul>"
                        + "<li><strong>Número:</strong> "
                        + alquiler.getId() + "</li>"
                        + "<li><strong>Bicicleta:</strong> "
                        + codigoBicicleta + "</li>"
                        + "<li><strong>Estación de retiro:</strong> "
                        + estacionRetiro + "</li>"
                        + "<li><strong>Inicio:</strong> "
                        + alquiler.getFechaInicio().format(formatoFecha)
                        + "</li>"
                        + "<li><strong>Precio por hora aplicado:</strong> US$ "
                        + alquiler.getPrecioPorHoraAplicado()
                        + "</li>"
                        + "<li><strong>Costo estimado:</strong> US$ "
                        + alquiler.getCostoTotal()
                        + "</li>"
                        + "</ul>"
                        + "<p>El importe definitivo se calculará "
                        + "cuando devuelvas la bicicleta.</p>"
                        + "<hr>"
                        + "<small>Turismo Sustentable</small>"
                        + "</div>";

        return enviarCorreo(
                alquiler.getUsuario().getEmail(),
                alquiler.getUsuario().getNombre(),
                "Comprobante de inicio de alquiler",
                contenidoHtml
        );
    }

    public boolean enviarComprobanteFinalizacion(
            Alquiler alquiler
    ) {

        DateTimeFormatter formatoFecha =
                DateTimeFormatter.ofPattern(
                        "dd/MM/yyyy HH:mm"
                );

        String nombre = escaparHtml(
                alquiler.getUsuario().getNombre()
        );

        String codigoBicicleta = escaparHtml(
                alquiler.getBicicleta().getCodigoBicicleta()
        );

        String estacionDevolucion = escaparHtml(
                alquiler.getUbicacionDevolucion().getNombre()
        );

        String contenidoHtml =
                "<div style=\"font-family:Arial,sans-serif;"
                        + "max-width:600px;margin:auto;"
                        + "padding:24px;color:#24352b;\">"
                        + "<h1 style=\"color:#198754;\">"
                        + "Ticket de devolución"
                        + "</h1>"
                        + "<p>Hola <strong>" + nombre + "</strong>,</p>"
                        + "<p>Tu alquiler fue finalizado correctamente.</p>"
                        + "<ul>"
                        + "<li><strong>Número:</strong> "
                        + alquiler.getId() + "</li>"
                        + "<li><strong>Bicicleta:</strong> "
                        + codigoBicicleta + "</li>"
                        + "<li><strong>Inicio:</strong> "
                        + alquiler.getFechaInicio().format(formatoFecha)
                        + "</li>"
                        + "<li><strong>Devolución:</strong> "
                        + alquiler.getFechaFin().format(formatoFecha)
                        + "</li>"
                        + "<li><strong>Estación de devolución:</strong> "
                        + estacionDevolucion + "</li>"
                        + "<li><strong>Total en USD:</strong> US$ "
                        + alquiler.getCostoTotal()
                        + "</li>"
                        + "<li><strong>Total en ARS:</strong> $ "
                        + alquiler.getCostoTotalArs()
                        + "</li>"
                        + "</ul>"
                        + "<p>Gracias por elegir una forma sustentable "
                        + "de recorrer la ciudad.</p>"
                        + "<hr>"
                        + "<small>Turismo Sustentable</small>"
                        + "</div>";

        return enviarCorreo(
                alquiler.getUsuario().getEmail(),
                alquiler.getUsuario().getNombre(),
                "Ticket de finalización de alquiler",
                contenidoHtml
        );
    }

    public boolean enviarRecuperacionPassword(
            String email,
            String nombre,
            String enlaceRecuperacion
    ) {

        String nombreSeguro = escaparHtml(nombre);
        String enlaceSeguro = escaparHtml(enlaceRecuperacion);

        String contenidoHtml =
                "<div style=\"font-family:Arial,sans-serif;"
                        + "max-width:600px;margin:auto;"
                        + "padding:24px;color:#24352b;\">"
                        + "<h1 style=\"color:#198754;\">"
                        + "Recuperación de contraseña"
                        + "</h1>"
                        + "<p>Hola <strong>"
                        + nombreSeguro
                        + "</strong>,</p>"
                        + "<p>Recibimos una solicitud para cambiar "
                        + "la contraseña de tu cuenta.</p>"
                        + "<p style=\"margin:30px 0;\">"
                        + "<a href=\"" + enlaceSeguro + "\" "
                        + "style=\"background:#198754;color:white;"
                        + "padding:12px 20px;text-decoration:none;"
                        + "border-radius:20px;\">"
                        + "Cambiar contraseña"
                        + "</a>"
                        + "</p>"
                        + "<p>Este enlace vence dentro de 30 minutos.</p>"
                        + "<p>Si no solicitaste el cambio, podés ignorar "
                        + "este mensaje.</p>"
                        + "<hr>"
                        + "<small>Turismo Sustentable</small>"
                        + "</div>";

        return enviarCorreo(
                email,
                nombre,
                "Recuperación de contraseña",
                contenidoHtml
        );
    }

    private String escaparHtml(String valor) {

        if (valor == null) {
            return "";
        }

        return valor
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&#39;");
    }

}