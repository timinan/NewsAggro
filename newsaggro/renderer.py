"""HTML renderer. Pure Python template, no LLM call.

Takes the structured pipeline output (stories + intro) and produces a
self-contained HTML document with the canonical NewsAggro design.
"""
from html import escape
from .fetchers import Story


def render_html(
    stories: list[Story],
    date_str: str,
    intro: str,
) -> str:
    """Render the pipeline output to a complete HTML page."""
    stories_html = "\n".join(_render_story(s) for s in stories)
    return _PAGE.format(
        date=escape(date_str),
        intro=escape(intro) if intro else "",
        stories_html=stories_html,
        stories_count=len(stories),
    )


def _render_story(story: Story) -> str:
    title = escape(story.get("title", "(untitled)"))
    url = escape(story.get("url", "#"))
    source = escape(story.get("source", ""))
    summary = escape(story.get("summary") or "")
    detailed = story.get("detailed_summary") or ""
    image_url = story.get("image_url")

    image_html = (
        f'<img class="story-image" src="{escape(image_url)}" alt="{title}" loading="lazy">'
        if image_url
        else f'<div class="story-image-placeholder">{source}</div>'
    )

    details_block = ""
    if detailed:
        details_block = (
            f'<details>\n'
            f'  <summary>More details</summary>\n'
            f'  <p class="details-body">{escape(detailed)}</p>\n'
            f'</details>'
        )

    return f'''<article class="story">
  <span class="source-pill">{source}</span>
  <h2><a href="{url}" target="_blank" rel="noopener">{title}</a></h2>
  {image_html}
  <p class="summary">{summary}</p>
  {details_block}
</article>'''


_PAGE = """<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NewsAggro — Daily Brief {date}</title>
<style>
  :root {{
    --bg: #0a0a0b;
    --surface: #15151a;
    --surface-hover: #1c1c22;
    --text: #e8e8ea;
    --text-strong: #ffffff;
    --muted: #8a8a92;
    --muted-2: #6b6b73;
    --border: rgba(255,255,255,0.08);
    --border-strong: rgba(255,255,255,0.12);
    --pill-bg: rgba(255,255,255,0.06);
    --accent-bg: rgba(255,255,255,0.03);
    --link: #74a8ff;
    --accent: #4ade80;
  }}
  :root[data-theme="light"] {{
    --bg: #f4f4f7;
    --surface: #ffffff;
    --surface-hover: #fafafc;
    --text: #1a1a1d;
    --text-strong: #000000;
    --muted: #6b7280;
    --muted-2: #9ca3af;
    --border: rgba(0,0,0,0.08);
    --border-strong: rgba(0,0,0,0.12);
    --pill-bg: rgba(0,0,0,0.05);
    --accent-bg: rgba(0,0,0,0.025);
    --link: #2563eb;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    transition: background 0.18s, color 0.18s;
  }}
  a {{ color: var(--link); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  header {{
    max-width: 880px;
    margin: 0 auto;
    padding: 28px 24px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }}
  .wordmark {{
    font-weight: 800;
    font-size: 19px;
    letter-spacing: -0.4px;
    color: var(--text-strong);
  }}
  .wordmark .dot {{ color: var(--accent); margin-left: 1px; }}
  .header-controls {{
    display: flex;
    gap: 8px;
    align-items: center;
  }}
  .refresh-btn {{
    background: var(--accent);
    color: #0a0a0b;
    border: none;
    border-radius: 10px;
    padding: 9px 14px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    line-height: 1;
    transition: filter 0.15s, transform 0.1s;
  }}
  .refresh-btn:hover:not(:disabled) {{ filter: brightness(1.08); }}
  .refresh-btn:active:not(:disabled) {{ transform: translateY(1px); }}
  .refresh-btn:disabled {{ opacity: 0.7; cursor: progress; }}
  .theme-toggle {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    cursor: pointer;
    font-size: 15px;
    padding: 7px 11px;
    line-height: 1;
    transition: background 0.15s, border-color 0.15s;
  }}
  .theme-toggle:hover {{ background: var(--surface-hover); border-color: var(--border-strong); }}

  main {{ max-width: 880px; margin: 0 auto; padding: 0 24px; }}

  .status {{
    color: var(--muted);
    font-size: 13px;
    margin: 8px 0 0 0;
    min-height: 18px;
    text-align: right;
  }}

  .hero {{ margin: 32px 0 36px; }}
  .hero time {{
    display: block;
    color: var(--muted);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    margin-bottom: 12px;
    font-weight: 500;
  }}
  .hero h1 {{
    font-size: clamp(38px, 6vw, 60px);
    margin: 0 0 18px;
    letter-spacing: -1.8px;
    font-weight: 800;
    color: var(--text-strong);
    line-height: 1.05;
  }}
  .hero .intro {{
    margin: 0;
    font-size: clamp(16px, 1.6vw, 18px);
    color: var(--muted);
    max-width: 680px;
  }}

  .stories {{
    display: flex;
    flex-direction: column;
    gap: 22px;
    padding-bottom: 48px;
  }}
  .story {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 26px 28px 22px;
    transition: background 0.18s, border-color 0.18s, transform 0.18s;
  }}
  .story:hover {{
    background: var(--surface-hover);
    border-color: var(--border-strong);
    transform: translateY(-1px);
  }}
  .source-pill {{
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    color: var(--muted);
    padding: 5px 11px;
    border-radius: 999px;
    background: var(--pill-bg);
    margin-bottom: 14px;
  }}
  .story h2 {{
    font-size: clamp(20px, 2.6vw, 26px);
    font-weight: 700;
    margin: 0 0 18px;
    line-height: 1.28;
    letter-spacing: -0.4px;
  }}
  .story h2 a {{
    color: var(--text-strong);
    text-decoration: none;
  }}
  .story h2 a:hover {{
    color: var(--link);
    text-decoration: none;
  }}
  .story-image {{
    display: block;
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 10px;
    margin: 0 0 18px;
    background: var(--accent-bg);
  }}
  .story-image-placeholder {{
    width: 100%;
    aspect-ratio: 16 / 9;
    border-radius: 10px;
    margin: 0 0 18px;
    background: linear-gradient(135deg, #2a2a35, #1f1f28);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--muted);
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }}
  .summary {{
    color: var(--text);
    margin: 0 0 6px;
    font-size: 15.5px;
    line-height: 1.65;
  }}

  details {{ margin: 0; }}
  details summary {{
    cursor: pointer;
    list-style: none;
    color: var(--muted);
    font-size: 13px;
    font-weight: 600;
    padding: 8px 0;
    user-select: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: color 0.15s;
  }}
  details summary::-webkit-details-marker {{ display: none; }}
  details summary::before {{
    content: "▸";
    font-size: 10px;
    color: var(--muted-2);
    transition: transform 0.15s;
    display: inline-block;
  }}
  details[open] summary::before {{ transform: rotate(90deg); }}
  details summary:hover {{ color: var(--text); }}
  .details-body {{
    color: var(--muted);
    font-size: 14.5px;
    line-height: 1.65;
    padding: 8px 0 12px;
  }}

  footer {{
    max-width: 880px;
    margin: 0 auto;
    padding: 24px 24px 40px;
    color: var(--muted-2);
    font-size: 12px;
    border-top: 1px solid var(--border);
    text-align: center;
    letter-spacing: 0.4px;
  }}

  @media (max-width: 640px) {{
    .hero {{ margin: 28px 0; }}
    .story {{ padding: 22px 20px 18px; }}
  }}
</style>
</head>
<body>

<header>
  <div class="wordmark">NewsAggro<span class="dot">•</span></div>
  <div class="header-controls">
    <button class="refresh-btn" id="refreshBtn">🔄 Refresh</button>
    <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">☀</button>
  </div>
</header>
<div style="max-width: 880px; margin: 0 auto; padding: 0 24px;">
  <div class="status" id="status"></div>
</div>

<main>
  <section class="hero">
    <time datetime="{date}">{date}</time>
    <h1>Daily Brief</h1>
    <p class="intro">{intro}</p>
  </section>
  <section class="stories">
{stories_html}
  </section>
</main>

<footer>
  Generated by NewsAggro · {stories_count} stories · {date}
</footer>

<script>
(function() {{
  const html = document.documentElement;
  const themeBtn = document.getElementById('themeToggle');
  const stored = localStorage.getItem('newsaggro-theme');
  if (stored) html.dataset.theme = stored;
  function refreshIcon() {{
    themeBtn.textContent = html.dataset.theme === 'dark' ? '☀' : '🌙';
  }}
  refreshIcon();
  themeBtn.addEventListener('click', () => {{
    const next = html.dataset.theme === 'dark' ? 'light' : 'dark';
    html.dataset.theme = next;
    localStorage.setItem('newsaggro-theme', next);
    refreshIcon();
  }});

  const refreshBtn = document.getElementById('refreshBtn');
  const status = document.getElementById('status');
  refreshBtn.addEventListener('click', async () => {{
    refreshBtn.disabled = true;
    refreshBtn.textContent = '⏳ Working...';
    status.textContent = 'Fetching, curating, summarizing...';
    try {{
      const res = await fetch('/api/generate', {{ method: 'POST' }});
      if (!res.ok) throw new Error('HTTP ' + res.status);
      status.textContent = '✓ Done. Loading new brief...';
      setTimeout(() => location.reload(), 300);
    }} catch (e) {{
      status.textContent = '✗ ' + (e.message || 'Error') + '. Try again.';
      refreshBtn.disabled = false;
      refreshBtn.textContent = '🔄 Refresh';
    }}
  }});
}})();
</script>

</body>
</html>"""
