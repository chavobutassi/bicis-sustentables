# Implementación de entidades

## Bloque 1 Catálogos de identificación

Estado: entidades incorporadas y revisadas estáticamente.
Compilación exitosa según la salida de terminal aportada por el desarrollador.
Pendientes las pruebas de validación y persistencia.

- Pais representa PAIS y TipoDocumento representa TIPO_DOCUMENTO del DER v5.
- Ambas tienen id INTEGER autogenerado y código obligatorio y único.
- Pais admite códigos de dos letras mayúsculas. La precarga deberá
  utilizar códigos ISO 3166-1 alfa-2 reales.
- El nombre del país es obligatorio y admite hasta 100 caracteres.
- TipoDocumento admite un código de hasta 10 caracteres y un nombre
  obligatorio de hasta 50 caracteres.
- Los tipos iniciales aprobados son DNI y PASAPORTE.
- Los códigos se normalizan con trim y mayúsculas; los nombres con trim.
- Estas longitudes corresponden a los catálogos, no al número de documento.
- Las relaciones desde Persona se declaran en JPA en el bloque 3.
  La carga inicial de los catálogos sigue pendiente.
- No se modifican Usuario, autenticación ni las entidades anteriores.
- La compilación no verifica tablas, restricciones ni conexiones con MySQL.

## Bloque 2 Catálogo de género

Estado: entidad incorporada y revisada estáticamente.
Compilación exitosa según la salida de terminal aportada por el desarrollador.
Pendientes las pruebas de validación y persistencia.

- Genero representa GENERO del DER v5.
- Tiene id INTEGER autogenerado y codigo obligatorio y único,
  con capacidad de hasta 20 caracteres.
- El código se normaliza con trim y mayúsculas.
- Los valores iniciales serán FEMENINO, MASCULINO, NO_BINARIO,
  OTRO y PREFIERO_NO_DECIR.
- La relación desde Persona se declara en JPA en el bloque 3.
  La carga inicial del catálogo sigue pendiente.
- GeneroUsuario se conserva temporalmente porque Usuario,
  sus DTO y la carga inicial anterior todavía lo utilizan.
- No se ha conectado este catálogo al registro ni al frontend.

## Bloque 3 Datos personales y documento

Estado: entidad incorporada y revisada estáticamente.
Compilación exitosa según la salida de terminal aportada por el desarrollador.
Pendientes las pruebas de validación y persistencia.

- Persona representa PERSONA del DER v5, con id INTEGER autogenerado.
- Nombre y apellido son obligatorios, admiten hasta 50 caracteres
  y conservan las validaciones del modelo anterior.
- Fecha de nacimiento es obligatoria y anterior a la fecha actual.
  No se establece una edad mínima de contratación.
- Genero, TipoDocumento y Pais se relacionan mediante tres FK
  obligatorias, con ManyToOne y carga LAZY, sin cascadas.
- Se declara uq_persona_documento sobre la combinación
  tipo_documento_id, pais_emisor_id y numero_documento.
- Las FK y la unicidad compuesta están declaradas en JPA;
  su generación y funcionamiento en MySQL todavía no se verificaron.
- NumeroDocumento es String de hasta 50 caracteres. Conserva
  ceros iniciales y letras; se recortan espacios externos
  y se normaliza a mayúsculas.
- La normalización y validación específica por tipo y país
  se completarán antes de conectar el nuevo registro.
- El DTO de registro se incorpora en el bloque 4, etapa 2.
  Los restantes DTO, servicios, repositorios, la precarga y las pruebas
  de persistencia quedan pendientes.
- La relación desde Usuario se incorpora en el bloque 4.
  El registro actual todavía no crea ni asigna Persona a la cuenta.

## Bloque 4 Adaptación incremental de Usuario

### Etapa 1 Relación con Persona

Estado: relación incorporada y revisada estáticamente.
Compilación exitosa según la salida de terminal aportada por el desarrollador:
`.\gradlew.bat compileJava`, con BUILD SUCCESSFUL en 2 segundos.
Pendientes las pruebas de validación y persistencia.

- Punto de partida: commit a5b88ed, con Persona incorporada. El 2 de
  noviembre de 2026 se comprobó que la referencia de la rama en GitHub
  coincide con el commit local y que el árbol de trabajo estaba limpio.
- Se incorporó persona a Usuario mediante OneToOne con carga LAZY,
  optional false y JoinColumn persona_id, obligatoria y única.
- La FK pertenece a USUARIO y referencia PERSONA.id. Su unicidad
  impide vincular la misma fila Persona a varias cuentas; la unicidad
  documental de Persona es una restricción distinta y se conserva.
- Se agregaron getPersona y setPersona. La relación no tiene cascadas
  de persistencia o borrado sobre Persona ni sobre los catálogos compartidos.
- Nombre, apellido, fecha de nacimiento y GeneroUsuario permanecen
  temporalmente en Usuario para conservar las referencias Java actuales.
  Esta duplicación es transitoria y no es el modelo final del DER v5.
- Autenticación por email, enum Rol, DTO, correos y controladores no
  se modificaron mediante este primer paso.
- La obligatoriedad de Persona exige adaptar el registro y la carga
  inicial antes de volver a ejecutarlos: los constructores antiguos
  todavía no asignan Persona. Una compilación exitosa no garantiza
  que el registro existente siga funcionando con esta relación nueva.
- Quedan pendientes la separación definitiva de datos personales,
  los restantes DTO y su integración, la creación transaccional de persona y cuenta,
  el nickname y su autenticación, los roles múltiples y los restantes
  ajustes de Usuario previstos en el DER v5.
- La verificación de esta etapa solo comprende revisión estática y
  la compilación comunicada. No acredita pruebas de contexto, registro,
  autenticación ni comprobación de esquema o datos en MySQL.

### Etapa 2 Contrato de registro y reglas del nickname

Estado: reglas del nickname aprobadas expresamente el 2 de noviembre de 2026.
RegistroUsuarioDTO está incorporado y revisado estáticamente.
Compilación exitosa según la salida de terminal aportada por el desarrollador:
`.\gradlew.bat compileJava`, con BUILD SUCCESSFUL en 1 segundo.
Todavía no se conectó al controlador. Sus validaciones generales y su
serialización cuentan con las diez pruebas unitarias verificadas en la etapa 3;
esto no acredita la integración del registro ni la persistencia.

#### Nickname aprobado

- Entre 3 y 30 caracteres después de normalizar.
- Debe comenzar por una letra de a a z.
- Después admite letras de a a z, números de 0 a 9, punto,
  guion y guion bajo. No se agregan restricciones sobre separadores
  consecutivos o finales que no hayan sido aprobadas.
- Sin espacios internos, tildes, ñ ni otros caracteres fuera de ese conjunto.
- Se recortan espacios externos y se convierte a minúsculas con Locale.ROOT.
  Las mayúsculas del dato de entrada se aceptan mediante normalización.
- Debe ser único sin distinguir mayúsculas de minúsculas. Su unicidad es
  independiente de la del email y se implementará en Usuario, repositorio
  y servicio; no la verifica una anotación de longitud del DTO.
- Son reglas del proyecto, no una longitud universal exigida por Java,
  Spring o una plataforma externa. Ejemplos admitidos: ana_23, juan.perez
  y maria-lopez. Juan.Perez se normaliza a juan.perez.

#### DTO de entrada incorporado

- Campos: nombre, apellido, fechaNacimiento, generoId, tipoDocumentoId,
  numeroDocumento, paisEmisorId, nickname, email y password.
- No es una entidad JPA ni una tabla. UsuarioDTO continúa siendo el DTO
  de salida existente y no se reemplaza mediante este paso.
- Los datos personales conservan las restricciones de Persona. Los tres
  identificadores de catálogo son Integer obligatorios y positivos;
  su existencia y admisión se comprobarán en el servicio de registro.
- NumeroDocumento conserva capacidad de 50 caracteres, trim y mayúsculas;
  el formato específico según tipo y país sigue pendiente.
- Email conserva límite de 254 caracteres, trim, minúsculas, formato actual
  y la regla existente que impide comenzar con un número.
- Password conserva la política actual: de 6 a 64 caracteres, al menos
  una minúscula, una mayúscula y un carácter de !@#$&*, sin espacios.
  No se añade una exigencia de dígitos mediante este DTO.
- Password no se recorta ni se normaliza y está declarado como
  WRITE_ONLY para excluirlo de la serialización JSON del DTO. Esto no
  lo hashea: BCrypt seguirá aplicándose en el servicio antes de persistir.
- El cliente no elige id de cuenta, rol, activo, versión, hash de contraseña
  ni datos de recuperación mediante este contrato. El registro público
  deberá asignar CLIENTE y activo desde el backend.
- En esta etapa del DTO no se modificaron el formulario, UsuarioController,
  Usuario, la autenticación por email ni la recuperación. El nickname todavía
  no está disponible para iniciar sesión.
- Las diez pruebas unitarias de esta etapa fueron superadas. Siguen pendientes
  controles de duplicados, creación
  transaccional de Persona y Usuario e integración HTTP y frontend.

### Etapa 3 Pruebas unitarias del DTO sin Spring

Estado: clase incorporada, revisada y ejecutada. El informe JUnit de la
ejecución corregida confirma 10 pruebas, 0 fallos, 0 errores y 0 omitidas.
La primera ejecución no seleccionó pruebas por un problema con el filtro;
el segundo intento se completó satisfactoriamente el 2 de noviembre de 2026.

- Clase incorporada: DSII.TurismoSustentable.dto.RegistroUsuarioDTOTest,
  dentro de src/test/java, no de src/main/java.
- Se utilizaron JUnit 5, Bean Validation y Jackson disponibles mediante
  las dependencias actuales. No se requiere iniciar Spring, MySQL o XAMPP.
- Casos ejecutados: datos válidos; normalización; nicknames permitidos,
  inválidos y límites de longitud; emails inválidos; contraseñas inválidas
  y conservación de su valor; identificadores obligatorios y positivos;
  fecha de nacimiento futura; campos obligatorios; recepción de password
  y exclusión de ese campo al serializar el DTO a JSON.
- Los identificadores y demás valores de las pruebas son ficticios.
  Su aceptación en el DTO no acredita existencia en los catálogos,
  unicidad en la base, autenticación ni funcionamiento del registro HTTP.
- Ejecución realizada, limitada exclusivamente a esta clase:

```powershell
.\gradlew.bat test --tests "RegistroUsuarioDTOTest"
```

- No se ejecutará test sin ese filtro por ahora: el test existente
  TurismoSustentableApplicationTests carga Spring y aún no dispone
  de una configuración de base de datos de pruebas aislada.

#### Corrección del filtro de ejecución

El primer intento con el nombre completamente calificado que comienza
por DSII terminó con No tests found for given includes. No se ejecutaron
las validaciones y no se registra como un fallo de sus reglas ni como
una prueba superada.

Gradle interpreta los filtros que comienzan con mayúscula como nombres
simples de clase o clase y método. El paquete DSII, escrito con mayúsculas,
hizo inadecuado el comando inicial. Se sustituye por el nombre simple
RegistroUsuarioDTOTest, sin cambiar paquetes, código o dependencias.

Referencia: [filtros de pruebas de Gradle](https://docs.gradle.org/current/userguide/java_testing.html#simple_name_pattern),
consultada el 2 de noviembre de 2026. El resultado corregido se verificó
en el XML de JUnit, no solamente a partir del mensaje BUILD SUCCESSFUL.

#### Resultado y evidencia del segundo intento

La terminal aportada por el desarrollador informó BUILD SUCCESSFUL en
8 segundos. El informe de la suite RegistroUsuarioDTOTest confirma:

| Prueba | Resultado |
| --- | --- |
| normalizaDatosSinPerderCeros | Superada |
| aceptaNicknamesPermitidosYLimites | Superada |
| rechazaNicknamesInvalidos | Superada |
| rechazaEmailsInvalidos | Superada |
| exigeTodosLosCamposObligatorios | Superada |
| rechazaIdsAusentesONoPositivos | Superada |
| rechazaPasswordsInvalidasSinModificarlas | Superada |
| aceptaDatosValidos | Superada |
| rechazaFechaDeNacimientoFutura | Superada |
| recibePasswordPeroNoLaSerializa | Superada |

Evidencia local consultada:

- XML: `build/test-results/test/TEST-DSII.TurismoSustentable.dto.RegistroUsuarioDTOTest.xml`.
- Informe HTML: `build/reports/tests/test/index.html`.
- Fecha del informe: 2 de noviembre de 2026. Solo se encontró el XML de
  esta suite en los resultados de la ejecución revisada.

Los informes de build son generados y no se versionan. Este resumen
conserva el resultado junto con el código de las pruebas; la ejecución
puede repetirse mediante el comando filtrado indicado anteriormente.

El resultado verifica los escenarios implementados del DTO, no todas
las entradas posibles. No acredita existencia de países, tipos o géneros
en MySQL, restricciones de unicidad en la base, formato documental por
país, creación transaccional de cuentas, autenticación ni registro HTTP.

### Etapa 4 Nickname en Usuario y consultas de repositorio

Estado: incorporado manualmente y revisado el 2 de noviembre de 2026.
La compilación y la repetición de las diez pruebas del DTO fueron
superadas. Las consultas JPA y la unicidad física siguen pendientes
de verificación con una base aislada. Punto de partida: commit 0a4463c.

- Se agregó Usuario.nickname, inmediatamente después de Persona, con las reglas ya aprobadas: obligatorio,
  de 3 a 30 caracteres, primera letra de a a z y el resto de a a z,
  números, punto, guion o guion bajo. No se introducen nuevas restricciones.
- Su columna está declarada como nickname, VARCHAR de 30 caracteres, NOT NULL y UNIQUE.
  La unicidad es independiente de la del email, no una clave compuesta
  entre ambos campos. La restricción física sigue pendiente de prueba en MySQL.
- Se agregaron getNickname y setNickname después de setPersona; el setter aplica trim y
  minúsculas con Locale.ROOT, igual que el DTO.
- El callback de Usuario que normalizaba email se sustituyó por uno
  que normalice email y nickname en PrePersist y PreUpdate.
  No se normaliza ni modifica la contraseña en ese callback.
- UsuarioRepository incorporó findByNicknameIgnoreCase,
  existsByNicknameIgnoreCase y existsByNicknameIgnoreCaseAndIdNot.
  Se conservaron todas las consultas actuales de email, estado y recuperación.
- Las consultas permiten buscar sin distinguir mayúsculas y excluir
  la propia cuenta al comprobar duplicados en una futura modificación.
  No sustituyen la restricción UNIQUE ni su manejo transaccional.
- El login todavía continúa configurado por email: no se modificó
  WebAuthentication, WebAuthorization, UsuarioDTO ni el frontend en este paso.
- El registro y los constructores anteriores todavía no asignan Persona
  ni nickname. No se considera listo el flujo HTTP ni la carga inicial.
- Los datos personales duplicados, roles, hash y demás ajustes de Usuario
  se continuarán adaptando en los siguientes pasos; esta no es su versión final.
- Se revisaron Usuario, UsuarioRepository, RegistroUsuarioDTO, Persona
  y la clase de pruebas. El diff de los dos primeros coincide con los
  agregados y el reemplazo indicados; no se eliminaron miembros anteriores
  ni se duplicó el callback. La normalización y las reglas del nickname
  coinciden entre la entidad y el DTO.
- La terminal aportada por el desarrollador informó BUILD SUCCESSFUL
  en 3 segundos al ejecutar únicamente RegistroUsuarioDTOTest.
  Se contrastó el XML de resultados: 10 pruebas, 0 fallos, 0 errores y
  0 omitidas; timestamp 2026-11-02T14:07:47.759Z
  (11:07:47 en Buenos Aires).
- Las diez pruebas verifican el DTO, no el callback ni las validaciones
  de Usuario, las consultas JPA, el índice UNIQUE, la autenticación
  o la creación de cuentas en MySQL. No se ejecutó la aplicación
  ni el test de contexto de Spring durante esta revisión.
- Detalle de comentario sin efecto funcional: el texto anterior al
  callback todavía dice normalizar mail, aunque ahora normaliza
  email y nickname. No requiere cambios para compilar o continuar.

### Etapa 5 Fecha y hora de registro y versión de Usuario

Estado: incorporado manualmente y revisado el 2 de noviembre de 2026.
La compilación y las diez pruebas del DTO fueron superadas. Siguen
pendientes las pruebas de persistencia de fecha y bloqueo optimista.

- Se implementaron dos campos ya previstos en el DER v5 y en la revisión
  de personas, usuarios y roles del documento 25, sin nuevas tablas
  ni cambios de reglas de negocio.
- Usuario.fechaRegistro pasó de LocalDate a LocalDateTime y su columna
  se declaró fecha_registro, obligatoria y no actualizable por JPA.
  Se conservó CreationTimestamp para asignarla al insertar la cuenta.
- Se retiró la asignación LocalDate.now del constructor antiguo.
  El valor de alta se generará al persistir, no lo decidirá el formulario.
  Se adaptaron el getter y el setter al nuevo tipo.
- UsuarioDTO conservó el atributo fechaRegistro, cambiando su tipo
  y el del getter a LocalDateTime. Se mantuvo LocalDate para
  fechaNacimiento. La búsqueda de referencias encontró esos consumidores
  Java y ningún uso de fechaRegistro en el frontend actual.
- Se agregó Usuario.version de tipo Integer con Version y columna
  version obligatoria. Persistencia administrará su valor; se agregó
  únicamente un getter y no se asignó manualmente en constructores.
- Fecha de registro y versión llevan JsonProperty de acceso READ_ONLY
  en Usuario. Jackson ignorará los valores enviados para esos campos;
  no se confiará en ellos al deserializar la entidad en el flujo anterior.
  Esto no sustituye la futura separación de todos los DTO de entrada.
- La versión sirve para detectar actualizaciones concurrentes sobre
  una misma versión persistida. No es un historial ni sustituye
  auditoría, controles de autorización, las restricciones de unicidad
  o el tratamiento de los conflictos en los servicios.
- LocalDateTime no contiene una zona horaria. Este paso no establece
  por sí solo una política horaria global ni migra fechas antiguas.
- Verificación realizada: revisión de Usuario y UsuarioDTO y sus diffs,
  sin detectar errores en los cambios de esta etapa. La terminal aportada
  por el desarrollador informó BUILD SUCCESSFUL en 3 segundos con
  el filtro RegistroUsuarioDTOTest. El XML confirma 10 pruebas,
  0 fallos, 0 errores y 0 omitidas; timestamp 2026-11-02T15:03:58.938Z
  (12:03:58 en Buenos Aires).
- Estas pruebas ejercitan el DTO de registro, no la generación de fecha,
  el bloqueo optimista, el acceso JSON de Usuario ni MySQL.
  Las verificaciones de persistencia siguen pendientes de una base aislada.
- No se arrancó la aplicación ni se ejecutó el test de contexto
  de Spring en este paso. El registro, los constructores antiguos y
  la autenticación por nickname todavía requieren las adaptaciones
  indicadas en las etapas anteriores.
- El desarrollador informó 19 avisos amarillos en IntelliJ, entre ellos
  Field may be final. No se inspeccionó el listado completo del IDE,
  por lo que no se clasifican los 19 como equivalentes ni se declaran
  todos inocuos. UsuarioDTO contiene campos asignados solo en su
  constructor para los que esa sugerencia puede ser válida y opcional.
  No se convierten automáticamente en final los atributos persistentes
  de las entidades JPA ni se desactivan globalmente las inspecciones.
  Los avisos de deprecación de Gradle se distinguen de estas inspecciones
  y no motivan una actualización de versiones durante esta etapa.

### Etapa 6 Repositorios de Persona y catálogos de registro

Estado: cuatro interfaces incorporadas manualmente y revisadas el
2 de noviembre de 2026. Compilación y pruebas del DTO superadas;
pendientes las pruebas de las consultas con persistencia aislada.

- Se crearon PersonaRepository, PaisRepository, TipoDocumentoRepository
  y GeneroRepository en el paquete repositories existente.
  Cada interfaz extiende JpaRepository de su entidad y de Integer,
  coincidiendo con el tipo de sus claves primarias.
- Los tres catálogos tienen findByCodigo con retorno Optional de la
  entidad correspondiente. La consulta recibirá el código normalizado
  del catálogo, no un texto libre suministrado como relación por el cliente.
  findById, heredado, permitirá posteriormente resolver los identificadores
  enviados por los selectores del formulario.
- PersonaRepository tiene existsByTipoDocumento_IdAndPaisEmisor_IdAndNumeroDocumento,
  con parámetros Integer tipoDocumentoId, Integer paisEmisorId y
  String numeroDocumento. Los guiones bajos expresan la navegación
  desde cada relación hasta su atributo id, no nombres de columnas SQL.
- La comprobación documental usa la combinación completa ya aprobada
  en D01: tipo de documento, país emisor y número normalizado.
  No se declara el número único por sí solo ni se verifica aquí la
  autenticidad o el formato documental específico de cada país.
- Esta consulta previa no sustituye uq_persona_documento ni el manejo
  de colisiones concurrentes en el futuro servicio transaccional.
- Estos repositorios preparan la consulta y persistencia del registro;
  no crean endpoints, datos iniciales ni tablas distintas de las entidades
  ya implementadas. No se habilitan operaciones HTTP de borrado físico
  ni se cambia la política de bajas lógicas.
- No se conectará todavía RegistroUsuarioDTO con UsuarioController
  ni se moverá el login a nickname. Continúan pendientes la separación
  definitiva de datos personales, el tratamiento del hash y los roles.
- El desarrollador informó compilación y pruebas superadas. Se revisaron
  las cuatro interfaces y el XML de RegistroUsuarioDTOTest: 10 pruebas,
  0 fallos, 0 errores y 0 omitidas, con timestamp
  2026-11-02T15:18:01.838Z (12:18:01 en Buenos Aires).
- El resultado no verifica la interpretación de estas consultas por
  Spring Data, el acceso real a MySQL, las FK o la unicidad documental.
  Las pruebas de repositorios se realizarán con una base aislada.

### Etapa 7 Datos personales de Persona en UsuarioDTO

Estado: incorporado manualmente, revisado y probado el 2 de noviembre
de 2026. Doce pruebas unitarias superadas; integración JPA y HTTP
todavía pendientes. La revisión no modificó archivos Java.

- Se adaptó UsuarioDTO, que representa la respuesta de la API,
  no RegistroUsuarioDTO, que representa la solicitud de registro.
- El constructor obtiene nombre, apellido, fechaNacimiento y el código
  de género desde usuario.persona y sus relaciones, conforme a la
  separación aprobada de PERSONA y USUARIO. No lee esos datos
  desde los atributos duplicados del modelo anterior.
- UsuarioDTO incorporó nickname y su getter, tomando el valor de Usuario.
  Conservó el tipo LocalDateTime de fechaRegistro y los otros campos
  y getters actuales. No expone contraseña, hash ni token de recuperación.
- Si falta Persona, el constructor lanza IllegalStateException con
  un mensaje explícito. No inventa datos ni usa una alternativa
  silenciosa tomada de los campos antiguos. Esto detecta una cuenta
  incompleta; no es una respuesta HTTP de dominio ya implementada.
- El tratamiento actual del único rol se conservó por compatibilidad
  hasta la adaptación coordinada de ROL y USUARIO_ROL. No se considera
  implementada la colección de roles ni el rol TECNICO.
- Se incorporaron dos pruebas unitarias en UsuarioDTOTest, sin Spring
  ni base de datos: comprobar el origen de datos personales y nickname,
  y rechazar una cuenta sin Persona. Sus objetos son ficticios y
  no prueban existencia de catálogos, unicidad ni carga LAZY desde JPA.
- Se revisaron el DTO y UsuarioDTOTest y se confirmó la ubicación
  de ambos archivos en main y test respectivamente, sin duplicar
  el constructor ni perder getters anteriores.
- El desarrollador aportó BUILD SUCCESSFUL en 3 segundos ejecutando:

```powershell
.\gradlew.bat test --tests "UsuarioDTOTest" --tests "RegistroUsuarioDTOTest"
```

- Los dos XML de build/test-results/test confirman 12 pruebas,
  0 fallos, 0 errores y 0 omitidas: RegistroUsuarioDTOTest contiene
  diez pruebas (timestamp 2026-11-02T15:27:06.606Z) y UsuarioDTOTest
  contiene dos (timestamp 2026-11-02T15:27:06.862Z).
- Las dos pruebas nuevas son tomaDatosPersonalesDesdePersona y
  rechazaUsuarioSinPersona. Los datos personales antiguos de Usuario
  quedan sin completar en la primera, por lo que el resultado acredita
  que los valores comprobados se obtienen de la nueva relación Persona.
- No se ejecutaron SpringBootTest, la aplicación ni consultas a MySQL
  durante la revisión. Los informes generados no se versionan; se
  conserva este resumen y el código de las pruebas para repetirlas.
- Los atributos personales y constructores anteriores de Usuario
  se mantienen temporalmente para no romper otros consumidores.
  La retirada de esos atributos, los demás DTO/servicios/controladores
  y la consulta estadística de género siguen pendientes.
- No se habilita el registro HTTP ni se cambia el login. El mapeo
  de las relaciones LAZY deberá realizarse dentro del futuro servicio
  transaccional; las pruebas unitarias propuestas no lo garantizan.

### Etapa 8 Lecturas personales en correos y estadísticas

Estado: cambios incorporados manualmente y revisados estáticamente
el 2 de noviembre de 2026; compilación y doce pruebas de DTO superadas.
Pendientes las pruebas funcionales de correos, recuperación y JPQL.
Punto de partida: commit 665b603, que coincide
con el push informado por el desarrollador y la referencia local de
su rama remota. El árbol de trabajo estaba limpio al iniciar la revisión.

- Se cambiaron cuatro expresiones de CorreoService desde
  alquiler.getUsuario().getNombre() a
  alquiler.getUsuario().getPersona().getNombre(): dos en el comprobante
  de inicio y dos en el de finalización, incluidos el HTML y el nombre
  del destinatario. Se conservaron el escape HTML, los importes y el envío.
- La solicitud de recuperación en RecuperacionPasswordService y
  la bienvenida en UsuarioController toman también el nombre desde
  Persona. Email, token, expiración y validación de contraseña no se
  cambiaron en esta etapa; no se ejecutaron envíos reales en la revisión.
- En AlquilerRepository, contarPreferenciasBicicletaPorGenero pasó
  de a.usuario.genero a a.usuario.persona.genero.codigo en SELECT,
  GROUP BY y ORDER BY. El segundo elemento de cada fila será el código
  String del catálogo, no la entidad Genero ni el enum anterior.
- Se conservaron la firma del método y el filtro de alquileres FINALIZADO,
  sin modificar conteos ni consultas restantes. El controlador estadístico
  actual devuelve las filas sin convertir ese valor a GeneroUsuario.
- No se cambiaron los nombres de estaciones, países o tipos documentales.
  La separación de Persona no afecta esos getNombre.
- Los setters personales del controlador de usuarios, sus DTO de entrada,
  constructores y carga inicial anteriores siguen pendientes. No se
  eliminarán todavía atributos ni métodos personales de Usuario.
- La lectura de relaciones LAZY en los servicios deberá quedar cubierta
  por la adaptación transaccional y de consultas de las próximas etapas.
  Los dos métodos de alquiler actuales ya son transaccionales; este paso
  no declara resuelta la recuperación fuera de un contexto de persistencia,
  la entrega de correos después del commit ni la nueva estadística por detalle.
- Se revisó el diff de los cuatro archivos Java y se confirmó que
  coincide con las seis sustituciones y la consulta propuestas. No se
  detectaron errores de copiado ni cambios adicionales en esos archivos.
  git diff --check no informó problemas de espacios.
- El desarrollador aportó BUILD SUCCESSFUL en 2 segundos ejecutando
  únicamente UsuarioDTOTest y RegistroUsuarioDTOTest. Se contrastaron
  ambos XML: 10 pruebas de registro y 2 de salida, sin fallos, errores
  ni omitidas. Timestamps: 2026-11-02T15:54:27.143Z y
  2026-11-02T15:54:27.385Z, respectivamente (12:54:27 en Buenos Aires).
- Esas doce pruebas no ejecutan CorreoService, recuperación ni JPQL.
  La consulta y las asociaciones requieren pruebas de integración aisladas.
  No se arrancó la aplicación ni se conectó a la base anterior durante
  esta revisión. No se modificó Java ni se realizaron operaciones Git
  de escritura; solo se actualizó este registro de implementación.

### Etapa 9 DTO de entrada para modificar datos de usuario

Estado: ActualizarUsuarioDTO incorporado manualmente y revisado el
2 de noviembre de 2026. Compila y las doce pruebas anteriores siguen
pasando; no se presentan como pruebas específicas de este DTO.

- El formulario administrativo actual envía nombre, apellido, email,
  fechaNacimiento y genero como código del enum anterior. No envía
  contraseña, roles, estado de cuenta, nickname ni documento.
- Se creó ActualizarUsuarioDTO en el paquete dto, separado tanto
  de UsuarioDTO de salida como de RegistroUsuarioDTO de registro.
  Tiene nombre, apellido, email, fechaNacimiento y generoId.
- La nueva operación PUT exigirá esos cinco campos completos. Es un
  cambio explícito frente al método anterior que admitía campos omitidos;
  no se presenta como un PATCH parcial. Todavía no se conecta el DTO al
  endpoint, por lo que no se declara aplicado ese contrato HTTP.
- Nombre y apellido son obligatorios, de hasta 50 caracteres y con
  las reglas existentes de letras Unicode, espacios, apóstrofes y guiones.
  Los setters recortan espacios externos, sin modificar espacios internos.
- Email es obligatorio, de hasta 254 caracteres, con el mismo formato
  y la misma regla de no comenzar con número ya implementados en registro.
  El setter aplica trim y minúsculas con Locale.ROOT. La comprobación
  de unicidad, incluyendo cuentas inactivas y exclusión del propio id,
  corresponde al futuro servicio y a la restricción física, no al DTO.
- Fecha de nacimiento es obligatoria y pasada. No se añade edad mínima.
  generoId es un Integer obligatorio y positivo; el futuro servicio
  comprobará que el catálogo contiene ese identificador.
- No se admitirán mediante este DTO cambios de id, Persona vinculada,
  documento, nickname, rol, activo, contraseña, fecha de registro,
  versión ni token de recuperación. No se eliminan otros circuitos de
  modificación o recuperación; se delimita esta edición de perfil.
- No se tocará todavía admin.js: el envío actual de genero no equivale
  a generoId. La adaptación del selector, el DTO de salida para disponer
  de su identificador y la petición HTTP sigue pendiente. Al conectar
  el nuevo PUT, un cuerpo sin generoId debe ser rechazado por validación,
  no aceptado silenciosamente ignorando el cambio de género.
- Se prepara primero el DTO para mantener el trabajo manual en pasos
  acotados. Después se implementarán el servicio transaccional, su
  tratamiento de duplicados y concurrencia y la delegación del controlador.
  Los campos personales duplicados de Usuario aún no se retirarán.
- Se revisó el archivo completo: paquete, cinco campos, anotaciones,
  constructor, getters y setters coinciden con las instrucciones.
  El desarrollador informó pruebas superadas y los XML confirman
  diez pruebas en RegistroUsuarioDTOTest y dos en UsuarioDTOTest,
  sin fallos, errores ni omitidas. Timestamps:
  2026-11-02T16:07:21.469Z y 2026-11-02T16:07:21.744Z
  (13:07:21 en Buenos Aires).
- Esas doce pruebas no ejercitan ActualizarUsuarioDTO, sus errores
  HTTP ni el futuro servicio; se requieren pruebas específicas antes
  de dar por terminado el flujo de modificación.

### Etapa 10 Servicio transaccional de modificación de usuario

Estado: UsuarioService incorporado manualmente y revisado estáticamente
el 2 de noviembre de 2026. Compilación y doce pruebas anteriores de DTO
superadas; pendientes las pruebas específicas del servicio y de persistencia.

- Se creó un servicio con inyección por constructor de
  UsuarioRepository, GeneroRepository y EntityManager.
- Su método actualizarUsuario recibe id y ActualizarUsuarioDTO,
  devuelve UsuarioDTO y tiene Transactional, validación de método
  mediante Validated/Valid y autorización PreAuthorize exclusiva ADMIN.
  La configuración actual ya habilita prePostEnabled.
- Se exige id positivo, DTO presente y sus validaciones. El usuario
  debe existir, estar activo y tener Persona; no se inventarán datos
  personales ni se reemplazará el vínculo para subsanar una cuenta incompleta.
- El género se resuelve por findById del catálogo, no creando una fila
  nueva con un id enviado por el cliente. Se comprueba el email con
  existsByEmailIgnoreCaseAndIdNot incluyendo cuentas inactivas y
  excluyendo la propia cuenta. La restricción UNIQUE sigue siendo
  imprescindible frente a solicitudes concurrentes.
- Solo se modifican email en Usuario y nombre, apellido,
  fechaNacimiento y genero en Persona. No se copian de nuevo esos
  datos a los atributos duplicados anteriores.
- Si cambia el email, se limpian conjuntamente tokenRecuperacion
  y vencimientoTokenRecuperacion. Es una medida de seguridad para
  invalidar enlaces anteriores tras cambiar la dirección de recuperación;
  el DTO no recibe ni permite elegir esos valores. No verifica la
  titularidad del nuevo correo ni cambia el plazo de los enlaces nuevos.
- Se solicita OPTIMISTIC_FORCE_INCREMENT sobre Usuario para que
  el control de versión cubra también transacciones participantes que
  solo modifican Persona. No se añadirá una columna version a Persona
  ni se asignará manualmente Usuario.version. Esto no detecta por sí
  solo formularios antiguos que no envían una versión esperada.
- La Persona cargada dentro de la transacción es una entidad administrada:
  sus cambios se persistirán por detección de cambios, sin cascade REMOVE,
  sin reemplazarla y sin necesitar otro save sobre PersonaRepository.
  Se hará flush antes de construir el DTO dentro de la misma transacción.
- No se capturan errores de persistencia dentro del servicio para
  simular éxito: se propagarán y se revertirá la unidad de trabajo.
  Los conflictos pueden aparecer al hacer flush o al confirmar;
  el futuro manejo HTTP deberá cubrir ambas situaciones.
- La conexión del controlador, respuestas 400/404/409, auditoría ADMIN,
  retirada de duplicados y coherencia de las sesiones ante cambio de
  email siguen pendientes. El principal actual todavía utiliza email;
  la futura autenticación por nickname debe adaptarse de forma coordinada.
- Se revisó el archivo completo: inyección, anotaciones, búsquedas,
  comprobaciones, control de versión, cambios en Persona, limpieza
  conjunta del token y devolución del DTO coinciden con lo indicado.
- El desarrollador informó pruebas superadas. Los dos XML confirman
  10 pruebas de RegistroUsuarioDTOTest y 2 de UsuarioDTOTest,
  sin fallos, errores ni omitidas. Timestamps:
  2026-11-02T16:20:54.072Z y 2026-11-02T16:20:54.327Z
  (13:20:54 en Buenos Aires).
- Estas pruebas no acreditan la validación o seguridad por proxies,
  el funcionamiento del servicio, su transacción o el bloqueo optimista.
  Las pruebas específicas y la integración aislada se realizarán antes
  de dar por terminado este flujo y de arrancar la aplicación.
- Referencias técnicas consultadas el 2 de noviembre de 2026:
  [Hibernate 5.6 LockMode](https://docs.hibernate.org/orm/5.6/javadocs/org/hibernate/LockMode.html)
  y [JPA LockModeType](https://docs.oracle.com/javaee/7/api/javax/persistence/LockModeType.html).

### Etapa 11 Conexión del PUT de usuarios con el servicio

Estado: UsuarioController modificado manualmente y revisado el
2 de noviembre de 2026. Compilación y doce pruebas anteriores de DTO
superadas. Pendientes las pruebas específicas del PUT y del servicio.

- Se inyectó UsuarioService por constructor, conservando las
  tres dependencias anteriores porque otros métodos todavía las usan.
- Se reemplazó únicamente actualizarUsuario: recibe
  Valid RequestBody ActualizarUsuarioDTO y delega en el servicio.
  Se retiraron de ese método las búsquedas, validaciones duplicadas,
  cambios sobre atributos personales antiguos y modificación de contraseña.
  GET, POST, DELETE y la recuperación de contraseña se conservaron.
- El PUT nuevo requiere los cinco campos del DTO, incluido generoId.
  La petición actual de admin.js todavía envía genero como texto:
  el frontend sigue pendiente y no se considera compatible por este paso.
- La validación del cuerpo previa a ejecutar el método sigue usando
  el GlobalExceptionHandler existente. El controlador maneja localmente
  ConstraintViolationException del servicio como 400, EntityNotFoundException
  como 404, IllegalArgumentException como 400 e IllegalStateException como 409.
- Los conflictos de versión, tanto JPA OptimisticLockException como
  Spring OptimisticLockingFailureException, tienen prevista respuesta 409 con un mensaje
  para recargar los datos. Los conflictos DataIntegrityViolationException
  tienen prevista respuesta 409 sin exponer detalles SQL ni atribuir todos los errores
  de integridad exclusivamente a un email duplicado.
- El try del controlador cubre toda la llamada al proxy transaccional,
  incluidos los errores propagados al confirmar antes de retornar al caller.
  No se agregaron catch genéricos que conviertan fallos inesperados en 400.
  La autorización ADMIN y las excepciones de acceso de Spring Security
  no están incluidas en esas capturas.
- Esta etapa no modifica GlobalExceptionHandler ni afirma unificar
  todos los formatos de error de la API. Persisten pruebas específicas
  de servicio, validación y HTTP, auditoría y retirada de duplicados.
- Se revisaron el archivo completo y el diff: los seis imports nuevos,
  el campo final, los cuatro parámetros del constructor y sus asignaciones,
  la firma con Valid y el DTO de entrada, la delegación y las seis ramas
  catch coinciden con las instrucciones. No quedaron un segundo método
  PUT ni escrituras sobre los campos personales antiguos en ese método.
  Se conservaron el cierre de la clase y los demás endpoints.
- git diff --check no informó problemas. La clase compilada tiene
  fecha posterior a la última modificación del archivo fuente.
- El desarrollador informó pruebas superadas. Los XML confirman
  10 pruebas en RegistroUsuarioDTOTest y 2 en UsuarioDTOTest,
  sin fallos, errores ni omitidas. Timestamps:
  2026-11-02T16:53:35.503Z y 2026-11-02T16:53:35.758Z
  (13:53:35 en Buenos Aires).
- Esas pruebas no prueban la ruta HTTP, seguridad por proxy,
  commit/rollback ni las respuestas de error nuevas. La revisión
  confirma el copiado y la compilación, no la integración completa.
  No se arrancó la aplicación ni se conectó a la base anterior.
  Solo se actualizó este MD; no se modificó Java ni se escribió en Git.

### Etapa 12 Pruebas unitarias de modificación de usuario

Estado: UsuarioServiceTest creado manualmente en src/test, revisado
y ejecutado el 2 de noviembre de 2026. Diez pruebas nuevas superadas;
22 en total junto a las dos suites anteriores, sin fallos ni errores.
No se modificaron dependencias ni código productivo en esta etapa.

- Se utilizaron JUnit 5 y MockitoExtension incluidos en el starter de
  pruebas existente. UsuarioRepository, GeneroRepository y EntityManager
  se simulan; UsuarioService se construye mediante InjectMocks.
- Los fixtures son cuentas, personas, catálogos y DTO ficticios en
  memoria. El valor de password será una cadena explícitamente simulada,
  no una contraseña utilizable ni un hash BCrypt probado. Los tokens
  son cadenas ficticias de 64 caracteres, no enlaces reales.
- Se implementaron y superaron diez pruebas:
  1. Actualiza Persona y devuelve sus datos conservando identidad del
     vínculo, documento, nickname, rol, password y token si el email es igual;
     solicita el control de versión y llama a flush.
  2. Al cambiar el email, limpia conjuntamente hash del token y vencimiento.
  3. Rechaza un usuario inexistente sin iniciar escrituras.
  4. Rechaza un usuario inactivo sin iniciar escrituras.
  5. Rechaza una cuenta sin Persona sin iniciar escrituras.
  6. Rechaza un género no encontrado sin iniciar escrituras.
  7. Rechaza un email ocupado sin cambiar datos ni iniciar escrituras.
  8. Propaga un error de versión simulado al solicitar el lock, antes
     de mutar datos; no es una carrera de base de datos ejecutada.
  9. Propaga un conflicto de integridad simulado en flush; no afirma
     revertir objetos Java ni probar un rollback real.
  10. Valida explícitamente ActualizarUsuarioDTO con Bean Validation:
      datos válidos, cinco campos obligatorios y datos inválidos para
      cada uno (nombre, apellido, email, nacimiento futuro y género no positivo).
- La primera prueba comprueba que la consulta de duplicados utiliza
  el email normalizado y excluye el propio id. El resultado simulado
  no prueba una restricción UNIQUE ni la existencia de filas reales.
- La prueba con Mockito solo confirma la solicitud de
  OPTIMISTIC_FORCE_INCREMENT, no que Hibernate incremente la versión.
  Al invocar directamente el servicio construido en el test no actúan
  los proxies de Transactional, PreAuthorize ni Validated. La décima
  prueba ejecuta el validador explícitamente sobre el DTO, no el proxy.
- Se revisó la clase completa, su ubicación y los tres XML de JUnit.
  Los métodos, fixtures, mocks y verificaciones coinciden con lo indicado.
  No se añadieron stubs globales que afecten a los casos de rechazo.
  La clase compilada tiene fecha posterior a su archivo fuente y
  git diff --check no informó problemas de espacios.
- El desarrollador aportó BUILD SUCCESSFUL en 3 segundos ejecutando:

```powershell
.\gradlew.bat test --tests "UsuarioServiceTest" --tests "UsuarioDTOTest" --tests "RegistroUsuarioDTOTest"
```

- Los XML confirman 22 pruebas, 0 fallos, 0 errores y 0 omitidas:
  RegistroUsuarioDTOTest, 10 pruebas (2026-11-02T17:05:02.340Z);
  UsuarioDTOTest, 2 (2026-11-02T17:05:02.606Z);
  UsuarioServiceTest, 10 (2026-11-02T17:05:02.624Z).
  Las tres corresponden a las 14:05:02 de Buenos Aires.
- No se ejecutó SpringBootTest ni test sin filtros. No se arrancó
  la aplicación, se conectó a MySQL ni se enviaron correos en esta revisión.
  Solo se actualizó este MD: no se modificó Java ni se escribió en Git.
- Continúan pendientes pruebas HTTP de estados 400/404/409, seguridad
  por proxy e integración con una base aislada, además de las adaptaciones
  de frontend, auditoría, registro y retirada de campos duplicados.

### Etapa 13 Retirada de datos personales duplicados de Usuario

Estado: implementado y revisado estáticamente el 2 de noviembre de 2026;
compilación y 22 pruebas filtradas confirmadas el 3 de noviembre de 2026.
El desarrollador autorizó excepcionalmente
al asistente a aplicar únicamente este bloque, excluyendo el paso 5
de ejecución de comprobaciones con Gradle. Se mantiene el trabajo manual
para los siguientes bloques salvo nueva autorización.

Punto de partida: commit e5916e9, publicado por el desarrollador en
codex/refactorizacion-practicas-iii. Se comprobaron HEAD y referencia
local de la rama remota. Antes de editar Java solo había cambios en
este MD, correspondientes a la preparación de esta etapa.

- La búsqueda de consumidores confirmó que los constructores antiguos
  de Usuario solo son utilizados por initData del main. Sus datos
  personales ya no se leen desde los consumidores adaptados. Persona,
  DTO de entrada y DTO de salida conservan sus propios campos y métodos.
- Se reemplazó TurismoSustentableApplication por el arranque mínimo
  de Spring Boot, conservando paquete, nombre de clase, SpringBootApplication
  y main. Se retiraron el CommandLineRunner antiguo y sus dependencias.
  Esa carga usa el modelo anterior, incluido usuario sin Persona/nickname,
  bicicletas, tarjetas y alquileres que requieren revisión para el DER v5.
- La carga inicial anterior queda conservada en el historial Git del
  commit e5916e9 y en main estable; no se crea una copia Java duplicada
  dentro de src. Se preparará después una configuración de carga inicial
  explícita de desarrollo compatible con el nuevo modelo. Esta etapa
  no la reemplaza todavía ni afirma que existan datos precargados.
- No se borró ni modificó una base de datos mediante esta edición de código.
  No se ejecutó la aplicación: el perfil refactor conserva create-drop
  sobre turismo_sustentable y requiere verificar su activación y destino
  antes del primer arranque. La separación de ramas no aísla una base.
- En Usuario se retiraron nombre, apellido, fechaNacimiento y genero
  del enum anterior, incluidas sus anotaciones y sus ocho getters/setters.
  No se trasladaron de nuevo a la cuenta: las validaciones y columnas
  correspondientes de Persona se conservaron sin cambios.
- Se retiraron los dos constructores con datos personales y se mantuvo
  el constructor vacío requerido por JPA. Se incorporó otro constructor
  con Persona, nickname, email y passwordHasheada, utilizando los setters
  de los cuatro atributos. No hashea en la entidad ni recibe roles del formulario.
- Se eliminó el import de LocalDate en Usuario; LocalDateTime sigue
  siendo necesario. El enum GeneroUsuario no se borró: queda
  pendiente revisar y retirar ese archivo sin consumidores.
- UsuarioDTOTest utiliza el constructor nuevo en su primer caso,
  conservando la prueba de normalización y lectura desde Persona.
  El caso de cuenta sin Persona mantuvo el constructor vacío.
- Rol único anterior, Tarjeta, los mappings de hash y recuperación,
  equals/hashCode, id y demás ajustes de Usuario no se cambian aquí.
  Esta retirada no se presenta como la versión final completa del DER v5.
- El POST de registro todavía recibe la entidad Usuario y requiere
  sustituirse por RegistroUsuarioDTO y creación transaccional de Persona
  y cuenta. No se considera seguro ni terminado el registro por esta
  limpieza. El nuevo constructor no sustituye esa capa de servicio.
- Se revisaron estáticamente los diffs de los tres archivos Java y
  las referencias restantes: GeneroUsuario solo aparece en la declaración
  de su propio enum; los tres usos restantes de new Usuario corresponden
  al nuevo constructor y a los dos constructores vacíos de las pruebas.
- Durante la implementación no se ejecutó Gradle, javac, pruebas, la aplicación, SQL ni operaciones
  Git de staging, commit o push. La compilación y las tres suites filtradas
  quedaron a cargo del desarrollador. En ese momento no se registraron
  como superadas: los informes de la etapa 12 correspondían al código anterior
  a esta retirada. La ejecución posterior se documenta a continuación.
- El alcance de escritura fue el main, Usuario, la primera preparación
  de datos de UsuarioDTOTest y este registro de implementación. No se
  modificaron Persona, los otros modelos, DTO, servicios, controladores,
  repositorios, frontend, dependencias ni configuración de la base.

#### Comprobación posterior de la etapa 13

- El desarrollador ejecutó el 3 de noviembre de 2026 las tres suites
  filtradas y aportó BUILD SUCCESSFUL en 28 segundos. Se revisaron los
  XML generados después de las modificaciones de los tres archivos Java:
  RegistroUsuarioDTOTest, 10 pruebas (2026-11-03T07:43:35.456Z);
  UsuarioDTOTest, 2 (2026-11-03T07:43:36.133Z);
  UsuarioServiceTest, 10 (2026-11-03T07:43:36.160Z).
  Total: 22 pruebas, 0 fallos, 0 errores y 0 omitidas.
- Los informes corresponden a las 04:43:35-36 de Buenos Aires.
  Confirman la compilación y las comprobaciones unitarias existentes
  después de retirar los campos duplicados, no el registro HTTP ni
  la creación del esquema. No se arrancó la aplicación ni se conectó
  a una base de datos durante esta revisión del asistente.

### Etapa 14 Separación entre contraseña de entrada y hash persistido

Estado: implementado manualmente y revisado el 3 de noviembre de 2026.
Compilación y 22 pruebas existentes confirmadas; no hay todavía pruebas
específicas de las nuevas anotaciones. El asistente solo actualiza este MD.

- Se mantiene la regla aprobada del documento 25: RegistroUsuarioDTO
  valida la contraseña en claro antes del hasheado. Usuario almacena
  el resultado del PasswordEncoder, no vuelve a aplicarle esa política.
- El cambio aplicado se limita al bloque password de Usuario:
  NotBlank y Size con máximo 255 para el dato persistido, sin la expresión
  de composición ni el límite 6-64 de la contraseña en claro.
  JsonProperty WRITE_ONLY evita incluir este campo al serializar la entidad.
- Se conservan nombre del atributo, getters/setters, nombre actual de la
  columna y su capacidad 255. No se cambia BCrypt ni se genera un hash
  mediante estas anotaciones; el servicio debe entregarlo ya hasheado.
  No se modifica RegistroUsuarioDTO ni su política de contraseña.
- El POST actual todavía recibe Usuario, no RegistroUsuarioDTO.
  Retirar las reglas del campo persistido no completa ni asegura el
  registro público: se debe conectar el DTO y la creación transaccional
  de Persona, Usuario y rol antes de considerar funcional ese circuito.
  No se debe desplegar esta etapa intermedia como un registro terminado.
- La recuperación existente valida la contraseña en claro mediante
  validarPassword antes de llamar a PasswordEncoder. Su adaptación
  transaccional y las pruebas de integración siguen pendientes.
- Se comprobó el bloque completo: comentario, JsonProperty WRITE_ONLY,
  NotBlank para el hash, Size máximo 255 y Column conservando nombre y
  longitud. Se retiraron el mínimo 6, el máximo 64 y el Pattern de
  contraseña en claro únicamente de este campo de la entidad.
- El POST sigue recibiendo Usuario: no se interpreta el mensaje del
  desarrollador como una adaptación ya realizada del controlador.
- El desarrollador aportó BUILD SUCCESSFUL en 10 segundos. Los XML
  posteriores al cambio confirman 22 pruebas, 0 fallos, 0 errores y 0 omitidas:
  RegistroUsuarioDTOTest, 10 (2026-11-03T07:50:38.254Z);
  UsuarioDTOTest, 2 (2026-11-03T07:50:38.947Z);
  UsuarioServiceTest, 10 (2026-11-03T07:50:39.019Z).
  La clase compilada Usuario tiene fecha posterior a su archivo fuente.
- Estas suites no validan específicamente las anotaciones del hash ni su
  exclusión JSON en Usuario. La exclusión que prueba RegistroUsuarioDTOTest
  corresponde al DTO, no a la entidad. Persistencia y HTTP siguen pendientes.
  No se ejecutaron pruebas ni la aplicación desde el asistente.

### Etapa 15 Preparación del registro transaccional mediante DTO

Estado: RegistroUsuarioService incorporado manualmente, revisado y compilado
el 3 de noviembre de 2026. Pruebas propias del registro pendientes.
No se modifica Java desde el asistente ni se da por conectado el POST.

- El servicio de registro se separa del servicio de edición existente para
  incorporar el alta sin reemplazar UsuarioService ni afectar sus pruebas.
  Recibe RegistroUsuarioDTO con Validated, Valid y NotNull mediante el
  proxy de Spring; no recibirá entidades o roles suministrados por el cliente.
- Dependencias incorporadas: UsuarioRepository, PersonaRepository,
  GeneroRepository, TipoDocumentoRepository, PaisRepository y PasswordEncoder.
  Se comprueban email y nickname ocupados, existencia de los tres catálogos
  y duplicidad del documento compuesto antes de iniciar las escrituras.
- Se aplica BCrypt mediante el PasswordEncoder ya configurado, se crea
  Persona, se vincula a Usuario y se guarda la cuenta en una transacción.
  Los errores se propagarán, sin capturas que conviertan un fallo en éxito
  parcial. La atomicidad real requiere una prueba de integración posterior.
- La asignación CLIENTE utiliza transitoriamente el enum Rol actual y
  activo se fija en el backend. No se afirma haber implementado ROL ni
  USUARIO_ROL del DER v5; ese cambio debe conservarse como tarea pendiente.
- Los precontroles no sustituyen las restricciones UNIQUE físicas de email,
  nickname, documento compuesto y persona_id. Las colisiones simultáneas
  deberán manejarse también en la respuesta HTTP del siguiente bloque.
- El servicio devuelve UsuarioDTO dentro de la transacción y no envía
  correo. Al adaptar el controlador, la bienvenida se conservará después
  de que el servicio haya confirmado el alta, no antes de un posible rollback.
- Continúan pendientes: conectar POST /api/usuarios al servicio y al DTO,
  respuestas HTTP, pruebas propias del registro, carga inicial de catálogos,
  frontend, reglas documentales específicas por tipo/país y los roles del DER.
  Las 22 pruebas anteriores no ejercitan este servicio nuevo.
- Se revisó el archivo completo: paquete services dentro de src/main/java,
  imports, seis campos final y sus asignaciones de constructor, anotaciones,
  precontroles antes de guardar, hasheado antes de crear Usuario, uso de la
  Persona devuelta por save, saveAndFlush de la cuenta y mapeo a UsuarioDTO.
  No se añadieron capturas que impidan propagar el fallo transaccional.
- El archivo fuente tiene fecha 2026-11-03T07:56:35Z y su clase compilada
  2026-11-03T07:58:24Z. Los XML disponibles confirman 22 pruebas sin fallos,
  errores ni omitidas: RegistroUsuarioDTOTest, 10 (07:58:28.211Z);
  UsuarioDTOTest, 2 (07:58:28.742Z); UsuarioServiceTest, 10 (07:58:28.779Z),
  todas del 3 de noviembre de 2026.
- El último comando informado terminó BUILD SUCCESSFUL en 2 segundos con
  las cuatro tareas UP-TO-DATE: reutiliza resultados, no representa otra
  ejecución de las pruebas ni añade casos del registro. Los artefactos
  revisados son posteriores al archivo fuente y respaldan su compilación.
  No prueban el proxy de validación, rollback real ni la persistencia.
- No se ejecutó Gradle desde el asistente ni se modificó staging. El archivo
  nuevo tiene cambios en índice y en directorio de trabajo del desarrollador;
  se conservaron ambos estados, sin descartar ni preparar modificaciones.

### Etapa 16 Conexión del controlador al registro mediante DTO

Estado: cambios incorporados manualmente, revisados y compilados el 3 de
noviembre de 2026. Las 22 pruebas existentes pasan; no son pruebas HTTP
ni casos propios del servicio de registro. El asistente solo edita este MD.

- Se añadieron RegistroUsuarioDTO y RegistroUsuarioService a los
  imports, retirar PasswordEncoder de este controlador e inyectar el nuevo
  servicio mediante el constructor existente. Rol se conserva para DELETE.
- Solo se reemplaza el POST /api/usuarios: recibe Valid RequestBody
  RegistroUsuarioDTO y delega el alta en registrarUsuario. Se retiran del
  controlador el hasheado, los precontroles y la persistencia directa del alta.
  Los demás endpoints y UsuarioService se conservan.
- Los errores de validación del cuerpo previos a entrar al método siguen
  atendidos por GlobalExceptionHandler. Se implementaron respuestas locales 400
  para ConstraintViolationException e IllegalArgumentException y 409 para
  IllegalStateException y DataIntegrityViolationException. En este último
  caso el mensaje no expondrá SQL ni atribuirá toda colisión solo al email.
- La llamada al servicio se mantiene dentro del try para abarcar errores
  propagados desde el proxy y al confirmar la transacción. No se incorpora
  Transactional al controlador ni una captura genérica de excepciones.
- La bienvenida se solicita fuera del try del alta, después del retorno
  del servicio, utilizando email y nombre del DTO de salida. Se conserva
  el comportamiento actual de CorreoService, que devuelve false cuando
  faltan credenciales o captura un RestClientException; no se agrega un
  mecanismo de entrega garantizada ni se prueba el envío en esta etapa.
- El resultado previsto del alta exitosa es 201 con UsuarioDTO, sin hash
  de contraseña ni datos del token. El formulario actual todavía requiere
  adaptación a los campos y catálogos nuevos; conectar el backend no se
  presenta como registro de punta a punta ya comprobado.
- Quedan pruebas propias de servicio y HTTP, integración con base aislada,
  carga inicial y adaptación de roles al DER v5, además del frontend.
- Se revisaron el archivo completo y su diff: se retiraron import, campo,
  parámetro y asignación de PasswordEncoder únicamente del controlador;
  los dos imports nuevos y la inyección de RegistroUsuarioService están
  correctos. El POST tiene las cuatro ramas catch previstas y el envío de
  bienvenida utiliza nombre y email del DTO después de la llamada al servicio.
- GET, DELETE y PUT no presentan cambios en el diff. Se conserva Rol para
  la protección de DELETE y no se agrega Transactional al controlador.
  No se encontraron métodos POST duplicados ni cambios fuera de ese bloque,
  los imports y la inyección del constructor.
- El desarrollador informó BUILD SUCCESSFUL en 8 segundos. La clase
  compilada UsuarioController (2026-11-03T08:15:02Z) es posterior al fuente
  (08:14:32Z). Los XML confirman 22 pruebas, 0 fallos, 0 errores y 0 omitidas:
  RegistroUsuarioDTOTest, 10 (08:15:05.730Z); UsuarioDTOTest, 2 (08:15:06.325Z);
  UsuarioServiceTest, 10 (08:15:06.422Z), del 3 de noviembre de 2026.
- Los resultados respaldan compilación y regresión unitaria existente,
  no demuestran respuestas HTTP, validación por proxy, commit/rollback ni
  envío de correo. No se ejecutó Gradle ni la aplicación desde el asistente.
  git diff --check no informó problemas de espacios; no se escribió en Git.

### Etapa 17 Pruebas unitarias del servicio de registro

Estado: RegistroUsuarioServiceTest creado manualmente, revisado y ejecutado
el 3 de noviembre de 2026. Ocho pruebas nuevas superadas; 30 junto a las
tres suites anteriores. El asistente solo actualiza este MD.

- Se utiliza JUnit 5 con MockitoExtension, seis dependencias simuladas
  e InjectMocks sobre RegistroUsuarioService. No se arranca Spring ni una
  base de datos y no se envían correos. Los fixtures se preparan sin stubs
  globales para no dejar configuraciones no utilizadas en los rechazos.
- Ocho casos implementados y superados: alta correcta, email ocupado, nickname ocupado,
  documento compuesto ocupado, género inexistente, tipo de documento
  inexistente, país emisor inexistente y propagación de un conflicto de
  integridad al guardar la cuenta.
- En el alta se comprueban los datos normalizados, los catálogos elegidos,
  el vínculo con Persona, la delegación a PasswordEncoder y la asignación
  CLIENTE/activo. La salida esperada es UsuarioDTO con id simulado.
- El valor retornado por el encoder es un hash explícitamente simulado;
  no se presenta como un hash BCrypt utilizable ni prueba del algoritmo.
  Los identificadores y catálogos son ficticios, no filas cargadas en la base.
- Los rechazos previos a las escrituras no deben guardar Persona o Usuario
  ni llamar al encoder. La excepción simulada al guardar Usuario debe
  propagarse, pero el test no afirma revertir la Persona en una base real.
- Por ser una instancia construida por Mockito, estas pruebas no ejecutan
  los proxies Validated/Transactional. Tampoco comprueban SQL UNIQUE,
  rollback real, autorización ni respuestas HTTP del controlador.
- Se revisó el archivo completo: paquete y ubicación de test, los seis
  mocks, InjectMocks, fixtures, capturas de Persona/Usuario, mensajes de
  rechazo, helpers y propagación de la excepción coinciden con lo indicado.
  No se agregaron stubs generales que rompan los casos de rechazo temprano.
- El archivo fuente tiene fecha 2026-11-03T08:25:12Z y su clase compilada
  08:25:40Z. El desarrollador aportó BUILD SUCCESSFUL en 8 segundos usando
  filtros explícitos para las cuatro suites, sin ejecutar contextLoads.
- Los XML confirman 30 pruebas, 0 fallos, 0 errores y 0 omitidas:
  RegistroUsuarioDTOTest, 10 (2026-11-03T08:25:42.960Z);
  UsuarioDTOTest, 2 (08:25:43.461Z);
  RegistroUsuarioServiceTest, 8 (08:25:43.491Z);
  UsuarioServiceTest, 10 (08:25:44.382Z), todas del 3 de noviembre de 2026.
- git diff --check no informó problemas de espacios. No se ejecutaron
  Gradle, la aplicación, SQL ni envíos de correo desde el asistente; tampoco
  se modificaron el índice de Git, commits o ramas del desarrollador.
- El bloque queda comprobado a nivel unitario. Continúan pendientes
  pruebas HTTP e integración real, frontend, carga inicial y roles múltiples
  del DER v5. Las 30 pruebas no equivalen a registro de punta a punta probado.
