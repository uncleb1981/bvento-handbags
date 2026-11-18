#!/usr/bin/env python3
"""Write the bag list from bags.json into index.html and llms.txt.

Edit bags.json (name, detail, price, "sold": true), then run:  python3 build.py
Photos stay at photos/bag-01.jpg, bag-02.jpg, ... in the same order as bags.json.
"""
import json, re, datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
PHOTO_TAG = "cream"  # bump when photos change, to refresh browser caches
bags = json.loads((ROOT / "bags.json").read_text())
pad = lambda n: f"{n:02d}"
color = lambda b: b["detail"].split(" · ")[-1]
in_stock = [b for b in bags if not b.get("sold")]
BAG_ICON = '<svg width="56" height="56" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 24v-4a10 10 0 0 1 20 0v4"/><path d="M12 24h40l-4 30H16z"/><path d="M26 34h12"/></svg>'

def card(i, b):
    n = pad(i + 1)
    sold = b.get("sold")
    price = b.get("price")
    label = f'View larger photo: {b["name"]}, {b["detail"]}' + (", sold" if sold else f", ${price}" if price else "")
    name, detail = escape(b["name"]), escape(b["detail"])
    cls = "bag sold" if sold else "bag"
    data_price = f' data-price="{price}"' if price else ""
    data_sold = " data-sold" if sold else ""
    sold_tag = '\n          <span class="sold-tag">Sold</span>' if sold else ""
    price_html = f'<span class="price">${price}</span>' if price else ""
    alt = f"{name} in {escape(color(b).lower())} — Italian leather handbag"
    return f"""      <article class="{cls}" tabindex="0" role="button" aria-label="{escape(label)}" data-name="{name}" data-detail="{detail}"{data_price}{data_sold}>
        <div class="frame">
          <img src="photos/bag-{n}.jpg?v={PHOTO_TAG}" alt="{alt}" loading="lazy">
          <div class="placeholder">{BAG_ICON}Photo coming soon</div>
          <span class="num">No. {n}</span>{sold_tag}
        </div>
        <div class="meta">
          <div class="line"><h3>{name}</h3>{price_html}</div>
          <div class="detail">{detail}</div>
        </div>
      </article>"""

ld = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "bvento handbags available now",
    "itemListElement": [{
        "@type": "ListItem",
        "position": i + 1,
        "item": {
            "@type": "Product",
            "name": f'{b["name"]} — {color(b)}',
            "description": f'{b["detail"]}. Made in Italy.',
            "image": f"https://bvento.com/photos/bag-{pad(i + 1)}.jpg",
            "brand": {"@type": "Brand", "name": "bvento"},
            "countryOfOrigin": "IT",
            "offers": {
                "@type": "Offer",
                "price": b.get("price"),
                "priceCurrency": "USD",
                "availability": "https://schema.org/SoldOut" if b.get("sold") else "https://schema.org/InStock",
                "seller": {"@type": "Organization", "name": "bvento"},
            },
        },
    } for i, b in enumerate(bags)],
}

def put(text, tag, body):
    pat = re.compile(rf"(<!-- {tag} -->).*?(<!-- /{tag} -->)", re.S)
    assert pat.search(text), f"marker {tag} missing"
    return pat.sub(lambda m: m.group(1) + body + m.group(2), text, count=1)

page = (ROOT / "index.html").read_text()
page = put(page, "BAGS-LD", '\n<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=2) + "\n</script>\n")
page = put(page, "STOCK", f'{len(in_stock)} {"bag" if len(in_stock) == 1 else "bags"} available in Bentonville today.')
page = put(page, "BAGS", "\n" + "\n".join(card(i, b) for i, b in enumerate(bags)) + "\n      ")
page = put(page, "YEAR", str(datetime.date.today().year))
(ROOT / "index.html").write_text(page)

prices = sorted({b["price"] for b in bags if b.get("price")})
lines = [
    "# bvento",
    "",
    "> bvento is a retailer of Italian-made leather and suede handbags in Bentonville, Arkansas (Northwest Arkansas). "
    "A small, hand-picked selection, each bag inspected by hand. Viewings by appointment; call or text 479-485-3374.",
    "",
    "## Contact",
    "",
    "- Phone (call or text): +1 479-485-3374",
    "- Location: Bentonville, Arkansas, USA (viewings by appointment; serves Bentonville, Rogers, Springdale, Fayetteville)",
    "- Website: https://bvento.com/",
    "",
    f"## Handbags available now ({len(in_stock)} in stock, ${prices[0]}–${prices[-1]})",
    "",
]
lines += [f'- {b["name"]} — {b["detail"]} — ${b["price"]} — made in Italy' for b in in_stock]
sold = [b for b in bags if b.get("sold")]
if sold:
    lines += ["", "## Recently sold", ""] + [f'- {b["name"]} — {b["detail"]}' for b in sold]
lines += ["", "## Pages", "", "- [bvento home and full selection](https://bvento.com/): photos, prices and availability of every bag", ""]
(ROOT / "llms.txt").write_text("\n".join(lines))
print(f"built {len(bags)} bags ({len(in_stock)} in stock)")
