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
- No se cambian aún el formulario, UsuarioController, Usuario,
  la autenticación por email ni la recuperación. El nickname todavía
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
