"""Builds the artwork for the profile README.

Run:  pip install fonttools uharfbuzz  &&  python tools/build_assets.py

Every piece of text is converted to vector outlines. GitHub shows README SVGs
through an <img> tag, which cannot load web fonts, so outlines are the only way
to get the same typography on every machine.

Each asset is written twice (light and dark) with a transparent background, so
it sits directly on the GitHub page in either theme. To change what the
profile says, edit LEDGER, STACK or the strip functions below and run again.
"""
import os
import urllib.request
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
import uharfbuzz as hb

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
OUT = os.path.join(HERE, "..", "assets")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# Both typefaces are open source (SIL Open Font License). They are fetched once
# and cached rather than committed, since only their outlines end up in the SVGs.
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONT_URLS = {
    "BricolageGrotesque.ttf": GF + "bricolagegrotesque/BricolageGrotesque%5Bopsz%2Cwdth%2Cwght%5D.ttf",
    "MartianMono.ttf": GF + "martianmono/MartianMono%5Bwdth%2Cwght%5D.ttf",
}
for _name, _url in FONT_URLS.items():
    _path = os.path.join(CACHE, _name)
    if not os.path.exists(_path):
        urllib.request.urlretrieve(_url, _path)

W = 880  # close to the README column width on desktop, so type renders near 1:1

THEMES = {
    "dark": dict(ink="#E6EDF3", muted="#9198A1", rule="#3D444D", soft="#151B23",
                 ok="#3DD68C", warn="#F2B544", stop="#FF6B5E"),
    "light": dict(ink="#1F2328", muted="#59636E", rule="#D1D9E0", soft="#F6F8FA",
                  ok="#0B8457", warn="#9A6700", stop="#C8362B"),
}


class Face:
    """One static instance of a variable font, shaped with HarfBuzz."""

    def __init__(self, key, file, **axes):
        self.key = key
        path = os.path.join(CACHE, key + ".ttf")
        tt = instancer.instantiateVariableFont(TTFont(os.path.join(CACHE, file)), axes)
        tt.save(path)
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet()
        self.upm = self.tt["head"].unitsPerEm
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(path)))

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset)
                for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


FACES = {
    "D": Face("D", "BricolageGrotesque.ttf", opsz=96, wdth=82, wght=800),   # name
    "H": Face("H", "BricolageGrotesque.ttf", opsz=40, wdth=90, wght=700),   # project titles
    "L": Face("L", "BricolageGrotesque.ttf", opsz=24, wdth=100, wght=500),  # tagline
    "B": Face("B", "BricolageGrotesque.ttf", opsz=14, wdth=100, wght=420),  # prose
    "S": Face("S", "BricolageGrotesque.ttf", opsz=14, wdth=100, wght=680),  # prose, strong
    "M": Face("M", "MartianMono.ttf", wdth=80, wght=400),                 # ledger data
    "N": Face("N", "MartianMono.ttf", wdth=80, wght=640),                 # ledger data, strong
}


class Svg:
    def __init__(self, h, theme, title, desc, css=""):
        self.h, self.t = h, THEMES[theme]
        self.title, self.desc, self.css = title, desc, css
        self.defs, self.used, self.body = [], set(), []

    def width(self, face, text, size, track=0.0):
        f = FACES[face]
        s = size / f.upm
        return sum(a for _, a, _, _ in f.shape(text)) * s + track * size * len(text)

    def text(self, face, text, x, y, size, color="ink", anchor="start", track=0.0, cls=None):
        f = FACES[face]
        s = size / f.upm
        if anchor != "start":
            w = self.width(face, text, size, track)
            x -= w if anchor == "end" else w / 2
        pen_x, uses = 0.0, []
        for gid, adv, xo, yo in f.shape(text):
            gname = f.tt.getGlyphName(gid)
            ref = f"{f.key}{gid}"
            if ref not in self.used:
                pen = SVGPathPen(f.gs, ntos=lambda v: str(int(round(v))))
                f.gs[gname].draw(pen)
                d = pen.getCommands()
                self.used.add(ref)
                if d:
                    self.defs.append(f'<path id="{ref}" d="{d}"/>')
                else:
                    self.defs.append(f'<path id="{ref}" d=""/>')
            if gname != "space":
                gx = pen_x + xo
                uses.append(f'<use href="#{ref}" x="{gx:.0f}"' + (f' y="{yo}"' if yo else "") + "/>")
            pen_x += adv + track * f.upm
        fill = self.t.get(color, color)
        c = f' class="{cls}"' if cls else ""
        self.body.append(
            f'<g{c} fill="{fill}" transform="translate({x:.1f} {y:.1f}) scale({s:.5f} {-s:.5f})">'
            + "".join(uses) + "</g>")
        return pen_x * s

    def raw(self, s):
        self.body.append(s)

    def line(self, x1, y1, x2, y2, color="rule", w=1, dash=None, cls=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        c = f' class="{cls}"' if cls else ""
        self.raw(f'<path{c} d="M{x1} {y1}L{x2} {y2}" stroke="{self.t.get(color, color)}" '
                 f'stroke-width="{w}" fill="none" stroke-linecap="round"{d}/>')

    def rect(self, x, y, w, h, r=0, fill="soft", stroke=None):
        st = f' stroke="{self.t.get(stroke, stroke)}"' if stroke else ""
        self.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
                 f'fill="{self.t.get(fill, fill)}"{st}/>')

    def dot(self, cx, cy, r, color, hollow=False, cls=None):
        c = f' class="{cls}"' if cls else ""
        col = self.t.get(color, color)
        if hollow:
            self.raw(f'<circle{c} cx="{cx}" cy="{cy}" r="{r - 0.75}" fill="none" stroke="{col}" stroke-width="1.5"/>')
        else:
            self.raw(f'<circle{c} cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>')

    def save(self, name):
        style = f"<style>{self.css}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>" if self.css else ""
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {self.h}" width="{W}" height="{self.h}" '
               f'role="img" aria-labelledby="t d"><title id="t">{self.title}</title><desc id="d">{self.desc}</desc>'
               f'{style}<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')
        with open(os.path.join(OUT, name), "w") as fh:
            fh.write(svg)
        return len(svg)


# ---------------------------------------------------------------- hero

LEDGER = [
    # when, project, built for, outcome, verdict colour
    ("Nov 2026", "AsOf", "IBM Db2Hack 2026", "0 of 65 wrong drafts released, blind sets", "ok"),
    ("Oct 2026", "SkillGuard", "Nebius x NVIDIA Global AI Hackathon", "1,058 tests passing", "ok"),
    ("Oct 2026", "Perfect Pair", "BSRM x ALDO Retail Gen AI Hackathon", "prize winner", "warn"),
    ("Since Jan 2026", "Ayebot", "Universities in India", "in production, pilot signed", "ok"),
]


def hero(theme):
    rows_y0, row_h = 296, 34
    n = len(LEDGER)
    h = rows_y0 + row_h * n + 22
    # The ledger writes itself once, row by row, then a caret waits on the next line.
    step, wipe, start = 0.34, 0.6, 0.35
    css = "@keyframes w{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    css += "@keyframes p{0%{transform:scale(0)}70%{transform:scale(1.5)}100%{transform:scale(1)}}"
    css += "@keyframes b{0%,49%{opacity:1}50%,100%{opacity:0}}"
    css += "@keyframes a{from{opacity:0}to{opacity:1}}"
    for i in range(n):
        css += f".c{i}{{animation:w {wipe}s cubic-bezier(.3,.6,.2,1) {start + i * step:.2f}s both}}"
        css += (f".d{i}{{transform-box:fill-box;transform-origin:center;"
                f"animation:p .4s ease-out {start + i * step + wipe - 0.12:.2f}s both}}")
    end = start + (n - 1) * step + wipe
    css += f".k{{animation:a .01s linear {end:.2f}s both,b 1.1s linear {end + 0.01:.2f}s infinite}}"

    s = Svg(h, theme, "Jay Malhotra, AI/ML engineer",
            "I build AI products end to end, from the model to the app people use. "
            "Founding engineer at Ayebot. Master of Management Analytics at McGill University, Montreal. "
            "Recent work: AsOf for IBM Db2Hack 2026, SkillGuard for the Nebius x NVIDIA Global AI Hackathon, "
            "Perfect Pair (prize winner, BSRM x ALDO Retail Gen AI Hackathon), Ayebot (in production).", css)

    s.text("D", "Jay Malhotra", -4, 84, 100, track=-0.012)
    s.text("L", "AI/ML engineer. I build AI products end to end,", 0, 136, 24.5)
    s.text("L", "from the model to the app people use.", 0, 168, 24.5)
    s.text("B", "Founding engineer at Ayebot. Master of Management Analytics at McGill University, Montreal.",
           0, 208, 15.5, "muted")

    cols = (0, 128, 252, 532)
    s.line(0, 240, W, 240, "ink", 1.5)
    for x, label in zip(cols, ("When", "Project", "Built for", "Outcome")):
        s.text("B", label, x, 263, 13, "muted")
    s.line(0, 275, W, 275, "rule", 1)

    for i, (when, proj, ctx, out, col) in enumerate(LEDGER):
        y = rows_y0 + i * row_h + 6
        s.raw(f'<clipPath id="c{i}"><rect class="c{i}" x="0" y="{y - 24}" width="{W}" height="{row_h}"/></clipPath>')
        s.raw(f'<g clip-path="url(#c{i})">')
        s.text("M", when, cols[0], y, 12.5, "muted")
        s.text("S", proj, cols[1], y, 16.5)
        s.text("B", ctx, cols[2], y, 14.5, "muted")
        s.text("M", out, cols[3] + 18, y, 12.5)
        s.raw("</g>")
        s.dot(cols[3] + 5, y - 4.5, 4.5, col, cls=f"d{i}")
        if i < n - 1:
            s.line(0, y + 11.5, W, y + 11.5, "rule", 1, dash="1 5")
    yk = rows_y0 + n * row_h + 6
    s.raw(f'<rect class="k" x="0" y="{yk - 13}" width="8" height="15" fill="{s.t["muted"]}"/>')
    return s.save(f"hero-{theme}.svg")


# ---------------------------------------------------------------- project strips

def strip_frame(s, title, desc_lines, facts, url):
    s.line(0, 1, W, 1, "rule", 1)
    s.text("H", title, -1, 58, 40, track=-0.01)
    y = 92
    for ln in desc_lines:
        s.text("B", ln, 0, y, 15.5)
        y += 23
    y += 12
    for ln in facts:
        s.text("M", ln, 0, y, 11.5, "muted")
        y += 19
    s.text("M", url, 0, s.h - 14, 11.5, "muted")


def chip(s, cx, y, label, color, hollow=False, anchor="middle"):
    """Verdict: a dot and a word, centred on cx (or starting at cx)."""
    tw = s.width("N", label, 12.5)
    x0 = cx - (tw + 15) / 2 if anchor == "middle" else cx
    s.dot(x0 + 4.5, y - 4.5, 4.5, color, hollow)
    s.text("N", label, x0 + 15, y, 12.5, color)


def asof(theme):
    s = Svg(262, theme, "AsOf",
            "Checks an AI assistant's answer against the policy that was in force on the customer's date. "
            "Built on IBM Db2. The same draft is corrected for 10 March 2026, when policy BRV-002 v1 was in force, "
            "and released for 2 June 2026 under BRV-002 v2. 1,331 tests. 0 of 65 wrong drafts released on blind sets.")
    strip_frame(s, "AsOf",
                ["Checks an AI assistant's answer against",
                 "the policy that was in force on the",
                 "customer's date. Built on IBM Db2."],
                ["1,331 tests, CI on IBM's Db2 image",
                 "0 of 65 wrong drafts released (blind sets)",
                 "bitemporal tables + vector search"],
                "github.com/JustJay7/asof")
    L, R = 392, W
    # the draft being checked
    s.rect(L, 24, R - L, 50, 8, "soft")
    s.text("B", "AI draft", L + 16, 45, 12, "muted")
    s.text("S", "\u201cYou qualify for a retroactive bereavement refund.\u201d", L + 16, 63, 14.5)
    # two policy versions on one time axis
    ya = 136
    mid = L + (R - L) * 0.5
    xa, xb = L + 112, mid + 132
    s.line(xa, 74, xa, ya, "warn", 1.5, dash="2 5")
    s.line(xb, 74, xb, ya, "ok", 1.5, dash="2 5")
    s.line(L + 3, ya, mid - 7, ya, "muted", 6)
    s.line(mid + 7, ya, R - 3, ya, "muted", 6)
    s.text("M", "BRV-002 v1", L, ya - 16, 11.5, "muted")
    s.text("M", "BRV-002 v2", mid + 4, ya - 16, 11.5, "muted")
    for x, col in ((xa, "warn"), (xb, "ok")):
        s.raw(f'<circle cx="{x}" cy="{ya}" r="7.5" fill="{s.t[col]}" stroke="{ "#0D1117" if theme == "dark" else "#FFFFFF"}" stroke-width="3"/>')
    s.text("M", "as of 10 Mar 2026", xa, ya + 32, 12, "ink", "middle")
    s.text("M", "as of 2 Jun 2026", xb, ya + 32, 12, "ink", "middle")
    s.text("B", "contradicts the policy in force", xa, ya + 54, 13, "muted", "middle")
    s.text("B", "supported by the policy in force", xb, ya + 54, 13, "muted", "middle")
    chip(s, xa, ya + 80, "corrected", "warn")
    chip(s, xb, ya + 80, "released", "ok")
    return s.save(f"asof-{theme}.svg")


def skillguard(theme):
    s = Svg(262, theme, "SkillGuard",
            "Runs a new skill in a sandbox and watches what it does before a personal AI agent is allowed to "
            "install it. A static scanner scored an unsafe receipt skill 7 of 100 and rated it safe. The SkillGuard "
            "sandbox run recorded 13 denied private-file reads and blocked it. 1,058 tests.")
    strip_frame(s, "SkillGuard",
                ["Runs a new skill in a sandbox and watches",
                 "what it does before a personal AI agent",
                 "is allowed to install it."],
                ["1,058 tests",
                 "NVIDIA OpenShell sandbox, Nemotron review",
                 "human approval, with rollback"],
                "github.com/JustJay7/skillguard")
    L, R = 392, W
    s.rect(L, 24, R - L, 50, 8, "soft")
    s.text("B", "Skill under review", L + 16, 45, 12, "muted")
    s.text("S", "A receipt organizer that also reads a private file.", L + 16, 63, 14.5)
    # two ways of judging the same skill
    xs = L + 16
    y1, y2 = 122, 196
    s.raw(f'<path d="M{xs} 74V{y2 - 5}H{xs + 14}M{xs} {y1 - 5}H{xs + 14}" fill="none" stroke="{s.t["rule"]}" stroke-width="1.5"/>')
    tx = xs + 26
    s.text("S", "Static scanner", tx, y1, 15)
    s.text("M", "risk score 7 of 100", tx, y1 + 21, 11.5, "muted")
    s.text("S", "SkillGuard sandbox run", tx, y2, 15)
    s.text("M", "12 of 12 receipt tasks correct", tx, y2 + 21, 11.5, "muted")
    s.text("M", "13 private-file reads denied", tx, y2 + 39, 11.5, "muted")
    vx = R - 112
    s.line(tx + 196, y1 - 5, vx - 16, y1 - 5, "rule", 1, dash="1 5")
    s.line(tx + 196, y2 - 5, vx - 16, y2 - 5, "rule", 1, dash="1 5")
    chip(s, vx, y1, "rated safe", "muted", hollow=True, anchor="start")
    chip(s, vx, y2, "blocked", "stop", anchor="start")
    return s.save(f"skillguard-{theme}.svg")


# ---------------------------------------------------------------- stack

STACK = [
    ("Languages", ["Python", "SQL", "C#", "JavaScript"]),
    ("ML and AI", ["LangGraph", "LangChain", "RAG", "scikit-learn", "YOLO", "U-Net"]),
    ("Agents", ["NVIDIA Nemotron", "Hermes", "OpenShell", "Harbor", "Docker"]),
    ("Apps", ["FastAPI", "Flask", "Next.js", "Flutter", "ASP.NET"]),
    ("Data", ["IBM Db2", "SQL Server", "MySQL", "SQLite", "Neo4j"]),
    ("Cloud", ["AWS Bedrock", "Google Cloud", "Nebius", "DigitalOcean"]),
]


def stack(theme):
    rows = max(len(v) for _, v in STACK)
    s = Svg(52 + rows * 22, theme, "Stack",
            ". ".join(f"{k}: {', '.join(v)}" for k, v in STACK) + ".")
    cw = W / len(STACK)
    s.line(0, 1, W, 1, "rule", 1)
    for i, (head, items) in enumerate(STACK):
        x = i * cw
        s.text("S", head, x, 28, 14)
        for j, it in enumerate(items):
            s.text("M", it, x, 56 + j * 22, 12, "muted")
    return s.save(f"stack-{theme}.svg")


if __name__ == "__main__":
    for th in THEMES:
        for fn in (hero, asof, skillguard, stack):
            print(fn.__name__, th, fn(th), "bytes")
