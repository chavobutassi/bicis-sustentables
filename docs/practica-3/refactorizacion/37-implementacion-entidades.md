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

### Etapa 18 Preparación de códigos para el catálogo de roles

Estado: implementado por el asistente el 3 de noviembre de 2026 con
autorización puntual del desarrollador; 30 pruebas filtradas superadas.
El desarrollador aclaró después que no desea conservar un enum de roles
en el diseño final; véase la aclaración al cierre de esta etapa.

- Punto de control confirmado: commit 6924569, Adaptar registro a Persona
  y DTO con pruebas unitarias, en codex/refactorizacion-practicas-iii.
  El desarrollador aportó el push satisfactorio; HEAD local coincide y
  el directorio de trabajo estaba limpio antes de actualizar este MD.
- El Rol anterior era un enum, no la entidad ROL del DER. Se renombró
  ese tipo a CodigoRol, incluyendo las referencias Java de src/main y
  src/test. Se libera así el nombre Rol para
  la futura entidad con id y codigo, sin convertir de golpe el tipo existente.
- CodigoRol enumera únicamente CLIENTE, ADMIN y TECNICO, los códigos
  ya aprobados. No se agrega una cuarta clase de usuario ni una tabla por
  cada código. Esta preparación no implementa aún el catálogo persistido.
- El cambio afecta al nombre del tipo y a sus referencias Java,
  no a las propiedades rol, los métodos getRol/setRol, los códigos de
  autoridades, cadenas JSON ni documentación histórica. La columna
  transitoria rol de Usuario sigue usando Enumerated STRING en esta fase.
- Se revisaron los usos explícitos: enum, Usuario, UsuarioController,
  RegistroUsuarioService, UsuarioServiceTest y RegistroUsuarioServiceTest.
  Antes de editar no existía CodigoRol.java. UsuarioDTO y WebAuthentication usan
  getRol().name() y no requieren cambiar sus cadenas por este renombrado.
- El atajo de IntelliJ no respondió al desarrollador, quien autorizó
  excepcionalmente al asistente a aplicar solo este bloque. Se utilizó
  apply_patch para mover Rol.java a CodigoRol.java y actualizar las
  referencias exactas de los cinco archivos consumidores. No se ejecutó
  una sustitución global de textos ni se renombraron campos o métodos.
- La próxima entidad Rol y las asignaciones USUARIO_ROL siguen pendientes.
  La preparación no transforma una cuenta en multirrol, no incorpora aún
  permisos técnicos ni resuelve la autenticación por nickname.
- Se ejecutaron las cuatro suites filtradas con JDK 11 del equipo.
  La primera invocación sin JAVA_HOME se interrumpió sin resultado; el
  segundo intento encontró un bloqueo de permisos en la caché de Gradle.
  Se obtuvo autorización para repetir el mismo comando con acceso a esa
  caché. JAVA_HOME se fijó únicamente para el proceso de comprobación,
  sin modificar variables persistentes ni la configuración del proyecto.
- Resultado confirmado: BUILD SUCCESSFUL en 13 segundos, cuatro tareas
  (tres ejecutadas y una UP-TO-DATE). Los XML posteriores al cambio tienen
  30 pruebas, 0 fallos, 0 errores y 0 omitidas:
  RegistroUsuarioDTOTest, 10 (2026-11-03T08:57:00.469Z);
  UsuarioDTOTest, 2 (08:57:01.026Z);
  RegistroUsuarioServiceTest, 8 (08:57:01.055Z);
  UsuarioServiceTest, 10 (08:57:02.086Z), del 3 de noviembre de 2026.
- Se revisaron los diffs y se comprobó que no quedan referencias Java
  al tipo Rol antiguo. Los métodos esAdministrador y puedeAlquilar y
  la protección de DELETE conservan las mismas condiciones. El registro
  público sigue asignando CLIENTE; agregar el código TECNICO no implementa
  por sí solo permisos ni altas técnicas.
- Se compararon hashes SHA-256 de 130 archivos versionados ajenos al bloque
  y permanecieron iguales. Solo se modificaron el enum renombrado, los
  cinco consumidores previstos y este MD. No se tocaron frontend, seguridad,
  DTO, repositorios, dependencias ni propiedades de la base de datos.
- No se arrancó la aplicación ni se ejecutaron contextLoads, SQL o envíos
  de correo. No se realizaron staging, commit o push. Las pruebas son
  unitarias y no demuestran integración con una base ni compatibilidad
  de todos los datos existentes. Se mantiene el trabajo manual en los
  siguientes bloques salvo nueva autorización.

#### Aclaración del diseño final de roles

- El desarrollador recordó expresamente que ROL será una entidad de base
  de datos y que no desea trabajar con un enum de roles en la solución final.
  Conservar CodigoRol como lista de códigos era una opción de implementación,
  no una exigencia del DER. No se impone esa opción.
- Se mantiene el DER aprobado: entidad Rol con id y codigo de tipo String,
  catálogo con CLIENTE, ADMIN y TECNICO, y asignaciones USUARIO_ROL con
  clave compuesta usuario_id/rol_id. No se agrega otra tabla para el enum.
- CodigoRol queda únicamente como puente transitorio del código anterior
  para que esta etapa compile. Se deberá retirar al reemplazar sus usos
  por el catálogo y las asignaciones; no se dará el bloque por finalizado
  mientras Usuario siga dependiendo del atributo de rol único.
- Esta aclaración no autoriza convertir de golpe todos los consumidores:
  la edición excepcional realizada se limita al bloque pedido. La entidad,
  asociaciones, autenticación y pruebas se adaptarán en los siguientes
  pasos coordinados con el desarrollador.

### Etapa 19 Entidad del catálogo Rol

Estado: Rol.java creado manualmente, revisado y compilado el 3 de noviembre
de 2026. Las 30 pruebas existentes pasan; todavía no prueban directamente
la entidad nueva ni su persistencia. El asistente solo actualiza este MD.

- Se contrastó el bloque con ROL del DER v5 y el documento 25: solo id
  como PK y codigo obligatorio y único. No se agregan nombre, descripción,
  campos de auditoría ni una tabla adicional para cada clase de usuario.
- La clase incorporada es una entidad JPA con Table rol, id Integer generado
  mediante IDENTITY y codigo String de capacidad 20, no un campo enum ni
  una anotación Enumerated. Los códigos aprobados son CLIENTE, ADMIN y TECNICO.
- Codigo utiliza NotBlank, Size máximo 20 y Pattern para admitir únicamente
  esos tres códigos. El constructor y setter normalizan trim y mayúsculas
  con Locale.ROOT. Estas validaciones Java no se confunden con un CHECK SQL:
  la obligatoriedad y unicidad física se declaran mediante Column.
- Se incluyen constructor vacío JPA, constructor con código, getters y setter
  de código; no se agrega setter público de id ni borrado físico en cascada.
- Esta etapa no conecta Rol a Usuario ni incorpora USUARIO_ROL. CodigoRol
  permanece transitoriamente solo porque sus consumidores aún no se
  adaptaron. No se lo conserva como dependencia de la entidad nueva.
- No se ejecuta la aplicación ni se crean filas de roles mediante el código
  propuesto. La carga inicial de catálogo, su repositorio, las asignaciones,
  el registro, DTO y autenticación se adaptarán en pasos siguientes.
- Se revisó el archivo completo: paquete models, imports javax, Entity y
  Table, generación del id, cuatro anotaciones de codigo, constructor JPA,
  constructor con código, getters y normalización coinciden con lo indicado.
  Rol no depende de CodigoRol ni declara relaciones prematuras con Usuario.
- CodigoRol sigue presente y sus usos Java continúan exclusivamente en
  el modelo transitorio y consumidores anteriores. No se borró ese archivo
  antes de adaptar Usuario, registro, seguridad y pruebas al catálogo.
- El desarrollador informó BUILD SUCCESSFUL en 7 segundos. La clase Rol
  compilada (2026-11-03T09:08:34Z) es posterior al fuente (09:08:20Z).
  Los XML confirman 30 pruebas, 0 fallos, 0 errores y 0 omitidas:
  RegistroUsuarioDTOTest, 10 (09:08:36.637Z); UsuarioDTOTest, 2 (09:08:37.172Z);
  RegistroUsuarioServiceTest, 8 (09:08:37.296Z);
  UsuarioServiceTest, 10 (09:08:38.167Z), del 3 de noviembre de 2026.
- No se ejecutó Gradle, la aplicación, SQL ni envíos desde el asistente.
  git diff --check no informó problemas. No se hicieron escrituras Git
  ni ediciones Java en esta revisión. Crear la clase no demuestra todavía
  que exista la tabla o que sus filas hayan sido precargadas.

### Etapa 20 Repositorio del catálogo Rol

Estado: RolRepository creado manualmente, revisado y compilado el 3 de
noviembre de 2026. No se modifica Java desde el asistente.

- Se incorporó una interfaz JpaRepository<Rol, Integer>, coherente con el
  tipo de la PK de la entidad. El método Optional<Rol> findByCodigo(String
  codigo) permite buscar, por ejemplo, la fila CLIENTE del catálogo.
- Se mantiene el mismo patrón que GeneroRepository. No se incorporan
  consultas SQL manuales, métodos innecesarios ni un endpoint público
  que permita crear o asignar roles desde el registro.
- Los códigos de búsqueda deberán usar la representación canónica en
  mayúsculas del catálogo. Declarar la interfaz no precarga las tres filas
  ni conecta por sí solo Rol con Usuario o con la autenticación.
- No se modifica Usuario ni se retira CodigoRol en esta etapa. La compilación no valida
  la consulta derivada contra una base; esa integración sigue pendiente.
- Se revisó el archivo completo: paquete repositories, imports Rol,
  JpaRepository y Optional, declaración de interfaz y firma findByCodigo
  coinciden con lo indicado. No se agregaron métodos ni anotaciones extra.
- El desarrollador informó BUILD SUCCESSFUL en 1 segundo, una tarea
  compileJava ejecutada. La clase compilada RolRepository tiene fecha
  2026-11-03T09:15:10Z, posterior al fuente (09:14:59Z).
  No se considera que se hayan repetido las 30 pruebas en esta ejecución.
- git diff --check no informó problemas. El asistente no ejecutó Gradle,
  la aplicación ni SQL y no realizó staging, commit o push.

### Etapa 21 Clase de clave compuesta de UsuarioRol

Estado: UsuarioRolId creado manualmente, revisado y compilado el 3 de
noviembre de 2026. El asistente solo actualiza este MD.

- Se conserva la PK aprobada de USUARIO_ROL: el par usuario_id/rol_id,
  sin identificador numérico adicional y con FK futuras a USUARIO y ROL.
  La clase representa ese valor compuesto, no una entidad o tabla nueva.
- Se incorporaron Embeddable, Serializable y serialVersionUID estático; campos
  Integer usuarioId y rolId con Column de nombres usuario_id y rol_id,
  no nulos, y validaciones NotNull/Positive para ambos identificadores.
- Tiene constructor vacío JPA, constructor con los dos identificadores,
  getters y equals/hashCode basados en ambas partes. No lleva Entity,
  GeneratedValue ni setters que faciliten cambiar una clave ya asignada.
- La próxima entidad UsuarioRol incorporará esta clase mediante EmbeddedId
  y coordinará los vínculos con MapsId. Las asociaciones no se declaran
  dentro de la clase de clave. Referencia técnica: [API JPA EmbeddedId](https://docs.oracle.com/javaee/7/api/javax/persistence/EmbeddedId.html).
- Crear esta clase por sí solo no materializa la PK ni las FK en la base
  ni evita duplicados persistidos sin la entidad que la use. La integración,
  validación del valor embebido y pruebas de igualdad seguirán después.
- En este paso no se modifica Usuario, Rol, registro, seguridad ni CodigoRol.
  Se ejecutó compileJava desde la terminal del desarrollador, sin arrancar
  la aplicación desde el asistente.
- Se revisó el archivo completo: paquete, seis imports, anotación,
  dos campos Integer con sus nombres de columna, validaciones, constructores,
  getters, comparación de ambas partes y hashCode coinciden con lo indicado.
  No tiene setters ni se agregó una tabla para la clave.
- El desarrollador informó BUILD SUCCESSFUL en 10 segundos, una tarea
  compileJava ejecutada. La clase compilada UsuarioRolId tiene fecha
  2026-11-03T19:01:07Z, posterior al archivo fuente (19:00:45Z).
  Esto confirma compilación, no pruebas de igualdad ni de mapeo con la base.
- git diff --check no informó problemas. El asistente no editó Java,
  ejecutó Gradle, SQL o la aplicación ni realizó operaciones de escritura Git.

### Etapa 22 Entidad de asignación UsuarioRol

Estado: UsuarioRol creado manualmente, revisado y compilado el 3 de
noviembre de 2026. La última invocación de compileJava reutilizó el
resultado existente. No se modifica Java desde el asistente.

- La entidad incorporada representa usuario_rol del DER: EmbeddedId de tipo
  UsuarioRolId, sin GeneratedValue, tercera columna id ni columnas de versión
  o fechas añadidas. NotNull y Valid sobre el identificador incluyen las
  validaciones de sus dos partes.
- Se vincula a Usuario y Rol mediante ManyToOne LAZY obligatorios,
  JoinColumn usuario_id/rol_id y MapsId usuarioId/rolId, exactamente con
  los nombres de los atributos del valor embebido. Cada columna es parte
  de la PK compuesta y FK al padre correspondiente; no se declara UNIQUE
  individual en esas dos columnas.
- No se incorpora cascade REMOVE ni otras cascadas sobre los padres.
  La asignación no recibe directamente datos de un formulario ni concede
  permisos por construirse; la autorización sigue siendo del servicio.
- Tiene constructor JPA vacío y otro con Usuario/Rol que exige sus
  identificadores positivos. La existencia real de las filas se comprobará
  en el servicio y mediante FK; un número positivo no la demuestra.
  El constructor arma la clave y se incluyen únicamente los getters.
- Para el futuro registro transaccional, el usuario debe obtener su id
  antes de construir esta asignación. Guardar Persona, Usuario y su rol
  seguirá siendo parte de la misma transacción, no tres altas independientes.
  Esta secuencia deberá coordinarse al adaptar el servicio.
- Referencia técnica: [API JPA MapsId](https://docs.oracle.com/javaee/7/api/javax/persistence/MapsId.html).
  La relación comparte la columna con la parte indicada de EmbeddedId;
  no son cuatro columnas ni claves adicionales.
- No se modifica aún Usuario, sus DTO, registro, autenticación ni CodigoRol.
  El repositorio de asignaciones y la conexión del rol múltiple siguen
  pendientes. Se solicita compileJava después de la creación manual;
  la compilación no prueba PK/FK reales ni operaciones de asignación.
- Las propuestas del documento 38 permanecen pendientes de confirmación
  y no se incorporan automáticamente al bloque actual de roles.
- Se revisó el archivo completo: paquete, imports javax, Entity/Table,
  EmbeddedId/Valid/NotNull, ambas relaciones y MapsId, nombres de columnas,
  comprobaciones del constructor, armado de la clave y tres getters coinciden
  con lo indicado. UsuarioRolId conserva los dos atributos compatibles.
- El desarrollador informó BUILD SUCCESSFUL en 1 segundo y una tarea
  UP-TO-DATE. No hubo una compilación nueva en esa última invocación,
  pero la clase UsuarioRol.class (2026-11-03T19:10:54Z) es posterior al fuente
  (19:10:31Z), por lo que el artefacto disponible respalda la compilación
  del archivo guardado. No se afirma haber ejecutado pruebas de este modelo.
- git diff --check no informó problemas. El asistente no ejecutó Gradle,
  SQL o la aplicación ni realizó staging, commit o push.

### Etapa 23 Repositorio de asignaciones UsuarioRol

Estado: UsuarioRolRepository creado manualmente, revisado y compilado el
3 de noviembre de 2026. El asistente solo actualiza este MD.

- Se incorporó JpaRepository<UsuarioRol, UsuarioRolId>: el segundo tipo es
  la clase de clave compuesta, no Integer ni un nuevo id autonumérico.
  Se conservan los métodos heredados de búsqueda por clave y guardado.
- Se agrega List<UsuarioRol> findByUsuario_Id(Integer usuarioId), navegando
  la relación usuario hasta su id para obtener sus asignaciones. El método
  no usa SQL concatenado ni recibe un nombre libre de atributo.
- La autorización, validación del usuario y restricciones de cambios de rol
  corresponderán al servicio. Declarar el repositorio no concede acceso a
  asignaciones ajenas ni incorpora endpoints de gestión pública.
- La consulta no carga automáticamente todas las asociaciones LAZY. Al
  consumir los datos del rol habrá que hacerlo en una transacción de servicio
  o adaptar expresamente la consulta; no se confiará en open-in-view.
- En este paso no se modifica Usuario, registro, DTO, autenticación ni
  CodigoRol. La compilación no prueba el SQL
  derivado ni las PK/FK de la tabla contra una base de datos.
- Se revisaron el archivo completo, ubicación, imports de entidad y clave,
  genéricos y firma findByUsuario_Id: coinciden con lo indicado. No hay
  métodos o anotaciones adicionales. El desarrollador informó compilación
  satisfactoria; la clase tiene fecha 2026-11-03T19:17:28Z, posterior al
  fuente (19:17:06Z). No se registra una nueva ejecución de las 30 pruebas.
- El asistente no editó Java, ejecutó Gradle o la aplicación ni realizó
  operaciones SQL, staging, commit o push en esta revisión.

### Etapa 24 Relación de Usuario con sus asignaciones de rol

Estado: tres inserciones aplicadas en Usuario.java por el asistente el
3 de noviembre de 2026, con autorización puntual del desarrollador.
Revisión estática realizada y comprobación del punto 4 completada por el
desarrollador: compilación y cuatro suites unitarias satisfactorias.
El asistente no ejecutó Gradle ni la aplicación. El mapeo con la base
de datos todavía no se ha probado.

- Se agregó una colección privada Set<UsuarioRol> usuarioRoles,
  inicializada con HashSet, OneToMany mappedBy usuario y fetch LAZY.
  El atributo usuario de UsuarioRol es el propietario de la relación.
  No se crea una columna adicional de roles en usuario ni otra tabla.
- Se agregó JsonIgnore a la colección y su import para no serializar ni
  deserializar libremente el grafo de asignaciones desde la entidad.
  Los contratos públicos seguirán siendo DTO y el registro no podrá elegir
  roles por enviar esa propiedad en JSON.
- Se incorporó solo el getter getUsuarioRoles, sin setter de reemplazo ni
  cascadas de borrado/orphanRemoval. El guardado o retirada de asignaciones
  deberá coordinarse explícitamente en los servicios con su autorización.
- No se agrega NotEmpty a esta colección en esta fase: el usuario debe
  obtener id antes de construir UsuarioRol con el constructor actual.
  La creación atómica de cuenta y rol obligatorio se garantizará en el
  servicio transaccional al adaptar el registro, sin dar por resuelta esa
  condición por la colección vacía inicial o por el mapping.
- Se conservan temporalmente el atributo CodigoRol rol, getRol/setRol,
  esAdministrador y puedeAlquilar. La revisión de consumidores confirma
  que registro, DTO, autenticación, DELETE y dos pruebas todavía los usan.
  No se mezcla la colección nueva con el enum para sumar autoridades ni
  se lo presenta como dos fuentes definitivas de permisos.
- Los próximos bloques adaptarán esos consumidores al catálogo y retirarán
  el atributo antiguo y CodigoRol. Esta edición aislada no habilita aún
  permisos múltiples ni resuelve sesiones existentes o login por nickname.
- Se solicita ejecutar las cuatro suites filtradas para compilar y comprobar
  regresión del código actual. No se arranca la aplicación ni se declara
  verificado el mapeo JPA o su persistencia mediante esas pruebas unitarias.
- La comparación contra el contenido anterior a esta intervención confirma
  exactamente tres inserciones: import JsonIgnore, colección anotada y getter.
  mappedBy usuario coincide con el atributo UsuarioRol.usuario; Set, HashSet
  y las anotaciones JPA ya contaban con los imports necesarios.
- Se revisó el resto de Usuario.java sin modificarlo: relación obligatoria
  con Persona, normalización de email/nickname, almacenamiento del hash y
  atributo Version se conservan. Esto no equivale a probar el módulo completo.
  El rol único anterior y la relación con Tarjeta siguen siendo transitorios.
- Pendiente detectado en esa revisión: equals/hashCode usan el email mutable.
  Si este cambia cuando el usuario está en una colección hash, puede fallar
  su búsqueda o retirada; además, dos usuarios distintos sin email comparan
  iguales. Se deberá definir y probar una identidad estable en un bloque
  separado, sin cambiarla silenciosamente durante la conexión de roles.
- Comprobación reservada al desarrollador:

```powershell
.\gradlew.bat test --tests "RegistroUsuarioServiceTest" --tests "UsuarioServiceTest" --tests "UsuarioDTOTest" --tests "RegistroUsuarioDTOTest"
```

- El desarrollador informó BUILD SUCCESSFUL en 6 segundos, tres tareas
  ejecutadas y una UP-TO-DATE. Se corroboraron los cuatro XML locales de
  build/test-results/test, correspondientes al 3 de noviembre de 2026,
  entre 19:37:03Z y 19:37:04Z: RegistroUsuarioDTOTest 10, UsuarioDTOTest 2,
  RegistroUsuarioServiceTest 8 y UsuarioServiceTest 10. Total: 30 pruebas,
  sin fallos, errores ni omisiones. Estos resultados verifican la regresión
  cubierta por las suites existentes, no la persistencia real de UsuarioRol
  ni la futura autorización con varios roles.
- El aviso de funcionalidades obsoletas de Gradle no impidió esta ejecución.
  No se modifican versiones de herramientas o dependencias en este bloque.

### Etapa 25 Dependencias del registro para asignar roles de catálogo

Estado: imports, atributos y constructor de RegistroUsuarioService.java
modificados por el asistente el 3 de noviembre de 2026, con autorización
puntual del desarrollador. Compilación del punto 4 completada por el
desarrollador. El asistente no ejecutó Gradle, SQL ni la aplicación.

- Se incorporaron los imports de RolRepository y UsuarioRolRepository, dos
  atributos final y sus parámetros/asignaciones en el constructor existente.
  Se conservan las seis dependencias anteriores; el constructor pasa a ocho.
  No se agrega otro constructor ni Autowired: la inyección de Spring seguirá
  utilizando el único constructor disponible.
- Este paso prepara la búsqueda del rol CLIENTE y el guardado explícito
  de UsuarioRol. No modifica todavía registrarUsuario, sus validaciones,
  el hash, la transacción, el DTO de salida ni la asignación transitoria
  de CodigoRol.CLIENTE. Los atributos nuevos quedarán sin uso hasta el
  siguiente bloque; no se afirma que ya se guarden asignaciones reales.
- La comprobación solicitada es compileJava desde la terminal del
  desarrollador, sin aplicación, SQL ni pruebas con contexto Spring.
- En el bloque siguiente se adaptará el método y sus pruebas unitarias
  conjuntamente: RolRepository deberá devolver CLIENTE con identificador
  válido; el Usuario guardado deberá tener id antes de construir UsuarioRol.
  Ambos repositorios necesitarán sus mocks al probar la nueva lógica.
  La falta del rol de catálogo deberá impedir un alta incompleta, no crear
  privilegios a partir de datos enviados por el cliente.
- Se revisaron los dos imports, atributos final y los ocho parámetros y
  asignaciones del constructor. registrarUsuario conserva su lógica anterior.
  El desarrollador informó BUILD SUCCESSFUL en 2 segundos, con compileJava
  ejecutada. La clase compilada tiene fecha 2026-11-03T19:59:06Z, posterior
  al fuente (19:50:31Z). No se registra una ejecución nueva de las pruebas.

### Etapa 26 Registro con asignación CLIENTE en usuario_rol

Estado: cambios aplicados el 3 de noviembre de 2026 por el asistente en
RegistroUsuarioService.java y RegistroUsuarioServiceTest.java, conforme a
la autorización puntual del desarrollador. Revisión estática realizada;
compilación y resultados de las cuatro suites filtradas corroborados tras
la comprobación del desarrollador: 32 pruebas sin fallos. La última
invocación reutilizó las cuatro tareas UP-TO-DATE; no ejecutó las pruebas
de nuevo. El asistente no ejecutó Gradle, SQL ni la aplicación.

- Se añadieron imports de Rol y UsuarioRol al servicio. Después de las
  comprobaciones actuales y antes de hashear o guardar, se busca CLIENTE
  mediante RolRepository.findByCodigo. Si no existe, se lanza
  IllegalStateException con el mensaje "El rol CLIENTE no está configurado."
  No se toma el rol ni su identificador del formulario ni se crea el catálogo
  dinámicamente al registrar una cuenta.
- Se conservan Persona, normalizaciones, validaciones, hash, activo y el puente
  CodigoRol.CLIENTE mientras el DTO y la autenticación dependan de él.
  No se conceden privilegios mediante una combinación de ambas fuentes.
- Se mantiene saveAndFlush del Usuario para contar con su id y construir
  UsuarioRol con ese Usuario y el Rol encontrado. Se guarda la asignación
  mediante save y se utiliza la instancia devuelta (que puede ser la instancia
  administrada tras un merge). Se añade a usuarioRoles para sincronizar la
  colección inversa y se ejecuta flush antes de crear el DTO de respuesta.
  No se modifica el constructor de UsuarioRol ni se agregan setters de ids.
- Se mantiene el único límite transaccional del método de registro. flush
  sincroniza cambios y adelanta la detección de restricciones; no confirma
  la transacción. Las excepciones de persistencia deben propagarse hasta
  salir del servicio para que la transacción pueda revertirse completa.
- Se adaptó la prueba existente: dos mocks de repositorios, rol CLIENTE real
  con id simulado 2 mediante ReflectionTestUtils solo en test, devolución
  del argumento al simular save de UsuarioRol, y captura/comprobación de
  los dos componentes de la clave, referencias y colección del Usuario.
  El id 2 no debe aparecer como supuesto en el código de producción.
- Se añadieron pruebas para catálogo sin CLIENTE (sin guardar ni hashear) y
  error al hacer flush de la asignación (excepción propagada). Las pruebas
  actuales de duplicados y catálogos inválidos deben seguir sin guardar
  asignaciones. Los stubs nuevos se ubican solo en los caminos que los usan,
  evitando stubbing innecesario con Mockito estricto.
- Con las dos pruebas nuevas se definen 10 casos de RegistroUsuarioServiceTest
  y 32 en las cuatro suites filtradas, corroborados en los informes locales.
  Los mocks no verifican rollback real, SQL,
  FK ni la seguridad por proxy; esas comprobaciones de integración siguen
  pendientes. No se ejecutará el test SpringBootTest sin base aislada.
- La carga inicial de CLIENTE/ADMIN/TECNICO sigue pendiente de su bloque de
  catálogos. Este cambio no habilita aún login por nickname, DTO multirrol
  ni autenticación basada en usuario_rol; CodigoRol no se elimina todavía.
- La revisión estática confirma que el servicio coincide con las inserciones
  propuestas, busca CLIENTE antes de hashear o guardar y conserva el método
  transaccional y CodigoRol.CLIENTE. El archivo de prueba define 10 casos;
  no se eliminó ninguno de los ocho anteriores y los otros siete métodos
  de prueba existentes, aparte del caso exitoso ampliado, conservan su
  contenido. Se revisaron los stubs de los caminos de éxito y error.
- La comparación de hashes de 140 archivos ajenos a este bloque no detectó
  cambios durante la intervención. Solo se editaron el servicio, su prueba
  y este MD. No se realizó staging, commit ni push. En esa revisión estática
  todavía no se había afirmado que las 32 pruebas pasaran; la evidencia de
  ejecución se corroboró posteriormente, como se detalla a continuación.
- Comprobación reservada al desarrollador:

```powershell
.\gradlew.bat test --tests "RegistroUsuarioServiceTest" --tests "UsuarioServiceTest" --tests "UsuarioDTOTest" --tests "RegistroUsuarioDTOTest"
```

- El desarrollador informó BUILD SUCCESSFUL en 1 segundo, con las cuatro
  tareas UP-TO-DATE. Esta invocación no constituye una ejecución nueva.
  Se revisaron los XML locales del 3 de noviembre de 2026 entre 20:49:12Z
  y 20:49:13Z: RegistroUsuarioDTOTest 10, UsuarioDTOTest 2,
  RegistroUsuarioServiceTest 10 y UsuarioServiceTest 10. Total: 32 pruebas,
  cero fallos, errores u omisiones. El informe de registro incluye
  rechazaRegistroSiNoExisteRolCliente y propagaConflictoAlPersistirLaAsignacion.
- Los fuentes del servicio y su prueba datan de 20:12:34Z/20:12:35Z; las
  clases compiladas correspondientes, de 20:49:10Z/20:49:11Z, y los XML son
  posteriores. Los artefactos disponibles respaldan la compilación y las
  pruebas del bloque modificado. No se pidió repetirlas innecesariamente
  ni se presentan como pruebas de base de datos o autorización real.

### Etapa 27 Consultas explícitas para datos personales y roles

Estado: tres imports y tres métodos agregados a UsuarioRepository.java
por el asistente el 3 de noviembre de 2026, con autorización puntual del
desarrollador. Revisión estática realizada; compilación del punto 3
corroborada el 4 de noviembre de 2026 tras la ejecución del desarrollador.
El asistente no ejecutó Gradle, SQL ni la aplicación. También se actualiza
este MD; la validación JPA contra una base sigue pendiente.

- Se revisaron UsuarioRepository, UsuarioDTO, los tres GET de UsuarioController,
  UsuarioService, RegistroUsuarioService y sus pruebas, WebAuthentication y
  los consumidores JavaScript. El DTO actual devuelve un único rol desde
  CodigoRol; index.js y admin.js todavía consumen ese campo. No se elimina
  ese contrato ni se presenta la autenticación multirrol como implementada.
- Se agregaron tres métodos nuevos con Query JPQL y EntityGraph sobre
  persona.genero y usuarioRoles.rol. Ambas rutas coinciden con los atributos
  actuales del modelo y abarcan las relaciones que necesitará UsuarioDTO.
  No se modifica el fetch LAZY global de las entidades.
- buscarActivosConDatosYRoles: select distinct u from Usuario u where
  u.activo = true; devuelve List<Usuario>.
- buscarPorIdConDatosYRoles: select distinct u from Usuario u where
  u.id = :id; devuelve Optional<Usuario>, con Param id de tipo Integer.
- buscarPorEmailConDatosYRoles: select distinct u from Usuario u where
  u.email = :email; devuelve Optional<Usuario>, con Param email de tipo String.
  No se concatenan valores recibidos dentro del JPQL. La selección por email
  del usuario actual continuará tomando la identidad del principal, no un
  email libre del formulario. No se cambia todavía el login a nickname.
- Los dos métodos individuales conservan la selección de los findById y
  findByEmail actuales; el filtro de activo del GET por id y los controles
  de acceso no se eliminan. La autorización no la otorga el repositorio.
  No se cambian las consultas de recuperación, escritura o autenticación.
- Se incorporaron tres imports nuevos: EntityGraph, Query y Param. Se agregaron
  los métodos sin borrar ni modificar los existentes. Todavía no se conectan
  al controlador o servicio, ni se cambia UsuarioDTO o CodigoRol.
- EntityGraph configura la carga para esas consultas concretas. No garantiza
  una única consulta SQL ni resuelve por sí solo los costes de las relaciones
  EAGER heredadas. Se consultó la documentación oficial de Spring Data JPA
  2.7 sobre [grafos de carga](https://docs.spring.io/spring-data/jpa/docs/2.7.18/reference/html/#jpa.entity-graph)
  y la API de [EntityGraph](https://docs.spring.io/spring-data/jpa/docs/current/api/org/springframework/data/jpa/repository/EntityGraph.html)
  que documenta rutas anidadas y soporte desde 1.9. No se actualizan librerías.
- La comprobación solicitada es compileJava. Esta tarea no valida el JPQL,
  la carga del grafo ni la persistencia contra una base real; esas pruebas
  de integración siguen pendientes. No se arranca el contexto SpringBootTest
  ni la aplicación contra la base actual para comprobar estos métodos.
- El siguiente bloque adaptará la representación de roles y sus consultas
  consumidoras de manera compatible con el front, sin elegir arbitrariamente
  un primer rol como autoridad ni sumar permisos del enum y la tabla.
- La comparación con el archivo anterior a esta intervención confirma
  únicamente las inserciones propuestas: tres imports y los tres métodos
  completos. No se borró ni modificó ningún método existente. Se comprobaron
  estáticamente los parámetros id/email, los tipos de retorno y las rutas
  persona.genero y usuarioRoles.rol frente a las entidades guardadas.
- La comparación de hashes de 141 archivos ajenos al repositorio y este MD
  no detectó cambios durante la intervención. No se modificaron el DTO,
  controladores, servicios, entidades, seguridad ni pruebas. No se realizó
  staging, commit ni push. La revisión no verifica el JPQL contra una base.
- Comprobación reservada al desarrollador:

```powershell
.\gradlew.bat compileJava
```

- El desarrollador informó BUILD SUCCESSFUL en 9 segundos, con una tarea
  compileJava ejecutada. Se revisó nuevamente el archivo completo: los tres
  imports, tres métodos, EntityGraph, JPQL, parámetros y tipos de retorno
  coinciden con lo indicado y se conservan los métodos anteriores.
  UsuarioRepository.class tiene fecha 2026-11-04T06:29:03Z, posterior al
  fuente (2026-11-03T21:41:00Z). No se registra una ejecución nueva de las
  suites unitarias ni se presenta compileJava como prueba de las consultas.

### Etapa 28 Representación multirrol del DTO y lecturas HTTP

Estado: cambios aplicados por el asistente el 4 de noviembre de 2026 en
UsuarioController.java, UsuarioDTO.java y UsuarioDTOTest.java, con
autorización puntual del desarrollador. Revisión estática realizada;
compilación y resultados del bloque 4 corroborados el 4 de noviembre de
2026: 34 pruebas sin fallos. El asistente no ejecutó Gradle, SQL ni la
aplicación.

- Se sustituyeron exclusivamente las consultas de los tres GET de UsuarioController:
  getUsuarios usa buscarActivosConDatosYRoles; getUsuarioPorId usa
  buscarPorIdConDatosYRoles; getUsuarioActual usa
  buscarPorEmailConDatosYRoles con el email del Principal. Se mantienen los
  filtros, respuestas HTTP y reglas de autorización existentes. No se cambia
  findById en DELETE ni ninguna consulta de escritura o autenticación.
- Se incorporaron a UsuarioDTO un atributo List<String> roles, su getter y el
  import Collectors. Se construye la lista desde usuario.getUsuarioRoles(),
  tomando el codigo del Rol de cada asignación, sin duplicados y ordenada
  alfabéticamente para una salida determinista. Ese orden no es una jerarquía
  de permisos ni se debe elegir su primer elemento como autoridad.
- Se mantienen por ahora el atributo singular rol, su getter y su asignación
  antigua, porque el front todavía los consume. El nuevo campo roles no se
  obtiene del enum ni usa CLIENTE como fallback ante una colección vacía.
  Esta compatibilidad es transitoria: no se suman las dos fuentes para
  autorizar y la autenticación sigue pendiente de su adaptación.
- Se aplicaron los cambios del DTO y los tres GET en el mismo bloque. Sus nuevas
  consultas solicitan cargar persona.genero y usuarioRoles.rol antes de
  construir el DTO, sin confiar en open-in-view para esas relaciones.
  Se verificó que los otros dos constructores de UsuarioDTO en producción
  están dentro de RegistroUsuarioService y UsuarioService transaccionales;
  el registro ya sincroniza la asignación con la colección en memoria.
  No se cambian las entidades a EAGER globalmente.
- Se añadieron dos pruebas a UsuarioDTOTest: todos los roles asignados aparecen
  ordenados e independientes del enum transitorio, y sin asignaciones la
  lista queda vacía sin inventar CLIENTE. Este caso de representación no
  autoriza cuentas válidas sin roles: el registro sigue creando su CLIENTE
  obligatorio y la futura autenticación deberá rechazar una cuenta sin roles.
- Los fixtures de prueba usan Rol y UsuarioRol reales, Usuario con id 17
  y ReflectionTestUtils solo para simular el id generado de Rol. Se mantienen
  intactas las dos pruebas existentes; no se añaden setters de ids a Rol.
  Se corroboraron 4 casos de UsuarioDTOTest y 34 en las cuatro suites
  filtradas, sin fallos, errores ni omisiones.
- Esta etapa no modifica login, sesiones, permisos, front, CodigoRol, bajas
  ni esquema. Las pruebas unitarias no validan las consultas JPQL, la carga
  JPA real, el aislamiento de sesión ni autorizaciones HTTP; esas pruebas
  de integración siguen pendientes en una base aislada.
- Se comparó el contenido anterior a esta intervención: UsuarioController
  coincide exactamente con los tres reemplazos propuestos, conservando
  findById en DELETE y el resto de su código. UsuarioDTO coincide con las
  cuatro adiciones previstas: import, atributo, mapeo y getter. Las dos
  pruebas anteriores conservan íntegramente su contenido y ahora se definen
  cuatro casos en UsuarioDTOTest. Esa revisión inicial fue estática; los
  resultados de ejecución se corroboraron después, como se detalla abajo.
- La comparación de hashes de 139 archivos ajenos a estos tres archivos
  y este MD no detectó cambios durante la intervención. No se realizó
  staging, commit ni push. git diff --check no informó errores de espacios;
  la advertencia de conversión LF/CRLF corresponde al índice documental
  previamente modificado y no motivó cambios de configuración Git.
- Comprobación reservada al desarrollador:

```powershell
.\gradlew.bat test --tests "RegistroUsuarioServiceTest" --tests "UsuarioServiceTest" --tests "UsuarioDTOTest" --tests "RegistroUsuarioDTOTest"
```

- El desarrollador informó BUILD SUCCESSFUL en 10 segundos, con tres tareas
  ejecutadas y una UP-TO-DATE. Se revisaron los cuatro XML locales del
  4 de noviembre de 2026 entre 06:48:47Z y 06:48:49Z: RegistroUsuarioDTOTest
  10, UsuarioDTOTest 4, RegistroUsuarioServiceTest 10 y UsuarioServiceTest 10.
  Se incluyen los casos nuevos incluyeTodosLosRolesSinUsarElEnum y
  noInventaRolesCuandoNoHayAsignaciones. Total: 34, cero fallos, errores
  y omisiones. Las clases del controlador/DTO/prueba (06:48:44Z-06:48:45Z)
  son posteriores a sus fuentes (06:45:37Z-06:45:39Z).
- La evidencia respalda la compilación y las suites unitarias indicadas;
  no demuestra el funcionamiento HTTP, JPQL o JPA real. El asistente no
  repitió las pruebas ni ejecutó el test con contexto SpringBootTest.

### Etapa 29 Cargador de credenciales y roles para Spring Security

Estado: UsuarioDetailsService.java creado por el asistente el 4 de noviembre
de 2026, con autorización puntual del desarrollador y conforme al código
propuesto. Revisión estática realizada y compilación del bloque 3 corroborada
tras la ejecución del desarrollador del 4 de noviembre de 2026.
El asistente no ejecutó Gradle, SQL ni la aplicación.
La prueba del servicio todavía no se creó.

- Se creó un servicio que implementa UserDetailsService, con UsuarioRepository
  por constructor y loadUserByUsername transaccional de solo lectura.
  Normalizar el identificador actual como email con trim y Locale.ROOT,
  rechazar identificadores nulos/vacíos y buscar mediante
  buscarPorEmailConDatosYRoles. Conservar el email como username del principal
  para no romper los consumidores actuales. El cambio a nickname sigue
  pendiente de su bloque coordinado; el nombre del método lo define Spring.
- Obtener todas las autoridades de usuarioRoles.rol.codigo, sin duplicados,
  sin leer CodigoRol, sin elegir solo el primer rol y sin fallback CLIENTE.
  Una cuenta sin asignaciones se rechaza mediante UsernameNotFoundException.
  Mantener los códigos ADMIN/CLIENTE/TECNICO sin prefijo ROLE_, compatibles
  con las reglas actuales hasAuthority/hasAnyAuthority.
- Devolver un User nuevo de Spring por invocación, con el hash ya guardado
  (sin volver a hashear ni comparar aquí la contraseña), activo como enabled
  y los otros tres indicadores del constructor en true. No se implementan
  vencimiento de cuenta/credenciales ni bloqueo nuevos, ni se agregan campos
  o tablas por esos indicadores. El proveedor de autenticación comprueba
  credenciales y enabled cuando se conecte el servicio al flujo.
- La transacción y la consulta con grafo cubren el acceso a las relaciones
  durante el armado del UserDetails, no durante una serialización HTTP.
  Este objeto interno contiene el hash y nunca debe devolverse como DTO
  público ni imprimirse con credenciales en logs.
- Se revisó la API oficial de [User de Spring Security 5.7.10](https://docs.spring.io/spring-security/site/docs/5.7.10/api/org/springframework/security/core/userdetails/User.html),
  incluidos los indicadores y la creación de una instancia nueva. No se
  actualizan dependencias ni se cambia el PasswordEncoder BCrypt existente.
- En este paso se solicita solo compileJava tras crear la clase. No se
  modifica WebAuthentication: su lambda actual sigue presente. Antes del
  cableado explícito se añadirán pruebas del servicio, incluyendo múltiples
  autoridades, ausencia de roles, identificación inválida y estado enabled.
  La compilación no es una prueba de login ni de configuración del proveedor.
- No se modifican WebAuthorization, front, sesiones, DTO, bajas, catálogos
  ni CodigoRol. La revocación de roles/inactivación en sesiones existentes,
  permisos específicos de TECNICO y pruebas HTTP/JPA reales siguen pendientes;
  crear este cargador no los resuelve automáticamente.
- La lectura posterior confirma coincidencia exacta con el código propuesto:
  paquete, imports, constructor, normalización, consulta con grafo, autoridades
  de las asignaciones, rechazo de identificador vacío/cuenta sin roles y
  construcción de User con activo como enabled. No usa CodigoRol ni encode.
  Es una revisión estática, no una ejecución del método ni una prueba de login.
- La comparación de hashes de 142 archivos existentes, excluido este MD,
  no detectó cambios durante la intervención. Solo se creó el servicio y
  se actualizó este documento. WebAuthentication conserva su contenido y
  no se realizó staging, commit ni push.
- Comprobación reservada al desarrollador:

```powershell
.\gradlew.bat compileJava
```

- El desarrollador informó BUILD SUCCESSFUL en 3 segundos, con una tarea
  compileJava ejecutada. Se revisó nuevamente el servicio completo: coincide
  con el código propuesto. La clase compilada tiene fecha
  2026-11-04T07:17:02Z, posterior al fuente (07:04:19Z). Esta evidencia
  corrobora compilación, no una prueba de login o una ejecución de sus ramas.

### Etapa 30 Pruebas unitarias de UsuarioDetailsService

Estado: UsuarioDetailsServiceTest.java creado por el asistente el 4 de
noviembre de 2026 dentro de src/test/java, en el paquete
DSII.TurismoSustentable.services, con autorización puntual del desarrollador.
Revisión estática realizada; compilación y ejecución de pruebas del punto 3
corroboradas tras la ejecución del desarrollador: 40 pruebas sin fallos.
No se ejecutó Gradle, SQL ni la aplicación desde el asistente.

- Se usan JUnit Jupiter y MockitoExtension, con UsuarioRepository simulado y
  UsuarioDetailsService inyectado por Mockito. No usar SpringBootTest ni
  arrancar un contexto, acceder a una base o enviar correos. Los fixtures
  de Persona, Usuario y asignaciones son objetos en memoria.
- Se incorporaron seis métodos de prueba: (1) email normalizado, username, hash,
  indicadores y autoridades ADMIN/TECNICO exactas sin agregar el rol legado;
  (2) activo false se transmite como enabled false; (3) usuario inexistente
  provoca UsernameNotFoundException; (4) ausencia de asignaciones también
  provoca esa excepción sin inventar CLIENTE; (5) email nulo, vacío o solo
  espacios se rechaza sin invocar el repositorio; (6) cada carga devuelve
  una instancia nueva y borrar sus credenciales en memoria no modifica el
  hash del Usuario ni el de una carga posterior.
- El segundo caso no comprueba que un proveedor real rechace el login;
  verifica el indicador entregado a Spring. El sexto usa CredentialsContainer
  sobre el UserDetails retornado, no sobre la entidad. No se compara una
  contraseña real ni se prueba BCrypt aquí: el hash del fixture es simulado.
- Reutilizar la consulta buscarPorEmailConDatosYRoles en los stubs. Los
  datos de preparación no se declaran globalmente como stubs para evitar
  configuraciones innecesarias en casos que fallan antes de consultar.
  ReflectionTestUtils se usa solo en los fixtures para el id generado de
  Rol; no se agregan setters ni se cambian las entidades.
- La comprobación indicada incluye las cinco suites unitarias por nombre
  simple, agregando UsuarioDetailsServiceTest a las cuatro existentes.
  Se corroboraron seis pruebas nuevas y 40 en total en los informes locales.
  No se repite el test de contexto ni se presume validado el grafo JPA,
  la transacción por proxy, el proveedor de autenticación o las sesiones.
- No se modifica UsuarioDetailsService, WebAuthentication, WebAuthorization,
  PasswordEncoder, front, DTO ni CodigoRol. El cableado explícito del cargador
  al login corresponde al bloque posterior a estas pruebas.
- La comparación del archivo creado con el código propuesto confirma
  coincidencia exacta y seis métodos Test definidos. Se revisaron paquete,
  imports, fixtures, ids positivos de Usuario/Rol, stubs y los caminos de
  error, sin iniciar un contexto Spring ni ejecutar las aserciones.
- La comparación de hashes de 143 archivos existentes, excluido este MD,
  no detectó cambios durante la intervención. Solo se creó la prueba y
  se actualizó este documento. No se realizó staging, commit ni push.
  Esa revisión inicial fue estática; los resultados de ejecución se
  corroboraron posteriormente, como se detalla a continuación.
- Comprobación reservada al desarrollador:

```powershell
.\gradlew.bat test --tests "UsuarioDetailsServiceTest" --tests "RegistroUsuarioServiceTest" --tests "UsuarioServiceTest" --tests "UsuarioDTOTest" --tests "RegistroUsuarioDTOTest"
```

- El desarrollador informó BUILD SUCCESSFUL en 9 segundos, con dos tareas
  ejecutadas y dos UP-TO-DATE. Se revisaron los cinco XML del 4 de noviembre
  de 2026 entre 07:34:54Z y 07:34:57Z: RegistroUsuarioDTOTest 10,
  UsuarioDTOTest 4, RegistroUsuarioServiceTest 10, UsuarioDetailsServiceTest 6
  y UsuarioServiceTest 10. Total: 40, sin fallos, errores ni omisiones.
  Los seis nombres de caso nuevos coinciden con los definidos en el fuente.
- UsuarioDetailsServiceTest.class (07:34:52Z) es posterior al fuente
  (07:30:25Z). Los artefactos respaldan compilación y las suites indicadas;
  no se afirma probado un login real, el grafo JPA o el cableado de seguridad.

### Etapa 31 Cableado de autenticación y protección de administradores

Estado: cambios aplicados por el asistente el 4 de noviembre de 2026 en
WebAuthentication.java y el DELETE de UsuarioController.java, con
autorización puntual del desarrollador. Revisión estática realizada;
compilación y resultados de las cinco suites del punto 3 corroborados
tras la ejecución del desarrollador: 40 pruebas sin fallos.
El asistente no ejecutó Gradle, SQL ni la aplicación.

- Se sustituyó la lambda antigua de WebAuthentication por delegación explícita
  a UsuarioDetailsService, con ese servicio y PasswordEncoder inyectados
  por el único constructor. Mantener Configuration, visibilidad de la clase,
  GlobalAuthenticationConfigurerAdapter e init(AuthenticationManagerBuilder).
  Encadenar userDetailsService(usuarioDetailsService).passwordEncoder(passwordEncoder)
  usando el bean BCrypt existente. No crear otro encoder, modificar hashes,
  cambiar a nickname ni alterar URLs, formulario o reglas de WebAuthorization.
- La revisión de consumidores detectó que DELETE protegía ADMIN
  mediante usuario.getRol() == CodigoRol.ADMIN. Se adaptó esa comprobación
  en el mismo bloque: se busca mediante buscarPorIdConDatosYRoles y se comprueba
  ADMIN en todas las asignaciones de usuarioRoles. Conservar respuesta 403,
  mensajes, filtros de existencia/inactivo y la baja lógica activo=false.
  No borrar Persona, Usuario, roles ni asignaciones físicamente.
- Se retiró solo el import CodigoRol de UsuarioController, que deja de usarse
  tras ese cambio. El enum y sus puentes de entidad/registro/DTO se mantienen
  temporalmente; esAdministrador y puedeAlquilar no tienen consumidores
  externos actuales según la búsqueda de referencias y siguen pendientes
  de limpieza. No se añade la propuesta MF09 de último ADMIN ni nuevas
  reglas de baja o concurrencia por esta modificación.
- Las autoridades para nuevas autenticaciones pasarán a provenir de la
  tabla de asignaciones. Una cuenta sin usuario_rol no podrá autenticarse
  aunque el campo legado diga ADMIN o CLIENTE. Antes de probar el arranque
  y login reales se deberá verificar el perfil y la carga inicial/migración
  de catálogos y asignaciones, sin introducir un fallback al enum.
- Se verificaron las firmas userDetailsService y passwordEncoder en el JAR
  local spring-security-config 5.7.10 con javap del JDK 11, sin ejecutar
  compilación, aplicación ni pruebas. Las consultas de documentación web
  de esas firmas no estuvieron disponibles; no se actualizaron dependencias.
- La comprobación indicada sigue siendo las cinco suites unitarias filtradas
  (40 casos existentes). Compilar y pasarlas no validará por sí solo el
  cableado del proveedor, BCrypt real, el DELETE HTTP o el contexto Spring;
  se añadirán comprobaciones específicas antes del ensayo completo del login.
- No se modifican front, DTO, catálogos, sesiones existentes ni rutas de
  TECNICO. El campo singular rol sigue siendo solo compatibilidad temporal
  de presentación; la revocación de sesiones y la actualización del front
  para todos los roles continúan pendientes. No se declara finalizada toda
  la migración de seguridad por conectar el servicio.
- La comparación posterior confirma que WebAuthentication coincide
  exactamente con el archivo propuesto y UsuarioController contiene solo
  los tres cambios previstos: import eliminado, consulta del DELETE con
  grafo y comprobación de ADMIN en todas las asignaciones. El resto del
  controlador, incluidos mensajes, filtros, respuestas HTTP y activo=false
  con save, conserva su contenido previo a esta intervención.
- La comparación de hashes de 142 archivos ajenos a esos dos archivos y
  este MD no detectó cambios durante la intervención. SecurityConfig,
  WebAuthorization, UsuarioDetailsService y las pruebas no se modificaron.
  No se realizó staging, commit ni push. La revisión estática no sustituye
  la compilación ni prueba que el contexto o el login real funcionen.
- Comprobación reservada al desarrollador:

```powershell
.\gradlew.bat test --tests "UsuarioDetailsServiceTest" --tests "RegistroUsuarioServiceTest" --tests "UsuarioServiceTest" --tests "UsuarioDTOTest" --tests "RegistroUsuarioDTOTest"
```

- El desarrollador informó BUILD SUCCESSFUL en 8 segundos, con dos tareas
  ejecutadas y dos UP-TO-DATE. Se revisaron los cinco XML del 4 de noviembre
  de 2026 entre 07:52:18Z y 07:52:20Z: RegistroUsuarioDTOTest 10,
  UsuarioDTOTest 4, RegistroUsuarioServiceTest 10, UsuarioDetailsServiceTest 6
  y UsuarioServiceTest 10. Total: 40, sin fallos, errores ni omisiones.
- WebAuthentication.class y UsuarioController.class tienen fecha
  2026-11-04T07:52:15Z, posterior a sus fuentes (07:49:32Z). Los resultados
  respaldan compilación y regresión de las suites existentes después de
  este cambio. Todavía no ejercitan init del configurador, comparación real
  con BCrypt, la protección del DELETE ni filtros HTTP o persistencia JPA.
  Las comprobaciones específicas de esos componentes siguen pendientes;
  no se arranca la aplicación contra la base actual ni se repiten pruebas
  desde el asistente para obtener este registro.

### Etapa 32 Prueba aislada del configurador de autenticación y BCrypt

Estado: paquete configurations y WebAuthenticationTest.java creados por el
asistente el 4 de noviembre de 2026 bajo src/test/java/DSII/TurismoSustentable,
con autorización puntual del desarrollador. Revisión estática realizada;
compilación y resultados del punto 3 corroborados tras la ejecución del
desarrollador: 43 pruebas sin fallos. El asistente no ejecutó Gradle,
SQL ni la aplicación.

- La prueba está en el mismo paquete que WebAuthentication para acceder
  a su clase de visibilidad de paquete, sin hacerla pública en producción.
  Usa JUnit Jupiter/MockitoExtension y únicamente UsuarioRepository como
  mock. No usa SpringBootTest, contexto de aplicación, MySQL o correos.
- Preparar el encoder mediante new SecurityConfig().passwordEncoder(),
  el UsuarioDetailsService real y AuthenticationManagerBuilder con un
  ObjectPostProcessor pasante solo para la prueba. Llamar a
  WebAuthentication.init(builder) y builder.build(), en lugar de configurar
  un proveedor separado que no ejercite el cableado de producción.
- Se inspeccionaron firmas y bytecode del JAR local spring-security-config
  5.7.10 con javap del JDK 11 para verificar ese armado sin un contexto.
  Esta inspección fue de solo lectura; no ejecutó los métodos, compiló ni
  probó el código propuesto.
- Se añadieron tres pruebas: contraseña correcta con email normalizado autentica
  y conserva todas las autoridades ADMIN/TECNICO, sin sumar el CLIENTE
  legado; contraseña incorrecta arroja BadCredentialsException; cuenta
  inactiva con contraseña correcta arroja DisabledException.
- El fixture guardará un hash BCrypt real creado con el mismo encoder.
  La prueba exitosa verificará nombre autenticado, autoridades, eliminación
  de las credenciales del resultado y conservación del hash del Usuario.
  No se fijará un hash literal dependiente de la sal aleatoria de BCrypt.
- Usar Persona/Usuario/Rol/UsuarioRol en memoria, con ids simulados solo
  para construir las asignaciones. Preparar el stub de búsqueda únicamente
  en los caminos que lo usan. ObjectPostProcessor pasante no modifica el
  postprocesado de la aplicación: pertenece únicamente a este test sin IoC.
- La comprobación incluyó WebAuthenticationTest y las cinco suites
  existentes por nombre simple. Se corroboraron tres pruebas nuevas y
  43 en total. No se cambian dependencias, fuerza
  de BCrypt ni código de producción por esta etapa.
- Esta es una prueba aislada de componentes: no valida descubrimiento de
  beans, transacciones por proxy, filtros HTTP, autorización de endpoints,
  sesiones o la consulta JPA real. La prueba del DELETE protector de ADMIN
  y el ensayo del contexto/base local aislada continúan pendientes.
- Se corroboró coincidencia exacta del archivo creado con el código
  propuesto: paquete de test, imports, BeforeEach, construcción del gestor,
  tres métodos Test, fixtures y stubs. La comparación de hashes de 144
  archivos existentes, excluido este MD, no detectó cambios durante la
  intervención. El código de producción y las pruebas anteriores quedaron
  intactos. No se realizó staging, commit ni push.
- La revisión inicial anterior fue estática. La evidencia de ejecución
  se corroboró posteriormente y se detalla a continuación.
- Comprobación reservada al desarrollador:

```powershell
.\gradlew.bat test --tests "WebAuthenticationTest" --tests "UsuarioDetailsServiceTest" --tests "RegistroUsuarioServiceTest" --tests "UsuarioServiceTest" --tests "UsuarioDTOTest" --tests "RegistroUsuarioDTOTest"
```

- El desarrollador informó BUILD SUCCESSFUL en 8 segundos, con dos tareas
  ejecutadas y dos UP-TO-DATE. Se revisaron los seis XML locales del
  4 de noviembre de 2026 entre 08:12:37Z y 08:12:40Z: WebAuthenticationTest
  3, RegistroUsuarioDTOTest 10, UsuarioDTOTest 4, RegistroUsuarioServiceTest
  10, UsuarioDetailsServiceTest 6 y UsuarioServiceTest 10. Total: 43,
  cero fallos, errores u omisiones. Los tres nombres de caso del configurador
  coinciden con los propuestos y figuran como satisfactorios.
- WebAuthenticationTest.class tiene fecha 2026-11-04T08:12:36Z, posterior
  al fuente (08:10:00Z). La evidencia respalda compilación y ejecución del
  armado manual del gestor mediante WebAuthentication.init y BCrypt real,
  usando repositorio simulado. Se verificaron credenciales, autoridades y
  estado habilitado de los casos definidos, no una sesión HTTP ni carga JPA.
  El asistente solo leyó esos resultados y actualizó este MD.

### Etapa 33 Reglas aprobadas para técnicos inactivos con órdenes

Fecha: 4 de noviembre de 2026.

Estado: diseño aprobado, pendiente de implementación. El usuario aprobó
primero la pausa administrativa excepcional al inactivar al técnico asignado
y después confirmó expresamente que PAUSADA pueda quedar temporalmente sin
técnico hasta su reasignación. Con ambas confirmaciones se consolidan las
reglas y la aclaración del DER v5, sin modificar originales, Java ni bases
de datos. La revisión de pruebas del bloque de usuarios puede retomarse;
la coordinación efectiva con mantenimiento requiere implementar ese módulo.

- Se contrastaron en lectura el PDF original (objetivos y requerimientos),
  la sección de mantenimiento del Diccionario de Estados original, RN-MAN-02,
  la revisión 27, la trazabilidad aprobada 36 y el Mermaid v5. El diccionario
  conserva cinco estados de orden; CREADA, EN_PROCESO y PAUSADA son abiertas.
  FINALIZADA/CANCELADA no se reabren por una baja de cuenta.
- El controlador actual permite inactivar cuentas TECNICO sin ADMIN, pero
  todavía no implementa la coordinación con el futuro módulo de órdenes.
  ADMIN + TECNICO sigue protegido por su rol ADMIN. No se cambió ese permiso.
- Recorrido aprobado: conservar la misma orden y su identificador. En CREADA,
  desasignar y conservar CREADA; en EN_PROCESO, pasar a PAUSADA con motivo
  administrativo y desasignar; en PAUSADA, conservar ese estado y desasignar.
  Las órdenes cerradas conservan estado, técnico histórico y demás datos.
  Pendiente de reasignación se representa por orden abierta sin tecnico_id,
  no mediante otra tabla, otro estado o una orden duplicada.
- Aprobado: ADMIN puede provocar excepcionalmente EN_PROCESO a PAUSADA
  solo como parte de inactivar al técnico asignado. La pausa exige motivo,
  fecha y registro del ADMIN real en el historial de la orden y en su
  auditoría administrativa. Conserva el trabajo, diagnóstico, costos y
  fecha de primer inicio; no cierra la orden ni habilita la bicicleta.
  Esta excepción acotada a RN-MAN-02 no concede a ADMIN un permiso general
  para pausar, ejecutar trabajo técnico, inventar diagnósticos o finalizar
  una orden. Su implementación queda pendiente.
- Segunda condición aprobada: PAUSADA puede quedar sin técnico hasta su
  reasignación. Se autoriza así la desasignación del recorrido descrito,
  sin permitir que una orden sin técnico inicie, reanude o registre trabajo.
- Conservar fecha_inicio, diagnóstico, trabajo, costos y todos los eventos
  anteriores. No fijar fecha_fin en una orden que sigue abierta ni habilitar
  la bicicleta: continúa su restricción de mantenimiento. En una orden ya
  PAUSADA, conservar el motivo previo y registrar la nueva desasignación
  con su contexto en un evento, sin inventar PAUSADA a PAUSADA como transición.
- Registrar técnico anterior, asignación nueva nula, estado anterior/nuevo
  cuando cambie, motivo, fecha y ADMIN real en HISTORIAL_ORDEN_MANTENIMIENTO
  y la auditoría ADMIN que corresponda. La pausa y la desasignación de una
  misma operación pueden conservarse en un evento completo según RN-TRZ-01.
  No atribuir la actuación a SISTEMA solo porque sus efectos sean automáticos.
- La baja, los cambios de las órdenes y sus evidencias deberán confirmarse
  juntos o revertirse, protegiendo la concurrencia. Reasignar seguirá siendo
  de ADMIN a un técnico activo con rol TECNICO, y reanudar seguirá requiriendo
  al técnico asignado; la asignación sola no reinicia automáticamente el trabajo.
- Se consolidaron RN-MAN-02 (sección 3.1), el diccionario de trabajo 08,
  la referencia de RN-MAN-03, las revisiones 22/27 y el índice 00. Ambos
  archivos Mermaid v5 aclaran tecnico_id opcional en CREADA o PAUSADA por
  baja del técnico; no se agregan campos, tablas, PK, FK o relaciones.
  El modelo conserva 29 entidades y 55 FK/relaciones. Los criterios de
  aceptación añadidos son especificaciones, no pruebas ejecutadas.
- Verificación documental: se comparó el Mermaid con su contenido anterior;
  solo cambió el comentario de tecnico_id. El TXT coincide íntegramente con
  el Mermaid y se contaron 29 entidades y 55 relaciones. Las huellas SHA-256
  de todos los archivos de src permanecieron iguales antes/después. Git
  diff --check no detectó errores de espacios; solo avisos de LF/CRLF.
- No se considera aprobado un tratamiento equivalente por quitar el rol
  TECNICO, ni se declara implementada la revocación de sesiones: esos
  alcances se revisarán aparte.
- No se ejecutaron pruebas, aplicación, SQL ni operaciones de escritura Git.
  Los originales consultados permanecen intactos; no se regeneró el Word
  exportado del diccionario. Se actualizan solo documentación de trabajo
  y el TXT/Mermaid del DER. La última evidencia de ejecución sigue siendo
  las 43 pruebas de la etapa 32, no una prueba del módulo de mantenimiento.

### Etapa 34 Pruebas de baja lógica de usuarios verificadas en aislamiento

Fecha: 4 de noviembre de 2026.

Estado: clase de prueba creada por el asistente con autorización puntual
del usuario, siguiendo el código propuesto. El usuario ejecutó el comando
filtrado y obtuvo BUILD SUCCESSFUL en 8 segundos; el asistente verificó
los siete XML locales. Resultado: 49 pruebas, sin fallos, errores ni
omisiones. Verificada la lógica aislada de los casos definidos, no HTTP
ni persistencia real o coordinación con mantenimiento.

- Se releyeron eliminarUsuarioLogico, su constructor, Usuario, Rol,
  UsuarioRol y los patrones de las pruebas existentes. El controlador ya
  consulta buscarPorIdConDatosYRoles, protege cualquier asignación ADMIN
  y realiza la baja mediante activo = false y save, sin borrado físico.
- Se creó en src/test/java/DSII/TurismoSustentable/controllers
  la clase UsuarioControllerTest, con JUnit Jupiter y Mockito. Sus seis
  casos cubren ADMIN protegido, ADMIN + TECNICO protegido, baja de CLIENTE,
  baja de TECNICO, usuario inexistente e intento sobre cuenta ya inactiva.
  Los casos ADMIN dejan el enum legado en su valor inicial: la decisión
  debe depender de las asignaciones UsuarioRol, no de ese enum temporal.
- Las bajas permitidas tienen aserciones para activo falso, respuesta 204, datos
  personales/de cuenta de la muestra y asignaciones conservados, y save
  de la misma instancia. Los rechazos tienen aserciones para estado/mensaje y que
  solo se haya consultado el repositorio, sin escrituras adicionales.
- Alcance: invocación directa del método del controlador y repositorio
  simulado; no prueba filtros HTTP, autorización de rutas, SQL/cascadas,
  sesiones ni efectos sobre órdenes. La regla aprobada de mantenimiento
  de la etapa 33 sigue pendiente de implementar en su módulo.
- La autorización puntual cubrió crear la clase propuesta y su paquete
  de pruebas y actualizar este diario, no modificar código de aplicación,
  pruebas anteriores, configuración, DER ni bases de datos. El usuario
  conserva el paso 3 de guardar/comprobar mediante el comando filtrado.
  No se requiere XAMPP ni se debe ejecutar la suite completa con el
  contexto no aislado.
- Revisión estática: la clase contiene los seis métodos @Test propuestos
  y no carga un contexto SpringBootTest. La comparación SHA-256 de src
  confirmó intactos todos sus archivos existentes; el único archivo nuevo
  es UsuarioControllerTest.java. No se detectaron espacios finales en la
  clase ni errores en git diff --check del diario. Esto no reemplaza la
  compilación ni la ejecución pendientes a cargo del usuario.

Comando propuesto para que ejecute el usuario:

```powershell
.\gradlew.bat test --tests "UsuarioControllerTest" --tests "WebAuthenticationTest" --tests "UsuarioDetailsServiceTest" --tests "RegistroUsuarioServiceTest" --tests "UsuarioServiceTest" --tests "UsuarioDTOTest" --tests "RegistroUsuarioDTOTest"
```

Comprobación informada por el usuario y contrastada en lectura:

- BUILD SUCCESSFUL en 8 segundos: dos tareas ejecutadas y dos UP-TO-DATE.
- Los siete XML del 4 de noviembre de 2026 tienen marcas entre
  09:10:51Z y 09:10:53Z: UsuarioControllerTest 6, WebAuthenticationTest 3,
  UsuarioDetailsServiceTest 6, RegistroUsuarioServiceTest 10,
  UsuarioServiceTest 10, UsuarioDTOTest 4 y RegistroUsuarioDTOTest 10.
  Total 49; en todos, cero fallos, errores u omisiones.
- Los seis nombres de caso de UsuarioControllerTest coinciden con los
  propuestos y figuran satisfactorios. Su .class tiene fecha UTC
  09:10:49Z, posterior al fuente de 09:07:34Z; la evidencia incluye la
  compilación de la clase nueva y su ejecución, no solo resultados viejos.
- La advertencia de funciones obsoletas de Gradle no impidió esta ejecución;
  no se actualizó Gradle ni se cambió configuración para ocultarla.
- El asistente solo leyó resultados/código y actualizó este diario. No
  volvió a ejecutar Gradle, aplicaciones o SQL ni realizó escrituras Git.
  La baja con efectos sobre órdenes sigue pendiente de implementación
  conforme a la etapa 33, no queda validada por estos seis casos.

### Etapa 35 UsuarioDTO sin dependencia del enum, verificado en aislamiento

Fecha: 4 de noviembre de 2026.

Estado: cambios aplicados por el asistente con autorización puntual del
usuario, siguiendo exactamente el bloque propuesto para UsuarioDTO y
UsuarioDTOTest. El usuario completó el paso 3 y obtuvo BUILD SUCCESSFUL
en 5 segundos. El asistente verificó los siete XML locales: 52 pruebas,
sin fallos, errores ni omisiones. El asistente no ejecutó Gradle, la
aplicación o SQL; no se verifica persistencia real ni navegación HTTP.

- Antes de editar se revisaron UsuarioDTO y sus pruebas, el registro y sus pruebas,
  index.js, admin.js y las rutas de WebAuthorization. La lista roles ya
  provenía de UsuarioRol; el singular rol todavía dependía del enum legado.
  index.js usa ese singular para navegación y guarda usuarioRol; admin.js
  lo usa para su control visual y la columna de usuarios.
- Cambio puntual aplicado: conservar el atributo/getter rol para esos
  consumidores, pero derivarlo exclusivamente de la lista roles. Para la
  presentación transitoria se elige ADMIN si está asignado; en su ausencia,
  CLIENTE si está asignado; en su ausencia, TECNICO si está asignado; sin
  asignaciones, null. No se toma el primer elemento alfabético ni se
  inventa CLIENTE ante una colección vacía.
- La prioridad es solo un puente de representación del frontend existente,
  no una jerarquía ni herencia de permisos. roles sigue incluyendo todos
  los códigos asignados y la seguridad sigue usando todas las autoridades
  del cargador de usuarios. No se suman permisos del enum y de la tabla.
- Se ampliaron las aserciones de los casos ADMIN + TECNICO y sin
  asignaciones, y se agregaron tres casos de DTO: CLIENTE, TECNICO y CLIENTE +
  TECNICO. Los roles se crean desde el catálogo en memoria; no se necesita
  cambiar RegistroUsuarioServiceTest para este paso porque el registro ya
  sincroniza la asignación CLIENTE antes de construir su respuesta.
- No se elimina todavía CodigoRol ni el campo legado de Usuario: el
  registro y dos pruebas de servicios aún los usan. Tampoco se modifica
  el frontend a multirrol, se cambia el login a nickname o se habilita
  la ruta de usuario actual para una cuenta exclusivamente TECNICO; ese
  recorrido y sus pantallas continúan pendientes de adaptación.
- Al aplicar este cambio, la evidencia previa eran las 49 pruebas de la
  etapa 34; la comprobación posterior del usuario se registra debajo.
  No se modificó el frontend, servicios,
  entidades, seguridad, configuración, DER ni otras pruebas. Además de
  los dos archivos Java indicados, solo se actualizó este diario.
- Revisión estática posterior: la comparación con los contenidos previos
  confirma exactamente el reemplazo del bloque singular y las inserciones
  de prueba propuestas, sin otros cambios de contenido en esos archivos.
  Antes de ejecutar se contaron siete métodos @Test en UsuarioDTOTest,
  sin declarar todavía resultados. La comparación SHA-256 de los archivos de src
  detectó cambios únicamente en UsuarioDTO.java y UsuarioDTOTest.java.
  Git diff --check no detectó errores de espacios. No se realizaron
  staging, commit o push ni se volvieron a ejecutar las suites anteriores.

Comprobación posterior informada por el usuario y contrastada en lectura:

- BUILD SUCCESSFUL en 5 segundos: tres tareas ejecutadas y una UP-TO-DATE.
- Los siete XML del 4 de noviembre de 2026 tienen marcas entre
  09:23:14Z y 09:23:16Z: UsuarioControllerTest 6, WebAuthenticationTest 3,
  UsuarioDetailsServiceTest 6, RegistroUsuarioServiceTest 10,
  UsuarioServiceTest 10, UsuarioDTOTest 7 y RegistroUsuarioDTOTest 10.
  Total 52; todos con cero fallos, errores u omisiones.
- Los siete casos del DTO figuran satisfactorios, incluidos los tres
  nuevos y las aserciones ampliadas sobre rol singular. UsuarioDTO.class
  tiene fecha UTC 09:23:12Z y UsuarioDTOTest.class 09:23:13Z, posteriores
  a sus fuentes de 09:21:38Z; se recompilaron los archivos modificados.
- El cambio queda verificado para esos casos aislados. No acredita
  consultas JPA, datos existentes migrados, sesiones o navegación real
  del frontend, ni habilita el flujo exclusivo de TECNICO.
- El asistente solo leyó resultados, fechas y código y actualizó el MD.
  No se modificaron Java ni otras pruebas durante esta corroboración,
  ni se ejecutaron aplicaciones, SQL u operaciones de escritura Git.

### Etapa 36 Enum de rol legado retirado y verificado en aislamiento

Fecha: 4 de noviembre de 2026.

Estado: bloque aplicado por el asistente con autorización puntual del
usuario, siguiendo la propuesta. Se modificaron Usuario, el registro y
las dos pruebas indicadas; tras retirar sus consumidores se eliminó
CodigoRol.java. El usuario completó el paso 5 con BUILD SUCCESSFUL en
6 segundos. El asistente contrastó los siete XML locales: 52 pruebas,
sin fallos, errores u omisiones. Se verifica este bloque en aislamiento,
no una migración o persistencia real. El asistente no ejecutó Gradle.

- Se releyeron Usuario, CodigoRol, RegistroUsuarioService y las dos pruebas
  de servicios afectadas. La búsqueda en src confirmó que los únicos usos
  restantes de CodigoRol están en esos cuatro archivos y el propio enum.
  esAdministrador y puedeAlquilar no tienen llamadas en el código actual.
- Se retiraron de Usuario el campo enum rol y su anotación, sus
  accesores getRol/setRol y los dos métodos de conveniencia antiguos sin
  consumidores. Se conserva usuarioRoles y su getter. No se eliminan los
  getters getRol de UsuarioRol ni UsuarioDTO: representan contratos distintos.
- En RegistroUsuarioService se quitaron únicamente el import de
  CodigoRol y usuario.setRol(CodigoRol.CLIENTE). Se conservan activo true,
  búsqueda de CLIENTE en el catálogo, persistencia transaccional de la
  asignación, sincronización de la colección y flush antes de devolver DTO.
- RegistroUsuarioServiceTest sustituyó la aserción del enum por la lista
  CLIENTE del DTO; se mantienen sus comprobaciones de la asignación real.
  UsuarioServiceTest incorporó una asignación CLIENTE válida en memoria
  en su preparación (usuario id 1 y rol id 2 con ReflectionTestUtils) y
  comprueba mediante aserciones la cantidad de asignaciones y los roles del
  resultado al actualizar. Ambas pruebas usan List.of desde java.util.List,
  disponible en JDK 11; los resultados posteriores se registran debajo.
- Solo después de quitar sus consumidores se eliminó el archivo
  CodigoRol.java, no Rol.java. No se retiran otros enums ni se modifica
  seguridad, frontend, controlador, DTO, DER o esquema de base de datos.
- Retirar el mapeo Java no migra asignaciones existentes ni garantiza que
  Hibernate elimine una columna antigua con ddl-auto=update. No se propone
  SQL destructivo ni se certifican datos reales migrados. Las cuentas que
  requieran acceso deben tener sus asignaciones en usuario_rol.
- Los cambios quedaron guardados en disco y se dejó al usuario el paso 5
  mediante el mismo comando filtrado de siete suites. Durante la edición
  el asistente no ejecutó Gradle, la aplicación, SQL ni escrituras Git.
- Revisión estática posterior: los cuatro archivos modificados coinciden
  exactamente con los reemplazos propuestos frente a sus contenidos al
  iniciar esta intervención. La comparación SHA-256 de src confirmó solo
  esos cuatro cambios y la eliminación de CodigoRol.java, sin archivos
  nuevos ni cambios en los demás fuentes/recursos. Rol.java, UsuarioRol,
  sus accesores y UsuarioDTO se conservan intactos en este paso. La búsqueda
  de CodigoRol y de los dos métodos retirados no devuelve referencias en
  src. Git diff --check no detectó errores de espacios. Estas comprobaciones
  estáticas no sustituyen compilar y ejecutar las pruebas, cuya evidencia
  posterior se registra a continuación.

Comprobación posterior informada por el usuario y contrastada en lectura:

- BUILD SUCCESSFUL en 6 segundos: tres tareas ejecutadas y una UP-TO-DATE.
- Los siete XML del 4 de noviembre de 2026 tienen marcas entre
  09:34:17Z y 09:34:19Z: UsuarioControllerTest 6, WebAuthenticationTest 3,
  UsuarioDetailsServiceTest 6, RegistroUsuarioServiceTest 10,
  UsuarioServiceTest 10, UsuarioDTOTest 7 y RegistroUsuarioDTOTest 10.
  Total 52; todos con cero fallos, errores u omisiones. Los dos casos
  modificados de registro/actualización figuran satisfactorios.
- Usuario.class y RegistroUsuarioService.class tienen fecha UTC 09:34:15Z;
  las dos clases de prueba modificadas, 09:34:16Z. Son posteriores a sus
  fuentes de 09:31:46Z/09:31:47Z, por lo que el resultado incluye recompilar
  los cuatro archivos, no solo consultar resultados anteriores.
- No existe CodigoRol.java en src ni CodigoRol.class en la salida principal
  de compilación. La búsqueda de sus referencias y de los dos métodos
  retirados sigue sin coincidencias en los fuentes Java de src.
- El asistente solo leyó resultados, fechas y código y actualizó este MD;
  no modificó otros archivos ni ejecutó Gradle, aplicaciones, SQL o
  escrituras Git durante esta corroboración. El acceso de cuentas existentes
  depende de sus asignaciones en usuario_rol; no se certifica su migración.

El archivo eliminado no estaba versionado en el índice de Git al empezar
este bloque. Para permitir recuperar su contenido, se conserva aquí como
antecedente únicamente; no es una clase vigente ni debe copiarse para
mantener dos fuentes de roles:

```java
package DSII.TurismoSustentable.models;

public enum CodigoRol {
    CLIENTE,
    ADMIN,
    TECNICO
}
```

### Etapa 37 Consulta propia de TECNICO configurada, regresión verificada

Fecha: 4 de noviembre de 2026.

Estado: cambio puntual aplicado por el usuario. El asistente revisó el
archivo y su diff: solo se agregó TECNICO al matcher GET del usuario actual.
El usuario ejecutó el comando filtrado con BUILD SUCCESSFUL en 4 segundos;
se contrastaron siete XML, 52 pruebas sin fallos, errores u omisiones.
Esta regresión no ejercita todavía la regla de autorización HTTP.

- Se revisaron WebAuthorization, getUsuarioActual, la autenticación y las
  pruebas existentes, y el bloque de roles del documento 25. La regla
  específica GET /api/usuarios/actual exigía ADMIN o CLIENTE;
  una cuenta exclusivamente TECNICO no la satisfacía antes de este paso.
- El usuario agregó únicamente TECNICO a hasAnyAuthority de ese matcher
  exacto, manteniéndolo antes de la regla general /api/usuarios/**, que
  sigue reservada a ADMIN. No se amplían los permisos de listado,
  consulta por ID, administración, alquiler ni métodos de escritura.
- El controlador conserva el email del Principal para identificar la
  cuenta consultada; no se acepta un ID o email libre desde el formulario.
  Este cambio no modifica la autenticación por email ni habilita el panel
  técnico o una nueva redirección de login; esos recorridos están pendientes.
- La comprobación propuesta utiliza el mismo comando filtrado de siete
  suites para compilar y detectar regresiones. Las 52 pruebas existentes
  no ejercitan la cadena de filtros HTTP de WebAuthorization: que pasen
  no certificará por sí solo el acceso/denegación del nuevo matcher.
  Su prueba HTTP aislada queda para un bloque específico posterior, sin
  ejecutar el contexto de aplicación que utiliza una base no aislada.
- Comprobación: los siete XML del 4 de noviembre de 2026 tienen marcas
  entre 09:44:49Z y 09:44:51Z. UsuarioControllerTest 6,
  WebAuthenticationTest 3, UsuarioDetailsServiceTest 6,
  RegistroUsuarioServiceTest 10, UsuarioServiceTest 10, UsuarioDTOTest 7
  y RegistroUsuarioDTOTest 10; total 52, sin fallos, errores u omisiones.
  El usuario informó dos tareas ejecutadas y dos UP-TO-DATE.
- WebAuthorization.class tiene fecha UTC 09:44:48Z, posterior al fuente
  de 09:44:35Z: se recompiló el cambio. Se verificó además que el matcher
  permanece antes de /api/usuarios/** y no se amplió otra regla. El
  asistente solo leyó fuentes, diff y resultados y actualizó este diario;
  no ejecutó Gradle, aplicación, SQL ni operaciones de escritura Git.

### Etapa 38 Pruebas HTTP aisladas de autorización verificadas

Fecha: 4 de noviembre de 2026.

Estado: dependencia y clase de prueba incorporadas por el usuario, quien
informó ejecución satisfactoria. El asistente revisó los ocho XML locales:
59 pruebas, sin fallos, errores u omisiones, incluidos los siete casos HTTP.
Se confirma el alcance MVC aislado definido debajo, no persistencia real
ni login completo. El asistente no ejecutó Gradle, la aplicación o SQL.

- Se agregó spring-security-test únicamente como testImplementation,
  sin versión explícita, bajo la gestión de dependencias actual de Boot.
  No se actualizan Spring Boot, Spring Security, Gradle ni JDK.
- Nueva clase incorporada: configurations.WebAuthorizationTest, con WebMvcTest
  y ContextConfiguration limitada a UsuarioController y WebAuthorization.
  El controlador y la cadena de filtros son reales; sus cuatro
  colaboradores y UserDetailsService son MockBean. Se simulan sesiones
  con WithMockUser y authorities sin prefijo ROLE_, no el proceso de login.
  No se utiliza SpringBootTest, servidor de aplicación ni repositorio real.
- Siete casos incorporados y satisfactorios: tres roles consultan su propio perfil con 200;
  anónimo recibe 401; CLIENTE y TECNICO reciben 403 al listar usuarios,
  consultar uno por ID o acceder a una ruta administrativa; ADMIN puede
  listar y consultar por ID. Se verifican también las llamadas esperadas
  o ausentes al repositorio simulado. La consulta propia ignora el email
  arbitrario enviado como parámetro y usa el Principal.
- Las cuentas y catálogos de la muestra se construyen en memoria con las
  entidades actuales; no se ejecutan inicializadores, Hibernate o SQL ni
  se envían correos. No se cambian las reglas de autorización de producción.
- El alcance verifica MVC y las reglas de acceso de esas rutas, no el
  recorrido completo de login, sesiones reales de navegador, revocación,
  JPQL, capacidad, mantenimiento ni migración de cuentas existentes.
- Se consultó documentación oficial de la línea 2.7 sobre
  [WebMvcTest](https://docs.spring.io/spring-boot/docs/2.7.18/api/org/springframework/boot/test/autoconfigure/web/servlet/WebMvcTest.html)
  y la API 5.7 de
  [WithMockUser](https://docs.spring.io/spring-security/site/docs/5.7.0/api/org/springframework/security/test/context/support/WithMockUser.html).
  Sus versiones documentales no son una propuesta de actualizar librerías.
  WebMvcTest limita la autoconfiguración al ámbito MVC; WithMockUser con
  authorities no agrega el prefijo ROLE_ que no utiliza esta aplicación.
- El usuario ejecutó las ocho suites explícitas, incluyendo
  WebAuthorizationTest, no la suite completa que contiene el contexto
  no aislado. Los ocho XML del 4 de noviembre de 2026 tienen marcas entre
  09:58:36Z y 09:58:40Z: WebAuthorizationTest 7, UsuarioControllerTest 6,
  WebAuthenticationTest 3, UsuarioDetailsServiceTest 6,
  RegistroUsuarioServiceTest 10, UsuarioServiceTest 10, UsuarioDTOTest 7
  y RegistroUsuarioDTOTest 10. Total 59; todos con cero fallos, errores
  u omisiones. Los siete nombres de caso HTTP coinciden con los propuestos.
- WebAuthorizationTest.class tiene fecha UTC 09:58:35Z, posterior al
  fuente de 09:58:10Z y a build.gradle de 09:57:21Z. Esta ejecución incluye
  compilar la prueba nueva con la dependencia añadida. El JAR resuelto es
  spring-security-test 5.7.10 y se comprobó mediante lectura del ZIP que
  contiene org/springframework/security/test/context/support/WithMockUser.class.
- El usuario informó siete marcas rojas cannot resolve symbol WithMockUser
  en IntelliJ pese a la ejecución correcta. El import y la dependencia son
  los propuestos; .idea/gradle.xml enlaza el proyecto actual con JVM 11.
  La evidencia apunta a falta de sincronización o indexación del IDE,
  no a un símbolo ausente del classpath de Gradle. Es un diagnóstico
  inferido: la recuperación visual del editor requiere confirmación del
  usuario y no se declara realizada.
- Se recomienda sincronizar el proyecto desde la ventana Gradle y esperar
  que finalice la indexación, según la documentación de
  [JetBrains](https://www.jetbrains.com/help/idea/work-with-gradle-projects.html).
  No se propone quitar el import, cambiar la versión, agregar dependencias
  a mano en los módulos ni borrar cachés o configuración del proyecto.
- Durante esta corroboración el asistente solo leyó fuentes, XML, fechas,
  configuración de enlace y el JAR; actualizó únicamente este diario.
  No cambió código, dependencias, archivos de IntelliJ, base de datos o Git.
- Después de la indicación de sincronizar, el usuario informó que las
  marcas rojas aparentemente desaparecieron. Se registra su confirmación,
  sin afirmar una inspección visual del IDE por parte del asistente.
  También informó BUILD SUCCESSFUL en 1 segundo con las cuatro tareas
  UP-TO-DATE. Los ocho XML conservan sus marcas de 09:58:36Z a 09:58:40Z:
  Gradle reutilizó la ejecución anterior de 59 pruebas correctas; no se
  contabiliza como una nueva ejecución ni como nuevos casos superados.
  El asistente no forzó repetir tareas ni borró cachés. Esta corroboración
  vuelve a actualizar únicamente este diario y no realiza escrituras Git.
