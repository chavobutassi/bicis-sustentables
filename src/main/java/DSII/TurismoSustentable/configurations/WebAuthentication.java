package DSII.TurismoSustentable.configurations;

import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.authentication.configuration.GlobalAuthenticationConfigurerAdapter;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.authentication.DisabledException;

@Configuration
class WebAuthentication extends GlobalAuthenticationConfigurerAdapter {

    @Autowired
    UsuarioRepository usuarioRepository;

    @Override
    public void init(AuthenticationManagerBuilder auth) throws Exception {
        auth.userDetailsService(inputName -> {
            Usuario usuario = usuarioRepository.findByEmail(inputName)
                    .orElse(null);

            if (usuario != null) {

                // --- ¡VERIFICACIÓN DE ESTADO ACTIVO! ---
                if (!usuario.isActivo()) {
                    // Si el usuario está borrado lógicamente, lo rechazamos.
                    throw new DisabledException("La cuenta para " + inputName + " ha sido desactivada.");
                }
                // ----------------------------------------

                // Si está activo, continuamos
                return new User(usuario.getEmail(), usuario.getPassword(),
                        AuthorityUtils.createAuthorityList(usuario.getRol().name()));
            } else {
                throw new UsernameNotFoundException("Usuario desconocido: " + inputName);
            }
        });
    }
}