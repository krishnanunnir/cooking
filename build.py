#!/usr/bin/env python3
"""
Static site generator for recipes.
Reads YAML recipes → generates a complete website.
"""

import os
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent
RECIPES_DIR = ROOT / "recipes"
BUILD_DIR = ROOT / "build"


# ── Helpers ────────────────────────────────────────────────────────────

def load_recipes():
    """Load all recipes from YAML files, organized by category."""
    recipes = []
    for path in sorted(RECIPES_DIR.rglob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if not data or "title" not in data:
            continue
        # Calculate totals
        data["_path"] = path.relative_to(RECIPES_DIR)
        data["_slug"] = path.stem
        data["_category"] = path.parent.name
        data["_total"] = calc_totals(data)
        recipes.append(data)
    return recipes


def calc_totals(recipe):
    """Sum up nutrition across all ingredients."""
    totals = {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}
    for ing in recipe.get("ingredients", []):
        for k in totals:
            totals[k] += ing.get(k, 0)
    servings = recipe.get("servings", 1)
    per_serving = {k: round(v / servings, 1) for k, v in totals.items()}
    return {
        "total": {k: round(v, 1) for k, v in totals.items()},
        "per_serving": per_serving,
        "servings": servings,
    }


def write_html(path, html):
    """Write HTML to build directory."""
    path = BUILD_DIR / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(html)
    print(f"  ✓ {path.relative_to(BUILD_DIR)}")


def fmt(val):
    """Format a number nicely."""
    if val == int(val):
        return str(int(val))
    return f"{val:.1f}"


# ── Templates ──────────────────────────────────────────────────────────

BASE_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#faf9f6;color:#2d2d2d;line-height:1.6}
.layout{max-width:960px;margin:0 auto;padding:20px}
header{background:#fff;border-bottom:1px solid #eee;padding:16px 20px;position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
header h1{margin:0;font-size:1.3rem}
header h1 a{color:#2d2d2d;text-decoration:none}
nav{display:flex;gap:16px;flex-wrap:wrap}
nav a{color:#666;text-decoration:none;font-size:.9rem;padding:4px 0;border-bottom:2px solid transparent}
nav a:hover,nav a.active{border-color:#e07c3c;color:#2d2d2d}
.page-title{font-size:1.8rem;margin:24px 0 16px;font-weight:700}
.card{background:#fff;border-radius:12px;padding:20px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,.06);transition:box-shadow .2s}
.card-title{font-size:1.15rem;font-weight:600;margin-bottom:4px}
.card-title a{color:#2d2d2d;text-decoration:none}
.card-title a:hover{color:#e07c3c}
.card-meta{color:#888;font-size:.85rem;display:flex;gap:16px;flex-wrap:wrap;margin-bottom:8px}
.card-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.tag{background:#f0ede8;color:#666;padding:2px 10px;border-radius:20px;font-size:.8rem}

/* ── Table: scrollable on mobile ── */
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:16px -4px}
table{width:100%;border-collapse:collapse;min-width:480px}
th,td{text-align:left;padding:10px 8px;border-bottom:1px solid #eee;white-space:nowrap}
th{font-size:.75rem;color:#888;text-transform:uppercase;letter-spacing:.3px;font-weight:600}
td{font-size:.9rem}
tr.total td{font-weight:700;border-top:2px solid #2d2d2d;border-bottom:none}
tr.per-serving td{border-bottom:none;color:#e07c3c;font-weight:600}

/* ── Amount inputs ── */
.amt-input{width:56px;padding:6px 4px;font-size:.9rem;border:1px solid #ddd;border-radius:6px;text-align:center;outline:none}
.amt-input:focus{border-color:#e07c3c;background:#fffdfa}
.amt-unit{color:#888;font-size:.8rem}
#servings-input:focus{border-color:#e07c3c;outline:none}

.instructions{margin:16px 0}
.instructions li{margin-bottom:8px;padding-left:8px}
.instructions ol{padding-left:20px}
.meta-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:16px 0}
.meta-item{text-align:center;padding:12px 8px;background:#faf9f6;border-radius:8px}
.meta-item .val{font-size:1.1rem;font-weight:600}
.meta-item .lbl{font-size:.75rem;color:#888}
.search-box{width:100%;padding:12px 16px;font-size:1rem;border:2px solid #ddd;border-radius:10px;outline:none;margin-bottom:20px;transition:border-color .2s}
.search-box:focus{border-color:#e07c3c}

/* ── Plan page ── */
.day-card{border-left:4px solid #e07c3c}
.treat-day{border-left-color:#e74c3c;background:linear-gradient(135deg,#fff 0%,#fff5f5 100%)}
.day-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #eee}
.day-name{font-size:1.1rem;font-weight:700}
.day-total{font-size:1rem;color:#e07c3c;font-weight:600}
.day-meals{display:flex;flex-direction:column;gap:8px}
.meal{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;font-size:.9rem}
.meal-big{background:#fef6ee}
.meal-small{background:#eef6ef}
.meal-vsmall{background:#fef0f0}
.meal-free{background:#f0f4ff}
.meal-badge{font-size:.7rem;font-weight:600;text-transform:uppercase;letter-spacing:.5px;padding:2px 8px;border-radius:4px;min-width:50px;text-align:center}
.big-badge{background:#e07c3c;color:#fff}
.small-badge{background:#4caf50;color:#fff}
.vs-badge{background:#e74c3c;color:#fff}
.free-badge{background:#5b7db5;color:#fff}
.meal-name{color:#2d2d2d;text-decoration:none;flex:1}
.meal-name:hover{color:#e07c3c}
.meal-kcal{color:#888;font-size:.85rem;white-space:nowrap}
.week-summary{text-align:center;padding:16px;background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.06);color:#666;font-size:.95rem}

footer{text-align:center;padding:32px 0;color:#aaa;font-size:.85rem;border-top:1px solid #eee;margin-top:40px}

/* ── Mobile ── */
@media(max-width:600px){
  .layout{padding:12px}
  .page-title{font-size:1.3rem;margin:16px 0 12px}
  .card{padding:14px;border-radius:10px}
  .meta-grid{grid-template-columns:repeat(2,1fr);gap:6px}
  .meta-item{padding:10px 6px}
  .meta-item .val{font-size:1rem}
  table{min-width:420px}
  th,td{padding:8px 6px;font-size:.8rem}
  .amt-input{width:48px;padding:5px 3px;font-size:.85rem;height:32px}
  header{padding:12px 16px}
  header h1{font-size:1.1rem}
  .card-title{font-size:1rem}
  .card-meta{font-size:.8rem;gap:10px}
  .search-box{padding:10px 14px;font-size:.9rem}
  #servings-input{width:40px!important;font-size:1rem!important}
}
"""

def make_header(title, root, active=''):
    """Generate HTML header with proper relative paths to index.html files.
    active: 'recipes' or 'plan' to highlight the nav link."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Cooking</title>
<link rel="stylesheet" href="{root}/assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🍳</text></svg>">
</head>
<body>
<header>
<h1><a href="{root}/index.html">🍳 Cooking</a></h1>
<nav>
  <a href="{root}/index.html" class="{'active' if active=='recipes' else ''}">All Recipes</a>
  <a href="{root}/plan/index.html" class="{'active' if active=='plan' else ''}">Weekly Plan</a>
</nav>
</header>
<div class="layout">
"""

HTML_FOOTER = """
</div>
<footer>Generated from YAML recipes • Open in any browser</footer>
</body>
</html>"""


# ── Page Generators ────────────────────────────────────────────────────

def build_homepage(recipes):
    """Generate the homepage with all recipes grouped by category + search."""
    categories = {}
    for r in recipes:
        cat = r.get("_category", "uncategorized")
        categories.setdefault(cat, []).append(r)
    
    # Build category HTML
    cats_html = ""
    for cat in sorted(categories):
        cat_recipes = categories[cat]
        cat_label = cat.replace("-", " ").title()
        total_cal = sum(r["_total"]["per_serving"]["kcal"] for r in cat_recipes)
        avg_cal = round(total_cal / len(cat_recipes), 0)
        
        card_html = f"""
        <div class="category-section" data-category="{cat}">
          <h2 class="page-title" style="margin-bottom:4px;font-size:1.4rem;text-transform:capitalize">{cat_label}</h2>
          <p style="color:#888;margin-bottom:16px;font-size:.9rem">{len(cat_recipes)} recipes · avg {fmt(avg_cal)} kcal/serving</p>
        """
        
        for r in cat_recipes:
            t = r["_total"]["per_serving"]
            tags = "".join(f'<span class="tag">{t}</span>' for t in r.get("tags", []))
            slug = f"{r['_category']}/{r['_slug']}.html"
            
            card_html += f"""
          <div class="card recipe-card" data-name="{r['title'].lower()}" data-tags="{' '.join(r.get('tags',[]))}">
            <div class="card-title"><a href="{slug}">{r['title']}</a></div>
            <div class="card-meta">
              <span>⏱ {r.get('prep_time','?')} + {r.get('cook_time','?')}</span>
              <span>🍽 {r.get('servings',1)} serving(s)</span>
              <span>🔥 {fmt(t['kcal'])} kcal/serving</span>
            </div>
            <div class="card-tags">{tags}</div>
          </div>
            """
        
        card_html += "</div>"
        cats_html += card_html
    
    search_html = """
    <input type="text" class="search-box" id="search" placeholder="Search recipes by name or tag..." autofocus>
    <div id="search-status" style="color:#888;font-size:.9rem;margin-bottom:8px"></div>
    """
    
    body = make_header("All Recipes", root=".", active="recipes")
    body += """
    <div class="page-title" style="margin-bottom:4px">All Recipes</div>
    <p style="color:#888;margin-bottom:20px">__COUNT__ recipes</p>
    __SEARCH__
    <div id="recipes-container">
    __CATS__
    </div>
    <script>
    const search = document.getElementById('search');
    const container = document.getElementById('recipes-container');
    const status = document.getElementById('search-status');

    search.addEventListener('input', function() {
      const q = this.value.toLowerCase().trim();
      const cards = container.querySelectorAll('.recipe-card');
      const sections = container.querySelectorAll('.category-section');
      let visible = 0;

      cards.forEach(card => {
        const name = card.dataset.name;
        const tags = card.dataset.tags;
        const match = q === '' || name.includes(q) || tags.includes(q);
        card.style.display = match ? '' : 'none';
        if (match) visible++;
      });

      sections.forEach(section => {
        const hasVisible = Array.from(section.querySelectorAll('.recipe-card')).some(c => c.style.display !== 'none');
        section.style.display = hasVisible ? '' : 'none';
      });

      status.textContent = q ? 'Showing ' + visible + ' of ' + __COUNT__ + ' recipes' : '';
    });
    </script>
    """.replace("__COUNT__", str(len(recipes))).replace("__SEARCH__", search_html).replace("__CATS__", cats_html)
    body += HTML_FOOTER
    
    write_html("index.html", body)


def build_category_pages(recipes):
    """Generate category index pages."""
    by_cat = {}
    for r in recipes:
        by_cat.setdefault(r["_category"], []).append(r)
    
    for cat, cat_recipes in by_cat.items():
        cat_label = cat.replace("-", " ").title()
        
        body = make_header(f"{cat_label} — Recipes", root="..")
        body += f'<div class="page-title" style="text-transform:capitalize">{cat_label}</div>'
        body += f'<p style="color:#888;margin-bottom:20px">{len(cat_recipes)} recipes</p>'
        
        for r in cat_recipes:
            t = r["_total"]["per_serving"]
            tags = "".join(f'<span class="tag">{t}</span>' for t in r.get("tags", []))
            slug = f"{r['_category']}/{r['_slug']}.html"
            
            body += f"""
            <div class="card">
              <div class="card-title"><a href="../{slug}">{r['title']}</a></div>
              <div class="card-meta">
                <span>⏱ {r.get('prep_time','?')} + {r.get('cook_time','?')}</span>
                <span>🍽 {r.get('servings',1)} serving(s)</span>
                <span>🔥 {fmt(t['kcal'])} kcal/serving</span>
              </div>
              <div class="card-tags">{tags}</div>
            </div>
            """
        
        body += HTML_FOOTER
        write_html(f"{cat}/index.html", body)


def build_recipe_pages(recipes):
    """Generate interactive recipe pages with editable amounts."""
    for r in recipes:
        t = r["_total"]
        tags = "".join(f'<span class="tag">{t}</span>' for t in r.get("tags", []))
        inst_html = "<ol>" + "".join(f"<li>{s}</li>" for s in r.get("instructions", [])) + "</ol>"
        
        # Build ingredient rows with data attributes and editable inputs
        ing_rows = ""
        ing_data = []  # for JS embedding
        for ing in r.get("ingredients", []):
            a = ing['amount']
            # Derive per-100g rates from total values
            scale = a / 100.0
            kcal_p100 = round(ing.get('kcal',0) / scale, 1) if scale else 0
            pro_p100  = round(ing.get('protein',0) / scale, 1) if scale else 0
            carb_p100 = round(ing.get('carbs',0) / scale, 1) if scale else 0
            fat_p100  = round(ing.get('fat',0) / scale, 1) if scale else 0
            
            ing_data.append({
                'name': ing['name'],
                'unit': ing['unit'],
                'amount': a,
                'kcal_p100': kcal_p100,
                'protein_p100': pro_p100,
                'carbs_p100': carb_p100,
                'fat_p100': fat_p100,
            })
            
            ing_rows += f"""
            <tr>
              <td>{ing['name']}</td>
              <td><input type="number" value="{a}" step="1" class="amt-input" data-unit="{ing['unit']}"> <span class="amt-unit">{ing['unit']}</span></td>
              <td class="c-kcal">{fmt(ing.get('kcal',0))}</td>
              <td class="c-pro">{fmt(ing.get('protein',0))}g</td>
              <td class="c-carb">{fmt(ing.get('carbs',0))}g</td>
              <td class="c-fat">{fmt(ing.get('fat',0))}g</td>
            </tr>"""
        
        ing_json = json.dumps(ing_data)
        servings = r.get('servings', 1)
        tot = t['total']
        per = t['per_serving']
        
        body = make_header(r['title'], root="..")
        
        body += f"""
        <div style="margin-bottom:8px">
          <a href="../index.html" style="color:#888;text-decoration:none;font-size:.9rem">← All Recipes</a>
          <span style="color:#ccc"> / </span>
          <a href="../{r['_category']}/index.html" style="color:#888;text-decoration:none;font-size:.9rem;text-transform:capitalize">{r['_category']}</a>
        </div>
        
        <div class="page-title" style="margin-bottom:4px">{r['title']}</div>
        <div class="card-tags" style="margin-bottom:12px">{tags}</div>
        
        <div class="meta-grid">
          <div class="meta-item"><div class="val">⏱ {r.get('prep_time','?')}</div><div class="lbl">Prep</div></div>
          <div class="meta-item"><div class="val">⏱ {r.get('cook_time','?')}</div><div class="lbl">Cook</div></div>
          <div class="meta-item">
            <div class="val"><input type="number" id="servings-input" value="{servings}" min="1" step="1" style="width:48px;text-align:center;font-size:1.1rem;font-weight:700;border:1px solid #ddd;border-radius:6px;padding:4px"></div>
            <div class="lbl">Servings</div></div>
          <div class="meta-item"><div class="val" id="kcalserv">{fmt(per['kcal'])}</div><div class="lbl">kcal/serving</div></div>
        </div>
        
        <div class="card">
          <h3 style="margin-bottom:12px;font-size:1rem;color:#666">🥗 Ingredients & Nutrition <span style="font-weight:400;color:#888;font-size:.85rem">— edit amounts to adjust</span></h3>
          <div class="table-wrap"><table id="nutrition-table">
            <thead>
              <tr><th>Ingredient</th><th>Amount</th><th>kcal</th><th>Protein</th><th>Carbs</th><th>Fat</th></tr>
            </thead>
            <tbody id="nut-tbody">
              {ing_rows}
              <tr class="total">
                <td><strong>Total</strong></td><td></td>
                <td id="tot-kcal"><strong>{fmt(tot['kcal'])}</strong></td>
                <td id="tot-pro"><strong>{fmt(tot['protein'])}g</strong></td>
                <td id="tot-carb"><strong>{fmt(tot['carbs'])}g</strong></td>
                <td id="tot-fat"><strong>{fmt(tot['fat'])}g</strong></td>
              </tr>
              <tr class="per-serving">
                <td><strong>Per serving</strong></td><td></td>
                <td id="per-kcal"><strong>{fmt(per['kcal'])}</strong></td>
                <td id="per-pro"><strong>{fmt(per['protein'])}g</strong></td>
                <td id="per-carb"><strong>{fmt(per['carbs'])}g</strong></td>
                <td id="per-fat"><strong>{fmt(per['fat'])}g</strong></td>
              </tr>
            </tbody>
          </table></div>
        </div>
        
        <div class="card">
          <h3 style="margin-bottom:12px;font-size:1rem;color:#666">📝 Instructions</h3>
          <div class="instructions">{inst_html}</div>
        </div>
        
        <script>
        const DATA = {ing_json};
        const servingsInput = document.getElementById('servings-input');
        const tbody = document.getElementById('nut-tbody');
        const inputs = tbody.querySelectorAll('.amt-input');

        function update() {{
          const sv = parseFloat(servingsInput.value) || 1;
          let tKcal = 0, tPro = 0, tCarb = 0, tFat = 0;

          inputs.forEach((input, i) => {{
            const newAmt = parseFloat(input.value) || 0;
            const d = DATA[i];
            // Recalculate using per-100g rates
            const scale = newAmt / 100;
            const kcal = Math.round(d.kcal_p100 * scale * 10) / 10;
            const pro  = Math.round(d.protein_p100 * scale * 10) / 10;
            const carb = Math.round(d.carbs_p100 * scale * 10) / 10;
            const fat  = Math.round(d.fat_p100 * scale * 10) / 10;

            const cells = input.closest('tr').querySelectorAll('td');
            cells[2].textContent = kcal;
            cells[3].textContent = pro + 'g';
            cells[4].textContent = carb + 'g';
            cells[5].textContent = fat + 'g';

            tKcal += kcal; tPro += pro; tCarb += carb; tFat += fat;
          }});

          tKcal = Math.round(tKcal * 10) / 10;
          tPro  = Math.round(tPro * 10) / 10;
          tCarb = Math.round(tCarb * 10) / 10;
          tFat  = Math.round(tFat * 10) / 10;

          document.getElementById('tot-kcal').innerHTML = '<strong>' + tKcal + '</strong>';
          document.getElementById('tot-pro').innerHTML  = '<strong>' + tPro + 'g</strong>';
          document.getElementById('tot-carb').innerHTML = '<strong>' + tCarb + 'g</strong>';
          document.getElementById('tot-fat').innerHTML  = '<strong>' + tFat + 'g</strong>';

          const sk = Math.round(tKcal / sv * 10) / 10;
          const sp = Math.round(tPro / sv * 10) / 10;
          const sc = Math.round(tCarb / sv * 10) / 10;
          const sf = Math.round(tFat / sv * 10) / 10;

          document.getElementById('per-kcal').innerHTML = '<strong>' + sk + '</strong>';
          document.getElementById('per-pro').innerHTML  = '<strong>' + sp + 'g</strong>';
          document.getElementById('per-carb').innerHTML = '<strong>' + sc + 'g</strong>';
          document.getElementById('per-fat').innerHTML  = '<strong>' + sf + 'g</strong>';
          document.getElementById('kcalserv').textContent = sk;
        }}

        inputs.forEach(inp => inp.addEventListener('input', update));
        servingsInput.addEventListener('input', update);
        </script>
        """
        
        body += HTML_FOOTER
        write_html(f"{r['_category']}/{r['_slug']}.html", body)


# ── Main ───────────────────────────────────────────────────────────────

def build_plan_page(recipes):
    """Generate weekly meal plan page that randomizes on every load."""
    # Group recipes by category
    big_recipes = [r for r in recipes if r["_category"] == "big"]
    small_recipes = [r for r in recipes if r["_category"] == "small"]
    vsmall_recipes = [r for r in recipes if r["_category"] == "very-small"]
    free_recipes = [r for r in recipes if r["_category"] == "free"]
    
    # Embed recipe data as JSON for JavaScript to use
    def rdata(r):
        return {"name": r["title"], "slug": f"../{r['_category']}/{r['_slug']}.html", "kcal": r["_total"]["per_serving"]["kcal"]}
    recipe_data = {
        "big": [rdata(r) for r in big_recipes],
        "small": [rdata(r) for r in small_recipes],
        "very_small": [rdata(r) for r in vsmall_recipes],
        "free": [rdata(r) for r in free_recipes],
    }
    recipes_json = json.dumps(recipe_data)
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_json = json.dumps(days)
    
    body = make_header("Weekly Plan", root="..", active="plan")
    
    body += """
    <div class="page-title" style="margin-bottom:4px">📅 Weekly Meal Plan</div>
    <p style="color:#888;margin-bottom:8px">Each day: <strong>2 Big</strong> (≈700 ea) + <strong>1 Small</strong> (≈300) + <strong>2x Tea</strong> (≈130) = <strong>≈1,830 kcal</strong></p>
    <p style="color:#888;font-size:.85rem;margin-bottom:4px">🎉 <strong>1-3 treat days</strong> get an extra <strong>Very Small</strong> (≈150 kcal) on top</p>
    <p style="color:#aaa;font-size:.85rem;margin-bottom:20px">Shuffle for a new random plan</p>
    
    <div id="plan"></div>
    
    <div style="text-align:center;margin:20px 0">
      <button class="calc-btn" onclick="generate()">Shuffle</button>
      <span id="seed-display" style="display:inline-block;margin-left:16px;font-size:.85rem;color:#aaa"></span>
    </div>
    
    <script>
    const RECIPES = __RECIPES__;
    const DAYS = __DAYS__;

    // Seeded PRNG (mulberry32)
    function mulberry32(a) {
      return function() {
        a |= 0; a = a + 0x6D2B79F5 | 0;
        var t = Math.imul(a ^ a >>> 15, 1 | a);
        t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
      }
    }

    // Seed = current week number (weeks since Jan 1 2020)
    // Override with ?seed=XXX for a specific plan
    var params = new URLSearchParams(window.location.search);
    var seed;
    if (params.has('seed')) {
      seed = parseInt(params.get('seed'), 10);
      if (isNaN(seed)) seed = currentWeek();
    } else {
      seed = currentWeek();
    }

    function currentWeek() {
      return Math.floor(Date.now() / (7 * 86400000));
    }

    var rng = mulberry32(seed);

    function pick(arr) {
      return arr[Math.floor(rng() * arr.length)];
    }

    function shuffle(arr) {
      var a = arr.slice();
      for (var i = a.length - 1; i > 0; i--) {
        var j = Math.floor(rng() * (i + 1));
        var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
      }
      return a;
    }

    function generate() {
      const container = document.getElementById('plan');
      let html = '';
      let weekTotal = 0;

      // Pick 1-3 random treat days
      const numTreatDays = 1 + Math.floor(rng() * 3);
      const treatDays = shuffle(DAYS).slice(0, numTreatDays);

      DAYS.forEach(day => {
        var big1 = pick(RECIPES.big);
        var big2 = pick(RECIPES.big);
        // Ensure the two bigs are different
        while (big2.name === big1.name) {
          big2 = pick(RECIPES.big);
        }
        const small = pick(RECIPES.small);
        const tea = RECIPES.free.length ? RECIPES.free[0] : null;
        const teaKcal = tea ? tea.kcal * 2 : 0;  // 2 cups per day
        const isTreat = treatDays.includes(day);
        const vs = isTreat ? pick(RECIPES.very_small) : null;
        const dayTotal = big1.kcal + big2.kcal + small.kcal + teaKcal + (vs ? vs.kcal : 0);
        weekTotal += dayTotal;

        let mealsHtml = '<div class="meal meal-big"><span class="meal-badge big-badge">Big 1</span><a href="' + big1.slug + '" class="meal-name">' + big1.name + '</a><span class="meal-kcal">' + Math.round(big1.kcal) + ' kcal</span></div>' +
          '<div class="meal meal-big"><span class="meal-badge big-badge">Big 2</span><a href="' + big2.slug + '" class="meal-name">' + big2.name + '</a><span class="meal-kcal">' + Math.round(big2.kcal) + ' kcal</span></div>' +
          '<div class="meal meal-small"><span class="meal-badge small-badge">Small</span><a href="' + small.slug + '" class="meal-name">' + small.name + '</a><span class="meal-kcal">' + Math.round(small.kcal) + ' kcal</span></div>';

        // 2 cups of tea every day
        if (tea) {
          mealsHtml += '<div class="meal meal-free"><span class="meal-badge free-badge">☕ 2x</span><a href="' + tea.slug + '" class="meal-name">' + tea.name + '</a><span class="meal-kcal">' + Math.round(teaKcal) + ' kcal</span></div>';
        }

        if (isTreat && vs) {
          mealsHtml += '<div class="meal meal-vsmall"><span class="meal-badge vs-badge">🎉 Treat</span><a href="' + vs.slug + '" class="meal-name">' + vs.name + '</a><span class="meal-kcal">' + Math.round(vs.kcal) + ' kcal</span></div>';
        }

        html += '<div class="card day-card' + (isTreat ? ' treat-day' : '') + '">' +
          '<div class="day-header"><span class="day-name">' + day + '</span><span class="day-total">' + Math.round(dayTotal) + ' kcal</span></div>' +
          '<div class="day-meals">' + mealsHtml + '</div></div>';
      });

      const avg = Math.round(weekTotal / 7);
      html += '<div class="week-summary"><strong>Week Total:</strong> ' + Math.round(weekTotal) + ' kcal &middot; <strong>Daily Avg:</strong> ' + avg + ' kcal</div>';

      container.innerHTML = html;
    }

    generate();

    // Update URL with seed (without reloading)
    if (!params.has('seed')) {
      var newUrl = window.location.pathname + '?seed=' + seed;
      window.history.replaceState(null, '', newUrl);
    }

    // Show seed for bookmarking
    var seedDisplay = document.getElementById('seed-display');
    if (seedDisplay) {
      var url = window.location.pathname + '?seed=' + seed;
      seedDisplay.innerHTML = 'Week <a href="' + url + '" style="color:#888;text-decoration:underline">#' + seed + '</a>';
    }
    </script>
    """.replace("__RECIPES__", recipes_json).replace("__DAYS__", days_json)
    
    body += HTML_FOOTER
    write_html("plan/index.html", body)


def build_assets():
    """Write CSS."""
    write_html("assets/style.css", BASE_CSS.strip())


def build():
    print(f"\n  🍳 Building recipe site...\n")
    
    # Clean build dir
    if BUILD_DIR.exists():
        import shutil
        shutil.rmtree(BUILD_DIR)
    
    recipes = load_recipes()
    print(f"  📖 Loaded {len(recipes)} recipes\n")
    
    build_assets()
    build_homepage(recipes)
    build_category_pages(recipes)
    build_recipe_pages(recipes)
    build_plan_page(recipes)
    print(f"\n  ✅ Site built at: {BUILD_DIR}")
    print(f"  🌐 Open: {BUILD_DIR / 'index.html'}\n")


if __name__ == "__main__":
    build()
