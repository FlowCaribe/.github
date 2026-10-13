# Mantenimiento y publicación

## Destino principal confirmado: flowcariberp

`flowcariberp` es una **cuenta personal**, según la API pública de GitHub. El usuario la confirmó como destino principal. Para mostrar la presentación en ese perfil, el repositorio público debe llamarse **`flowcariberp/flowcariberp`** y contener el **`README.md` raíz** generado aquí, junto con `profile/assets/`. Conviene trasladar también `profile/profile.json`, `profile/docs/`, `scripts/` y el workflow para mantener la fuente editable.

El remoto de este checkout es **`FlowCaribe/.github`** y la rama de implementación es **`codex/flow-caribe-profile`**. Subir esa rama al remoto permite revisar la versión de organización; para mostrarla en el perfil personal de `flowcariberp`, se deben trasladar los archivos al repositorio indicado arriba.

Se entrega también `profile/README.md`, que corresponde al perfil de una organización si se publica en su repositorio público `.github`. Ambas entradas tienen el mismo contenido, con rutas relativas adaptadas a su posición. `profile/README.md` por sí solo no aparecerá en el perfil personal de `flowcariberp`.

GitHub explica ambas convenciones en [perfiles personales](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme) y [perfiles de organizaciones](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/customizing-your-organizations-profile).

## Fuentes editables

| Archivo | Qué modificar |
| :--- | :--- |
| `profile/profile.json` | Participantes, destinos públicos, canales confirmados, colores |
| `scripts/build_profile.py` | Composición, textos de presentación, proyectos y referencias técnicas |
| `profile/assets/branding/flow-logo.png` | Reemplazar sólo por un original oficial confirmado |
| `profile/assets/team/` | Retratos auténticos de Discord guardados como PNG locales |
| `profile/discord-profiles.json` | Snapshot público de los nombres, IDs y fuentes de los avatares |
| `scripts/sync_discord_profiles.py` | Actualización manual de nombres de usuario y avatares de Discord |
| `profile/assets/hosting/master-it-support.png` | Original publicado por el proveedor |
| `profile/docs/audit.md` | Evidencia pública y limitaciones de verificación |

Los README y SVG son archivos generados. Editar las fuentes y ejecutar, desde la raíz del repositorio:

```powershell
python scripts/build_profile.py
python scripts/validate_profile.py
```

Ambos comandos usan Python 3.10 o posterior y sólo su biblioteca estándar. La generación es determinista: no consulta APIs, no toma fechas del sistema y no produce commits.

Para renovar los perfiles públicos de Discord antes de regenerar:

```powershell
python scripts/sync_discord_profiles.py --checked-on AAAA-MM-DD
python scripts/build_profile.py
python scripts/validate_profile.py
```

Sustituir `AAAA-MM-DD` por la fecha local de la consulta. La sincronización usa el servicio público de lookup empleado por el README de OscarDev; valida cada ID y descarga los PNG directamente de `cdn.discordapp.com`. No requiere tokens ni consulta mensajes, presencia o membresías. Si una consulta falla, no sustituye los datos anteriores. Los PNG quedan embebidos en los SVG: abrir el README no hace consultas al servicio de lookup.

Los nombres visibles y roles editoriales permanecen en `profile/profile.json`. Bifi conserva el nombre solicitado por el usuario, aunque su nombre global en Discord sea «PRESIDENTE BIFI». Muek tiene el rol principal Developer y la función adicional Owner de Master IT Support; `hosting.owner` mantiene la atribución en la tarjeta del proveedor. La sincronización no modifica estas funciones ni inventa cuentas de GitHub.

`community` contiene valores `null` para Discord, web, TikTok, Instagram del servidor, documentación y conexión FiveM. Añadir una URL HTTPS oficial confirmada y regenerar: aparecerá en el ecosistema. Los valores vacíos no crean botones ni enlaces de relleno.

Los proyectos públicos están definidos en `PROJECTS` en el generador. Antes de añadir o cambiar uno, comprobar que es público, su descripción, su lenguaje predominante y si es un fork. Los enlaces y textos derivados del código no certifican uso en producción. No incorporar información de repositorios privados.

## Validación automática

`.github/workflows/profile-check.yml` ejecuta la comprobación offline al cambiar los README, fuentes o assets en un push o pull request; también permite ejecución manual. Tiene sólo permiso `contents: read`, no modifica archivos ni crea commits.

La comprobación regenera los archivos y verifica que coincidan con las fuentes, además de validar rutas y fuentes responsive, XML/viewBox de SVG, metadatos accesibles, ausencia de scripts y dependencias externas en SVG, límite de 1 MiB por SVG y firmas PNG/JPEG. No garantiza que una web externa siga disponible ni reproduce el sanitizador de GitHub.

No se programa actualización de repositorios ni de avatares: la selección editorial y la ausencia de servicios de estadísticas mantienen el README estable.

## Revisión visual local

La comprobación visual opcional usa Node.js con `marked` y `playwright`. En esta sesión se utilizaron `marked 17.0.5` y `playwright 1.62.1`. El renderizado se hace localmente, sin subir el README a otra aplicación.

1. Instalar esas dependencias de desarrollo en el entorno de revisión y disponer de Chromium para Playwright.
2. Colocar la hoja pública [github-markdown.css](https://github.com/sindresorhus/github-markdown-css/blob/main/github-markdown.css) en `.preview/github-markdown.css`. Ese archivo es sólo para la previsualización.
3. Ejecutar `node scripts/preview_profile.cjs`. Si Chromium no está en la ruta predeterminada de Playwright, indicar su ruta con la variable `PROFILE_CHROMIUM_PATH`.
4. Inspeccionar las capturas y `.preview/qa.json`. Se revisan 1440, 900, 390 y 320 px, claro/oscuro, carga de imágenes, igualdad de las tarjetas y límites de texto en los SVG.

`.preview/` se excluye del control de versiones. El archivo HTML de esa carpeta permite abrir la vista local, con rutas relativas hacia los assets del repositorio. Esta aproximación utiliza GFM y una hoja de estilo de GitHub; el renderizado final en GitHub se confirma después de publicar con autorización.

## Resultado de la entrega

- Dos entradas README y 21 SVG estáticos, con cinco imágenes originales locales.
- Logo original transparente de 460 × 460 px; no se fabrica un maestro de mayor resolución ni un SVG del logotipo.
- Identidad centrada en Flow Caribe RP y tres tarjetas equivalentes con avatares y enlaces de Discord. Muek es Developer y propietario de Master IT Support; Bifi es Developer / Owner del servidor. El hosting conserva su rol diferenciado.
- Código público atribuido como forks, con referencias a tecnologías verificables y sin afirmaciones sobre despliegue.
- Enlaces de GitHub e Instagram comprobados con HTTP 200; el hosting fue accesible en navegador, pero bloquea algunas consultas HTTP automatizadas con 403.
- La generación y la validación no crean commits ni publican cambios. El commit y el push se realizan únicamente cuando el usuario los autoriza.
