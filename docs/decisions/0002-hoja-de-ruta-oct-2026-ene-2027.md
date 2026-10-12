# 0002. Hoja de ruta 2026-10 → 2027-01: release, spike y bifurcación

- **Estado:** propuesta
- **Fecha:** 2026-10-12
- **Tipo:** hoja de ruta

## Contexto
Hay que priorizar qué construir en los próximos tres meses. El proyecto lo mantiene
una sola persona, con 5-10 h/semana (≈1,6-3,2 semanas-persona en el trimestre). El
objetivo a 6-12 meses es «un caso real»: un equipo con un monolito Python que use
unskein. `develop` lleva 19.094 líneas sin publicar desde v0.3.0 (2026-10-02), entre
ellas `untangle --prove`, las fugas de API, los imports con asterisco y los módulos
nativos. Python 3.15 se publicó el 2026-10-09 con `lazy import` (PEP 810), y unskein
todavía no lo soporta.

## Decisión
1. Semanas 1-2: soportar `lazy import` (clasificarlo como LAZY y añadir 3.15 al CI) y
   publicar v0.4.0 con el README y la ficha de PyPI alineados al lema del ADR 0001.
2. Semanas 3-5: spike en NetBox (≈0,5 semanas). Mide la tasa de cortes probados y
   declara a mano 2-3 apps como contextos para medir qué cruza las fronteras.
3. Semana 6, bifurcación:
   - Si la tasa de NetBox supera el 70 % y la maraña principal se reduce mucho:
     estudio de caso público con la suite de tests del proyecto antes y después.
   - Si la tasa está por debajo del 30 %, o un equipo real pide fronteras: MVP del
     contrato `[contexts]` (no cabe entero en el trimestre).
   - Entre el 30 % y el 70 %: se decide con lo que diga el primer contacto con un
     equipo; sin contacto, MVP de `[contexts]`.

## Alternativas consideradas
- Estudio de caso público directamente, sin spike — fuera de litellm la tasa de
  cortes probados ronda el 19 % (rich 5/29, networkx 7/32, aiohttp 0/1). Publicar
  un «6 de 40» haría daño.
- `[contexts]` completo ya — cuesta ≈2,5 semanas, casi todo el trimestre, y el
  spike puede abaratarlo o descartarlo.
- `--prove --run-tests` como producto — no hay demanda observada; se hace a mano
  dentro del estudio de caso.
- Gate CI determinista (`--fail-on`) — commodity (import-linter y Tach lo tienen) y
  choca con un principio declarado.
- Adaptador Django de cableado dinámico — mantenimiento alto; Tach ya lee
  `INSTALLED_APPS` y `ForeignKey("app.Model")` (PR #596).
- Salida JSON versionada — demanda real pero paridad; queda primera en la cola
  si sobra capacidad.
- Diagramas Mermaid, otros lenguajes — impacto bajo o esfuerzo fuera de alcance.

## Argumentos en contra y respuesta
- Los cortes LAZY y TYPE_CHECKING no reducen Ca/Ce: cambian cuándo se importa, no si
  hay dependencia. La demanda observada pide fronteras, no cortes de ciclos.
  → El lema del ADR 0001 ya solo promete ciclos al importar, y la bifurcación lleva a
  `[contexts]` si el spike o un equipo lo piden.
- Riesgo de sobreajuste a litellm, el proyecto sobre el que se iteró la funcionalidad.
  → El spike en NetBox es justo la prueba fuera de litellm, y va antes de publicar
  cualquier caso.
- En Django, unskein no ve el 24-27 % del código (cableado dinámico). → Se declara en
  el estudio de caso. El adaptador queda aplazado y no descartado.
- Sin soporte de 3.15, el código con `lazy import` da `SyntaxError` al parsearse con
  Python ≤3.14 y, presumiblemente, ciclos falsos con 3.15. → Va antes de la release.

## Evidencia
- Python 3.15.0 publicado el 2026-10-09 — python.org — consultado 2026-10-12
- PEP 810 en estado Final: `lazy` solo a nivel de módulo, ni en funciones ni en `try`
  — peps.python.org — resolución 2025-11-03
- `ast.parse("lazy import json")` con Python 3.12 da `SyntaxError`; el parser no menciona
  `lazy` — prueba local y lectura del código — 2026-10-12
- Descargas del último mes, con CI incluido: unskein 389, import-linter 21,2 M (crece
  desde 4,1 M en abril), tach 4,6 M (plano desde julio) — pypistats — 2026-10-12
- Demanda de JSON: import-linter #291 (abierto desde 2025-10-08, comentario del
  2026-09-15 pidiendo un esquema estable); tach #678, #680 — issues — 2025-2026
- Demanda de fronteras declaradas: import-linter #262 (apps Django y sus models), #240;
  tach #584, #759 — issues — 2024-2025
- Demanda de visualización: tach #905 (2026-01-25), #767, #677 — issues
- Ciclos: tach #476, el check se para en el primer ciclo y no da la ruta — issue — 2024-12
- Tach PR #596: lee `INSTALLED_APPS` y `ForeignKey("app.Model")` — repo — 2025-02-05
- En la documentación leída, ninguno de import-linter, Tach, Packwerk, Sonargraph,
  SonarQube, Structure101 ni ArchUnit propone o comprueba cortes entre grupos
  declarados; import-linter sugiere un conjunto mínimo de dependencias a quitar
  (`nominate_cycle_breakers`) — docs — consultadas 2026-10-12
- Cortes probados: litellm 218/240, rich 5/29, networkx 7/32, aiohttp 0/1, todos sin
  ejecutar tests — autoinforme — 2026-10-10
- Spike Zulip/NetBox: el 24-27 % del código no alcanzado es cableado dinámico de Django
  — autoinforme (docs/research/spike-slices-zulip-netbox.md) — 2026-10-11
- Puntuación RICE+D (R estimado, C con techo del 50 %): release 10,0; spike 3,0;
  estudio de caso 3,0; soporte 3.15 2,5; JSON 1,33; `[contexts]` 1,2; Mermaid 1,0;
  `--run-tests` 0,96; gate CI 0,67; adaptador Django 0,6. Orden robusto a
  sensibilidad — `rice.py` — 2026-10-12

## Confianza
Media. Publicar v0.4.0 y soportar 3.15 tienen respaldo claro. El resto depende de
datos que todavía no existen: la tasa en NetBox y lo que pida un equipo real. Las
cifras de unskein son autoinformes sobre proyectos elegidos por el mantenedor. Los
esfuerzos son estimaciones a partir del tamaño del código.

## Principios del proyecto afectados
Ninguno en lo decidido. Los aplazados chocarían con principios declarados (no
marcados como no negociables): `--run-tests` con «`--run` es lo único que ejecuta
código del proyecto», y el gate CI con «los hallazgos nunca cambian el código de salida».

## Qué haría revisar esta decisión
- El resultado del spike en NetBox (semana 5), que activa la bifurcación.
- Un equipo real que diga si su bloqueo son los ciclos al importar o las fronteras.
- Que los tests de un proyecto Django detecten roturas reales al aplicar cortes: eso
  subiría la prioridad de `--run-tests`.
- Que import-linter o Tach publiquen propuesta o comprobación de cortes entre grupos
  declarados.
- Revisión obligatoria el 2027-01-12.

## Consecuencias
- Rama nueva desde `develop` para `lazy import`; CI con 3.12-3.15.
- Release v0.4.0 por el flujo de Trusted Publishing existente; el README y la ficha de
  PyPI usan solo el lema del ADR 0001.
- El spike no toca `src/`; sus notas van a `docs/research/`.
- Mantenimiento: bajo hasta la semana 6. El MVP de `[contexts]` añadiría una tabla de
  configuración y una regla nueva (medio).
- Contactar con equipos lo hace el mantenedor; unskein no contacta a nadie.
- Oportunidad pendiente de evaluar: emitir el corte LAZY como `lazy import` en
  proyectos que exigen Python ≥3.15.
