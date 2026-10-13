# Personas e infraestructura

| Participante | Rol indicado por el equipo | Destino público |
| :--- | :--- | :--- |
| OscarDev | Developer | https://github.com/Oscar-Dev0 |
| Muek | Developer | https://github.com/iMuek |
| bfgeezy | Server Owner | https://www.instagram.com/bfgeezy |
| Master IT Support | Infrastructure & Hosting | https://masteritsupport.com/ |

La presentación reconoce a OscarDev y Muek con el mismo peso visual. No atribuye áreas exclusivas, jerarquías de liderazgo, propiedad ni autoría única. El retrato del propietario no se utiliza; su tarjeta contiene sólo su nombre, rol y enlace facilitados.

## Incorporar un desarrollador

1. Confirmar con el equipo su nombre público, rol y URL de GitHub.
2. Obtener su avatar auténtico y guardarlo en `profile/assets/team/` con una extensión correspondiente al formato real.
3. Añadir un objeto a `developers` en `profile/profile.json`, siguiendo los campos existentes: `name`, `handle`, `role`, `avatar` y `slug`. La ruta de avatar es relativa a `profile/assets/`; el slug debe ser único.
4. Ejecutar `python scripts/build_profile.py` y `python scripts/validate_profile.py`.
5. Revisar el conjunto en móvil y escritorio. Cada tarjeta conservará el mismo tratamiento visual; los nuevos integrantes se distribuyen en filas de dos.

Un cambio de función o proveedor debe confirmarse antes de actualizar la información pública. Para renovar retratos o logos, sustituir el archivo auténtico y regenerar los SVG; no hay sincronización automática ni commits programados.
