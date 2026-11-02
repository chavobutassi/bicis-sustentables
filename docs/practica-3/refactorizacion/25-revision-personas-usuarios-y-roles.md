# Revisión de personas usuarios y roles

Fecha: 28 de octubre de 2026.

Estado: las tres incorporaciones de identificación y acceso fueron aprobadas expresamente el 28 de octubre de 2026 y se integraron al DER v5: TIPO_DOCUMENTO y PAIS, documento compuesto obligatorio al registrarse y nickname único para iniciar sesión. Email conserva su unicidad independiente, recuperación y notificaciones. El modelo tiene 28 entidades; no se modificaron Java ni la base de datos. Las longitudes nuevas, normalizaciones específicas, datos iniciales y transición del legado se concretarán en el diseño físico y la implementación.

## 1. Fuentes y comparación con la aplicación

Se contrastaron el [DER v4 original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/DER/DERv4.txt>), el [PDF de visión](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>), el [diccionario original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>) y las reglas aprobadas de esta carpeta. El PDF contempla turistas y residentes y gestión de perfiles y roles; el Word enumera CLIENTE, ADMIN y TECNICO y los cinco valores de género. Ninguno de esos documentos resuelve por sí solo la identificación documental de extranjeros ni una edad mínima de contratación.

En la aplicación actual, Usuario reúne datos personales y credenciales, no tiene DNI, y usa un único valor del enum Rol, que contiene CLIENTE y ADMIN. El registro solicita nombre, apellido, email, fecha de nacimiento, género y contraseña. El backend fuerza CLIENTE y activo al registrar; normaliza email, controla su unicidad y utiliza BCrypt. La recuperación guarda el hash del token, su vencimiento y los borra al consumirlo; el plazo observado es de 30 minutos. Son observaciones de archivos, no pruebas de ejecución en esta revisión.

El [DER v5 de trabajo](der-v5-propuesto.mmd) ya separa PERSONA, USUARIO, ROL y USUARIO_ROL y conserva la recuperación. Esa separación se mantiene: no se vuelve a concentrar todo en Usuario ni se elimina una funcionalidad que ya existe.

## 2. PERSONA

Representa los datos de la persona, no su sesión ni sus permisos. Los identificadores internos no dependen del email o del número de documento y no cambian cuando se modifica un dato de perfil.

| Campo del modelo | Tipo y clave | Condiciones |
| --- | --- | --- |
| id | int, PK | Identificador generado internamente; no editable por el formulario |
| nombre | string, longitud 50 | Obligatorio, sin quedar vacío después de recortar espacios externos; conservar la validación actual de nombres |
| apellido | string, longitud 50 | Obligatorio, con los mismos criterios de limpieza y validación |
| fecha_nacimiento | date | Obligatoria y anterior a la fecha actual; no se inventa una edad mínima de contratación |
| genero_id | int, FK a GENERO.id | Obligatorio; valor existente del catálogo, incluidos los cinco códigos del diccionario y PREFIERO_NO_DECIR |
| tipo_documento_id | int, FK a TIPO_DOCUMENTO.id | Obligatorio; DNI o PASAPORTE; parte de la unicidad documental compuesta |
| numero_documento | string, longitud propuesta 50 | Obligatorio; conservar letras y ceros iniciales cuando corresponda; parte de la unicidad compuesta, no un entero |
| pais_emisor_id | int, FK a PAIS.id | Obligatorio; país emisor, no nacionalidad o residencia; parte de la unicidad compuesta |

Nombre y apellido conservan el límite que ya tiene el código. Los límites del documento son capacidades propuestas de almacenamiento, no normas de validez de documentos oficiales. El formato y su normalización deben ser coherentes con el tipo y país; no se reutiliza una validación numérica de DNI para todos los pasaportes.

### Decisión D01 de identificación aprobada

El usuario confirmó expresamente que el documento es obligatorio al registrarse, no recién antes del primer alquiler. Esta condición se aplicará al flujo de registros nuevos cuando se implemente; no declara resuelta la migración de cuentas existentes sin documento ni cambia ahora el formulario.

La propuesta inicial de códigos directos buscaba reducir tablas. Después de las consultas se recomendaron los dos catálogos y el usuario aprobó expresamente incorporarlos, admitir DNI o pasaporte y reemplazar dni por tipo_documento_id, numero_documento y pais_emisor_id. Esa representación ya figura en el Mermaid, sin crear una tabla adicional de nacionalidades ni modificar la aplicación vigente.

Se define UQ_PERSONA_DOCUMENTO como una restricción única compuesta sobre (tipo_documento_id, pais_emisor_id, numero_documento normalizado). No son tres restricciones UNIQUE individuales: muchas personas comparten país y tipo. Así, dos pasaportes de países diferentes no se rechazan solo por repetir su numeración. El Mermaid identifica la restricción en un comentario global y en sus tres atributos, sin marcar cada uno como UK independiente. La futura migración deberá materializar esa única restricción sobre el conjunto, además de las dos FK y su obligatoriedad; el dibujo por sí solo no la ejecuta.

Esto evita reutilizar la misma identificación declarada en varias cuentas, pero no verifica la autenticidad del documento ni demuestra que dos documentos distintos no pertenezcan a la misma persona. No se implementan consultas oficiales ni carga de fotografías del documento mediante esta propuesta.

No se agrega teléfono, domicilio o nacionalidad por iniciativa de esta revisión. La edad mínima para contratar no se deduce de tener fecha de nacimiento: requerirá una regla explícita si se incorpora.

### Catálogos incorporados de identificación

TIPO_DOCUMENTO tiene id como PK, codigo único y nombre; sus códigos iniciales aprobados son DNI y PASAPORTE. PAIS tiene id como PK, codigo único y nombre. Los nombres son obligatorios, pero no se declaran únicos: la unicidad del catálogo corresponde a codigo. Son dos entidades nuevas, no una por cada tipo o país, y llevan el modelo de 26 a 28. Sus PK y las FK de PERSONA usan el mismo tipo lógico int. Un tipo o país puede no tener personas asociadas o tener muchas; cada PERSONA referencia exactamente uno de cada catálogo.

PAIS sería un catálogo compartido con una fila por país incluido en el listado de países admitidos. Sus datos se cargarían una vez mediante una carga inicial reproducible; no habría que programar cada país ni escribir una lista distinta en cada formulario. El selector consultaría ese catálogo y PERSONA guardaría solamente pais_emisor_id. Los identificadores de un ejemplo no son valores ya cargados y el conjunto concreto de datos aún no se importó.

## 3. USUARIO

Representa la cuenta de acceso. Conserva los nueve campos anteriores y añade nickname como décimo campo aprobado en el Mermaid, sin duplicar nombre, género o documento. El cambio de autenticación todavía no se implementó en Java ni en el frontend.

| Campo | Tipo y clave | Condiciones |
| --- | --- | --- |
| id | int, PK | Identificador interno estable de la cuenta; las referencias históricas apuntan a este identificador |
| persona_id | int, FK a PERSONA.id y UNIQUE | Obligatorio; una cuenta pertenece a una persona y una misma PERSONA no tiene varias cuentas |
| email | string, longitud 254, UNIQUE | Obligatorio; conservar normalización trim y minúsculas, formato válido y control de duplicados también en la base |
| nickname | string, longitud pendiente, UNIQUE | Obligatorio; inicio de sesión junto con contraseña; normalización y restricción única individuales, no combinadas con email |
| password_hash | string, longitud 255 | Obligatorio; conserva el hash BCrypt, nunca la contraseña en claro; no se devuelve en el DTO ni se vuelca en auditoría |
| activo | boolean | Obligatorio; el registro público conserva el valor activo; la inactivación no borra la cuenta ni su historia |
| fecha_registro | datetime | Obligatoria en altas nuevas, fijada por el backend; en el legado actual solo se guarda fecha |
| token_recuperacion_hash | string, longitud 64, UNIQUE y opcional | Conservar la representación hash actual del token; ausente cuando no hay recuperación pendiente |
| vencimiento_token_recuperacion | datetime, opcional | Se completa y limpia junto con el hash del token; conservar vencimiento y uso único del flujo actual |
| version | int | Control optimista propuesto para concurrencia; administrado por persistencia, no por un valor libre del cliente |

La unicidad de email se mantiene también para cuentas inactivas. No se reutiliza silenciosamente la dirección para crear otra cuenta y heredar o separar de forma incorrecta sus operaciones.

Email y nickname se comprobarán por separado y tendrán restricciones únicas independientes. Un email usado con otro nickname se rechaza por email; un nickname usado con otro email se rechaza por nickname. Se recomienda no distinguir mayúsculas y minúsculas en el nickname; el formato y su representación física se concretarán antes de implementar. El backend deberá manejar también colisiones simultáneas y señalar el campo correspondiente; consultar disponibilidad antes de insertar no sustituye la restricción en la base. La clave primaria sigue siendo id y persona_id continúa como FK única.

Iniciar sesión por nickname requerirá adaptar la búsqueda de autenticación y sus consumidores, no solamente agregar una columna. Actualmente UsuarioController, AlquilerController y AlquilerService obtienen la cuenta por email a partir del principal autenticado: no debe sustituirse ese dato por nickname sin adaptar esas búsquedas y la identificación estable de la cuenta. Email conservará recuperación y notificaciones; conocer la dirección no autoriza por sí solo a cambiar la contraseña, pues se mantiene el enlace con token temporal y de un uso. El cambio del modelo no se presenta como funcionalidad de login ya implementada.

Las reglas de contraseña se validarán sobre el dato de entrada antes de hashearlo; no deben aplicarse los requisitos de una contraseña en claro al campo password_hash persistido. Esta revisión no cambia la política actual de composición de contraseña ni la regla existente del prefijo del email. Su adaptación a DTO de entrada forma parte de la futura implementación, no de un cambio ya ejecutado.

Los dos campos de recuperación son nulos juntos o están presentes juntos. Solicitar otro enlace reemplaza la recuperación pendiente y consumir uno válido limpia ambos campos. La comprobación del token, su vencimiento y el cambio de contraseña deben coordinarse en una operación transaccional; la presencia de version no demuestra por sí sola que eso ya esté resuelto.

No se agrega un booleano de deuda o permiso de alquiler en USUARIO. La deuda y demás restricciones se determinan por las reglas de negocio ya aprobadas; no se confunden con una cuenta inactiva. Tampoco se agrega email_verificado ni se afirma que el correo de bienvenida verifique la titularidad del email.

## 4. ROL

| Campo | Tipo y clave | Condiciones |
| --- | --- | --- |
| id | int, PK | Identificador del rol |
| codigo | string, longitud propuesta 20, UNIQUE | Obligatorio; CLIENTE, ADMIN o TECNICO, sin duplicados ni valores libres enviados por el registro público |

Se conserva el catálogo del DER y los tres roles del diccionario; no se agrega otra columna rol en USUARIO. Sus permisos son los de las reglas aprobadas: el nombre del rol no concede excepciones adicionales. En particular, ADMIN no sustituye TECNICO ni la asignación a una orden para ejecutar trabajo técnico, según [RN-MAN-02](17-permisos-y-transiciones-mantenimiento.md).

## 5. USUARIO_ROL

| Campo | Tipo y clave | Condiciones |
| --- | --- | --- |
| usuario_id | int, FK a USUARIO.id y parte de la PK | Obligatorio |
| rol_id | int, FK a ROL.id y parte de la PK | Obligatorio |

Se mantiene la clave primaria compuesta por usuario_id y rol_id. No hace falta una tercera columna id: el par ya identifica la asignación y evita repetir el mismo rol para una cuenta.

Una cuenta puede tener varios roles y debe conservar al menos uno. El registro público asigna únicamente CLIENTE, aunque el cuerpo de la petición intente incluir ADMIN, TECNICO u otras asignaciones. Los cambios de roles corresponden a un circuito administrativo autorizado y auditado, no a la edición libre del perfil.

Para evitar una ambigüedad con la clave compuesta, la auditoría de asignaciones se vincula a USUARIO mediante entidad_afectada y su id, conservando en los valores permitidos el rol asignado o retirado y la composición anterior/nueva. No se inventa un identificador numérico de USUARIO_ROL ni se pierde qué rol cambió. La acción, fecha y actor real se conservan en AUDITORIA_SISTEMA junto con la modificación; no se agregan aquí otra tabla ni solo una columna de última modificación como sustituto del historial.

Las autorizaciones deben usar todos los roles vigentes y las condiciones de la operación, no escoger arbitrariamente el primero. Cómo se actualizan sesiones existentes ante revocación de roles o inactivación es parte de la implementación de seguridad; no se declara solucionado por agregar la tabla o la columna version.

## 6. Relaciones y límites del bloque

- PERSONA y USUARIO mantienen una relación uno a uno, como en el DER original; ambas filas se crean juntas. La FK UNIQUE evita varias cuentas para la misma fila PERSONA, pero no impide por sí sola duplicar personas: ese control depende de D01.
- GENERO tiene muchas personas; cada persona referencia un único valor permitido.
- TIPO_DOCUMENTO y PAIS pueden tener cero o muchas personas asociadas; cada persona nueva tiene un tipo y un país emisor obligatorios. No se configura una relación uno a uno que impida compartir esos valores.
- USUARIO se relaciona con uno o muchos registros de USUARIO_ROL; cada asignación pertenece a una cuenta.
- ROL puede no tener asignaciones o tener muchas; cada asignación referencia un rol existente.
- Se conservan los vínculos desde alquileres, órdenes, incidencias e historiales hacia USUARIO. No se reemplazan con email o nombres que puedan cambiar.

La creación de PERSONA, USUARIO y su rol inicial debe ser atómica: un error no deja una persona huérfana o una cuenta sin rol. El dibujo no sustituye esa operación transaccional. No se habilitan borrados físicos en cascada de cuentas, personas o catálogos que destruyan alquileres, pagos o autorías históricas.

## 7. Reutilización y migración posterior

La separación no requiere volver a pedir contraseñas a todos los usuarios: se conservan los hashes existentes sin hashearlos otra vez. Se mantendrán los identificadores de cuenta o se preparará un mapeo de migración que preserve todas sus referencias; no se altera ahora ninguna fila.

Los datos personales existentes se trasladarán a PERSONA. No se inventan documentos para las cuentas actuales ni una hora exacta de registro donde solo existe una fecha. La compatibilidad de esos datos con campos obligatorios se resolverá en el plan de migración D06, sin bloquear devoluciones de viajes existentes por un perfil antiguo incompleto. La identificación ya fue aprobada; sigue pendiente cómo completar datos reales en el legado y asignar nicknames sin colisiones.

El enum actual de un solo rol deberá convertirse en asignaciones USUARIO_ROL, manteniendo CLIENTE y ADMIN existentes. TECNICO es parte del nuevo alcance, no un rol ya implementado. La autenticación deberá construir las autoridades a partir de la colección completa; el frontend y los DTO deberán adaptarse sin exponer hashes o tokens.

## 8. Comprobaciones previstas

Son criterios para implementar y probar después, no pruebas ejecutadas:

- CP-USR-01: el registro crea persona, cuenta y únicamente CLIENTE; si falla una parte, no queda una alta parcial.
- CP-USR-02: un email normalizado duplicado se rechaza también ante altas concurrentes o una cuenta anterior inactiva.
- CP-USR-03: una persona no queda vinculada a dos cuentas y un mismo par usuario/rol no se inserta dos veces.
- CP-USR-04: una cuenta ADMIN y TECNICO conserva ambos roles; trabajar sobre una orden sigue exigiendo la asignación autorizada.
- CP-USR-05: recuperar contraseña conserva vencimiento y uso único; ningún DTO o registro de auditoría expone contraseña, hash o token secreto.
- CP-USR-06: quitar un rol o inactivar una cuenta conserva actor y fecha y no borra sus alquileres ni autorías.
- CP-USR-07: la unicidad documental usa la combinación completa y no rechaza por sí sola números iguales emitidos por países diferentes; sí rechaza repetir la combinación completa.
- CP-USR-08: el registro sin tipo, número o país emisor se rechaza y no deja altas parciales.
- CP-USR-09: email y nickname duplicados se rechazan individualmente, también ante registros concurrentes; cambiar uno no permite repetir el otro.

## 9. Incorporación y siguiente bloque

El usuario aprobó las tres incorporaciones: catálogos TIPO_DOCUMENTO y PAIS; sustitución de DNI por tipo, país y número con unicidad compuesta, admitiendo DNI o pasaporte; y nickname único para el login con email único por separado. La obligatoriedad documental al registrarse ya estaba aprobada. Se añadieron dos entidades y dos relaciones, se modificaron únicamente PERSONA y USUARIO y se mantuvieron las otras 24 entidades y las 49 relaciones anteriores. En ese paso el modelo quedó en 28 entidades y 51 FK/relaciones; el total vigente después de otras incorporaciones se consulta en el [mapa de cambios](22-revision-del-der-y-mapa-de-cambios.md).

La política base de identificación y acceso queda cerrada para el DER lógico. Siguen pendientes longitudes nuevas, formato exacto del nickname, normalización documental por tipo/país, carga inicial y tratamiento del legado; son tareas de diseño físico e implementación, no autorización para inventar datos. Continúa la revisión de estaciones, tipos y bicicletas en el documento 26, sin dar por aprobado todo el modelo ni modificar código o la base.
