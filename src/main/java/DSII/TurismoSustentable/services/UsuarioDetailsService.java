package DSII.TurismoSustentable.services;

import DSII.TurismoSustentable.models.Usuario;
import DSII.TurismoSustentable.repositories.UsuarioRepository;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Locale;

@Service
public class UsuarioDetailsService implements UserDetailsService {

    private final UsuarioRepository usuarioRepository;

    public UsuarioDetailsService(
            UsuarioRepository usuarioRepository
    ) {
        this.usuarioRepository = usuarioRepository;
    }

    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String email) {

        if (email == null || email.trim().isEmpty()) {
            throw new UsernameNotFoundException(
                    "Usuario desconocido."
            );
        }

        String emailNormalizado =
                email.trim().toLowerCase(Locale.ROOT);

        Usuario usuario = usuarioRepository
                .buscarPorEmailConDatosYRoles(emailNormalizado)
                .orElseThrow(() -> new UsernameNotFoundException(
                        "Usuario desconocido."
                ));

        String[] autoridades = usuario.getUsuarioRoles().stream()
                .map(asignacion -> asignacion.getRol().getCodigo())
                .distinct()
                .toArray(String[]::new);

        if (autoridades.length == 0) {
            throw new UsernameNotFoundException(
                    "La cuenta no tiene roles asignados."
            );
        }

        return new User(
                usuario.getEmail(),
                usuario.getPassword(),
                usuario.isActivo(),
                true,
                true,
                true,
                AuthorityUtils.createAuthorityList(autoridades)
        );
    }
}
