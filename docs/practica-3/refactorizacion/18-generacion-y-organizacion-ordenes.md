# RN-MAN-03 Generación y organización de órdenes

Fecha de aprobación: 28 de octubre de 2026.

Estado: tres reglas aprobadas expresamente por el usuario. No implementadas en Java ni en la base de datos. Las pruebas están especificadas, no ejecutadas.

## 1. Orden correctiva a partir de una devolución con falla

Al confirmar una devolución válida con falla reportada, se conservan los efectos ya aprobados: el detalle queda DEVUELTO, termina su tiempo de uso y la bicicleta queda MANTENIMIENTO, fuera de alquiler para revisión.

El sistema garantiza además que el reporte quede asociado a una orden abierta. Si no existe una para esa bicicleta, crea automáticamente una orden de tipo CORRECTIVO y estado CREADA. Se conservan la relación con el reporte, su bicicleta y el origen del evento.

La orden es generada por el sistema a partir del reporte del cliente; no se inventa una acción de un administrador humano. El reporte y la orden no prueban por sí solos una avería, responsabilidad del cliente ni un cargo por daños.

## 2. Una única orden abierta por bicicleta

Cada bicicleta admite como máximo una orden abierta. Se consideran abiertas las que están CREADA, EN_PROCESO o PAUSADA. Las órdenes FINALIZADA y CANCELADA se conservan como historia y no consumen ese límite.

Si ya hay una orden abierta, se incorpora el reporte a su atención sin crear otra ni borrar la información nueva. No se cambia automáticamente el tipo de la orden existente. Si la orden no corresponde al trabajo necesario, ADMIN puede resolverla mediante el recorrido autorizado de cancelación con motivo y creación de la que corresponda, conservando los registros anteriores.

Las solicitudes repetidas o concurrentes no deben producir órdenes abiertas duplicadas. Repetir un mismo evento no debe generar otra intervención para un reporte ya atendido ni alterar una orden posterior.

## 3. Asignación inicial opcional

Una orden CREADA puede quedar inicialmente sin técnico. ADMIN realiza la asignación posterior conforme a RN-MAN-02.

Iniciar o reanudar exige un técnico activo, con rol TECNICO y asignado a esa orden. La ausencia inicial de asignación no permite iniciar el trabajo ni autoriza a cualquier técnico a tomarla por una petición directa.

El DER deberá permitir esa falta de asignación mientras la orden está CREADA. Esto no transforma en opcional la asignación requerida para ejecutar el trabajo.

## 4. Coherencia y límites

Se mantienen los permisos, motivos, registro del resultado técnico y habilitación posterior por ADMIN de [RN-MAN-02](17-permisos-y-transiciones-mantenimiento.md). La vuelta al servicio sigue exigiendo revisión favorable vigente y ausencia de impedimentos; ni crear ni cancelar una orden libera por sí solo la bicicleta.

La creación manual de órdenes preventivas por ADMIN continúa aprobada. Posteriormente el usuario aprobó incorporar preventivas automáticas por calendario y sus condiciones de aplicación como requisito separado en [RN-MAN-04](19-propuesta-preventivo-por-calendario.md). Si hay un correctivo abierto se conserva la necesidad preventiva, sin crear dos órdenes abiertas ni cambiar automáticamente su tipo; se atiende después del correctivo y antes de habilitar. Los intervalos numéricos iniciales y detalles técnicos siguen pendientes; no se fijan por los ejemplos de la consulta.

Esta regla no permite convertir una unidad EN_USO o RESERVADA a mantenimiento mediante una intervención manual que eluda su alquiler. El cierre mínimo por incidencia se aprobó después y por separado en [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md), con corte validado y sin sustituir el trabajo técnico. No se incorpora un cierre forzoso por demora.

## 5. Criterios de aceptación

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-MAN-03-01 | Devolución válida con falla sin orden abierta | Detalle DEVUELTO, costo detenido, bicicleta MANTENIMIENTO y orden CORRECTIVO en CREADA |
| CP-MAN-03-02 | Nuevo reporte con una orden abierta | Se conserva y vincula la información sin crear otra orden abierta ni cambiar automáticamente su tipo |
| CP-MAN-03-03 | Dos solicitudes intentan crear una orden abierta para la misma unidad | Como máximo una queda abierta; no se pierde el reporte |
| CP-MAN-03-04 | Se repite un reporte ya procesado | No se crea una nueva orden por la repetición ni se altera una intervención posterior |
| CP-MAN-03-05 | Orden CREADA sin técnico | Se permite conservarla pendiente de asignación |
| CP-MAN-03-06 | Se intenta iniciar una orden sin técnico válido asignado | El backend rechaza la operación |
| CP-MAN-03-07 | ADMIN asigna un técnico válido a una orden CREADA | El técnico asignado puede iniciar conforme a RN-MAN-02 |
| CP-MAN-03-08 | Una orden anterior terminó y corresponde una nueva intervención distinta | Se conserva la historia y se permite una nueva orden respetando el máximo de una abierta |

Las relaciones físicas de reporte, orden e historial y sus restricciones se consolidarán en el DER. No se modificaron Word, PDF, DER original, código ni base de datos. No se ejecutaron aplicaciones ni pruebas de integración.
