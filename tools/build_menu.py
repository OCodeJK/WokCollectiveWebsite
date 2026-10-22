"""Rebuild the <nav> chips and <main> of menu.html from the client's price sheet.

Usage (from the repo root; needs openpyxl):
    python tools/build_menu.py "path/to/Website Price.xlsx" menu.html

To give a dish a photo: put a square ~720x720 JPG in assets/img/menu/ and add
"English name as in the sheet": "file-name-without-.jpg" to PHOTOS below.
"""
import html
import re
import sys

import openpyxl

XLSX, MENU = sys.argv[1], sys.argv[2]

CATS = [  # sheet category prefix -> (id, chip label)
    ("Crab", "crab", "Crab"),
    ("Fish", "fish", "Fish"),
    ("Prawn", "prawn", "Prawn"),
    ("Sotong", "sotong", "Sotong"),
    ("Soup", "soup", "Soup"),
    ("Beef", "beef", "Beef"),
    ("Chicken", "chicken", "Chicken"),
    ("Pork", "pork", "Pork"),
    ("Vegetable", "veg", "Vegetables"),
    ("Egg", "egg", "Egg"),
    ("Beancurd", "beancurd", "Beancurd"),
    ("Rice", "rice", "Rice"),
    ("Noodle", "noodles", "Noodles"),
]

# English name in the sheet -> photo in assets/img/menu
PHOTOS = {
    "Single Crab": "chilli-crab",
    "2 Crabs Promo": "creamy-corn-crab",
    "Fruity Red Grouper": "fruity-crispy-red-grouper",
    "Assam Fish Head": "assam-fish-head-tail",
    "Curry Fish Head": "curry-fish-head",
    "Sliced Fish with Spring Onion": "sliced-fish-with-spring-onion",
    "Sliced Fish with Dried Chilli": "sliced-fish-with-dried-chilli",
    "Steamed Fish Tail": "steamed-fish",
    "Braised Fish Tail with Bittergourd in Black Bean Sauce": "fish-tail-with-bitter-gourd-sauce",
    "Fish Head with Bittergourd in Black Bean Sauce": "fish-head-with-bitter-gourd-sauce",
    "Salted Egg Prawn Ball": "salted-egg-prawn-ball",
    "Cereal Prawn": "cereal-prawn",
    "Handmade Fried Prawn Roll": "handmade-prawn-roll",
    "Salad Prawn Ball": "salad-prawn-ball",
    "Crispy Fried Baby Squid": "crispy-fried-sotong",
    "Salted Egg Squid": "salted-egg-sotong",
    "Sambal Squid": "assam-sambal-sotong",
    "Sliced Fish Soup": "sliced-fish-soup",
    "Sliced Beef with Spring Onion": "stir-fried-spring-onion-beef",
    "Prawn Paste Chicken": "prawn-paste-chicken",
    "Salted Egg Chicken": "salted-egg-chicken",
    "Three Cup Chicken": "three-cup-chicken",
    "Red Wine Pork Rib": "red-wine-pork-ribs",
    "Pork Ribs King": "king-pork-ribs",
    "Stir Fry Sambal / Garlic Kang Kong": "sambal-kang-kong",
    "French Bean with Dried Shrimps": "french-beans-with-dried-shrimp",
    "Yu Xiang Style Eggplant": "yu-xiang-eggplant",
    "Bean Sprout with Salted Fish": "salted-fish-beansprouts",
    "Qing Long Veg": "qing-long-vegetables",
    "Onion Omelette": "spring-onion-omelette",
    "Hotplate Beancurd": "hotplate-beancurd",
    "Salted Fish Fried Rice": "salted-fish-fried-rice",
    "Yang Zhou Fried Rice": "yangzhou-fried-rice",
    "Sambal Fried Rice": "sambal-fried-rice",
    "Mui Fan": "mui-fan",
    "Salted Egg Chicken Rice": "salted-egg-chicken-rice",
    "Pork Rib Rice": "pork-ribs-rice",
    "Gong Bao Chicken Rice": "gong-bao-rice",
    "Sambal Sotong Rice": "sambal-sotong-rice",
    "Sweet & Sour Pork Rice": "sweet-sour-rice",
    "Black Pepper Chicken Rice": "black-pepper-rice",
    "Signature Claypot Noodle": "signature-claypot-noodles",
    "Braised Pork Knuckle Bee Hoon": "braised-pork-knuckle-bee-hoon",
    "Stir Fry Hor Fun": "stir-fried-hor-fun",
    "Mee Goreng": "mee-goreng",
    "Fried Hokkien Mee": "fried-hokkien-noodles",
    "Sin Chew Fried Bee Hoon": "xin-zhou-bee-hoon",
    "Stewed Seafood Ee Fu Noodles": "stewed-ee-fu-noodles",
    "Hor Fun with Gravy": "hor-fun-with-gravy",
    "Bee Hoon with Gravy": "bee-hoon-with-gravy",
    "Stir Fry Beef Hor Fun": "stir-fried-beef-hor-fun",
    "Fish Sauce Bee Hoon": "fish-sauce-bee-hoon",
    "Wa Dan Hor Fun": "wat-dan-hor-fun",
    "Seafood White Noodles": "seafood-white-noodles",
    "Seafood Crispy Noodles": "seafood-crispy-noodles",
    "Seafood Hor Fun": "seafood-hor-fun",
}

# Obvious typos in the sheet, fixed for display (reported back to the client)
FIXES = {
    "Braised Pork Knucle Bee Hoon": "Braised Pork Knuckle Bee Hoon",
    "Broccolli with Stir Fry Prawn": "Broccoli with Stir Fry Prawn",
}

esc = html.escape

# Dishes without a photo are hidden for now; flip to True to list them under each category
SHOW_UNPHOTOGRAPHED = False


def split_name(raw):
    raw = raw.strip()
    m = re.match(r"^([^\x00-\x7f]+?)\s+(.+)$", raw)
    zh, en = (m.group(1), m.group(2).strip()) if m else ("", raw)
    if zh == "鱼尾炉" and en == "Fish Head Steamboat/Pot":
        en = "Fish Tail Steamboat/Pot"  # sheet repeats the fish-head name for the tail pot
    return zh, FIXES.get(en, en)


def money(s):
    s = str(s).strip().lstrip("$").strip()
    return "$" + s


def prices(raw, note):
    """Return a list of (label, price) pairs."""
    if isinstance(raw, (int, float)):
        return [("", money(f"{raw:g}"))]
    raw = raw.strip()
    if "\n" in raw:  # crab weights: "600g - $48"
        return [tuple(p.strip() for p in line.split("-", 1)) for line in raw.splitlines() if line.strip()]
    parts = [p for p in re.split(r"\s*/\s*|\s+(?=\$)", raw) if p]
    parts = [money(p) for p in parts]
    if len(parts) == 3:
        return list(zip(["S", "M", "L"], parts))
    if len(parts) == 2 and note == "Medium / Large":
        return list(zip(["M", "L"], parts))
    if len(parts) == 2 and note == "6 pieces / 12 pieces":
        return list(zip(["6 pcs", "12 pcs"], parts))
    return [("", p) for p in parts]


def price_html(pairs):
    out = []
    for label, p in pairs:
        lab = f'<span class="price-size">{esc(label)}</span> ' if label else ""
        out.append(f"<span>{lab}{esc(p)}</span>")
    return '<p class="menu-price">' + "".join(out) + "</p>"


wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb.active
items = {c[1]: [] for c in CATS}
flavours = None
cat = None
for row in ws.iter_rows(min_row=5, values_only=True):
    sheet_cat, name, price, d, e = (list(row) + [None] * 5)[:5]
    if not name:
        continue
    if sheet_cat:
        cat = next(cid for prefix, cid, _ in CATS if sheet_cat.startswith(prefix))
    zh, en = split_name(name)
    notes = []
    for n in (d, e):
        if not n:
            continue
        n = str(n).strip()
        if n.startswith("Crab Flavours:"):
            flavours = [l.strip() for l in n.splitlines()[1:] if l.strip()]
        elif n not in ("No Modifier", "Medium / Large", "6 pieces / 12 pieces"):
            notes.append(n.lstrip("*").strip())
    items[cat].append(
        {"zh": zh, "en": en, "prices": prices(price, str(d).strip() if d else ""), "notes": notes, "photo": PHOTOS.get(en)}
    )

missing = set(PHOTOS) - {i["en"] for c in items.values() for i in c}
assert not missing, f"photo keys not in sheet: {missing}"


def shown(cid):
    return [d for d in items[cid] if SHOW_UNPHOTOGRAPHED or d["photo"]]


chips = "\n".join(
    f'      <a class="menu-chip" href="#cat-{cid}">{esc(label)}</a>' for _, cid, label in CATS if shown(cid)
)

sections = []
for prefix, cid, label in CATS:
    dishes = shown(cid)
    if not dishes:
        continue
    sheet_title = {"Vegetable": "Vegetables"}.get(prefix, prefix)
    zh_title = {
        "crab": "螃蟹", "fish": "鱼", "prawn": "虾", "sotong": "苏东", "soup": "汤类", "beef": "牛肉类",
        "chicken": "鸡肉类", "pork": "猪肉类", "veg": "菜类", "egg": "鸡蛋类", "beancurd": "豆腐类",
        "rice": "饭类", "noodles": "面类",
    }[cid]
    s = [f'      <section class="menu-category" id="cat-{cid}" data-category="{cid}">']
    s.append(
        f'        <h2 class="menu-category-title">{esc(sheet_title)} <span class="menu-category-zh">{zh_title}</span>'
        f' <span class="menu-count">{len(dishes)}</span></h2>'
    )
    with_photo = [d for d in dishes if d["photo"]]
    without = [d for d in dishes if not d["photo"]]
    if with_photo:
        s.append('        <div class="menu-grid">')
        for d in with_photo:
            s.append('          <article class="menu-card">')
            s.append(
                f'            <img src="assets/img/menu/{d["photo"]}.jpg" alt="{esc(d["en"])}" width="720" height="720" loading="lazy" decoding="async">'
            )
            s.append('            <div class="menu-card-body">')
            if d["zh"]:
                s.append(f'              <p class="menu-card-zh" lang="zh">{esc(d["zh"])}</p>')
            s.append(f'              <h3 class="menu-card-name">{esc(d["en"])}</h3>')
            s.append("              " + price_html(d["prices"]))
            for n in d["notes"]:
                s.append(f'              <p class="menu-note">{esc(n)}</p>')
            s.append("            </div>")
            s.append("          </article>")
        s.append("        </div>")
    if without:
        s.append('        <ul class="menu-list">')
        for d in without:
            zh = f'<span class="menu-card-zh" lang="zh">{esc(d["zh"])}</span>' if d["zh"] else ""
            notes = "".join(f'<span class="menu-note">{esc(n)}</span>' for n in d["notes"])
            s.append(
                f'          <li><div class="menu-list-name">{zh}<span class="menu-list-en">{esc(d["en"])}</span>{notes}</div>'
                + price_html(d["prices"])
                + "</li>"
            )
        s.append("        </ul>")
    if cid == "crab" and flavours:
        s.append('        <div class="crab-flavours">')
        s.append('          <h3>Choose Your Crab Flavour</h3>')
        s.append('          <ul>')
        for f in flavours:
            m = re.match(r"^(.*?)\s*(\+\$\d+)$", f)
            name, extra = (m.group(1), m.group(2)) if m else (f, "")
            extra_html = f' <span class="flavour-extra">{esc(extra)}</span>' if extra else ""
            s.append(f"            <li>{esc(name)}{extra_html}</li>")
        s.append("          </ul>")
        s.append("        </div>")
    s.append("      </section>")
    sections.append("\n".join(s))

page = open(MENU, encoding="utf-8").read()
page = re.sub(
    r'(<div class="container menu-nav-inner">\n).*?(\n  </div>\n</nav>)',
    lambda m: m.group(1) + chips + m.group(2),
    page,
    count=1,
    flags=re.S,
)
main = (
    '<main class="menu-page">\n  <div class="container">\n'
    '      <p class="portion-note"><strong>Portions:</strong> S serves 2–3 pax · M serves 3–5 pax · L serves 6–8 pax</p>\n'
    + "\n".join(sections)
    + "\n  </div>\n</main>"
)
page, n = re.subn(r"<main class=\"menu-page\">.*?</main>", lambda m: main, page, count=1, flags=re.S)
assert n == 1
open(MENU, "w", encoding="utf-8", newline="\n").write(page)

total = sum(len(v) for v in items.values())
print(f"{total} dishes, {sum(len(shown(c)) for c in items)} shown")
for cid, v in items.items():
    print(cid, len(shown(cid)), "of", len(v))
