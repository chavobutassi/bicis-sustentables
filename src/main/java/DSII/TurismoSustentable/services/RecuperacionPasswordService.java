package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.Locale;

@Service
public class RecuperacionPasswordService {

    private final UsuarioRepository usuarioRepository;
    private final PasswordEncoder passwordEncoder;
    private final CorreoService correoService;

    private final SecureRandom secureRandom =
            new SecureRandom();

    @Value("${app.base-url}")
    private String baseUrl;

    public RecuperacionPasswordService(
            UsuarioRepository usuarioRepository,
            PasswordEncoder passwordEncoder,
            CorreoService correoService
    ) {
        this.usuarioRepository = usuarioRepository;
        this.passwordEncoder = passwordEncoder;
        this.correoService = correoService;
    }

    public void solicitarRecuperacion(String email) {

        if (email == null || email.trim().isEmpty()) {
            return;
        }

        String emailNormalizado = email
                .trim()
                .toLowerCase(Locale.ROOT);

        /*
         * Si el correo no existe, no se informa el error.
         * evita revelar qué emails están registrados.
         */
        Usuario usuario = usuarioRepository
                .findByEmail(emailNormalizado)
                .filter(Usuario::isActivo)
                .orElse(null);

        if (usuario == null) {
            return;
        }

        String tokenOriginal = generarTokenSeguro();
        String hashToken = calcularHash(tokenOriginal);

        usuario.setTokenRecuperacion(hashToken);
        usuario.setVencimientoTokenRecuperacion(
                LocalDateTime.now().plusMinutes(30)
        );

        usuarioRepository.saveAndFlush(usuario);

        String urlBase = baseUrl.endsWith("/")
                ? baseUrl.substring(0, baseUrl.length() - 1)
                : baseUrl;

        String enlace = urlBase
                + "/restablecer-password.html?token="
                + tokenOriginal;

        correoService.enviarRecuperacionPassword(
                usuario.getEmail(),
                usuario.getPersona().getNombre(),
                enlace
        );
    }

    public void restablecerPassword(
            String tokenOriginal,
            String nuevaPassword
    ) {

        if (tokenOriginal == null
                || tokenOriginal.trim().isEmpty()) {

            throw new IllegalArgumentException(
                    "El enlace de recuperación no es válido."
            );
        }

        validarPassword(nuevaPassword);

        String hashToken = calcularHash(
                tokenOriginal.trim()
        );

        Usuario usuario = usuarioRepository
                .findByTokenRecuperacion(hashToken)
                .orElseThrow(() ->
                        new IllegalArgumentException(
                                "El enlace de recuperación no es válido."
                        )
                );

        LocalDateTime vencimiento =
                usuario.getVencimientoTokenRecuperacion();

        if (vencimiento == null
                || vencimiento.isBefore(LocalDateTime.now())) {

            usuario.setTokenRecuperacion(null);
            usuario.setVencimientoTokenRecuperacion(null);
            usuarioRepository.saveAndFlush(usuario);

            throw new IllegalArgumentException(
                    "El enlace de recuperación venció."
            );
        }

        if (!usuario.isActivo()) {
            throw new IllegalArgumentException(
                    "La cuenta no se encuentra activa."
            );
        }

        usuario.setPassword(
                passwordEncoder.encode(nuevaPassword)
        );

        /*
         * El token queda inutilizado inmediatamente después
         * de cambiar la contraseña.
         */
        usuario.setTokenRecuperacion(null);
        usuario.setVencimientoTokenRecuperacion(null);

        usuarioRepository.saveAndFlush(usuario);
    }

    private String generarTokenSeguro() {

        byte[] bytes = new byte[32];
        secureRandom.nextBytes(bytes);

        return Base64.getUrlEncoder()
                .withoutPadding()
                .encodeToString(bytes);
    }

    private String calcularHash(String valor) {

        try {
            MessageDigest digest =
                    MessageDigest.getInstance("SHA-256");

            byte[] hash = digest.digest(
                    valor.getBytes(StandardCharsets.UTF_8)
            );

            StringBuilder resultado =
                    new StringBuilder();

            for (byte parte : hash) {
                resultado.append(
                        String.format(
                                "%02x",
                                parte & 0xff
                        )
                );
            }

            return resultado.toString();

        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(
                    "No se pudo proteger el token.",
                    e
            );
        }
    }

    private void validarPassword(String password) {

        if (password == null
                || !password.matches(
                "^(?=.*[a-z])(?=.*[A-Z])"
                        + "(?=.*[!@#$&*])"
                        + "(?=\\S+$).{6,64}$"
        )) {

            throw new IllegalArgumentException(
                    "La clave debe tener entre 6 y 64 caracteres, "
                            + "una minúscula, una mayúscula, "
                            + "un carácter especial y ningún espacio."
            );
        }
    }
}