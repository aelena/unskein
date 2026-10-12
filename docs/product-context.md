# Contexto de producto: unskein
Última revisión: 2026-10-12

## Qué es
CLI open source (MIT) de análisis estático de imports en Python a nivel módulo:
grafo, acoplamiento Ca/Ce, ciclos al importar, plan de cortes (`untangle`) y
comprobación de cortes sobre una copia (`--prove`). — [leído de CLAUDE.md, 2026-10-12]

## Estado actual
v0.3.0 publicada (alpha); `develop` con `untangle --prove`, API leaks, star imports,
módulos nativos. Sin salida JSON; `[contexts]` solo propuesto. — [leído de CHANGELOG
y memoria del proyecto, 2026-10-12]

## Usuario objetivo y problema
Equipos con un monolito que quieren desacoplarlo, strangularlo, crear microservicios
o modernizarlo. — [dicho por el developer, 2026-10-12]

## Diferenciación buscada
Verificar fronteras que el humano declara, no descubrirlas; cortes concretos
comprobados; offline, gratis. — [pivote 2026-10-11 en memoria; lema pendiente de decidir]

## Principios del proyecto
No negociables (marcados por el developer): ninguno marcado (confirmado por el developer, 2026-10-12).
Declarados, no marcados: separación grafo determinista / IA; cero telemetría;
offline; LiteLLM sin SDKs de proveedores; `--prove` nunca toca el proyecto
— [leído de CLAUDE.md, 2026-10-12]

## Restricciones
Único mantenedor, presupuesto propio, sin límites de empleador ni de propiedad
intelectual. — [dicho por el developer, 2026-10-12]

## Éxito (6 y 12 meses)
Un caso real. — [dicho por el developer, 2026-10-12; horizonte no precisado]

## Suposiciones abiertas
- Qué exigiría ese caso real (JSON, CI, Django) no está contrastado con ningún equipo.
- Horizonte (6 o 12 meses) del caso real no indicado.
- Lo que unskein hace mejor que import-linter o Tach en proyectos distintos de litellm no está medido.
- Sonargraph/SonarQube Architecture: no verificado si ofrecen cortes comprobados para Python.

## Fuentes leídas
CLAUDE.md, README, CHANGELOG, docs/research/*, memoria del proyecto (rama develop, 2026-10-12);
informes de investigación de import-linter, Tach, Sonargraph/Structure101 y CAST de esta sesión.
