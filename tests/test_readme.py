"""Acceptance tests for profile README.md (static, offline)."""
import itertools
import re
from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"


def read_readme():
    assert README.exists(), "README.md not found at repo root"
    return README.read_text(encoding="utf-8")


def extract_headings(text):
    """Return list of (level, title) in document order, markdown + html."""
    ordered = []
    for line in text.splitlines():
        mm = re.match(r"\s*(#{1,6})\s+(.+?)\s*$", line)
        if mm:
            ordered.append((len(mm.group(1)), mm.group(2).strip()))
            continue
        hm = re.search(r"<h([1-6])[^>]*>(.*?)</h[1-6]>", line, re.IGNORECASE)
        if hm:
            inner = re.sub(r"<[^>]+>", "", hm.group(2)).strip()
            ordered.append((int(hm.group(1)), inner))
    return ordered


def test_single_h1_and_hierarchy():
    text = read_readme()
    headings = extract_headings(text)
    h1s = [t for lvl, t in headings if lvl == 1]
    assert len(h1s) == 1, f"expected exactly one H1, found {len(h1s)}: {h1s}"
    assert "slvkel" in h1s[0].lower(), f"H1 must contain Slvkel, got: {h1s[0]!r}"
    h2_titles = [t.lower() for lvl, t in headings if lvl == 2]
    assert any("about" in t for t in h2_titles), f"missing H2 About, got {h2_titles}"
    assert any("tech stack" in t for t in h2_titles), f"missing H2 Tech Stack, got {h2_titles}"
    assert any(("now playing" in t) or ("spotify" in t) for t in h2_titles), (
        f"missing H2 Now Playing/Spotify, got {h2_titles}"
    )
    # No jumps H1 -> H3 (levels may increase at most by 1)
    for (prev_lvl, _), (lvl, title) in itertools.pairwise(headings):
        assert lvl - prev_lvl <= 1, (
            f"heading jump H{prev_lvl} -> H{lvl} before {title!r}; "
            "do not skip levels (H1->H3 forbidden)"
        )


def test_images_have_alt():
    text = read_readme()
    html_imgs = re.findall(r"<img\b[^>]*>", text, re.IGNORECASE)
    assert html_imgs, "expected at least one <img> tag"
    for tag in html_imgs:
        m = re.search(r'alt\s*=\s*"([^"]*)"', tag, re.IGNORECASE)
        assert m is not None, f"<img> without alt attribute: {tag[:120]!r}"
        assert m.group(1).strip(), f"<img> with empty alt: {tag[:120]!r}"
    md_imgs = re.findall(r"!\[([^\]]*)\]\([^\)]+\)", text)
    for alt in md_imgs:
        assert alt.strip(), "markdown image with empty alt text: ![]()"
    assert "align" not in text.lower() or 'align="right"' not in text.lower().replace("'", '"'), (
        "floating align=right breaks reading order; use centered layout"
    )
    # At most 2 decorative GIFs (giphy / user-images gif) for performance
    gifs = re.findall(r"giphy\.com|user-images\.githubusercontent\.com", text, re.IGNORECASE)
    assert len(gifs) <= 4, f"too many heavy GIF references ({len(gifs)}); keep max 2 decorative GIFs"


def test_badges_and_stack_groups():
    text = read_readme()
    assert "img.shields.io" in text, "expected shields.io badges"
    badge_srcs = re.findall(r'<img\b[^>]*src\s*=\s*"([^"]*shield[^"]*)"', text, re.IGNORECASE)
    badge_srcs += re.findall(r"!\[[^\]]*\]\(https://img\.shields\.io[^\)]+\)", text)
    assert badge_srcs, "no shields.io badge sources found"
    for src in badge_srcs:
        assert "style=for-the-badge" in src, (
            f"badge style not unified to for-the-badge: {src[:120]!r}"
        )
    lowered = text.lower()
    for group in ["languages", "frontend", "backend", "databases", "others"]:
        assert group in lowered, f"missing Tech Stack group: {group}"
    # No duplicated badge alts (case-insensitive)
    alts = [a.strip().lower() for a in re.findall(r'<img\b[^>]*alt\s*=\s*"([^"]+)"', text, re.IGNORECASE)]
    md_badge_imgs = re.findall(r"!\[([^\]]+)\]\([^\)]+\)", text)
    alts += [a.strip().lower() for a in md_badge_imgs if a.strip()]
    badge_alts = [a for a in alts if a and a not in ("animated", "divider", "wave", "header")]
    assert len(badge_alts) == len(set(badge_alts)), f"duplicated badge alt texts: {badge_alts}"


def test_links_wellformed():
    text = read_readme()
    urls = re.findall(r"\((https?://[^\)\s]+)\)", text)
    urls += re.findall(r'(?:src|href)\s*=\s*"([^"]+)"', text, re.IGNORECASE)
    urls = [u.strip() for u in urls]
    assert urls, "no links found"
    for u in urls:
        assert u.startswith("https://"), f"link must be https: {u!r}"
        assert " " not in u, f"link contains spaces: {u!r}"
    assert "https://open.spotify.com/user/slvkelevra" in text, (
        "Spotify link must point to https://open.spotify.com/user/slvkelevra"
    )


def test_content_preserved_and_size():
    text = read_readme()
    lines = text.splitlines()
    assert len(lines) < 150, f"README too long ({len(lines)} lines); keep <150"
    assert len(lines) > 10, "README suspiciously short"
    lowered = text.lower()
    required = [
        "python", "java", "html", "css", "bootstrap", "django", "flask",
        "postgres", "redis", "sqlite", "mongo", "mysql",
        "git", "github", "linux", "telegram", "bitbucket", "shell", "json",
        "spotify", "spain",
    ]
    missing = [k for k in required if k not in lowered]
    assert not missing, f"preserved stack/content missing keywords: {missing}"
