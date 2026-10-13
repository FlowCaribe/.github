# Personas e infraestructura

| Participante | Rol indicado por el equipo | Destino público |
| :--- | :--- | :--- |
| OscarDev | Developer | [Discord · @oscar_dev](https://discord.com/users/518251720128856084) · [GitHub](https://github.com/Oscar-Dev0) |
| Muek | Developer · Owner de Master IT Support | [Discord · @muek](https://discord.com/users/193858356052623360) · [GitHub](https://github.com/iMuek) |
| Bifi | Developer / Owner | [Discord · @bfbifi](https://discord.com/users/1234631585727254582) |
| Master IT Support | Infrastructure & Hosting | https://masteritsupport.com/ |

La presentación reconoce a los tres con el mismo peso visual y con sus avatares originales de Discord. El usuario confirmó que Muek es desarrollador de Flow Caribe RP y propietario de **Master IT Support**; su tarjeta y la tarjeta del proveedor identifican la empresa de la que es dueño. Bifi forma parte del equipo de desarrollo y es propietario del servidor; por eso aparece como **Developer / Owner**. El nombre visible «Bifi» procede del usuario; su nombre público de Discord en la consulta era «PRESIDENTE BIFI». No se atribuyen especialidades exclusivas ni autoría única.

La sección de dirección mantiene el enlace de Instagram `bfgeezy` facilitado en el encargo original. No se ha inventado un GitHub de Bifi. Los perfiles de Discord son enlaces personales, no invitaciones al servidor.

## Incorporar un desarrollador

1. Confirmar con el equipo su nombre público, rol e ID de Discord; su GitHub es opcional.
2. Añadir un objeto a `developers` en `profile/profile.json`, siguiendo los campos existentes: `name`, `handle`, `role`, `avatar`, `slug`, `discord_id` y `discord_username`. Usar `null` en `handle` cuando no haya un GitHub confirmado. La ruta de avatar es relativa a `profile/assets/`; el slug debe ser único.
3. Ejecutar `python scripts/sync_discord_profiles.py --checked-on AAAA-MM-DD` con la fecha local de la consulta. Se guardan los nombres públicos y PNG originales después de validar los IDs y el CDN de Discord.
4. Ejecutar `python scripts/build_profile.py` y `python scripts/validate_profile.py`.
5. Revisar el conjunto en móvil y escritorio. Tres integrantes ocupan una fila de tarjetas iguales; sus versiones móviles adaptan la tipografía. Los campos opcionales `secondary_role` y `secondary_role_mobile` permiten indicar una función adicional con su entidad correspondiente.

Un cambio de función o proveedor debe confirmarse antes de actualizar la información pública. Para renovar los retratos de Discord, ejecutar la sincronización manual y regenerar los SVG; no hay sincronización automática ni commits programados. Los roles del proyecto y nombres editoriales permanecen bajo control del equipo, no se deducen de apodos ni de datos de Discord.
