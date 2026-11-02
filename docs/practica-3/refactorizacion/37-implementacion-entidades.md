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
