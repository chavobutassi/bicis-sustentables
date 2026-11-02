# RN-INC-01 Incidencias durante un viaje

Fecha de propuesta: 28 de octubre de 2026.

Fecha de aprobación de la incorporación del circuito mínimo: 28 de octubre de 2026.

Fecha de aprobación de la precisión económica: 28 de octubre de 2026.

Estado: circuito mínimo y precisión económica de la sección 8 aprobados expresamente para incorporar al diseño. La respuesta «Sí, esperar la revisión antes de liquidar» confirma registrar inmediatamente la devolución sin seguir contando tiempo y esperar la validación del corte antes de determinar el ajuste final. No se implementaron estados, tablas o endpoints nuevos ni se ejecutaron pruebas.

## 1. Decisión de incorporación

El usuario decidió incorporar el circuito mínimo en lugar de posponerlo. Resuelve el vacío que existiría si una pérdida, robo, avería o accidente impide una devolución normal de un detalle EN_CURSO: permite un cierre autorizado sin simular recepción física y fija un corte de uso distinto de la fecha posterior de revisión.

No se resuelve cambiando libremente la bicicleta a INACTIVA, DE_BAJA o DISPONIBLE ni marcando DEVUELTO sin recepción física. RN-BIC-02 sigue protegiendo el viaje frente a esos cambios; RN-INC-01 agrega una operación excepcional específica, no un permiso general para alterar estados.

Se releyeron el Word de estados, el PDF de visión completo y el DER v4 antes de consolidar esta aprobación. El Word ya incluye EXTRAVIADA; el PDF contempla el ciclo del alquiler, estados, mantenimiento, roles y trazabilidad. El reporte y el cierre separado encajan en esa visión. No se conserva el cierre forzoso de las 24 horas del Word: no prueba una pérdida, una devolución ni la fecha real del incidente. La política de cobro validado es una decisión de este proyecto, no una afirmación sobre todos los servicios de alquiler.

## 2. Alcance mínimo aprobado

Se cubre una incidencia que interrumpe efectivamente el uso e impide una devolución normal. Una situación que permite devolver la unidad conserva el recorrido de devolución y su reporte de falla cuando corresponda. La aceptación de un reporte no exige que la bicicleta permanezca desaparecida o fuera de una estación para siempre: su situación se vuelve a comprobar al decidir y al recibirla. El caso de devolución antes de la revisión económica se desarrolla en la sección 8.

El tiempo de uso ordinario es el tiempo transcurrido desde el retiro hasta la devolución válida, no solo los minutos en movimiento. Una parada voluntaria no congela el reloj. El corte anticipado por incidencia exige validación y no introduce un cálculo por GPS, distancia o tiempo de pedaleo.

No se automatizan asistencia física, seguros, atribución de responsabilidad o indemnizaciones.

El cliente propietario puede registrar el incidente de su detalle activo, con tipo, descripción y fecha del hecho informada. ADMIN también puede registrar un reporte recibido por otro canal, conservando quién lo comunicó y quién lo cargó. El sistema guarda por separado la fecha de registro del servidor. Un reporte no es una prueba automática de pérdida, responsabilidad ni fecha de interrupción. La información conocida sobre dónde quedó o se vio por última vez la bicicleta sirve para gestionar su recuperación; no se obliga al usuario a inventar coordenadas o una estación.

ADMIN revisa el caso y resuelve la solicitud de cierre excepcional con motivo. El mero reporte no cierra el alquiler ni congela unilateralmente el cobro. Se distinguen solicitud pendiente, cierre autorizado y solicitud descartada; los códigos exactos y su representación se consolidarán al revisar el DER. Descartar la solicitud de cierre no significa necesariamente negar que hubo un incidente. No se borra la descripción ni se declara culpa del cliente por esa decisión.

### Corte de uso y cierre excepcional

Si se autoriza el cierre, ADMIN valida y registra la fecha y hora en que la incidencia interrumpió el uso. El costo se calcula desde el retiro real hasta ese corte, con la tarifa y cotización contratadas. La fecha de revisión administrativa se conserva aparte y no agrega tiempo al costo del cliente. También se conserva la fecha informada originalmente, aunque la fecha validada sea diferente.

El corte no puede ser anterior al retiro ni posterior a la decisión y debe apoyarse en la revisión del caso, conservando el motivo y la información utilizada. No se acepta sin comprobación la fecha enviada por el navegador. Como precisión técnica de ese criterio, se propone además exigir que el corte no sea posterior al registro del reporte que acredita esa interrupción: se está comunicando un hecho que ya ocurrió, no un corte futuro. Las validaciones de zona horaria y cronología se concretarán en el DER y las pruebas. No se prometen verificaciones automáticas o integraciones que no existen.

Se incorpora CERRADO_POR_INCIDENCIA como estado terminal de ALQUILER_DETALLE. No se marca DEVUELTO ni se inventa una fecha o estación de devolución. El cierre guarda su propia fecha de corte y vínculo a la decisión. Una solicitud descartada no produce ese estado ni altera por sí sola el recorrido normal.

Las demás bicicletas del conjunto conservan sus viajes o reservas. Cuando todos los detalles son terminales, la cabecera puede quedar FINALIZADO. La liquidación conjunta requiere además resolver las incidencias que puedan cambiar el importe, conforme a la sección 8 aprobada. Se conservan los movimientos confirmados, tarifa y cotización contratadas. CERRADO_POR_INCIDENCIA amplía los terminales de RN-ALQ-07 y RN-ALQ-09 sin cambiar los seis nombres anteriores.

### Situación de la bicicleta y recuperación

- Pérdida o robo confirmados y bicicleta todavía no recuperada: se incorpora EXTRAVIADA a BICICLETA, sin ofrecerla a clientes ni atribuirle una estación de devolución. No es una baja definitiva automática. Si ya se recuperó cuando se decide, se registra la situación actual y su revisión; no se la presenta falsamente como todavía desaparecida.
- Avería o accidente que deja la bicicleta fuera de uso: MANTENIMIENTO, con revisión correctiva por el recorrido correspondiente. No se inventaría presencia en una estación ni aptitud técnica. El inicio de trabajo efectivo requiere acceso físico a la unidad; una orden CREADA no significa que ya fue recogida o revisada.
- Recuperación física: registrar recepción y ubicación reales, respetando capacidad si ingresa a una estación. Una EXTRAVIADA recuperada pasaría a MANTENIMIENTO para revisión, no directamente a DISPONIBLE. La habilitación posterior mantendría RN-MAN-02 y RN-MAN-04.
- Retiro definitivo de una EXTRAVIADA: requeriría una decisión específica de ADMIN con motivo, después del cierre autorizado del detalle y sin órdenes abiertas incompatibles. Conservaría historia y no simularía una recepción física. No sería una transición por simple demora.

Recuperar una unidad después de su cierre excepcional no reabre su contador ni duplica la liquidación. No se revierte una DE_BAJA desde el panel normal por el solo hecho de encontrarla después.

Mientras el reporte sigue pendiente y el detalle EN_CURSO, la bicicleta no se libera ni se ofrece a otro cliente. El reporte no se usa como un cambio directo de EN_USO a MANTENIMIENTO que eluda el contrato. Si se recibe físicamente antes de decidir, se conserva la recepción real y no se pierde un reporte de falla o accidente que requiera revisión técnica. La decisión administrativa del cobro no sustituye el control técnico de disponibilidad.

El diagnóstico y la aptitud siguen siendo trabajo del TECNICO asignado; ADMIN autoriza el cierre administrativo del viaje, no sustituye la inspección técnica ni puede declarar apta una bicicleta por aprobar un reporte.

## 3. Límites del alcance aprobado

No se generan multas, cargos por daños o reposición, indemnizaciones ni cobros automáticos por el simple reporte. Si luego se quieren agregar, necesitarán una política separada, comunicación al cliente y su implementación. Aquí solo se resuelve el uso contratado, el estado de la unidad y la trazabilidad.

No se declara extravío por exceder la duración estimada ni se introduce un cierre automático a las 24 horas. Tampoco se altera la restricción de nuevas contrataciones por deuda mediante un bloqueo de cuenta nuevo deducido de la mera existencia de un reporte.

El circuito exige intervención administrativa. No promete verificación policial, evaluación de seguros, localización en tiempo real ni respuesta de emergencia. No reemplaza esas gestiones externas.

Para que funcione cotidianamente, la aplicación necesita un acceso visible al reporte y al contacto del servicio, una bandeja administrativa de pendientes y una respuesta informativa para el cliente. Debe diferenciar reporte recibido de cierre autorizado y mostrar cualquier importe aún no validado como provisional. No se presupone atención las 24 horas ni que completar el formulario coordine automáticamente una recogida física.

La prestación real también requiere personas y procedimientos de contacto, recuperación y asistencia. Este diseño académico no garantiza por sí solo esas capacidades ni define obligaciones o responsabilidad por daños. No se pedirán datos médicos ni documentación sensible como requisito indiscriminado para registrar el aviso básico.

## 4. Impacto inicial en el DER y en la aplicación

Se aprueba incorporar una entidad INCIDENCIA vinculada a ALQUILER_DETALLE; la bicicleta y el titular se obtienen de ese detalle. Debe conservar tipo, descripción, fecha informada, fecha de registro, autor, decisión, responsable de resolución, motivo y corte de uso autorizado. La recepción física posterior se conserva separada del corte y de la revisión. Los nombres de columnas y catálogos no son todavía un esquema físico aprobado.

Se aprueban un estado adicional de detalle, CERRADO_POR_INCIDENCIA, y uno de bicicleta, EXTRAVIADA. Los tipos de incidente y las fases de revisión pueden representarse sin asumir de antemano una tabla por cada catálogo; se decidirá en el DER. La existencia de un solo cierre autorizado por detalle y la ausencia de duplicación económica deben protegerse también ante solicitudes concurrentes. Los reintentos conservan los reportes y antecedentes; no los sobrescriben para simular un incidente distinto.

Se necesitarían operaciones de reporte del propietario, revisión/cierre por ADMIN y recepción o baja de la bicicleta. TECNICO conservaría las operaciones de mantenimiento ya aprobadas. El frontend necesitaría mostrar la solicitud pendiente, su resolución y el cierre diferenciado de una devolución; no basta con agregar columnas a la base.

Antes de crear la migración se verificará esta dirección contra el DER original y el modelo consolidado. La incorporación puede aumentar el número de entidades, que el usuario ya permitió ajustar; no se preserva una cantidad de tablas a costa de perder hechos distintos.

## 5. Verificaciones del circuito aprobado

Estos criterios documentan qué verificar en el circuito aprobado; no son pruebas ejecutadas:

- CP-INC-01-01: un reporte no permite a otro cliente actuar sobre ese detalle ni cambiar la fecha de corte directamente.
- CP-INC-01-02: ADMIN no puede autorizar dos cierres o dos ajustes por solicitudes repetidas.
- CP-INC-01-03: el costo usa el corte validado, no la fecha posterior de revisión; conserva tarifa y cotización congeladas.
- CP-INC-01-04: no se completa ni reabre un detalle distinto del afectado, ni se fuerza la liquidación antes del cierre del conjunto.
- CP-INC-01-05: una carrera entre devolución normal y cierre excepcional produce un solo cierre de uso válido. Si ya hubo devolución, se conserva DEVUELTO y la recepción real; el efecto económico de una incidencia previa pendiente se resuelve antes de liquidar según la sección 8 aprobada. No se vuelve a cerrar ni se recalcula silenciosamente una liquidación ya definitiva.
- CP-INC-01-06: si la decisión excepcional se confirmó primero, la recepción física posterior se registra como recuperación, no como una segunda devolución facturable.
- CP-INC-01-07: la bicicleta extraviada o pendiente de revisión no se ofrece a clientes ni ocupa una estación ficticia.
- CP-INC-01-08: la recuperación no evita la revisión técnica, no reinicia el uso y no revierte automáticamente una baja.
- CP-INC-01-09: la decisión, su motivo, el corte, los reportes y los responsables quedan en la historia sin borrar pagos originales.

## 6. Contraste con servicios existentes

Consulta de referencias operativas oficiales: 28 de octubre de 2026.

La ayuda de [Citi Bike sobre problemas de una bicicleta](https://help.citibikenyc.com/hc/en-us/articles/360032369051-There-is-a-problem-with-my-bike) distingue devolver y señalar la unidad para revisión de pedir asistencia cuando no se puede terminar el viaje. Su ayuda de [pérdida o robo](https://help.citibikenyc.com/hc/en-us/articles/360032030752-My-bike-was-lost-or-stolen) remite a atención al cliente. [Lime también ofrece reporte y asistencia cuando un daño impide finalizar](https://help.li.me/hc/en-us/articles/115004748747-Reporting-a-damaged-vehicle). Estos ejemplos respaldan el patrón de aviso, atención y control de la unidad; no establecen nuestra tarifa ni prueban que todos los operadores detengan el cobro de la misma forma.

No se copian sus cargos, plazos, términos contractuales o reglas de responsabilidad. Se mantiene la política específica de este proyecto: tiempo de uso validado, sin multa ni cargo por daños automático y con tarifa/cotización congeladas. Las condiciones jurídicas y comerciales para una operación real requerirán su revisión propia; no se consideran resueltas por esta comparación.

## 7. Casos cotidianos analizados

| Caso | Tratamiento del circuito aprobado |
| --- | --- |
| Parada voluntaria para descansar | No es un cierre por incidencia; continúa el tiempo ordinario del alquiler |
| Falla que impide seguir y devolver por el recorrido normal | Aviso y revisión administrativa; cierre excepcional con corte validado y unidad fuera de alquiler para revisión |
| Reporte falso o insuficiente para autorizar el cierre | No se congela el cobro solo por pulsar el botón; se conserva la solicitud y la decisión motivada |
| Pérdida o robo confirmados, unidad ausente | Cierre excepcional distinto de devolución; EXTRAVIADA, sin estación ficticia ni baja automática |
| La bicicleta vuelve después del cierre excepcional | Recepción o recuperación física real; no se reinicia el contador ni se duplica la liquidación |
| La bicicleta vuelve antes de resolver el aviso | Se conserva DEVUELTO y su recepción real; si el incidente puede cambiar el importe, se espera su validación antes de liquidar, sin contar tiempo posterior a la devolución |
| Una unidad del conjunto tiene el incidente y otra sigue circulando | Solo cambia la afectada; la otra mantiene su viaje y su costo, con ajuste conjunto al cerrar |
| El vehículo aparece cuando ya estaba DE_BAJA | No se reactiva automáticamente ni se borra la decisión anterior |

La validación anterior es un análisis de reglas y escenarios, no una prueba del software ni una certificación de que esté listo para prestar el servicio real.

## 8. Devolución previa a la revisión y liquidación aprobadas

Se detectó una insuficiencia en la propuesta inicial: un usuario puede avisar una falla, conseguir después llevar la bicicleta a una estación y que ADMIN revise el caso más tarde. Desechar el corte de uso por el solo hecho de que ya devolvió podría cobrarle la espera de asistencia. Alterar después una liquidación ya definitiva requeriría un circuito de ajustes económicos posterior que no se ha definido.

Condiciones aprobadas expresamente el 28 de octubre de 2026 mediante «Sí, esperar la revisión antes de liquidar»:

- Una incidencia reportada durante el viaje y pendiente de validación, si puede afectar el importe, mantiene provisional el costo de esa unidad. No impide devolver ni prolonga su tiempo por la espera de revisión.
- La devolución se confirma físicamente con fecha y estación reales y el detalle queda DEVUELTO. No se transforma luego en CERRADO_POR_INCIDENCIA solo para representar la revisión económica.
- Si todos los detalles son terminales, la cabecera puede estar FINALIZADO, pero la situación financiera permanece SIN_LIQUIDAR hasta resolver las incidencias que puedan cambiar el importe. No se inicia un cobro adicional ni un reembolso calculados sobre una suma todavía provisional. Se conserva el anticipo y no se borra ningún movimiento confirmado.
- Si se valida una interrupción anterior a la recepción, se calcula ese uso hasta el corte validado y se conserva la devolución posterior como hecho físico. Si no corresponde ese corte, rige el fin de uso ordinario. La decisión y sus razones quedan registradas, sin atribución automática de culpa.
- Cuando no quedan usos o retiros pendientes ni revisiones económicas abiertas, se fija el costo conjunto y se aplica una sola liquidación con los valores contratados.
- Devolución, decisión y liquidación se coordinan para que ninguna solicitud saltee una revisión ya registrada. No se obliga al cliente a seguir mostrando la bicicleta EN_USO para diferir el dinero.

Ejemplo aprobado: retiro a las 10:00, falla que interrumpe el uso a las 10:45 y se reporta, recepción física a las 11:00, revisión administrativa a las 12:00. Si ADMIN valida el corte de las 10:45, se facturan 45 minutos; se conserva la recepción de las 11:00 y no se cobra hasta las 12:00. Si se descarta el corte y no hay otro impedimento, se usa el fin ordinario de las 11:00. Son importes pendientes de validación, no dos cargos.

Esta precisión amplía expresamente RN-ALQ-01/RN-ALQ-02: el costo de una unidad devuelta con una incidencia previa pendiente de efecto económico sigue provisional hasta la decisión. La devolución y el fin del tiempo no esperan a ADMIN; el ajuste final del conjunto sí espera esa revisión. La aprobación no crea otro estado financiero: se utiliza SIN_LIQUIDAR. No se espera por la reparación técnica en sí ni se modifica el anticipo confirmado.

Criterios adicionales de aceptación, documentados pero no ejecutados: devolución previa a la decisión con corte validado; devolución con solicitud descartada; cierre excepcional previo a recuperación; revisión y liquidación concurrentes; conservación del anticipo y ausencia de reembolsos duplicados.

No se modificaron el código, la base de datos ni los documentos originales. El circuito mínimo y la precisión económica de esta sección están aprobados para el diseño e implementación futura; quedan los detalles físicos indicados. No se ejecutaron pruebas ni se realizaron pagos o reembolsos.
