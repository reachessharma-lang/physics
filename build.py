"""Build the Physics Decoded static site into public/.

    python build.py          # validate src/ and build public/
    python build.py --check  # validate only (nothing is written)

Sources (the only things anyone edits):
    src/content.json           site info + syllabus for each grade
    src/lessons/<slug>.json    an MCQ set (data only)          -> /posts/<slug>.html
    src/lessons/<slug>.html    notes (content-only HTML)       -> /posts/<slug>.html
                               or a legacy full HTML page (starts with <!doctype>)
    src/assets/                shared CSS, JS, images (copied as-is)
    docs/examples/             example files; example-notes.html is built to /styleguide.html

Each lesson file carries its own metadata (see docs/AUTHORING.md), so adding a lesson
means adding one file. Vercel runs this script on every push (see vercel.json).
Only the Python standard library is used.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "public"
GRADE_SLUG = {"XI": "grade-xi", "XII": "grade-xii"}
KIND_LABEL = {"notes": "Notes", "mcq": "MCQs"}
KIND_ICON = {"notes": "📘", "mcq": "📝"}
DIFFICULTIES = {"easy", "medium", "hard"}
# Things content-only notes must not contain: styling and behaviour come from the shared assets.
FORBIDDEN_IN_NOTES = [(r"<\s*(html|head|body|!doctype)\b", "full-page tags"), (r"<\s*style\b", "<style> blocks"),
                      (r"<\s*script\b", "<script> tags"), (r"<\s*link\b", "<link> tags"), (r"\sstyle\s*=", "style=\"…\" attributes")]

esc = html.escape


class Problems(list):
    def add(self, file, msg):
        self.append(f"{file}: {msg}")


# ---------------------------------------------------------------- reading lessons

def parse_front_matter(text, file, problems):
    """'---' / key: value lines / '---' at the top of an HTML lesson."""
    m = re.match(r"﻿?---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        problems.add(file, "missing front matter (the --- block with title, grade, chapters, date)")
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            problems.add(file, f"front matter line is not 'key: value': {line!r}")
            continue
        value = value.strip()
        if value[:1] in "[{":
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                problems.add(file, f"could not read {key.strip()}: {value!r} (use e.g. [4] or [7, 8])")
        meta[key.strip()] = value
    return meta, text[m.end():]


def validate_meta(meta, file, grades, problems):
    for field in ("title", "grade", "chapters", "date"):
        if field not in meta:
            problems.add(file, f"missing '{field}'")
    if meta.get("grade") not in grades:
        problems.add(file, f"grade must be one of {list(grades)}, got {meta.get('grade')!r}")
        return
    chapters = meta.get("chapters")
    if isinstance(chapters, int):
        chapters = meta["chapters"] = [chapters]
    if not isinstance(chapters, list) or not chapters:
        problems.add(file, "chapters must be a list such as [4] or [7, 8, 9]")
        return
    valid = {c["n"] for c in grades[meta["grade"]]["syllabus"]}
    for n in chapters:
        if n not in valid:
            problems.add(file, f"grade {meta['grade']} has no chapter {n} (valid: 1–{max(valid)})")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta.get("date", ""))):
        problems.add(file, "date must look like 2026-01-31")


def validate_questions(qs, file, problems):
    if not isinstance(qs, list) or not qs:
        problems.add(file, "'questions' must be a non-empty list")
        return
    for n, q in enumerate(qs, 1):
        where = f"question {n}"
        if not isinstance(q, dict):
            problems.add(file, f"{where} is not an object")
            continue
        extra = set(q) - {"q", "options", "answer", "explanation", "difficulty"}
        if extra:
            problems.add(file, f"{where}: unknown field(s) {sorted(extra)}")
        if not isinstance(q.get("q"), str) or not q["q"].strip():
            problems.add(file, f"{where}: 'q' (the question text) is missing")
        opts = q.get("options")
        if not isinstance(opts, list) or not 2 <= len(opts) <= 6 or not all(isinstance(o, str) and o.strip() for o in opts):
            problems.add(file, f"{where}: 'options' must be a list of 2–6 non-empty strings")
            continue
        if len(set(opts)) != len(opts):
            problems.add(file, f"{where}: two options are identical")
        a = q.get("answer")
        if not isinstance(a, int) or isinstance(a, bool) or not 0 <= a < len(opts):
            problems.add(file, f"{where}: 'answer' must be the option number counting from 0 (0 = A, 1 = B …), got {a!r}")
        if "difficulty" in q and q["difficulty"] not in DIFFICULTIES:
            problems.add(file, f"{where}: difficulty must be easy, medium or hard")
        if "explanation" in q and not isinstance(q["explanation"], str):
            problems.add(file, f"{where}: 'explanation' must be text")


def load():
    problems = Problems()
    site_data = json.loads((SRC / "content.json").read_text(encoding="utf-8"))
    grades = site_data["grades"]
    posts = []
    for f in sorted((SRC / "lessons").iterdir()):
        rel = f"src/lessons/{f.name}"
        if f.suffix not in (".json", ".html"):
            problems.add(rel, "only .json (MCQ) and .html (notes) files belong here")
            continue
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", f.stem):
            problems.add(rel, "file name must be lowercase words joined by hyphens, e.g. wave-motion.html")
        text = f.read_text(encoding="utf-8")
        if f.suffix == ".json":
            try:
                meta = json.loads(text)
            except json.JSONDecodeError as e:
                problems.add(rel, f"invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}")
                continue
            meta.setdefault("kind", "mcq")
            meta["format"] = "mcq"
            validate_questions(meta.get("questions"), rel, problems)
        else:
            meta, body = parse_front_matter(text, rel, problems)
            meta.setdefault("kind", "notes")
            meta["body"] = body
            if re.match(r"\s*<!doctype", body, re.I):
                meta["format"] = "legacy"
            else:
                meta["format"] = "notes"
                for pattern, what in FORBIDDEN_IN_NOTES:
                    if re.search(pattern, body, re.I):
                        problems.add(rel, f"notes must not contain {what} — the site stylesheet handles styling")
        if meta.get("kind") not in KIND_LABEL:
            problems.add(rel, f"kind must be 'notes' or 'mcq'")
        validate_meta(meta, rel, grades, problems)
        meta["slug"] = f.stem
        meta["file"] = rel
        posts.append(meta)
    slugs = [p["slug"] for p in posts]
    for s in {s for s in slugs if slugs.count(s) > 1}:
        problems.append(f"src/lessons: '{s}' exists as both .json and .html")
    posts.sort(key=lambda p: (p.get("date", ""), p["slug"]), reverse=True)
    return site_data, posts, problems


# ---------------------------------------------------------------- helpers

def chapter_of(data, post):
    syl = {c["n"]: c for c in data["grades"][post["grade"]]["syllabus"]}
    return [syl[n] for n in post["chapters"]]


def post_url(post):
    return f"/posts/{post['slug']}.html"


def plain(s):
    return re.sub(r"<[^>]+>", "", s)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", plain(html.unescape(text)).lower()).strip("-") or "section"


def shell(data, *, title, body, description=None, path="", current=None, css=(), scripts=(), noindex=False):
    site = data["site"]
    full_title = f"{title} | {site['name']}" if title != site["name"] else f"{site['name']} — Grade XI & XII Physics"
    desc = description or site["tagline"]

    def nav(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    styles = "".join(f'<link rel="stylesheet" href="/assets/css/{c}.css">\n' for c in ("tokens", "site", *css))
    js = "".join(f'<script src="/assets/js/{s}.js" defer></script>\n' for s in scripts)
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{site['url']}/{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(site['name'])}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta name="theme-color" content="#1a237e">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
{styles}{js}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <nav class="nav" aria-label="Main">
    <a class="brand" href="/"><img src="/assets/favicon.svg" alt="" width="30" height="30"> {esc(site['name'])}</a>
    <div class="nav-links">
      {nav('/pages/grade-xi.html', 'Grade XI', 'XI')}{nav('/pages/grade-xii.html', 'Grade XII', 'XII')}{nav('/search.html', 'All lessons', 'search')}
    </div>
    <form class="nav-search" action="/search.html" role="search"><input type="search" name="q" placeholder="Search topics…" aria-label="Search topics"></form>
  </nav>
</header>
<main class="container" id="main">
{body}
</main>
<footer class="footer"><div class="footer-inner">
  <strong>{esc(site['name'])}</strong><span>by {esc(site['author'])} · {esc(site['curriculum'])}</span>
  <span class="spacer"></span>
  <a href="/pages/grade-xi.html">Grade XI</a><a href="/pages/grade-xii.html">Grade XII</a>
  <a href="{site['youtube']}" target="_blank" rel="noopener">YouTube ▶</a>
</div></footer>
</body>
</html>
"""


def card(data, post):
    chaps = ", ".join(c["title"] for c in chapter_of(data, post))
    return f"""<article class="card kind-{post['kind']}">
  <div><span class="badge {post['kind']}">{'MCQ' if post['kind'] == 'mcq' else 'Notes'}</span></div>
  <h3><a href="{post_url(post)}">{esc(post['title'])}</a></h3>
  <div class="meta">Grade {post['grade']} · {esc(chaps)}</div>
</article>"""


def related(data, posts, post):
    return [p for p in posts if p is not post and p["grade"] == post["grade"] and set(p["chapters"]) & set(post["chapters"])]


def crumbs(data, post):
    ch = chapter_of(data, post)[0]
    grade = data["grades"][post["grade"]]
    return (f'<div class="crumbs"><a href="/">Home</a> › <a href="/pages/{GRADE_SLUG[post["grade"]]}.html">{esc(grade["title"])}</a>'
            f' › <a href="/pages/{GRADE_SLUG[post["grade"]]}.html#ch-{ch["n"]}">{esc(ch["title"])}</a></div>')


def lesson_head(data, post):
    chaps = ", ".join(f"Ch. {c['n']} {c['title']}" for c in chapter_of(data, post))
    extra = f'<span class="badge">{len(post["questions"])} questions</span>' if post["kind"] == "mcq" else ""
    lead = f'<p class="lead">{esc(post["description"])}</p>' if post.get("description") else ""
    return f"""{crumbs(data, post)}
<header class="lesson-head">
  <div class="tags"><span class="badge {post['kind']}">{KIND_LABEL[post['kind']]}</span><span class="badge">Grade {post['grade']}</span>{extra}</div>
  <h1>{esc(post['title'])}</h1>
  {lead}
  <p class="meta">{esc(chaps)} · Updated {post['date']}</p>
</header>"""


def related_block(data, posts, post):
    rel = related(data, posts, post)
    if not rel:
        return ""
    return f"""<section class="related"><h2>Also in this chapter</h2>
<div class="grid">{''.join(card(data, p) for p in rel)}</div></section>"""


# ---------------------------------------------------------------- lesson pages

def build_mcq(data, posts, post):
    qs = []
    for i, q in enumerate(post["questions"]):
        diff = q.get("difficulty")
        opts = "".join(f'<li><button class="option" type="button"><span class="letter" aria-hidden="true">{"ABCDEF"[j]}</span><span>{esc(o)}</span></button></li>'
                       for j, o in enumerate(q["options"]))
        exp = f"<strong>Explanation:</strong> {esc(q['explanation'])}" if q.get("explanation") else ""
        qs.append(f"""<li class="question" data-i="{i}" data-answer="{q['answer']}" data-difficulty="{diff or ''}">
  <div class="q-head"><p class="q-text"><span class="q-num">{i + 1}.</span> {esc(q['q'])}</p>{f'<span class="diff {diff}">{diff}</span>' if diff else ''}</div>
  <ol class="options" type="A">{opts}</ol>
  <div class="explanation" hidden role="status"><span class="verdict"></span> {exp}</div>
</li>""")
    body = f"""{lesson_head(data, post)}
<div class="quiz" data-quiz="{post['slug']}">
  <div class="quiz-bar">
    <span class="score" aria-live="polite"></span>
    <span class="progress" aria-hidden="true"><span></span></span>
    <label>Show <select data-filter>
      <option value="all">All questions</option><option value="unanswered">Unanswered</option><option value="wrong">Wrong answers</option>
      <option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
    </select></label>
    <button type="button" data-action="shuffle">Shuffle</button>
    <button type="button" data-action="reset">Reset</button>
  </div>
  <ol class="questions">
{''.join(qs)}
  </ol>
  <div class="result card" hidden><div class="big"></div><p class="msg"></p></div>
</div>
{related_block(data, posts, post)}"""
    desc = post.get("description") or f"{post['title']} — Grade {post['grade']} physics MCQ practice with answers and explanations."
    return shell(data, title=post["title"], body=body, description=desc, path=post_url(post)[1:],
                 current=post["grade"], css=("lesson",), scripts=("quiz",))


def build_notes(data, posts, post, *, path=None, noindex=False):
    body_html = post["body"]
    toc, used = [], set()

    def add_id(m):
        attrs, inner = m.group(1), m.group(2)
        idm = re.search(r'\bid="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slugify(inner)
        base, n = hid, 2
        while hid in used:
            hid, n = f"{base}-{n}", n + 1
        used.add(hid)
        toc.append((hid, plain(inner)))
        if not idm:
            attrs += f' id="{hid}"'
        return f"<h2{attrs}>{inner}</h2>"

    body_html = re.sub(r"<h2([^>]*)>(.*?)</h2>", add_id, body_html, flags=re.S | re.I)
    toc_html = ""
    if len(toc) >= 3:
        items = "".join(f'<li><a href="#{i}">{esc(html.unescape(t))}</a></li>' for i, t in toc)
        toc_html = f'<nav class="toc" aria-label="On this page"><strong>On this page</strong><ol>{items}</ol></nav>'
    body = f"""{lesson_head(data, post)}
<div class="lesson{'' if toc_html else ' no-toc'}">
<article class="notes-body">
{body_html.strip()}
</article>
{toc_html}
</div>
{related_block(data, posts, post)}"""
    desc = post.get("description") or f"{post['title']} — Grade {post['grade']} physics notes ({data['site']['curriculum']})."
    return shell(data, title=post["title"], body=body, description=desc, path=path or post_url(post)[1:],
                 current=post["grade"], css=("lesson",), scripts=("notes",), noindex=noindex)


def build_legacy(data, posts, post):
    """Old standalone pages: keep their own styling, add the site bar and footer."""
    site = data["site"]
    doc = post["body"]
    chaps = chapter_of(data, post)
    grade_url = f"/pages/{GRADE_SLUG[post['grade']]}.html"
    full_title = f"{post['title']} | {site['name']}"
    head = f"""<link rel="canonical" href="{site['url']}{post_url(post)}">
<meta name="description" content="{esc(post.get('description') or post['title'] + ' — Grade ' + post['grade'] + ' physics notes.')}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/css/lesson-bar.css">
"""
    bar = f"""<div class="pd-bar" role="navigation" aria-label="Site">
<a class="pd-brand" href="/"><img src="/assets/favicon.svg" alt=""><span>{esc(site['name'])}</span></a>
<a class="pd-crumb" href="{grade_url}#ch-{chaps[0]['n']}">Grade {post['grade']} › {esc(chaps[0]['title'])}</a>
<span class="pd-spacer"></span>
<a class="pd-hide-sm" href="/pages/grade-xi.html">Grade XI</a><a class="pd-hide-sm" href="/pages/grade-xii.html">Grade XII</a><a href="/search.html">Search</a>
</div>
"""
    more = "".join(f'<a href="{post_url(p)}">{KIND_ICON[p["kind"]]} {esc(p["title"])}</a>' for p in related(data, posts, post))
    foot = f"""<div class="pd-footer" role="contentinfo">
{f'<div class="pd-more"><span>Also in this chapter:</span>{more}</div>' if more else ''}
<a href="/">{esc(site['name'])}</a> · {esc(site['author'])} · <a href="{grade_url}">All Grade {post['grade']} chapters</a> · <a href="{site['youtube']}" target="_blank" rel="noopener">YouTube</a>
</div>
"""
    doc, n = re.subn(r"<title>.*?</title>", f"<title>{esc(full_title)}</title>", doc, count=1, flags=re.S | re.I)
    if not n:
        head = f"<title>{esc(full_title)}</title>\n" + head
    doc = re.sub(r"</head>", lambda m: head + "</head>", doc, count=1, flags=re.I)
    doc = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + bar, doc, count=1, flags=re.I)
    if re.search(r"</body>", doc, re.I):
        doc = re.sub(r"</body>(?![\s\S]*</body>)", lambda m: foot + "</body>", doc, count=1, flags=re.I)
    else:
        print(f"  warning: {post['file']} has no </body> (file looks truncated)")
        doc += "\n" + foot + "</body>\n</html>\n"
    return doc


# ---------------------------------------------------------------- site pages

def build_index(data, posts):
    site = data["site"]
    n_notes = sum(p["kind"] == "notes" for p in posts)
    n_questions = sum(len(p.get("questions", [])) for p in posts)
    grade_cards = []
    for g, grade in data["grades"].items():
        gp = [p for p in posts if p["grade"] == g]
        covered = len({n for p in gp for n in p["chapters"]})
        grade_cards.append(f"""<a class="card grade-card" href="/pages/{GRADE_SLUG[g]}.html">
  <h3>{esc(grade['title'])}</h3>
  <p>{len(grade['syllabus'])} chapters · {covered} with lessons so far</p>
  <div class="chapter-links"><span class="chip notes">{sum(p['kind'] == 'notes' for p in gp)} Notes</span><span class="chip mcq">{sum(p['kind'] == 'mcq' for p in gp)} MCQ sets</span></div>
</a>""")
    body = f"""<section class="hero">
  <h1>{esc(site['name'])}</h1>
  <p>{esc(site['tagline'])}</p>
  <form class="hero-search" action="/search.html" role="search">
    <input type="search" name="q" placeholder="Search a topic, e.g. “surface tension”" aria-label="Search topics">
    <button class="btn">Search</button>
  </form>
  <div class="stats"><div><b>{n_notes}</b><span>note sets</span></div><div><b>{len(posts) - n_notes}</b><span>MCQ sets</span></div><div><b>{n_questions}</b><span>practice questions</span></div></div>
</section>
<section class="section">
  <div class="section-head"><h2>Choose your grade</h2></div>
  <div class="grade-cards">{''.join(grade_cards)}</div>
</section>
<section class="section">
  <div class="section-head"><h2>Recently added</h2><a href="/search.html">Browse all →</a></div>
  <div class="grid">{''.join(card(data, p) for p in posts[:6])}</div>
</section>"""
    return shell(data, title=site["name"], body=body, path="")


def build_grade(data, posts, g):
    site, grade = data["site"], data["grades"][g]
    gp = [p for p in posts if p["grade"] == g]
    out, area = [], None
    for ch in grade["syllabus"]:
        if ch["area"] != area:
            area = ch["area"]
            out.append(f'<h2 class="area">{esc(area)}</h2>')
        mine = sorted((p for p in gp if ch["n"] in p["chapters"]), key=lambda p: (p["kind"] != "notes", p["title"]))
        counts = "".join(f'<span class="badge {k}">{sum(p["kind"] == k for p in mine)} {KIND_LABEL[k]}</span>'
                         for k in KIND_LABEL if any(p["kind"] == k for p in mine))
        links = "".join(f'<a class="chip {p["kind"]}" href="{post_url(p)}">{KIND_ICON[p["kind"]]} {esc(p["title"])}</a>' for p in mine)
        if not mine:
            links = '<span class="chip soon">Notes &amp; MCQs coming soon</span>'
        links += f'<a class="chip video" href="{site["youtube"]}" target="_blank" rel="noopener">▶ Videos</a>'
        topics = "".join(f"<li>{t}</li>" for t in ch["topics"])
        out.append(f"""<details class="chapter" id="ch-{ch['n']}"{' open' if mine else ''}>
  <summary><span class="num">{ch['n']}</span>{esc(ch['title'])}<span class="counts">{counts}</span></summary>
  <div class="chapter-body"><ul>{topics}</ul><div class="chapter-links">{links}</div></div>
</details>""")
    body = f"""<div class="crumbs"><a href="/">Home</a> › {esc(grade['title'])}</div>
<section class="hero">
  <h1>{esc(grade['title'])}</h1>
  <p>Complete {esc(site['curriculum'])} syllabus — open a chapter for its topics, notes and MCQ practice.</p>
  <div class="stats"><div><b>{len(grade['syllabus'])}</b><span>chapters</span></div><div><b>{grade['hours']}</b><span>teaching hours</span></div><div><b>{len(gp)}</b><span>lessons</span></div></div>
</section>
{''.join(out)}"""
    return shell(data, title=grade["title"], body=body, path=f"pages/{GRADE_SLUG[g]}.html", current=g,
                 description=f"{grade['title']} — full NEB syllabus with notes and MCQ practice for every chapter.")


def build_search(data):
    body = """<div class="crumbs"><a href="/">Home</a> › All lessons</div>
<h1>All lessons</h1>
<form id="search-form" class="search-box" role="search">
  <input id="q" type="search" placeholder="Search topics…" aria-label="Search topics">
  <button class="btn">Search</button>
</form>
<div id="filters" class="filters" role="group" aria-label="Filter by type">
  <button type="button" data-kind="all">All</button><button type="button" data-kind="notes">Notes</button><button type="button" data-kind="mcq">MCQs</button>
</div>
<h2 class="sr-only">Results</h2>
<div id="results" class="grid" aria-live="polite"></div>"""
    return shell(data, title="All lessons", body=body, path="search.html", current="search", scripts=("search",))


def build_404(data):
    body = """<section class="hero"><h1>Page not found</h1><p>That page has moved or never existed. Try searching for the topic instead.</p>
<form class="hero-search" action="/search.html" role="search"><input type="search" name="q" placeholder="Search topics…" aria-label="Search topics"><button class="btn">Search</button></form></section>"""
    return shell(data, title="Page not found", body=body, path="404.html", noindex=True)


def build_search_index(data, posts):
    items = []
    for p in posts:
        chaps = chapter_of(data, p)
        words = [p["title"], p.get("description", ""), p["kind"], "notes" if p["kind"] == "notes" else "mcq mcqs questions practice",
                 f"grade {p['grade']}", p["slug"].replace("-", " ")]
        for c in chaps:
            words += [c["title"], c["area"], *[plain(t) for t in c["topics"]]]
        items.append({"title": p["title"], "url": post_url(p), "kind": p["kind"], "grade": p["grade"],
                      "chapter": ", ".join(c["title"] for c in chaps), "date": p["date"],
                      "haystack": re.sub(r"[^a-z0-9 ]+", " ", " ".join(words).lower())})
    items.sort(key=lambda x: (x["grade"] != "XI", x["title"]))
    return json.dumps(items, ensure_ascii=False, indent=1) + "\n"


def build_sitemap(data, posts):
    site = data["site"]
    rows = [("", None), ("search.html", None)] + [(f"pages/{s}.html", None) for s in GRADE_SLUG.values()]
    rows += [(post_url(p)[1:], p["date"]) for p in posts]
    urls = "".join(f"  <url><loc>{site['url']}/{u}</loc>{f'<lastmod>{d}</lastmod>' if d else ''}</url>\n" for u, d in rows)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def build_styleguide(data, posts):
    """docs/examples/example-notes.html rendered like a real lesson, so the components can be previewed."""
    example = ROOT / "docs/examples/example-notes.html"
    problems = Problems()
    meta, body = parse_front_matter(example.read_text(encoding="utf-8"), "docs/examples/example-notes.html", problems)
    validate_meta(meta, "docs/examples/example-notes.html", data["grades"], problems)
    if problems:
        raise SystemExit("\n".join(problems))
    meta.update(slug="styleguide", kind="notes", body=body, file="docs/examples/example-notes.html")
    return build_notes(data, [], meta, path="styleguide.html", noindex=True)


# ---------------------------------------------------------------- main

def write(rel, text):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data, posts, problems = load()
    if problems:
        print(f"Found {len(problems)} problem(s) — nothing was built:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    if "--check" in sys.argv:
        print(f"OK: {len(posts)} lessons are valid.")
        return

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    write("index.html", build_index(data, posts))
    write("search.html", build_search(data))
    write("404.html", build_404(data))
    write("styleguide.html", build_styleguide(data, posts))
    write("sitemap.xml", build_sitemap(data, posts))
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {data['site']['url']}/sitemap.xml\n")
    write("assets/search-index.json", build_search_index(data, posts))
    for g, slug in GRADE_SLUG.items():
        write(f"pages/{slug}.html", build_grade(data, posts, g))
    builders = {"mcq": build_mcq, "notes": build_notes, "legacy": build_legacy}
    for post in posts:
        write(f"posts/{post['slug']}.html", builders[post["format"]](data, posts, post))
    formats = {f: sum(p["format"] == f for p in posts) for f in builders}
    print(f"Built {len(posts)} lessons into public/ ({formats['mcq']} MCQ sets, {formats['notes']} notes, {formats['legacy']} legacy pages).")


if __name__ == "__main__":
    main()
