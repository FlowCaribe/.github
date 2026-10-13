# Auditoría de fuentes públicas

Fecha de comprobación: **12 de octubre de 2026**, America/Costa_Rica.
Alcance: perfiles, repositorios y recursos gráficos públicos. No se consultaron repositorios privados ni configuraciones del servidor.

## Identidad y destino del README

- [flowcariberp](https://github.com/flowcariberp) es un perfil de tipo **User**, según su [API pública](https://api.github.com/users/flowcariberp). Se mantiene como enlace del proyecto solicitado en el encargo.
- [FlowCaribe](https://github.com/FlowCaribe) es una **Organization**, según su [API pública](https://api.github.com/orgs/FlowCaribe), y es propietaria del remoto del repositorio local [FlowCaribe/.github](https://github.com/FlowCaribe/.github). El README de organización corresponde a `profile/README.md`.
- El usuario confirmó **flowcariberp** como destino principal. Para que aparezca en ese perfil personal, el archivo de entrada es el `README.md` raíz del repositorio público `flowcariberp/flowcariberp`; no el README de organización. Ambos archivos se generan desde la misma fuente.
- Las fuentes públicas consultadas no establecen por sí solas una relación formal entre ambos perfiles. No deben describirse como una única cuenta.
- En `main`, los repositorios públicos de la organización sólo aportaban `LICENSE` y, en [FlowCaribe/FlowCaribe](https://github.com/FlowCaribe/FlowCaribe), un README con el título «FlowCaribe». No proporcionaban evidencia de un stack desplegado.

## Procedencia de imágenes y roles

| Elemento | Fuente y comprobación |
| --- | --- |
| Logo de Flow Caribe | [Avatar publicado por la organización](https://avatars.githubusercontent.com/u/209276971?v=4), identificado por la API. Copia en `assets/branding/flow-logo.png`: PNG original de 460 × 460 píxeles, con canal alfa. No se redibuja ni se presenta como un original vectorial. |
| Avatar de flowcariberp | [Imagen publicada por el perfil](https://avatars.githubusercontent.com/u/211046857?v=4): es un identicon de GitHub, por lo que no se utiliza como logo del servidor. |
| OscarDev y Muek | GitHub: [Oscar-Dev0](https://github.com/Oscar-Dev0) e [iMuek](https://github.com/iMuek). Sus tarjetas utilizan ahora los avatares auténticos de Discord y enlazan a los IDs facilitados por el usuario. El rol equivalente **Developer** procede del encargo. |
| Bifi | El usuario lo incorporó al equipo con rol **Developer / Owner** y facilitó su ID de Discord. El nombre visible «Bifi» procede de esa instrucción; no se deduce un cargo del apodo global de Discord. La sección de dirección conserva el [enlace de Instagram](https://www.instagram.com/bfgeezy) del encargo; no se inventa una cuenta GitHub de Bifi. |
| Master IT Support | Logo observado en el encabezado y pie de la [web oficial](https://masteritsupport.com/), con texto alternativo «Master IT Support»: [PNG original, 160 × 55 píxeles](https://masteritsupport.com/templates/lagom2/assets/img/logo/logo_big.839953647.png). Su papel como proveedor de hosting de Flow Caribe procede del encargo; la web pública no verifica ese acuerdo. |

## Repositorios y tecnologías verificables

Los [repositorios públicos de flowcariberp](https://api.github.com/users/flowcariberp/repos?type=owner&per_page=100) son **forks**. Su presencia no demuestra autoría íntegra, uso en producción ni el stack actual del servidor.

| Repositorio | Origen y referencia comprobada | Lenguaje predominante |
| --- | --- | --- |
| [k5_documents](https://github.com/flowcariberp/k5_documents) | Fork de `kac5a/k5_documents`; [`master` en 7f71cc2](https://github.com/flowcariberp/k5_documents/tree/7f71cc21982f6ede6f35ffba277e4a7246f7ccf4). | **TypeScript**, 67.829 bytes en la [API de lenguajes](https://api.github.com/repos/flowcariberp/k5_documents/languages). El campo general `language` del repositorio devuelve `null`. |
| [weapon_rebalancer](https://github.com/flowcariberp/weapon_rebalancer) | Fork de `Oscar-Dev0/weapon_rebalancer`; [`main` en 95c1541](https://github.com/flowcariberp/weapon_rebalancer/tree/95c15415a5862f088e3be1198c485b4cc8f2d106). | **Python**, corroborado por los metadatos y 797.683 bytes en la [API de lenguajes](https://api.github.com/repos/flowcariberp/weapon_rebalancer/languages). |

El [manifiesto de k5_documents](https://github.com/flowcariberp/k5_documents/blob/7f71cc21982f6ede6f35ffba277e4a7246f7ccf4/fxmanifest.lua) declara FiveM/GTA5, Lua 5.4, una interfaz NUI y `mysql-async`. Su [package.json](https://github.com/flowcariberp/k5_documents/blob/7f71cc21982f6ede6f35ffba277e4a7246f7ccf4/web/package.json) declara React, TypeScript, Material UI y CRACO. Estas afirmaciones se limitan al código público revisado.

No se deducen cifras de jugadores, disponibilidad, recursos instalados, especificaciones del hosting, cargos adicionales ni canales comunitarios. Los enlaces futuros deben incorporarse sólo cuando el equipo proporcione sus URLs oficiales.

## Comprobación de enlaces

Los dos perfiles del proyecto, ambos desarrolladores, ambos forks y sus dos referencias técnicas respondieron HTTP 200 al comprobarlos. Instagram respondió HTTP 200; su contenido y la propiedad del perfil no quedan certificados por esa respuesta. Master IT Support fue accesible en navegador durante la auditoría; la consulta HTTP automatizada posterior respondió 403 por su protección de acceso. El archivo de su logo se descargó correctamente del dominio oficial.

La validación del README final se realiza localmente. La API de Markdown de GitHub no se utilizó: la revisión automática de permisos rechazó enviar contenido todavía no publicado. La compatibilidad final del renderizador de GitHub debe confirmarse después de la publicación autorizada.

## Actualización del equipo desde Discord

El usuario facilitó los tres IDs y pidió utilizar sus perfiles de Discord, con los tres como desarrolladores y Bifi también como propietario. Se consultó el mismo servicio público de lookup que utiliza el [sincronizador del README de referencia](https://github.com/Oscar-Dev0/Oscar-Dev0/blob/main/scripts/update_discord.py). El servicio es de terceros; los avatares se descargan del CDN oficial de Discord después de comprobar que el ID devuelto coincide.

| Miembro | ID confirmado en la respuesta | Usuario público | Nombre global consultado | Fuente |
| :--- | :--- | :--- | :--- | :--- |
| OscarDev | `518251720128856084` | `oscar_dev` | OscarDev | [Consulta pública](https://www.vibebot.gg/api/tools/avatar-lookup?id=518251720128856084) |
| Muek | `193858356052623360` | `muek` | Muek | [Consulta pública](https://www.vibebot.gg/api/tools/avatar-lookup?id=193858356052623360) |
| Bifi | `1234631585727254582` | `bfbifi` | PRESIDENTE BIFI | [Consulta pública](https://www.vibebot.gg/api/tools/avatar-lookup?id=1234631585727254582) |

`profile/discord-profiles.json` registra la fecha local indicada, los datos públicos seleccionados y las URLs originales de los PNG. No se obtienen ni publican mensajes, presencia, membresías o credenciales. El avatar asociado a una cuenta no identifica físicamente a las personas que aparezcan en su imagen. Los roles de Flow Caribe RP proceden de las instrucciones del usuario.
