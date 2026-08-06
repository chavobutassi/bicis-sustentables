package DSII.TurismoSustentable.configurations;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.logout.HttpStatusReturningLogoutSuccessHandler;
import org.springframework.security.web.WebAttributes;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import org.springframework.http.HttpMethod;

@EnableWebSecurity
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class WebAuthorization {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {

// REGLAS DE AUTORIZACIÓN
        http.authorizeRequests()

                // 1. RECURSOS PÚBLICOS
                .antMatchers(
                        "/",
                        "/index.html",
                        "/registro.html",
                        "/css/**",
                        "/js/**",
                        "/img/**",
                        "/*.ico"
                ).permitAll()

                // 2. AUTENTICACIÓN Y REGISTRO
                .antMatchers(
                        HttpMethod.POST,
                        "/api/usuarios",
                        "/api/login",
                        "/api/logout"
                ).permitAll()

                // El mapa público necesita consultar las estaciones
                .antMatchers(
                        HttpMethod.GET,
                        "/api/estaciones"
                ).permitAll()

                // 3. PÁGINAS PRIVADAS
                .antMatchers(
                        "/alquiler.html",
                        "/mis_alquileres.html"
                ).hasAnyAuthority("ADMIN", "CLIENTE")

                .antMatchers(
                        "/admin.html"
                ).hasAuthority("ADMIN")

                // 4. DATOS DEL USUARIO ACTUAL
                // Esta regla debe estar antes de /api/usuarios/**
                .antMatchers(
                        HttpMethod.GET,
                        "/api/usuarios/actual"
                ).hasAnyAuthority("ADMIN", "CLIENTE")

                // 5. OPERACIONES PERMITIDAS PARA CLIENTES
                .antMatchers(
                        HttpMethod.GET,
                        "/api/alquileres",
                        "/api/cotizacion",
                        "/api/bicicletas/disponibles"
                ).hasAnyAuthority("ADMIN", "CLIENTE")

                .antMatchers(
                        HttpMethod.POST,
                        "/api/alquileres"
                ).hasAnyAuthority("ADMIN", "CLIENTE")

                .antMatchers(
                        HttpMethod.PATCH,
                        "/api/alquileres/finalizar/**"
                ).hasAnyAuthority("ADMIN", "CLIENTE")

                // 6. CONSULTAS DE USUARIOS: SOLO ADMIN
                .antMatchers(
                        HttpMethod.GET,
                        "/api/usuarios",
                        "/api/usuarios/**"
                ).hasAuthority("ADMIN")

                // 7. ENDPOINTS ADMINISTRATIVOS
                .antMatchers(
                        "/api/admin/**"
                ).hasAuthority("ADMIN")

                // Cualquier otro GET de la API será administrativo
                .antMatchers(
                        HttpMethod.GET,
                        "/api/**"
                ).hasAuthority("ADMIN")

                // Cualquier otra alta será administrativa
                .antMatchers(
                        HttpMethod.POST,
                        "/api/**"
                ).hasAuthority("ADMIN")

                // Todas las modificaciones restantes son administrativas
                .antMatchers(
                        HttpMethod.PUT,
                        "/api/**"
                ).hasAuthority("ADMIN")

                // Todos los borrados son administrativos
                .antMatchers(
                        HttpMethod.DELETE,
                        "/api/**"
                ).hasAuthority("ADMIN")

                // Cualquier ruta o metodo no declarado queda denegado
                .anyRequest().denyAll();

        // CONFIGURACION DEL LOGIN/LOGOUT (FormLogin) - Mantiene la configuración REST
        http.formLogin()
                .usernameParameter("email")
                .passwordParameter("password")
                .loginPage("/api/login");

        http.logout().logoutUrl("/api/logout");

        // CONFIGURACION REST (Reemplaza HTML por códigos HTTP)
        http.csrf().disable();
        http.headers().frameOptions().disable();

        http.exceptionHandling().authenticationEntryPoint((req, res, exc) ->
                res.sendError(HttpServletResponse.SC_UNAUTHORIZED));

        http.formLogin().successHandler((req, res, auth) ->
                clearAuthenticationAttributes(req));

        http.formLogin().failureHandler((req, res, exc) ->
                res.sendError(HttpServletResponse.SC_UNAUTHORIZED));

        http.logout().logoutSuccessHandler(new HttpStatusReturningLogoutSuccessHandler());

        return http.build();
    }

    // Función de utilidad requerida por el successHandler
    private void clearAuthenticationAttributes (HttpServletRequest request) {
        HttpSession session = request.getSession(false);
        if (session != null) {
            session.removeAttribute (WebAttributes.AUTHENTICATION_EXCEPTION);
        }
    }
}