import os
import glob
import zipfile
import xml.etree.ElementTree as ET
import re

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def extract_paragraphs(docx_path):
    document = zipfile.ZipFile(docx_path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = ET.XML(xml_content)
    paragraphs = []
    for paragraph in tree.iter(WORD_NAMESPACE + 'p'):
        texts = [node.text for node in paragraph.iter(WORD_NAMESPACE + 't') if node.text]
        text = ''.join(texts).strip()
        if text:
            paragraphs.append(text)
    return paragraphs

def parse_chapter(file_path):
    paras = extract_paragraphs(file_path)
    
    # Heuristics for Title
    # Typically first few lines have Chapter X
    ch_number = "Chapter"
    ch_title = "Untitled"
    
    content_start = 0
    for i, p in enumerate(paras[:5]):
        if p.lower().startswith('chapter'):
            if ':' in p:
                parts = p.split(':', 1)
                ch_number = parts[0].strip()
                ch_title = parts[1].strip()
            elif '-' in p:
                parts = p.split('-', 1)
                ch_number = parts[0].strip()
                ch_title = parts[1].strip()
            elif '–' in p:
                parts = p.split('–', 1)
                ch_number = parts[0].strip()
                ch_title = parts[1].strip()
            else:
                ch_number = p.strip()
                if i + 1 < len(paras) and not paras[i+1].lower().startswith('chapter'):
                    ch_title = paras[i+1].strip()
                    content_start = i + 2
                    break
            content_start = i + 1
            
            # Keep searching if the next paragraph also starts with Chapter and has a better title
            # In CHAPTER 1.docx: "CHAPTER 1 : REALITY ENTITY", then "Chapter 1: The Day Reality Blinked"
            continue
            
    # Fallback to remove empty lines from start
    while content_start < len(paras) and not paras[content_start].strip():
        content_start += 1
        
    return ch_number, ch_title, paras[content_start:]

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{ch_number} — The Reality Entity | Luminae</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Cinzel+Decorative:wght@400;700&family=Raleway:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #0d0a1a; --parchment: #fdf8f0; --cream: #f5ede0;
    --gold: #c9933a; --gold-light: #e8c97a; --gold-glow: #f0d898;
    --violet: #6b3fa0; --violet-dark: #3d1f6e; --violet-light: #a67dd0;
    --rose: #c45a7a; --midnight: #0f0820; --mist: #c8bfe0; --star: #f8f0e3;
    --accent: #0ea5e9; --accent-glow: rgba(14,165,233,0.4);
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{ background: var(--midnight); color: var(--star); font-family: 'Raleway', sans-serif; font-weight: 300; overflow-x: hidden; min-height: 100vh; }}
  .starfield {{ position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }}
  .star-dot {{ position: absolute; border-radius: 50%; background: white; animation: twinkle var(--d, 3s) ease-in-out infinite; animation-delay: var(--delay, 0s); opacity: 0; }}
  @keyframes twinkle {{ 0%, 100% {{ opacity: 0; transform: scale(0.5); }} 50% {{ opacity: var(--op, 0.7); transform: scale(1); }} }}
  .top-nav {{ position: sticky; top: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 1rem 3rem; background: linear-gradient(to bottom, rgba(15,8,32,0.98), rgba(15,8,32,0.9)); backdrop-filter: blur(8px); border-bottom: 1px solid rgba(124,58,237,0.2); }}
  .logo {{ font-family: 'Cinzel Decorative', cursive; font-size: 1.1rem; color: var(--accent); letter-spacing: 0.08em; text-shadow: 0 0 20px var(--accent-glow); text-decoration: none; }}
  .nav-chapter-info {{ font-size: 0.7rem; color: var(--mist); letter-spacing: 0.1em; text-transform: uppercase; }}
  .toc-link {{ color: var(--accent); text-decoration: none; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; transition: color 0.3s; }}
  .toc-link:hover {{ color: #7c3aed; }}
  .reader-page {{ position: relative; z-index: 1; max-width: 720px; margin: 0 auto; padding: 4rem 2rem 3rem; }}
  .ch-header {{ text-align: center; margin-bottom: 3.5rem; padding-bottom: 2.5rem; border-bottom: 1px solid rgba(124,58,237,0.2); }}
  .ch-number {{ font-size: 0.65rem; letter-spacing: 0.4em; text-transform: uppercase; color: var(--accent); margin-bottom: 1.2rem; display: block; }}
  .ch-title {{ font-family: 'Cormorant Garamond', serif; font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 300; line-height: 1.15; color: var(--star); margin-bottom: 0.8rem; }}
  .ch-title em {{ font-style: italic; color: #7c3aed; text-shadow: 0 0 30px rgba(124,58,237,0.4); }}
  .ch-divider {{ display: flex; align-items: center; gap: 0.8rem; margin: 1.5rem auto 0; max-width: 160px; }}
  .ch-divider-line {{ flex: 1; height: 1px; background: linear-gradient(to right, transparent, rgba(124,58,237,0.5), transparent); }}
  .ch-divider-glyph {{ color: var(--accent); font-size: 0.8rem; }}
  .ch-content {{ font-family: 'Cormorant Garamond', serif; font-size: 1.18rem; color: var(--mist); line-height: 2; font-weight: 400; }}
  .ch-content p {{ margin-bottom: 1.5rem; }}
  .ch-content p.first::first-letter {{ font-family: 'Cinzel Decorative', cursive; font-size: 3.8rem; float: left; line-height: 1; margin: 0.05em 0.12em -0.1em 0; color: var(--accent); text-shadow: 0 0 20px var(--accent-glow); }}
  .ch-content em {{ color: #7c3aed; font-style: italic; }}
  .ch-content .dialogue {{ color: var(--star); }}
  .ch-content .thought {{ color: #0ea5e9; font-style: italic; }}
  .ch-content hr {{ border: none; text-align: center; margin: 2.5rem 0; }}
  .ch-content hr::after {{ content: '✦ ✦ ✦'; color: var(--accent); font-size: 0.7rem; letter-spacing: 0.5em; }}
  .author-note {{ background: rgba(0, 0, 0, 0.15); border: 1px solid rgba(124, 58, 237, 0.15); border-radius: 4px; padding: 2.5rem; margin-top: 4rem; }}
  .author-note .note-label {{ font-family: 'Raleway', sans-serif; font-size: 0.65rem; font-weight: 500; letter-spacing: 0.3em; text-transform: uppercase; color: #a67dd0; margin-bottom: 1.5rem; }}
  .author-note p {{ font-size: 1.15rem; color: var(--mist); line-height: 2; margin-bottom: 1rem; }}
  .author-note p:last-child {{ margin-bottom: 0; }}
  .ch-end {{ text-align: center; padding: 3rem 0 0; margin-top: 3rem; border-top: 1px solid rgba(124,58,237,0.2); }}
  .ch-end-text {{ font-family: 'Cormorant Garamond', serif; font-size: 0.85rem; font-style: italic; color: rgba(200,191,224,0.4); letter-spacing: 0.1em; margin-bottom: 2rem; }}
  .ch-nav {{ display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }}
  .ch-nav-btn {{ display: inline-flex; align-items: center; gap: 0.6rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(124,58,237,0.3); color: var(--star); padding: 0.8rem 1.8rem; font-family: 'Raleway', sans-serif; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none; transition: all 0.3s; border-radius: 2px; }}
  .ch-nav-btn:hover {{ background: rgba(124,58,237,0.15); border-color: rgba(14,165,233,0.5); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); }}
  .ch-nav-btn.disabled {{ opacity: 0.3; pointer-events: none; }}
  .ch-nav-toc {{ color: var(--accent); text-decoration: none; font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; transition: color 0.3s; }}
  .ch-nav-toc:hover {{ color: #7c3aed; }}
  .progress-wrap {{ position: fixed; top: 0; left: 0; right: 0; height: 2px; z-index: 100; background: rgba(0,0,0,0.3); }}
  .progress-fill {{ height: 100%; width: 0; background: linear-gradient(to right, #7c3aed, #0ea5e9); transition: width 0.1s; }}
  .fade-in {{ opacity: 0; transform: translateY(20px); animation: fadeUp 0.8s ease forwards; }}
  @keyframes fadeUp {{ to {{ opacity: 1; transform: translateY(0); }} }}
  .delay-1 {{ animation-delay: 0.15s; }}
  .delay-2 {{ animation-delay: 0.3s; }}
</style>
</head>
<body>

<div class="progress-wrap"><div class="progress-fill" id="progressFill"></div></div>
<div class="starfield" id="starfield"></div>

<nav class="top-nav">
  <a href="../index.html" class="logo">Luminae</a>
  <span class="nav-chapter-info">Chapter {ch_idx} of {total_chapters}</span>
  <a href="index.html" class="toc-link">☰ Chapters</a>
</nav>

<div class="reader-page">

  <header class="ch-header fade-in">
    <span class="ch-number">✦ {ch_number} ✦</span>
    <h1 class="ch-title">{ch_title}</h1>
    <div class="ch-divider">
      <div class="ch-divider-line"></div>
      <span class="ch-divider-glyph">✦</span>
      <div class="ch-divider-line"></div>
    </div>
  </header>

  <article class="ch-content fade-in delay-1">
{content_html}
  </article>

  <div class="ch-end fade-in delay-2">
    <p class="ch-end-text">— End of {ch_number} —</p>
    <div class="ch-nav">
      <a href="{prev_url}" class="ch-nav-btn {prev_disabled}">← Previous</a>
      <a href="index.html" class="ch-nav-toc">All Chapters</a>
      <a href="{next_url}" class="ch-nav-btn {next_disabled}">Next →</a>
    </div>
  </div>

</div>

<script>
const starfield = document.getElementById('starfield');
for (let i = 0; i < 60; i++) {{
  const s = document.createElement('div');
  s.className = 'star-dot';
  const size = Math.random() < 0.7 ? 1 : 2;
  s.style.cssText = `width:${{size}}px;height:${{size}}px;left:${{Math.random()*100}}%;top:${{Math.random()*100}}%;--d:${{2+Math.random()*4}}s;--delay:${{Math.random()*5}}s;--op:${{0.2+Math.random()*0.5}};`;
  starfield.appendChild(s);
}}
const progressFill = document.getElementById('progressFill');
window.addEventListener('scroll', () => {{
  const h = document.documentElement;
  const pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
  progressFill.style.width = Math.min(pct, 100) + '%';
}});
</script>
</body>
</html>
"""

def generate():
    files = sorted(glob.glob('The_Reality_Entity/*.docx'))
    total_chapters = len(files)
    chapters_info = []
    
    for idx, f in enumerate(files):
        ch_idx = idx + 1
        ch_number, ch_title, paras = parse_chapter(f)
        
        # Clean up title highlighting for visual flair
        words = ch_title.split()
        if len(words) > 1:
            words[-1] = f"<em>{words[-1]}</em>"
            ch_title = " ".join(words)
        else:
            ch_title = f"<em>{ch_title}</em>"
            
        content_html = ""
        in_author_note = False
        for i, p in enumerate(paras):
            if not in_author_note and re.match(r'^Author[\'’]s\s*Note', p.strip(), re.IGNORECASE):
                in_author_note = True
                content_html += '    <div class="author-note">\n'
                content_html += '      <div class="note-label">AUTHOR\'S NOTE</div>\n'
                continue
                
            # Format dialogue
            p = re.sub(r'([“"].*?[”"])', r'<span class="dialogue">\1</span>', p)
            # Format thought
            p = re.sub(r'(\'(.*?)\')', r'<span class="thought">\1</span>', p)
            
            if p.strip() in ['***', '---']:
                content_html += "    <hr>\n"
            else:
                css_class = ' class="first"' if i == 0 and not in_author_note else ''
                content_html += f"    <p{css_class}>{p}</p>\n"
                
        if in_author_note:
            content_html += "    </div>\n"
            
        prev_url = f"chapter{ch_idx-1}.html" if ch_idx > 1 else "#"
        next_url = f"chapter{ch_idx+1}.html" if ch_idx < total_chapters else "#"
        prev_disabled = "disabled" if ch_idx == 1 else ""
        next_disabled = "disabled" if ch_idx == total_chapters else ""
        
        html = html_template.format(
            ch_idx=ch_idx,
            total_chapters=total_chapters,
            ch_number=ch_number,
            ch_title=ch_title,
            content_html=content_html,
            prev_url=prev_url,
            next_url=next_url,
            prev_disabled=prev_disabled,
            next_disabled=next_disabled
        )
        
        out_name = f'The_Reality_Entity/chapter{ch_idx}.html'
        with open(out_name, 'w', encoding='utf-8') as out_f:
            out_f.write(html)
            
        chapters_info.append((ch_idx, ch_number, ch_title.replace('<em>', '').replace('</em>', '')))
        
    # Generate index.html
    index_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Reality Entity — Chapters | Luminae</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Cinzel+Decorative:wght@400;700&family=Raleway:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --ink: #0d0a1a; --parchment: #fdf8f0; --cream: #f5ede0;
    --gold: #c9933a; --gold-light: #e8c97a; --gold-glow: #f0d898;
    --violet: #6b3fa0; --violet-dark: #3d1f6e; --violet-light: #a67dd0;
    --rose: #c45a7a; --midnight: #0f0820; --mist: #c8bfe0; --star: #f8f0e3;
    --accent: #0ea5e9; --accent-glow: rgba(14,165,233,0.4);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body { background: var(--midnight); color: var(--star); font-family: 'Raleway', sans-serif; font-weight: 300; overflow-x: hidden; min-height: 100vh; }
  .starfield { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
  .star-dot { position: absolute; border-radius: 50%; background: white; animation: twinkle var(--d, 3s) ease-in-out infinite; animation-delay: var(--delay, 0s); opacity: 0; }
  @keyframes twinkle { 0%, 100% { opacity: 0; transform: scale(0.5); } 50% { opacity: var(--op, 0.7); transform: scale(1); } }
  .orb { position: fixed; border-radius: 50%; filter: blur(80px); pointer-events: none; z-index: 0; animation: drift var(--orb-d, 20s) ease-in-out infinite alternate; }
  .orb-1 { width: 400px; height: 400px; background: rgba(124,58,237,0.25); top: -10%; left: -10%; --orb-d: 18s; }
  .orb-2 { width: 300px; height: 300px; background: rgba(14,165,233,0.2); bottom: 20%; right: -5%; --orb-d: 23s; }
  @keyframes drift { from { transform: translate(0,0) scale(1); } to { transform: translate(30px,-20px) scale(1.1); } }
  .top-nav { position: relative; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 1.5rem 3rem; border-bottom: 1px solid rgba(124,58,237,0.2); }
  .logo { font-family: 'Cinzel Decorative', cursive; font-size: 1.3rem; color: var(--accent); letter-spacing: 0.08em; text-shadow: 0 0 20px var(--accent-glow); text-decoration: none; }
  .back-link { color: var(--mist); text-decoration: none; font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; transition: color 0.3s; display: flex; align-items: center; gap: 0.5rem; }
  .back-link:hover { color: var(--accent); }
  .page { position: relative; z-index: 1; max-width: 860px; margin: 0 auto; padding: 0 2rem 5rem; }
  .book-hero { text-align: center; padding: 5rem 0 3rem; }
  .book-hero-tag { font-size: 0.65rem; letter-spacing: 0.4em; text-transform: uppercase; color: var(--accent); margin-bottom: 1.5rem; display: block; }
  .book-hero-title { font-family: 'Cormorant Garamond', serif; font-size: clamp(2.5rem, 6vw, 4.5rem); font-weight: 300; line-height: 1.1; color: var(--star); margin-bottom: 0.8rem; }
  .book-hero-title em { font-style: italic; color: #7c3aed; text-shadow: 0 0 40px rgba(124,58,237,0.4); }
  .book-hero-author { font-size: 0.82rem; letter-spacing: 0.15em; color: var(--mist); text-transform: uppercase; margin-bottom: 1rem; }
  .book-hero-genre { font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: #0ea5e9; }
  .hero-divider { display: flex; align-items: center; gap: 1rem; margin: 2.5rem auto; max-width: 240px; }
  .hero-divider-line { flex: 1; height: 1px; background: linear-gradient(to right, transparent, rgba(124,58,237,0.5), transparent); }
  .hero-divider-glyph { font-family: 'Cormorant Garamond', serif; color: var(--accent); font-size: 1.1rem; }
  .chapters-label { font-size: 0.68rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--accent); margin-bottom: 2rem; font-weight: 500; }
  .chapter-list { list-style: none; }
  .chapter-item { border-bottom: 1px solid rgba(124,58,237,0.15); }
  .chapter-item:first-child { border-top: 1px solid rgba(124,58,237,0.15); }
  .chapter-link { display: flex; align-items: center; justify-content: space-between; padding: 1.4rem 1.2rem; text-decoration: none; color: var(--star); transition: all 0.3s; position: relative; }
  .chapter-link::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(124,58,237,0.08), transparent); opacity: 0; transition: opacity 0.3s; }
  .chapter-link:hover { background: rgba(255,255,255,0.02); }
  .chapter-link:hover::before { opacity: 1; }
  .chapter-link:hover .chapter-arrow { transform: translateX(4px); color: var(--accent); }
  .chapter-left { display: flex; align-items: center; gap: 1.2rem; position: relative; z-index: 1; }
  .chapter-num { font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 300; color: #7c3aed; min-width: 32px; }
  .chapter-name { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 400; margin-bottom: 0.2rem; }
  .chapter-meta { font-size: 0.7rem; color: var(--mist); letter-spacing: 0.05em; }
  .chapter-arrow { font-size: 0.9rem; color: var(--mist); transition: all 0.3s; position: relative; z-index: 1; }
  .toc-footer { border-top: 1px solid rgba(124,58,237,0.2); padding: 2rem 0; margin-top: 3rem; text-align: center; }
  .toc-footer-text { font-size: 0.7rem; color: rgba(200,191,224,0.35); letter-spacing: 0.1em; }
  .fade-in { opacity: 0; transform: translateY(20px); animation: fadeUp 0.8s ease forwards; }
  @keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }
  .delay-2 { animation-delay: 0.2s; }
</style>
</head>
<body>

<div class="starfield" id="starfield"></div>
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>

<nav class="top-nav">
  <a href="../index.html" class="logo">Luminae</a>
  <a href="../index.html" class="back-link">&larr; Back to Home</a>
</nav>

<div class="page">
  <section class="book-hero fade-in">
    <span class="book-hero-tag">✦ Now Reading ✦</span>
    <h1 class="book-hero-title">The Reality <em>Entity</em></h1>
    <p class="book-hero-author">by Lance Ames</p>
    <p class="book-hero-genre">Sci-Fi · Parallel Timelines · Psychological</p>
    <div class="hero-divider">
      <div class="hero-divider-line"></div>
      <span class="hero-divider-glyph">✦</span>
      <div class="hero-divider-line"></div>
    </div>
  </section>

  <section class="fade-in delay-2">
    <p class="chapters-label">Chapters</p>
    <ol class="chapter-list">
"""
    for ch_idx, ch_number, ch_title in chapters_info:
        index_template += f"""      <li class="chapter-item">
        <a href="chapter{ch_idx}.html" class="chapter-link">
          <div class="chapter-left">
            <span class="chapter-num">{ch_idx}</span>
            <div class="chapter-info">
              <div class="chapter-name">{ch_title}</div>
              <div class="chapter-meta">~5 min read</div>
            </div>
          </div>
          <span class="chapter-arrow">→</span>
        </a>
      </li>\n"""
      
    index_template += """    </ol>
  </section>

  <div class="toc-footer">
    <p class="toc-footer-text">✦ More chapters coming soon ✦</p>
  </div>
</div>

<script>
const starfield = document.getElementById('starfield');
for (let i = 0; i < 80; i++) {
  const s = document.createElement('div');
  s.className = 'star-dot';
  const size = Math.random() < 0.7 ? 1 : Math.random() < 0.5 ? 2 : 3;
  s.style.cssText = `width:${size}px;height:${size}px;left:${Math.random()*100}%;top:${Math.random()*100}%;--d:${2+Math.random()*4}s;--delay:${Math.random()*5}s;--op:${0.3+Math.random()*0.7};`;
  starfield.appendChild(s);
}
</script>
</body>
</html>"""

    with open('The_Reality_Entity/index.html', 'w', encoding='utf-8') as out_f:
        out_f.write(index_template)

if __name__ == '__main__':
    generate()
