#!/usr/bin/env python3
"""Gera as figuras do lab multidominio/flex-algo-anycast em variante clara e escura.

Mesma paleta e tipografia das figuras do lab inter-as/bgp-lu. Topologia, custos
e pilhas estao descritos nas tabelas NODES, LINKS e WIRE abaixo: ao mudar o lab,
edite-as e gere de novo.

Uso, a partir da raiz do repositorio:
    python3 labs/cisco/sr-mpls/multidominio/diagrams/gerar-figuras.py \
        labs/cisco/sr-mpls/multidominio/flex-algo-anycast/images
"""
import math
import pathlib
import sys

SANS = "Inter,'Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','DejaVu Sans Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

LIGHT = dict(
    bg="#ffffff", bg_stroke="#dde8ec", panel="#f4f8fa", panel_stroke="#c6dae2",
    card="#ffffff", card_stroke="#d4e1e7", ink="#0e2430", muted="#55707c",
    faint="#8ba2ad", green="#0a7f5c", amber="#a2660a", red="#bd2f56",
    blue="#2b6a93", rule="#e4edf0",
)
DARK = dict(
    bg="#0b1820", bg_stroke="#1d3542", panel="#10222c", panel_stroke="#254554",
    card="#14262f", card_stroke="#2c4857", ink="#e8f2f6", muted="#9db4be",
    faint="#6d8896", green="#42cf9a", amber="#f0b352", red="#ff7592",
    blue="#75b8e8", rule="#1c333f",
)


class Svg:
    def __init__(self, w, h, title, desc, p):
        self.w, self.h, self.p = w, h, p
        self.out = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="titulo descricao" font-family="{SANS}">',
            f'<title id="titulo">{title}</title>',
            f'<desc id="descricao">{desc}</desc>',
            f'<rect width="{w}" height="{h}" rx="18" fill="{p["bg"]}" stroke="{p["bg_stroke"]}"/>',
        ]

    def add(self, s):
        self.out.append(s)

    def text(self, x, y, s, size=12, fill=None, weight=None, anchor="start", mono=False,
             spacing=None, opacity=None):
        fill = fill or self.p["ink"]
        attrs = [f'x="{x:g}"', f'y="{y:g}"', f'font-family="{MONO if mono else SANS}"',
                 f'font-size="{size}"', f'fill="{fill}"']
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if spacing:
            attrs.append(f'letter-spacing="{spacing}"')
        if opacity:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<text {" ".join(attrs)}>{s}</text>')

    def rect(self, x, y, w, h, rx=10, fill=None, stroke=None, sw=1, dash=None, opacity=None):
        a = f'x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" fill="{fill or "none"}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(f"<rect {a}/>")

    def line(self, x1, y1, x2, y2, color, sw=4.5, dash=None, opacity=None, cap="round"):
        a = (f'x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{color}" '
             f'stroke-width="{sw}" stroke-linecap="{cap}"')
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(f"<line {a}/>")

    def badge(self, x, y, s, color):
        self.add(f'<circle cx="{x:g}" cy="{y:g}" r="13.5" fill="{self.p["card"]}" '
                 f'stroke="{color}" stroke-width="1.6"/>')
        self.text(x, y + 4, s, size=11.5, fill=color, weight=700, anchor="middle")

    def header(self, kicker, title, right):
        self.text(57, 44, kicker, size=10.5, fill=self.p["faint"], weight=700, spacing=1.7)
        self.text(57, 78, title, size=25, weight=700, spacing=-0.4)
        self.text(self.w - 57, 78, right, size=12.5, fill=self.p["muted"], anchor="end")

    def save(self, path):
        path.write_text("\n".join(self.out + ["</svg>"]) + "\n")


# ---------------------------------------------------------------------------
# Figura 1 - topologia
# ---------------------------------------------------------------------------

NODES = {
    # nome: (x, y, papel, linha 3, cor do papel)
    "pe1": (180, 400, "PE · HEADEND", "10.1.255.1", "blue"),
    "p1": (450, 255, "P", "10.1.255.2", "muted"),
    "p2": (450, 545, "P", "10.1.255.3", "muted"),
    "dbr-ab1": (700, 255, "DBR · A + B", "anycast 10.255.12.12", "green"),
    "dbr-ab2": (700, 545, "DBR · A + B", "anycast 10.255.12.12", "green"),
    "dbr-bc1": (1200, 255, "DBR · B + C", "anycast 10.255.23.23", "amber"),
    "dbr-bc2": (1200, 545, "DBR · B + C", "anycast 10.255.23.23", "amber"),
    "p3": (1450, 255, "P", "10.3.255.3", "muted"),
    "p4": (1450, 545, "P", "10.3.255.4", "muted"),
    "pe9": (1720, 400, "PE · ENDPOINT", "10.3.255.9", "blue"),
}

# (a, b, custo, red, deslocamento x para enlaces verticais paralelos, t do badge)
LINKS = [
    ("pe1", "p1", 10, False, 0, 0.5),
    ("pe1", "p2", 5, True, 0, 0.5),
    ("p1", "p2", 10, False, 0, 0.5),
    ("p1", "dbr-ab1", 10, False, 0, 0.5),
    ("p2", "dbr-ab2", 10, False, 0, 0.5),
    ("dbr-ab1", "dbr-bc1", 20, False, 0, 0.5),
    ("dbr-ab1", "dbr-bc2", 5, True, 0, 0.3),
    ("dbr-ab2", "dbr-bc1", 20, False, 0, 0.3),
    ("dbr-ab2", "dbr-bc2", 10, False, 0, 0.5),
    ("dbr-ab1", "dbr-ab2", 30, False, 60, 0.5),
    ("dbr-bc1", "dbr-bc2", 30, False, -60, 0.5),
    ("dbr-bc1", "p3", 10, False, 0, 0.5),
    ("dbr-bc2", "p4", 5, False, 0, 0.5),
    ("dbr-bc1", "dbr-bc2", 5, False, 60, 0.5),
    ("p3", "p4", 10, False, 0, 0.5),
    ("p3", "pe9", 10, False, 0, 0.5),
    ("p4", "pe9", 5, True, 0, 0.5),
]

POLICY_PATH = ["pe1", "p1", "dbr-ab1", "dbr-bc1", "p3", "pe9"]


def node_box(s, name):
    p = s.p
    x, y, role, sub, color = NODES[name]
    dbr = name.startswith("dbr")
    w, h = (196, 78) if dbr else (156, 70)
    s.add("<g>")
    s.rect(x - w / 2, y - h / 2, w, h, rx=13, fill=p["card"], stroke=p[color], sw=1.6)
    s.text(x, y - h / 2 + 20, role, size=9, fill=p[color], weight=700, anchor="middle", spacing=0.75)
    s.text(x, y - h / 2 + 41, name, size=15, weight=700, anchor="middle", mono=True)
    s.text(x, y - h / 2 + 59, sub, size=10.5, fill=p["muted"], anchor="middle", mono=True)
    s.add("</g>")


def topology(p):
    s = Svg(1900, 880, "Topologia lógica do laboratório multidomínio OSPF com Flex-Algo",
            "Três domínios OSPF independentes, A, B e C. DBR-AB1 e DBR-AB2 pertencem a A e B; "
            "DBR-BC1 e DBR-BC2 pertencem a B e C. Em cada domínio um enlace red mais barato atrai "
            "o SPF default e é excluído pelo Flex-Algo 128. A SR Policy de PE1 segue PE1, P1, "
            "DBR-AB1, DBR-BC1, P3 e PE9.", p)
    s.header("FIGURA 1 · SR-MPLS MULTIDOMÍNIO", "Topologia lógica",
             "três processos OSPF · DBRs compartilhados · Flex-Algo 128 exclui red")

    panels = [
        (40, 690, "Domínio A", "OSPF 100 · área 0 · 10.1.0.0/16"),
        (710, 1190, "Domínio B", "OSPF 200 · área 0 · 10.2.0.0/16"),
        (1210, 1860, "Domínio C", "OSPF 300 · área 0 · 10.3.0.0/16"),
    ]
    for x1, x2, name, sub in panels:
        s.rect(x1, 112, x2 - x1, 560, rx=20, fill=p["panel"], stroke=p["panel_stroke"], sw=1.5,
               dash="8 7")
        cx = (x1 + x2) / 2
        s.text(cx, 150, name, size=17, weight=700, anchor="middle")
        s.text(cx, 172, sub, size=12, fill=p["muted"], anchor="middle")

    for bx, label in ((700, "fronteira AB"), (1200, "fronteira BC")):
        s.line(bx, 120, bx, 664, p["faint"], sw=1.5, dash="4 8", opacity=0.6)
        s.rect(bx - 52, 640, 104, 22, rx=11, fill=p["card"], stroke=p["card_stroke"])
        s.text(bx, 655, label, size=10.5, fill=p["muted"], weight=700, anchor="middle")

    def ends(a, b, dx):
        ax, ay = NODES[a][:2]
        bx, by = NODES[b][:2]
        return ax + dx, ay, bx + dx, by

    # caminho da policy por baixo de tudo
    for a, b in zip(POLICY_PATH, POLICY_PATH[1:]):
        x1, y1, x2, y2 = ends(a, b, 0)
        s.line(x1, y1, x2, y2, p["blue"], sw=22, opacity=0.22)

    for a, b, cost, red, dx, t in LINKS:
        x1, y1, x2, y2 = ends(a, b, dx)
        color = p["red"] if red else p["green"]
        s.line(x1, y1, x2, y2, color, dash="9 7" if red else None)

    for name in NODES:
        node_box(s, name)

    for a, b, cost, red, dx, t in LINKS:
        x1, y1, x2, y2 = ends(a, b, dx)
        s.badge(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, str(cost), p["red"] if red else p["green"])

    # legenda
    ly = 712
    s.line(60, ly, 110, ly, p["green"])
    s.text(122, ly + 4, "enlace limpo · custo OSPF no círculo, igual nos dois lados", size=12,
           fill=p["muted"])
    s.line(560, ly, 610, ly, p["red"], dash="9 7")
    s.text(622, ly + 4, "afinidade red · mais barato, atrai o SPF default · excluído pelo Algo 128",
           size=12, fill=p["muted"])
    s.line(1170, ly, 1220, ly, p["blue"], sw=22, opacity=0.22, cap="butt")
    s.text(1232, ly + 4, "caminho da SR Policy color 128 · pilha 17120 / 17230 / 17309", size=12,
           fill=p["muted"])

    rows = [
        ("green", "Anycast AB", "10.255.12.12/32 · index 1120 · label 17120 · DBR-AB1 e DBR-AB2, "
                                "anunciado em OSPF 100 e OSPF 200"),
        ("amber", "Anycast BC", "10.255.23.23/32 · index 1230 · label 17230 · DBR-BC1 e DBR-BC2, "
                                "anunciado em OSPF 200 e OSPF 300"),
        ("blue", "Node-SID PE9", "10.3.255.9/32 · index 1309 · label 17309 · só no domínio C"),
    ]
    for i, (c, k, v) in enumerate(rows):
        y = 768 + i * 30
        s.rect(60, y - 13, 112, 20, rx=10, fill=p[c], opacity=0.14)
        s.text(116, y + 1, k, size=10.5, fill=p[c], weight=700, anchor="middle")
        s.text(186, y + 1, v, size=12, fill=p["muted"], mono=True)
    return s


# ---------------------------------------------------------------------------
# Figura 2 - pilha salto a salto e o caso maligno
# ---------------------------------------------------------------------------

HOPS = ["pe1", "p1", "dbr-ab1", "dbr-bc1", "p3", "pe9"]
HOP_X = [170 + i * 312 for i in range(6)]
SEG_COLOR = {"17120": "green", "17230": "amber", "17309": "blue"}
# pilha no fio entre o salto i e o i+1
WIRE = [
    ["17120", "17230", "17309"],
    ["17230", "17309"],
    ["17309"],
    ["17309"],
    [],
]
WHY = [
    "PE1 impõe a lista",
    "P1: PHP de 17120",
    "DBR-AB1: PHP de 17230",
    "DBR-BC1: swap 17309",
    "P3: PHP de 17309",
]


def hop_row(s, y, upto=None, fail_at=None):
    p = s.p
    last = len(HOPS) if upto is None else upto
    for i in range(last - 1):
        s.line(HOP_X[i] + 70, y, HOP_X[i + 1] - 70, y, p["faint"], sw=2.5)
    for i in range(last):
        name = HOPS[i]
        color = NODES[name][4]
        failed = fail_at == i
        s.rect(HOP_X[i] - 70, y - 26, 140, 52, rx=12, fill=p["card"],
               stroke=p["red"] if failed else p[color], sw=2 if failed else 1.6)
        s.text(HOP_X[i], y + 5, name, size=14.5, weight=700, anchor="middle", mono=True)


def stack(s, x, y, labels):
    p = s.p
    if not labels:
        s.rect(x - 52, y, 104, 28, rx=7, fill=p["card"], stroke=p["card_stroke"])
        s.text(x, y + 19, "IP", size=12, fill=p["muted"], weight=700, anchor="middle", mono=True)
        return
    for j, lab in enumerate(labels):
        c = p[SEG_COLOR[lab]]
        s.rect(x - 52, y + j * 32, 104, 28, rx=7, fill=c, opacity=0.16)
        s.rect(x - 52, y + j * 32, 104, 28, rx=7, stroke=c, sw=1.4)
        s.text(x, y + j * 32 + 19, lab, size=13, fill=c, weight=700, anchor="middle", mono=True)


def labels_fig(p):
    s = Svg(1900, 900, "Pilha de labels da SR Policy color 128, salto a salto",
            "Em cima, o caso normal: PE1 impõe 17120, 17230 e 17309; P1 remove 17120 por PHP, "
            "DBR-AB1 remove 17230 por PHP, DBR-BC1 encaminha 17309 e P3 o remove antes de PE9. "
            "Embaixo, o caso maligno: DBR-AB1 perdeu o domínio B, ainda atrai o anycast AB e "
            "descarta o pacote porque não tem entrada para 17230.", p)
    s.header("FIGURA 2 · SR POLICY COLOR 128", "A pilha no fio",
             "um segmento por domínio · o label só precisa existir onde vira topo")

    # faixas de domínio
    bands = [(0, 2, "Domínio A · 17120 resolve aqui", "green"),
             (2, 3, "Domínio B · 17230 resolve aqui", "amber"),
             (3, 5, "Domínio C · 17309 resolve aqui", "blue")]
    for a, b, label, c in bands:
        x1 = HOP_X[a] - 90 if a == 0 else HOP_X[a] + 4
        x2 = HOP_X[b] + 90 if b == 5 else HOP_X[b] - 4
        s.rect(x1, 112, x2 - x1, 30, rx=10, fill=p[c], opacity=0.12)
        s.text((x1 + x2) / 2, 132, label, size=12, fill=p[c], weight=700, anchor="middle")

    s.text(57, 190, "Caso normal", size=15, weight=700)
    s.text(57, 210, "traceroute sr-mpls policy name srte_c_128_ep_10.3.255.9", size=11.5,
           fill=p["muted"], mono=True)
    hop_row(s, 250)
    for i, labels in enumerate(WIRE):
        mx = (HOP_X[i] + HOP_X[i + 1]) / 2
        stack(s, mx, 292, labels)
        s.text(mx, 412, WHY[i], size=11.5, fill=p["muted"], anchor="middle")

    s.line(57, 450, 1843, 450, p["rule"], sw=1.5, cap="butt")

    s.text(57, 500, "Caso maligno · DBR-AB1 sem nenhum enlace no domínio B", size=15, weight=700,
           fill=p["red"])
    s.text(57, 520, "OSPF 100 continua FULL com P1 · OSPF 200 sem vizinhos", size=11.5,
           fill=p["muted"], mono=True)
    hop_row(s, 560, upto=3, fail_at=2)
    for i in range(2):
        mx = (HOP_X[i] + HOP_X[i + 1]) / 2
        stack(s, mx, 602, WIRE[i])
        s.text(mx, 722, WHY[i] if i else "PE1 ainda escolhe DBR-AB1", size=11.5, fill=p["muted"],
               anchor="middle")
    # X no DBR-AB1
    x, y = HOP_X[2], 560
    s.line(x + 90, y - 18, x + 126, y + 18, p["red"], sw=5)
    s.line(x + 90, y + 18, x + 126, y - 18, p["red"], sw=5)
    s.text(x + 146, y - 6, "sem entrada LFIB para 17230", size=13, fill=p["red"], weight=700)
    s.text(x + 146, y + 14, "N 2 10.1.0.7 MRU 0 [No Label]", size=12, fill=p["muted"], mono=True)

    notes = [
        "PE1 calcula o anycast AB só no domínio A: DBR-AB1 continua o contribuidor de menor métrica (21 contra 31).",
        "A policy segue Admin up / Operational up: o headend valida o primeiro SID, não a lista inteira.",
        "O anycast prova alcance da borda dentro do domínio local, não a capacidade de seguir para o próximo.",
    ]
    for i, n in enumerate(notes):
        y = 790 + i * 28
        s.add(f'<circle cx="66" cy="{y - 4}" r="3.5" fill="{p["red"]}"/>')
        s.text(80, y, n, size=12.5, fill=p["muted"])
    return s


def main():
    out = pathlib.Path(sys.argv[1])
    for suffix, pal in (("", LIGHT), ("-escuro", DARK)):
        topology(pal).save(out / f"topology-flex-algo-anycast{suffix}.svg")
        labels_fig(pal).save(out / f"diagram-pilha-anycast{suffix}.svg")
    print("ok")


if __name__ == "__main__":
    main()
