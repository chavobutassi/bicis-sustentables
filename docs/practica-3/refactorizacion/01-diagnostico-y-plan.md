# Turismo Sustentable: diagnóstico y comienzo de la refactorización

Fecha de revisión: 25 de octubre de 2026.

Estado: revisión inicial del código, del PDF de Prácticas III y del DER v4. Este documento propone correcciones y un orden de trabajo. No aprueba todavía un esquema definitivo ni autoriza modificaciones de la base existente.

## 1. Conclusión

La propuesta está encaminada: el modelo incorpora detalles por bicicleta, mantenimiento, pagos y trazabilidad que el prototipo actual no tiene. Sin embargo, no conviene trasladar el DER v4 literalmente a Java. Antes deben cerrarse las reglas de reserva, cobro, devolución y permisos.

No es una reescritura completa. Se pueden reutilizar el frontend, la autenticación, el correo y buena parte de las reglas de estaciones y alquileres. El cambio de mayor impacto es pasar de un alquiler asociado directamente a una bicicleta a una cabecera con uno o varios detalles.

El usuario confirmó que la cantidad de 21 tablas puede ajustarse. Todavía no está definido si la entrega exige pagos reales y un candado físico o acepta un entorno de pruebas y una simulación. No se toma ninguna de esas alternativas como aprobada.

## 2. Evidencia y límites de esta revisión

- Repositorio local: rama `main`, último commit observado `ab91d6a`.
- Se identificaron seis clases persistentes: `Usuario`, `Estacion`, `Bicicleta`, `Alquiler`, `Tarjeta` y `Suscripcion`. Esto verifica el modelo Java, no el contenido ni el esquema efectivo de una instancia de MySQL.
- El DER v4 contiene 21 entidades conceptuales, contando `USUARIO_ROL`.
- La configuración local predeterminada apunta a MySQL y usa `ddl-auto=update`; puede ser reemplazada por variables de entorno.
- Solo se encontró un test `contextLoads()` con `@SpringBootTest`, sin un perfil de pruebas separado en los archivos inspeccionados.
- No se arrancó Spring Boot, no se ejecutaron tests que carguen el contexto, no se consultó ni modificó una base de datos y no se cambió código de la aplicación.
- La revisión es estática. La presencia de una regla en el código no demuestra por sí sola que esté libre de fallos bajo concurrencia ni que funcione hoy con servicios externos.

## 3. Comparación entre lo actual y lo propuesto

| Área | Código actual | Propuesta de Prácticas III | Trabajo principal |
| --- | --- | --- | --- |
| Identidad | Datos personales y cuenta en `Usuario` | `Persona`, `Genero`, `Usuario` | Separar datos sin romper el registro ni la recuperación |
| Permisos | Un enum `Rol`, CLIENTE o ADMIN | `Rol` y `UsuarioRol`, con técnicos | Adaptar autenticación, autorización, DTO y frontend |
| Bicicletas | Tipo y estado como enums; tarifa por unidad | Catálogos y tarifa en `TipoBicicleta` | Decidir política tarifaria y traducir búsquedas/validaciones |
| Estaciones | Coordenadas, disponibilidad y validaciones de capacidad | Se conserva el núcleo | Preservar diferencia entre presencia física y disponibilidad |
| Alquiler | Una bicicleta, un retiro y una devolución por registro | Cabecera y varios detalles | Rediseñar el servicio, las respuestas y el historial |
| Costos | Tarifa aplicada guardada; importe estimado reemplazado por final | Estimado y real separados | Mantener también moneda y conversión histórica |
| Pagos | No hay módulo de transacciones de pasarela | `Pago` y `EstadoPago` | Definir cobro, confirmación, reintentos y devoluciones de dinero |
| Mantenimiento | Estado MANTENIMIENTO | Orden, técnico e historial | Implementar un recorrido completo de trabajo |
| QR | No implementado | Validación y apertura del candado | Separar identificación de bicicleta de control físico |
| Trazabilidad | Sin tablas de auditoría/historial operativo | Tres historiales y auditoría general | Registrar actor, origen y transición dentro de la operación |
| Correo | Mailjet, bienvenida, recuperación y tickets | Debe conservarse | Adaptar mensajes al alquiler con detalles |
| Tarjetas y suscripciones | Entidades presentes; sin módulo completo equivalente | No aparecen en el nuevo DER | Decidir retiro controlado o nuevo alcance, sin borrar datos a ciegas |

El destino sería un modelo total revisado, no seis tablas actuales más otras 21. Una tabla de unión tampoco obliga siempre a tener una clase `@Entity` propia: esa decisión se toma al definir el mapeo.

## 4. Correcciones que deben resolverse antes de las entidades

### C01. Reserva y exclusividad de una bicicleta

El caso de uso crea un alquiler RESERVADO y permite pagar, pero recién cambia la bicicleta a EN_USO después del QR. No define una exclusión previa que impida reservar o pagar la misma unidad dos veces.

La reserva fue aprobada por el usuario y se documentó en [RN-ALQ-03](04-reserva-y-vencimiento.md). Condiciones aprobadas y controles técnicos necesarios:

- Reservar cada unidad de forma atómica al confirmar la solicitud.
- Representar la reserva mediante un estado o una regla equivalente de exclusividad, sin confundirla con un viaje iniciado.
- Persistir un vencimiento de 15 minutos desde la confirmación para completar pago y retiro. Al vencer, liberar solo las unidades no retiradas, sin cobrarles tiempo de uso. Sus anticipos se incluyen en el ajuste conjunto; si no se retiró ninguna, corresponde reembolso total del anticipo confirmado.
- Mantener la bicicleta físicamente en su estación hasta el retiro efectivo. Una bicicleta reservada no está disponible para otro cliente, pero sí ocupa un lugar físico.
- Volver a verificar la reserva al procesar el pago y al autorizar el retiro. Un pago confirmado tarde no debe reactivar una reserva vencida ni asignar una unidad ya tomada.
- Para varias bicicletas, definir reserva de todo el conjunto o rechazo completo. Bloquear las unidades en un orden consistente para reducir conflictos entre operaciones.

Un bloqueo de fila dura una transacción, no puede mantenerse durante toda la navegación del usuario por una pasarela de pago. Por eso hacen falta una reserva persistida y transacciones cortas.

### C02. Pago previo y costo real

Decisión confirmada por el usuario el 25 de octubre de 2026: cobrar anticipadamente la duración estimada y liquidar según el tiempo real. Si se paga por dos horas y se utilizan 45 minutos, corresponde el costo de esos 45 minutos y un reembolso de la diferencia. El pago previo es un anticipo, no una compra irrevocable de un bloque de tiempo.

También se confirmó que el tiempo adicional se cobra con la misma tarifa, sin multas para esta entrega. La devolución termina el viaje aunque quede un saldo deudor. Ese saldo impide iniciar nuevos alquileres hasta pagarlo, pero no impide ingresar, pagar ni devolver otras bicicletas ya en uso. No se efectuarán débitos adicionales automáticos en esta primera versión.

También se aprobaron las devoluciones individuales, la liquidación final conjunta, la reserva de 15 minutos con vencimiento de unidades no retiradas y la cancelación voluntaria sin penalización antes del retiro, documentada en [RN-ALQ-05](06-cancelacion-antes-del-retiro.md). Queda por completar el tratamiento operativo de fallos del reembolso.

La devolución física y la liquidación financiera deben registrarse por separado: una bicicleta devuelta puede quedar disponible aunque su reembolso continúe pendiente. Un fallo de la pasarela no debe mantener artificialmente activo el viaje ni generar un segundo reembolso por un reintento.

Se registró la decisión y sus consecuencias propuestas en [02-regla-de-cobro.md](02-regla-de-cobro.md). No se implementó todavía un proveedor ni se realizaron movimientos de dinero.

El pago requiere moneda, identificación del proveedor y su operación, tipo de movimiento si hay anticipos/saldos/reembolsos y prevención de confirmaciones duplicadas. Una redirección de éxito del navegador no debe bastar para aprobar un pago. La autenticidad y el procesamiento de las notificaciones se definirán con la documentación del proveedor elegido.

### C03. Tarifa y monedas históricas

El DER ubica `precio_por_hora` en `TIPO_BICICLETA`, pero no conserva una tarifa aplicada en `ALQUILER_DETALLE`. Eso perdería la protección que hoy existe en `Alquiler.precioPorHoraAplicado`.

La política se aprobó en [RN-ALQ-04](05-tarifa-moneda-y-cotizacion.md). Correcciones y decisiones vigentes:

- Guardar la tarifa aplicada por detalle cuando se contrata y mantenerla inmutable para esa operación.
- Mantener tarifas de referencia USD y realizar pagos, adicionales y reembolsos en ARS. Identificar las monedas de subtotales y totales.
- Congelar tarifa y cotización al confirmar la contratación, antes del anticipo. Persistir los importes y la cotización aplicada, con fecha y fuente. No recalcular un viaje histórico con la cotización actual.
- Usar una misma cotización congelada para todas las unidades del alquiler, aunque vuelvan en momentos diferentes. Los adicionales y reembolsos mantienen ese valor, aunque se procesen después.
- Mantener el estimado y el real separados, sin sobrescribir uno con el otro.
- Definir si el precio por tipo reemplaza intencionalmente al precio por bicicleta. Los datos antiguos podrían tener tarifas distintas dentro de un mismo tipo.

### C04. Alquiler con varios detalles

La relación cabecera/detalle es razonable, pero el caso de uso del PDF solo desarrolla la selección de una bicicleta. La regla ampliada ya fue aprobada por el usuario y se documentó en [RN-ALQ-02](03-alquiler-con-varias-bicicletas.md):

- Un alquiler puede incluir varias bicicletas, cada una con su tarifa y fechas reales de retiro y devolución.
- Las unidades pueden devolverse por separado y en estaciones distintas, siempre con capacidad.
- La devolución detiene el costo y libera únicamente la bicicleta recibida.
- La liquidación económica del conjunto se realiza al terminar el uso de todas, no en cada devolución intermedia.
- El costo total real se compara con el anticipo total para determinar reembolso, igualdad o saldo deudor.

Las unidades reservadas pero no retiradas vencen conforme a RN-ALQ-03, con costo de uso cero. Todavía deben concretarse los nombres de los estados, las restricciones del conjunto y el rechazo de bicicletas repetidas. La cabecera debe distinguir el estado del uso del estado financiero.

Se recomienda soportar primero un detalle por alquiler sobre el nuevo modelo y verificar el recorrido completo. Luego habilitar varios detalles, con pruebas de devolución parcial. Ese primer paso es un incremento técnico, no una cancelación del alcance de varias unidades.

### C05. Actor de los cambios y mantenimiento

Los historiales y la auditoría usan `administrador_id`, aunque también actuarán clientes, técnicos y procesos automáticos.

Corrección propuesta: un nombre como `usuario_actor_id`, más el origen de la operación. Debe poder representarse un evento automático sin inventar un administrador real. La obligatoriedad del actor depende del origen acordado.

La FK `tecnico_id` solo garantiza que existe un usuario. El servicio debe comprobar que tenga el rol adecuado. Si una orden puede crearse antes de asignarse, la asignación y la fecha de inicio efectivo deben poder estar pendientes.

Los historiales registran transiciones del dominio; la auditoría registra operaciones críticas. Conviene distinguir su propósito y excluir contraseñas, tokens y datos sensibles de los valores auditados.

### C06. Claves, restricciones y nulabilidad

El DER conceptual no sustituye al diseño físico. Agregar o documentar:

- PK compuesta o restricción UNIQUE de `(usuario_id, rol_id)` en `USUARIO_ROL`.
- UNIQUE de `usuario.persona_id` si se mantiene una cuenta por persona.
- Email normalizado y único, códigos de catálogos únicos, código de bicicleta único y referencia externa del pago con la unicidad que corresponda al proveedor y tipo de evento.
- Capacidad positiva, importes no negativos y coherencia entre fechas.
- Estación actual opcional para una bicicleta que está en viaje. No debe ser obligatoria por el solo hecho de dibujar una relación con ESTACION.
- Fechas reales de retiro/devolución y estación de devolución opcionales hasta que esos hechos ocurran.
- Una restricción/regla transaccional para evitar más de una reserva o uso activo incompatible por bicicleta.
- Regla de unicidad y obligatoriedad del documento de identidad. Un DNI argentino obligatorio no cubre por sí solo el público de turistas extranjeros.
- Si los historiales incluyen el estado inicial, crearlo con la entidad en la misma transacción. De lo contrario, ajustar su cardinalidad mínima.

No todos los catálogos requieren ABM en el frontend. Los estados pueden mantenerse como listas controladas. Su cantidad y representación se deciden por necesidad, no para alcanzar 21 tablas.

### C07. Funciones que el nuevo DER no debe perder

- El usuario conserva email, hash de contraseña, estado activo y los datos de recuperación de contraseña o un mecanismo equivalente. Los dos campos actuales de recuperación no aparecen en el DER v4.
- Registro público crea clientes. La asignación de roles administrativos o técnicos nunca debe depender de lo que envía el formulario público.
- Las reglas de propietario del alquiler se aplican también al detalle, QR y futuras operaciones de pago.
- Se conservan las validaciones de capacidad y la distinción entre bicicletas físicas y disponibles.
- DTO de entrada para aceptar solo campos autorizados y validarlos. Las entidades persistentes no deben ser la entrada general de operaciones de registro/administración.
- Las respuestas del backend pueden mantener nombres que ya consume el frontend mientras se realizan cambios controlados.

### C08. Coherencia del PDF

- El DFD de nivel 2 coloca el escaneo antes de la creación de reserva/viaje. El caso de uso ubica reserva y pago antes del QR. Deben describir el mismo comportamiento y conservar los flujos de datos que cruzan el límite del proceso.
- Un DFD muestra intercambio de datos; la secuencia de decisiones y estados debe quedar clara en el caso de uso o diagrama de actividades, sin tratar las flechas del DFD como un algoritmo.
- En el flujo de error de creación del pago, distinguir el fallo local de una transacción de la interacción externa con la pasarela. No borrar operaciones confirmadas o con movimiento financiero para ocultar un error.
- Unificar nombres de estados. Por ejemplo, hoy existen INICIADO y ALQUILADA, mientras la propuesta usa EN_PROGRESO y EN_USO. Un cambio de nombre impacta código, datos, DTO y JavaScript.
- Incorporar los recorridos de devolución, mantenimiento y pago tardío/rechazado, no solo el de contratación exitosa.
- Identificar requerimientos con un código y un criterio comprobable. Evitar promesas absolutas de disponibilidad exacta: el backend debe validar de nuevo cuando se opera.
- Distinguir objetivos de movilidad/turismo de resultados medidos. El software por sí solo no demuestra una reducción de congestión o emisiones.

## 5. Decisiones para limitar el riesgo de estas tres semanas

1. Mantener Java, Spring Boot, frontend y MySQL local como punto de partida. No sumar a esta refactorización una reescritura del frontend, microservicios ni un cambio simultáneo de framework y motor de base.
2. Tratar QR de identificación y apertura física como integraciones diferentes. La identificación puede validarse en el software; el hardware necesita requisitos, equipo y acceso concretos.
3. Preguntar al profesor qué acepta en pagos/hardware cuanto antes. No prometer una integración física ni presentarla como funcional si solo existe una simulación.
4. No construir un ABM genérico para cada tabla. Los catálogos de estados y los historiales no necesitan las mismas pantallas que bicicletas o mantenimiento.
5. No reutilizar `Tarjeta` tal cual para pagos reales: incluye un campo CVV persistente. Para el nuevo alcance conviene delegar el manejo de los datos sensibles al proveedor y conservar las referencias necesarias. PCI SSC prohíbe almacenar el código de verificación después de la autorización, incluso cifrado: [FAQ oficial 1319](https://www.pcisecuritystandards.org/faqs/1319/).
6. El requerimiento de guardar métodos de pago del PDF no está resuelto por tener una tabla PAGO. Debe definirse si se elimina del alcance inicial o se integra mediante referencias/tokens del proveedor, sin inventar una tabla extra antes de acordarlo.

## 6. Orden de implementación recomendado

Las franjas son un presupuesto tentativo de días de calendario, no una garantía de terminación. Deben ajustarse a las horas disponibles, el reparto entre compañeros y la respuesta sobre pagos/hardware.

| Franja | Entrega verificable | Condición para avanzar |
| --- | --- | --- |
| Días 1 a 2 | Reglas de negocio acordadas, DER corregido y lista de casos mínimos | Reserva, cobro, varios detalles y alcance QR sin contradicciones |
| Días 3 a 7 | Base de desarrollo separada, migraciones reproducibles e identidad/catálogos adaptados | Registro, login, permisos y recuperación siguen funcionando |
| Días 8 a 12 | Alquiler con detalles, reserva, retiro y devoluciones | Una unidad no se duplica, tarifa estable y capacidad protegida |
| Días 13 a 16 | Orden de mantenimiento y trazabilidad conectadas al flujo | Técnico autorizado, cambios de estado e historial consistentes |
| Días 17 a 18 | Integraciones QR/pago según alcance aprobado | Confirmaciones repetidas, rechazos y fallos tratados correctamente |
| Días 19 a 21 | Regresión completa, evidencia, documentación y correcciones | Recorrido de demostración completo sin depender de cambios de última hora |

La validación de viabilidad de pasarela y hardware debe ocurrir al principio, no recién en los días 17 a 18. Esas franjas corresponden al cierre e integración de trabajo ya preparado. Si el alcance o las horas no alcanzan, hay que negociar una reducción explícita antes de consumir el margen final.

## 7. Seguridad de la transformación de datos

- Preservar la versión aprobada y preparar una rama de trabajo antes de cambios de código. Este documento no creó ninguna rama ni commit.
- Verificar qué cambios/documentos locales están sin versionar antes de decidir qué se guarda en Git.
- Obtener y comprobar una copia de respaldo de la base que interese conservar antes de migrarla.
- Preferir inicialmente una base de desarrollo separada, por ejemplo `turi_practica3`, sin sustituir la actual `turi`.
- Usar scripts/migraciones versionadas. `ddl-auto=update` no reemplaza un plan para separar columnas en Persona, transformar roles o crear detalles a partir de alquileres existentes.
- Cada alquiler anterior se transforma en una cabecera y un detalle, conservando identificadores/referencias según el plan de migración.
- En los registros INICIADO actuales, `fechaFin` representa la estimación. En los FINALIZADO representa el fin real. No copiar ese campo indiscriminadamente a ambas fechas nuevas.
- En la versión actual el importe estimado se sobrescribe al finalizar. No inventar estimados históricos que ya no se conservaron ni tarifas aplicadas antiguas que estén ausentes.
- Documentar los campos que no pueden reconstruirse y las políticas para datos de demostración frente a datos que deban preservarse.
- Retirar Tarjeta/Suscripcion y sus referencias solo después de verificar dependencias y decidir el destino de sus datos. Quitar una clase Java no equivale a una migración segura del esquema.

## 8. Pruebas que definen una entrega utilizable

- Registro válido y email duplicado.
- Ingreso de usuario inactivo y verificación de permisos CLIENTE, ADMIN y TECNICO.
- Recuperación con enlace válido, vencido y ya utilizado.
- Dos solicitudes sobre la misma bicicleta: solo una obtiene una reserva válida.
- Reserva vencida o cancelada: se libera la unidad y no se habilita el retiro.
- QR de otra bicicleta u otro alquiler: operación rechazada por el backend.
- Devolución a estación llena y dos devoluciones que compiten por el último lugar.
- Dos peticiones de finalización del mismo detalle: solo una transición efectiva.
- Cambio de tarifa durante una reserva/viaje: conserva el precio contratado según la regla aprobada.
- Dos detalles con devoluciones distintas: la cabecera no finaliza prematuramente.
- Pago rechazado, confirmado dos veces o recibido después del vencimiento.
- Fallo del proveedor de correo: no debe generar una operación de negocio duplicada.
- Orden de mantenimiento: una unidad no se ofrece para alquilar mientras está fuera de servicio.
- Historial/auditoría con actor y origen correctos, sin secretos en los datos registrados.
- Repetición completa de la demostración local con datos conocidos y guía de uso.

Los tests necesitan una base/perfil aislados antes de ejecutar pruebas que carguen Spring. Para servicios externos se deben controlar respuestas de prueba; no usar correos, cobros o infraestructura reales sin autorización.

## 9. Organización en pareja y documentación mínima

- Acordar una entrega pequeña por vez y revisar cada cambio antes de integrarlo.
- Designar quién modifica el núcleo de entidades, migraciones y alquileres. Evitar editar simultáneamente la misma clase central.
- El otro compañero puede trabajar en adaptación de pantallas, casos de prueba y evidencias contra un contrato de API acordado.
- Registrar por incremento: requerimiento, regla, entidades involucradas, prueba y evidencia. No dejar toda la documentación para la última semana.
- Mantener un único repositorio compartido y una rama principal utilizable. La distribución definitiva depende del tiempo real que tenga cada uno.

## 10. Próximo paso concreto

Las reglas de cobro por menor o mayor uso ya están confirmadas en `02-regla-de-cobro.md`: anticipo por tiempo estimado, costo por uso real, reembolso del excedente o saldo deudor sin multas. El saldo deudor impide nuevas contrataciones, no la devolución física.

El funcionamiento de varias bicicletas y su liquidación conjunta está aprobado en `03-alquiler-con-varias-bicicletas.md`; la reserva de 15 minutos y el vencimiento de unidades nunca retiradas, en `04-reserva-y-vencimiento.md`; tarifa USD, movimientos ARS y cotización congelada al confirmar, en `05-tarifa-moneda-y-cotizacion.md`; y la cancelación voluntaria de unidades no retiradas, en `06-cancelacion-antes-del-retiro.md`. El siguiente bloque es consolidar estados y relaciones para corregir el DER, cerrar la precisión de cálculo y acordar las condiciones de obtención de la cotización. El seguimiento de decisiones se encuentra en [00-indice-y-estado.md](00-indice-y-estado.md).

Después se prepara el entorno aislado y se implementa el primer incremento. No empezar creando 21 clases desconectadas, y no cambiar todavía la base aprobada.

## Fuentes revisadas

- [Propuesta de Prácticas III](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>): alcance y requerimientos, páginas 2 a 5; DFD y DER, páginas 6 a 8; caso de uso, páginas 9 a 15.
- [DER v4 original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/DER/DERv4.txt>).
- [Alquiler y campos actuales](<D:/Karim/Downloads/Turismo Sustentable/_versiones/TurismoSustentable/src/main/java/DSII/TurismoSustentable/models/Alquiler.java>).
- [Servicio de alquileres](<D:/Karim/Downloads/Turismo Sustentable/_versiones/TurismoSustentable/src/main/java/DSII/TurismoSustentable/services/AlquilerService.java>).
- [Usuario y recuperación](<D:/Karim/Downloads/Turismo Sustentable/_versiones/TurismoSustentable/src/main/java/DSII/TurismoSustentable/models/Usuario.java>) y `services/RecuperacionPasswordService.java`.
- Controladores, repositorios, DTO, configuraciones de seguridad, frontend, `application.properties`, `build.gradle`, inicialización y test de contexto del mismo repositorio.

Los documentos originales se conservaron sin cambios. No se generó todavía un DER v5 definitivo porque las decisiones comerciales y de integración siguen pendientes.
