# Identidad visual de Flow Caribe RP

El logo original es el centro de la presentación. Se conserva byte por byte en `assets/branding/flow-logo.png` y se incorpora a los SVG sin recolorear, recortar ni redibujar. La fuente pública disponible mide **460 × 460 px** y ya contiene transparencia. No se ha localizado un archivo maestro de mayor resolución ni un SVG oficial; el banner vectorial no convierte el logo rasterizado en un original vectorial.

## Paleta

La paleta se apoya en el violeta y el celeste del logo auténtico. El celeste dominante observado se aproxima a `#B0D0E0`; los violetas, a `#8050B0` y `#6020A0`. Los tonos claros de interfaz son derivados para mantener contraste sobre fondos oscuros. El cian acompaña el contorno original, sin sustituirlo.

| Token | Color | Función |
| :--- | :--- | :--- |
| background | `#090710` | Fondo del hero y escena nocturna |
| surface | `#171125` | Tarjetas y fondos secundarios |
| raised | `#211831` | Inicio del degradado de las tarjetas |
| violet | `#8550B0` | Ambiente y detalles de marca |
| primary | `#A775EA` | Iconos, bordes y acentos claros |
| ice | `#B0D0E0` | Roles y texto secundario destacado |
| cyan | `#24D9FF` | Detalles discretos del horizonte |
| text | `#FFFFFF` | Títulos y nombres |
| muted | `#BFB3D1` | Descripciones y referencias |
| line | `#443154` | Bordes decorativos |

Los tokens editables están en `profile/profile.json`. Los colores propios de las marcas y retratos originales permanecen intactos.

## Tipografía y composición

- Títulos gráficos: `Trebuchet MS`, con alternativas `Segoe UI`, `Arial` y `sans-serif`. Cuerpo: `Segoe UI`, `Arial`, `sans-serif`. No se cargan fuentes externas.
- SVG de escritorio: lienzo base de 1200 px; las cards de Discord miden 960 × 440 px, con nombres de hasta 42 px, roles de 27 px y texto secundario de 23 px.
- SVG móvil: lienzo de 600 × 640 px para cada card de Discord. Se reorganizan nombre, usuario, roles y botón en una columna con tipografía de 22–42 px. Las tarjetas de dirección y hosting conservan su lienzo de 288 px.
- Espaciado gráfico habitual: 24, 28, 32 y 42 px. Radios: 20 px en tarjetas, 24 px en hero y retratos. Los tamaños se escalan con la imagen.
- Hero centrado, logo dominante, palmeras y silueta urbana originales dibujadas en SVG. El escenario es una ilustración ambiental; no representa una ubicación real o un mapa confirmado del servidor.
- OscarDev, Muek y Bifi comparten exactamente las mismas dimensiones, estilo y tipografía. OscarDev es Developer; Muek es Developer y Owner de Master IT Support; Bifi es Developer / Owner del servidor, según las correcciones del usuario. La propiedad del servidor y el hosting aparecen en tarjetas separadas. La tarjeta del proveedor identifica a Muek como su propietario.
- Iconos de línea hechos para estos componentes, con trazo de 1,65 unidades y extremos redondeados.

## Formatos y accesibilidad

Los 21 SVG son autocontenidos: PNG auténticos embebidos, degradados internos, texto nativo y geometría vectorial. No contienen JavaScript, `foreignObject`, CSS externo ni estadísticas remotas. La decoración de OscarDev es el APNG original de su tarjeta de referencia; se oculta cuando el visor solicita `prefers-reduced-motion: reduce`, dejando el retrato estático. Las otras composiciones no añaden movimiento. El separador queda disponible como recurso reutilizable.

Cada componente informativo tiene `title`, `desc` y texto alternativo en el README. Los enlaces principales también aparecen como texto en la tabla de ecosistema, para que la navegación no dependa exclusivamente de las imágenes. Las referencias técnicas quedan en un bloque desplegable.

El texto blanco, celeste y muted supera **4,5:1** sobre ambos extremos del fondo de las tarjetas. Los bordes y el horizonte son decorativos. El fondo oscuro forma parte de los SVG y permite conservar su identidad tanto en GitHub claro como oscuro.

Las imágenes se seleccionan con `<picture>` y `media="(max-width: 600px)"`. Las cards de Discord ocupan el 100 % de la anchura y se muestran una debajo de otra, cada una enlazada a su perfil. Tienen encabezado con banner auténtico o fondo de marca, retrato circular, nombre público, usuario, roles y botón visual «Abrir mi perfil». El enlace abarca la card completa. Las tarjetas de dirección y hosting ocupan un 49 % cada una. No se necesita CSS de usuario en GitHub.

Los logos y avatares pertenecen a sus titulares. El archivo `LICENSE` del repositorio no se interpreta como una cesión de los derechos sobre marcas o retratos de terceros. Su procedencia está registrada en [audit.md](audit.md).
