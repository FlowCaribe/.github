"""Build self-contained SVG artwork and both GitHub README entry points.

Python 3.10+, standard library only. No network calls, remote state or commits.
Original brand/portrait files are embedded byte for byte, never redrawn.
"""
from __future__ import annotations

import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile"
ASSETS = PROFILE / "assets"
CONFIG = json.loads((PROFILE / "profile.json").read_text(encoding="utf-8"))
C = CONFIG["colors"]
BODY = "Segoe UI,Arial,sans-serif"
DISPLAY = "Trebuchet MS,Segoe UI,Arial,sans-serif"


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, value, size=24, fill=None, weight=400, anchor="start", display=False):
    family = DISPLAY if display else BODY
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill or C["text"]}">{esc(value)}</text>')


def lines(x, y, values, size=24, step=34, **kwargs):
    return "".join(text(x, y + i * step, value, size, **kwargs) for i, value in enumerate(values))


def image(path, x, y, width, height, extra=""):
    data = (ASSETS / path).read_bytes()
    mime = "image/jpeg" if data.startswith(b"\xff\xd8") else "image/png"
    encoded = base64.b64encode(data).decode("ascii")
    return (f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
            f'preserveAspectRatio="xMidYMid meet" href="data:{mime};base64,{encoded}" {extra}/>')


def svg(width, height, title, description, content):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{esc(title)}</title>\n<desc id="desc">{esc(description)}</desc>\n'
            f'{content}\n</svg>\n')


def write(path, content):
    target = ASSETS / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")


def panel(w, h):
    return (f'<defs><linearGradient id="panel" x2="1" y2="1">'
            f'<stop stop-color="{C["raised"]}"/><stop offset="1" stop-color="{C["surface"]}"/>'
            f'</linearGradient></defs><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="20" '
            f'fill="url(#panel)" stroke="{C["line"]}"/>')


ICONS = {
    "code": '<path d="m8 7-5 5 5 5m8-10 5 5-5 5m-3-13-2 16"/>',
    "screen": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8m-4-4v4"/>',
    "data": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/>',
    "tools": '<path d="m14 4 6 6M5 21l-2-2L17 5l2 2ZM14 3l3-1 5 5-1 3M3 4l4-1 3 3-1 4M15 15l6 6"/>',
    "server": '<rect x="3" y="2" width="18" height="8" rx="2"/><rect x="3" y="14" width="18" height="8" rx="2"/><path d="M7 6h1m-1 12h1m5-12h4m-4 12h4"/>',
    "team": '<circle cx="8" cy="7" r="3"/><circle cx="18" cy="8" r="2"/><path d="M2 21v-4a6 6 0 0 1 12 0v4m3-7a5 5 0 0 1 5 5v2"/>',
    "crown": '<path d="m2 6 5 5 5-8 5 8 5-5-3 14H5Zm4 17h12"/>',
    "document": '<path d="M5 2h10l5 5v15H5ZM15 2v6h5M8 12h9m-9 4h9"/>',
    "branch": '<circle cx="6" cy="4" r="2"/><circle cx="18" cy="5" r="2"/><circle cx="6" cy="20" r="2"/><path d="M6 6v12m12-11v3c0 5-12 2-12 7"/>',
}


def icon(name, x, y, size=32, color=None):
    return (f'<g transform="translate({x} {y}) scale({size/24})" fill="none" '
            f'stroke="{color or C["primary"]}" stroke-width="1.65" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS[name]}</g>')


def palm(x, y, scale=1, flip=1):
    return (f'<g transform="translate({x} {y}) scale({scale*flip} {scale})" fill="#0A0814">'
            '<path d="M-8 224Q15 108 0 0L8-2Q29 115 6 224Z"/>'
            '<path d="M4 0Q-55-75-112-25Q-47-47 4 0ZM4 0Q-80-31-119 34Q-65-6 4 0Z'
            'M4 0Q-55 2-62 73Q-31 17 4 0ZM4 0Q26-76 90-46Q47-48 4 0Z'
            'M4 0Q78-50 115 14Q60-15 4 0ZM4 0Q71 0 71 66Q45 26 4 0Z"/></g>')


def skyline(w, horizon):
    out = f'<g fill="#100C1D" stroke="#362143" stroke-width="1">'
    shapes = [(0, 67, 108), (60, 44, 175), (95, 84, 130), (170, 53, 205),
              (217, 71, 151), (283, 40, 85), (w-292, 71, 160),
              (w-230, 45, 218), (w-188, 79, 136), (w-113, 58, 179), (w-60, 61, 111)]
    for x, bw, bh in shapes:
        out += f'<path d="M{x} {horizon}v-{bh}h{bw}v{bh}Z"/>'
        for row in range(3):
            out += f'<path d="M{x+10} {horizon-bh+22+row*23}h{max(10,bw-20)}" stroke="#79528F" opacity=".28"/>'
    return out + '</g>'


def hero(mobile=False):
    w, h = (600, 700) if mobile else (1200, 610)
    horizon = 460 if mobile else 399
    out = ('<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#0B0815"/>'
           '<stop offset=".56" stop-color="#28143E"/><stop offset="1" stop-color="#090710"/></linearGradient>'
           '<radialGradient id="halo"><stop stop-color="#8050C9" stop-opacity=".46"/>'
           '<stop offset="1" stop-color="#51258B" stop-opacity="0"/></radialGradient>'
           '<linearGradient id="horizon"><stop stop-color="#8050B0" stop-opacity="0"/>'
           '<stop offset=".5" stop-color="#B0D0E0" stop-opacity=".8"/>'
           '<stop offset="1" stop-color="#24D9FF" stop-opacity="0"/></linearGradient>'
           f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="24"/></clipPath></defs>')
    out += f'<g clip-path="url(#frame)"><rect width="{w}" height="{h}" fill="url(#sky)"/>'
    out += f'<ellipse cx="{w/2}" cy="{horizon-140}" rx="{w*.52}" ry="300" fill="url(#halo)"/>'
    out += f'<circle cx="{w/2}" cy="{horizon-120}" r="{185 if mobile else 210}" fill="none" stroke="#8A59AF" stroke-opacity=".19"/>'
    out += f'<circle cx="{w/2}" cy="{horizon-120}" r="{210 if mobile else 242}" fill="none" stroke="#8A59AF" stroke-opacity=".1"/>'
    out += skyline(w, horizon)
    out += f'<path d="M0 {horizon}H{w}" stroke="url(#horizon)" stroke-width="2"/>'
    for y in range(horizon+18, h, 27):
        out += f'<path d="M0 {y}H{w}" stroke="#A775EA" stroke-opacity=".035"/>'
    out += f'<path d="M0 {h} {w/2-55} {horizon}M{w} {h} {w/2+55} {horizon}" stroke="#684098" stroke-opacity=".3" fill="none"/>'
    out += palm(45 if mobile else 107, 250 if mobile else 208, .74 if mobile else .94)
    out += palm(w-26 if mobile else w-97, 279 if mobile else 228, .68 if mobile else .84, -1)
    out += text(w/2, 54, "FLOW CARIBE RP", 22 if mobile else 20, C["ice"], 700, "middle", True)
    if mobile:
        out += image("branding/flow-logo.png", 22, 56, 556, 556)
        out += text(w/2, 527, "FiveM Roleplay Community", 28, weight=600, anchor="middle")
        out += text(w/2, 572, CONFIG["tagline"], 22, C["muted"], anchor="middle")
        out += '<path d="M246 618h108" stroke="#A775EA" stroke-width="2"/>'
        out += text(w/2, 657, "Un proyecto. Un equipo. Una comunidad.", 18, C["ice"], anchor="middle")
    else:
        out += image("branding/flow-logo.png", 280, -47, 640, 640)
        out += text(w/2, 488, "FiveM Roleplay Community", 31, weight=600, anchor="middle")
        out += text(w/2, 531, CONFIG["tagline"], 24, C["muted"], anchor="middle")
        out += text(w/2, 580, "Un proyecto. Un equipo. Una comunidad.", 17, C["ice"], anchor="middle")
    out += f'</g><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="24" fill="none" stroke="{C["line"]}"/>'
    write(f'hero/{"mobile" if mobile else "desktop"}.svg', svg(w, h, CONFIG["name"],
          "Logo auténtico de Flow Caribe sobre una ciudad costera ilustrada. FiveM Roleplay Community. " + CONFIG["tagline"], out))


def developer(person, mobile=False):
    w, h = (288, 344) if mobile else (584, 330)
    avatar_size = 120 if mobile else 126
    x, y = (w-avatar_size)/2, 34
    out = panel(w, h)
    out += f'<defs><clipPath id="avatar"><rect x="{x}" y="{y}" width="{avatar_size}" height="{avatar_size}" rx="24"/></clipPath></defs>'
    out += f'<circle cx="{w/2}" cy="{y+avatar_size/2}" r="{avatar_size*.64}" fill="#30203F"/>'
    out += image(person["avatar"], x, y, avatar_size, avatar_size, 'clip-path="url(#avatar)"')
    out += f'<rect x="{x}" y="{y}" width="{avatar_size}" height="{avatar_size}" rx="24" fill="none" stroke="#A775EA" stroke-opacity=".6"/>'
    out += text(w/2, 211, person["name"], 35 if mobile else 34, weight=700, anchor="middle", display=True)
    out += text(w/2, 251, person["role"], 25 if mobile else 23, C["ice"], anchor="middle")
    out += text(w/2, 303, "@"+person["handle"], 21 if mobile else 20, C["muted"], anchor="middle")
    write(f'team/{person["slug"]}{"-mobile" if mobile else ""}.svg', svg(w, h, person["name"]+" · Developer",
          f'Avatar público auténtico de GitHub. {person["name"]}, integrante del equipo de desarrollo de Flow Caribe RP. GitHub: {person["handle"]}.', out))


def owner(mobile=False):
    w, h = (288, 320) if mobile else (584, 242)
    out = panel(w, h) + icon("crown", 28, 28, 35)
    out += text(28, 100 if mobile else 102, "Server Owner", 25 if mobile else 21, C["ice"])
    out += text(28, 163 if mobile else 153, CONFIG["owner"]["name"], 39 if mobile else 36, weight=700, display=True)
    if mobile:
        out += lines(28, 213, ["Dirección del", "proyecto"], 24, 29, fill=C["muted"])
    else:
        out += text(28, 202, "Dirección del proyecto", 20, C["muted"])
    if mobile:
        out += text(28, 287, "Instagram", 24, C["ice"])
    write(f'components/owner{"-mobile" if mobile else ""}.svg', svg(w, h, "bfgeezy · Server Owner",
          "bfgeezy, propietario de Flow Caribe RP. Abrir su perfil de Instagram.", out))


def hosting(mobile=False):
    w, h = (288, 320) if mobile else (584, 242)
    out = panel(w, h) + icon("server", 28, 28, 35)
    # The original dark-lettered provider logo stays unaltered on a light plate.
    out += f'<rect x="{100 if mobile else 365}" y="24" width="160" height="60" rx="8" fill="#FFFFFF"/>'
    out += image(CONFIG["hosting"]["logo"], 108 if mobile else 373, 29, 144, 49.5)
    out += text(28, 116 if mobile else 102, "Hosting", 25 if mobile else 21, C["ice"])
    if mobile:
        out += lines(28, 164, ["Master IT", "Support"], 33, 39, weight=700, display=True)
        out += lines(28, 253, ["Proveedor de", "infraestructura"], 24, 30, fill=C["muted"])
    else:
        out += text(28, 153, CONFIG["hosting"]["name"], 36, weight=700, display=True)
        out += text(28, 202, "Proveedor de infraestructura", 20, C["muted"])
    write(f'hosting/hosting{"-mobile" if mobile else ""}.svg', svg(w, h, "Master IT Support · Infrastructure & Hosting",
          "Master IT Support, proveedor de hosting de Flow Caribe RP. Logo auténtico. Abrir sitio oficial.", out))


def development(mobile=False):
    w, h = (600, 740) if mobile else (1200, 410)
    out = panel(w, h)
    out += text(32 if mobile else 42, 60, "El trabajo detrás del roleplay.", 31 if mobile else 34, weight=700, display=True)
    items = [("code", "FiveM", "Lua"), ("screen", "Web & NUI", "React · TypeScript"),
             ("data", "Datos", "mysql-async"), ("tools", "Herramientas", "Python"),
             ("server", "Infraestructura", "Master IT Support"), ("team", "Desarrollo", "OscarDev + Muek")]
    cols = 2 if mobile else 3
    for i, (symbol, name, detail) in enumerate(items):
        col, row = i % cols, i // cols
        cx = (150 + col*300) if mobile else (213 + col*387)
        top = (113 + row*202) if mobile else (111 + row*142)
        out += icon(symbol, cx-19, top, 38)
        out += text(cx, top+76, name, 27 if mobile else 25, weight=600, anchor="middle")
        out += text(cx, top+110, detail, 22 if mobile else 20, C["muted"], anchor="middle")
    write(f'components/development{"-mobile" if mobile else ""}.svg', svg(w, h, "Behind the experience",
          "Tecnologías observadas en repositorios públicos: FiveM y Lua, React y TypeScript, mysql-async y Python. No confirma su despliegue. Infraestructura: Master IT Support. Desarrollo: OscarDev y Muek.", out))


PROJECTS = [
    {"slug": "documents", "repo": "k5_documents", "language": "TypeScript", "icon": "document",
     "summary": ["Documentos para FiveM", "con interfaz NUI."], "upstream": "kac5a/k5_documents", "ref": "master"},
    {"slug": "weapons", "repo": "weapon_rebalancer", "language": "Python", "icon": "tools",
     "summary": ["Herramientas para revisar", "y ajustar archivos META."], "upstream": "Oscar-Dev0/weapon_rebalancer", "ref": "main"},
]


def project(item, mobile=False):
    w, h = (600, 286) if mobile else (1200, 210)
    out = panel(w, h)
    out += icon(item["icon"], 30, 31, 34)
    out += text(82, 56, item["repo"], 30 if mobile else 32, weight=700, display=True)
    out += text(30 if mobile else 858, 107 if mobile else 56, "Fork público · " + item["language"], 22 if mobile else 21, C["ice"])
    if mobile:
        out += lines(30, 155, item["summary"], 24, 33, fill=C["muted"])
        out += text(30, 244, "Origen: " + item["upstream"], 19, C["muted"])
    else:
        out += text(30, 110, " ".join(item["summary"]), 26, C["muted"])
        out += icon("branch", 30, 151, 22, C["muted"])
        out += text(66, 170, "Origen: " + item["upstream"], 20, C["muted"])
    write(f'components/project-{item["slug"]}{"-mobile" if mobile else ""}.svg', svg(w, h, item["repo"]+" · Fork público",
          f'{item["repo"]}, fork de {item["upstream"]}. {" ".join(item["summary"])} Lenguaje predominante: {item["language"]}.', out))


def finishing(mobile=False):
    w, h = (600, 270) if mobile else (1200, 226)
    out = panel(w, h)
    out += f'<path d="M0 {h-28}Q{w/4} {h-95} {w/2} {h-34}T{w} {h-28}" fill="none" stroke="#8550B0" stroke-opacity=".4"/>'
    out += text(w/2, 91 if mobile else 88, "FLOW CARIBE RP", 39 if mobile else 42, weight=700, anchor="middle", display=True)
    out += lines(w/2, 140, ["Powered by people,", "code and community."] if mobile else ["Powered by people, code and community."],
                 25 if mobile else 26, 35, fill=C["ice"], anchor="middle")
    write(f'components/footer{"-mobile" if mobile else ""}.svg', svg(w, h, "Flow Caribe RP",
          "Powered by people, code and community.", out))


def picture(prefix, desktop, mobile, alt, width="100%"):
    return (f'<picture><source media="(max-width: 600px)" srcset="{prefix}{mobile}" />'
            f'<img src="{prefix}{desktop}" width="{width}" alt="{esc(alt)}" /></picture>')


def linked(url, contents):
    return f'<a href="{esc(url)}">{contents}</a>'


def readme(prefix, docs):
    hero_img = picture(prefix, "hero/desktop.svg", "hero/mobile.svg", "Flow Caribe RP. FiveM Roleplay Community. " + CONFIG["tagline"])
    out = [f'<!-- Generated by scripts/build_profile.py. Edit profile/profile.json or the builder. -->\n\n<p align="center">\n  {linked(CONFIG["github"], hero_img)}\n</p>',
           '## ABOUT FLOW CARIBE RP\n\n**Flow Caribe RP** es un proyecto de FiveM que reúne comunidad, desarrollo y operación técnica alrededor de una experiencia de roleplay con identidad caribeña. El trabajo en equipo sostiene la evolución del servidor, sus sistemas personalizados y las experiencias que comparte la comunidad.',
           '## THE DEVELOPMENT TEAM\n\nDos desarrolladores, una misma visión para Flow Caribe RP.']
    cards = []
    for person in CONFIG["developers"]:
        name = person["slug"]
        cards.append(linked("https://github.com/"+person["handle"], picture(prefix, f"team/{name}.svg", f"team/{name}-mobile.svg",
                      f'{person["name"]} · Developer. Ver perfil de GitHub: {person["handle"]}.', "49%")))
    out.append('<p align="center">\n  ' + '\n  '.join(cards) + '\n</p>')
    out.append('## PROJECT & INFRASTRUCTURE')
    out.append('<p align="center">\n  ' + linked(CONFIG["owner"]["url"], picture(prefix, "components/owner.svg", "components/owner-mobile.svg",
               "bfgeezy · Server Owner. Dirección del proyecto. Ver Instagram.", "49%")) + '\n  ' + linked(CONFIG["hosting"]["url"], picture(prefix,
               "hosting/hosting.svg", "hosting/hosting-mobile.svg", "Master IT Support · Infrastructure & Hosting. Ver sitio oficial.", "49%")) + '\n</p>')
    out.append('## BEHIND THE EXPERIENCE')
    out.append('<p align="center">\n  ' + picture(prefix, "components/development.svg", "components/development-mobile.svg",
               "Repositorios públicos: FiveM y Lua; Web y NUI con React y TypeScript; datos con mysql-async; herramientas con Python. Hosting: Master IT Support. Desarrollo: OscarDev y Muek.") + '\n</p>')
    out.append('Las tecnologías mostradas se pueden consultar en el código público de `flowcariberp`. Describen esos repositorios y no constituyen un inventario de lo que está desplegado en el servidor.')
    out.append('<details>\n<summary>Consultar las referencias técnicas</summary>\n\n'
               '| Área | Evidencia pública |\n| :--- | :--- |\n'
               '| FiveM, Lua y datos | [`fxmanifest.lua`](https://github.com/flowcariberp/k5_documents/blob/master/fxmanifest.lua): GTA V, Lua 5.4 y mysql-async. |\n'
               '| Web & NUI | [`web/package.json`](https://github.com/flowcariberp/k5_documents/blob/master/web/package.json): React y TypeScript; interfaz NUI declarada en el manifiesto. |\n'
               '| Herramientas | [`weapon_rebalancer`](https://github.com/flowcariberp/weapon_rebalancer): utilidades para archivos META; Python es el lenguaje predominante. |\n\n</details>')
    out.append('## PUBLIC CODE\n\nUna selección del código disponible en [GitHub de Flow Caribe RP](' + CONFIG["github"] + '). Estos repositorios son **forks**; cada tarjeta reconoce su proyecto de origen.')
    for item in PROJECTS:
        slug = item["slug"]
        out.append('<p align="center">\n  ' + linked(CONFIG["github"]+'/'+item["repo"], picture(prefix, f'components/project-{slug}.svg',
                   f'components/project-{slug}-mobile.svg', f'{item["repo"]}. Fork de {item["upstream"]}. {" ".join(item["summary"])} Lenguaje predominante: {item["language"]}.')) + '\n</p>')
    out.append('## OUR ECOSYSTEM\n\n'
               '| Espacio | Enlace |\n| :--- | :--- |\n'
               f'| **Flow Caribe RP** | [GitHub · flowcariberp]({CONFIG["github"]}) |\n'
               f'| Organización de GitHub | [FlowCaribe]({CONFIG["organization"]}) |\n' +
               ''.join(f'| {p["name"]} · Developer | [GitHub · {p["handle"]}](https://github.com/{p["handle"]}) |\n' for p in CONFIG["developers"]) +
               f'| bfgeezy · Server Owner | [Instagram]({CONFIG["owner"]["url"]}) |\n'
               f'| Master IT Support · Hosting | [Sitio oficial]({CONFIG["hosting"]["url"]}) |')
    extra = {"discord": "Discord", "website": "Web oficial", "tiktok": "TikTok", "instagram": "Instagram del servidor",
             "documentation": "Documentación", "fivem": "Conexión FiveM"}
    for key, value in CONFIG["community"].items():
        if value:
            if not value.startswith("https://"):
                raise ValueError(f"community.{key} must be a verified HTTPS URL")
            out[-1] += f'\n| {extra[key]} | [{extra[key]}]({value}) |'
    out.append('<p align="center">\n  ' + picture(prefix, "components/footer.svg", "components/footer-mobile.svg",
               "Flow Caribe RP. Powered by people, code and community.") + '\n</p>')
    out.append(f'<!-- Branding, sources and deployment: {docs}maintenance.md -->')
    return '\n\n'.join(out) + '\n'


def main():
    for mobile in (False, True):
        hero(mobile)
        for person in CONFIG["developers"]:
            developer(person, mobile)
        owner(mobile)
        hosting(mobile)
        development(mobile)
        for item in PROJECTS:
            project(item, mobile)
        finishing(mobile)
    write("components/divider.svg", svg(1200, 24, "Separador", "Línea decorativa violeta y celeste.",
          '<defs><linearGradient id="line"><stop stop-color="#8550B0" stop-opacity="0"/><stop offset=".5" stop-color="#B0D0E0"/><stop offset="1" stop-color="#24D9FF" stop-opacity="0"/></linearGradient></defs><path d="M0 12h1200" stroke="url(#line)"/>'))
    (PROFILE / "README.md").write_text(readme("assets/", "docs/"), encoding="utf-8", newline="\n")
    (ROOT / "README.md").write_text(readme("profile/assets/", "profile/docs/"), encoding="utf-8", newline="\n")
    print("Built 19 SVG assets and 2 README entry points.")


if __name__ == "__main__":
    main()
