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
<title>Chapter {ch_idx} — Always There 4U | Luminae</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Cinzel+Decorative:wght@400;700&family=Raleway:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #0d0a1a; --parchment: #fdf8f0; --cream: #f5ede0;
    --gold: #c9933a; --gold-light: #e8c97a; --gold-glow: #f0d898;
    --violet: #6b3fa0; --violet-dark: #3d1f6e; --violet-light: #a67dd0;
    --rose: #c45a7a; --midnight: #0f0820; --mist: #c8bfe0; --star: #f8f0e3;
    --accent: #f97316; --accent-glow: rgba(249,115,22,0.4);
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{ background: var(--midnight); color: var(--star); font-family: 'Raleway', sans-serif; font-weight: 300; overflow-x: hidden; min-height: 100vh; }}
  .starfield {{ position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }}
  .star-dot {{ position: absolute; border-radius: 50%; background: white; animation: twinkle var(--d, 3s) ease-in-out infinite; animation-delay: var(--delay, 0s); opacity: 0; }}
  @keyframes twinkle {{ 0%, 100% {{ opacity: 0; transform: scale(0.5); }} 50% {{ opacity: var(--op, 0.7); transform: scale(1); }} }}
  .top-nav {{ position: sticky; top: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 1rem 3rem; background: linear-gradient(to bottom, rgba(15,8,32,0.98), rgba(15,8,32,0.9)); backdrop-filter: blur(8px); border-bottom: 1px solid rgba(236,72,153,0.2); }}
  .logo {{ font-family: 'Cinzel Decorative', cursive; font-size: 1.1rem; color: var(--accent); letter-spacing: 0.08em; text-shadow: 0 0 20px var(--accent-glow); text-decoration: none; }}
  .nav-chapter-info {{ font-size: 0.7rem; color: var(--mist); letter-spacing: 0.1em; text-transform: uppercase; }}
  .toc-link {{ color: var(--accent); text-decoration: none; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; transition: color 0.3s; }}
  .toc-link:hover {{ color: #ec4899; }}
  .reader-page {{ position: relative; z-index: 1; max-width: 720px; margin: 0 auto; padding: 4rem 2rem 3rem; }}
  .ch-header {{ text-align: center; margin-bottom: 3.5rem; padding-bottom: 2.5rem; border-bottom: 1px solid rgba(236,72,153,0.2); }}
  .ch-number {{ font-size: 0.65rem; letter-spacing: 0.4em; text-transform: uppercase; color: var(--accent); margin-bottom: 1.2rem; display: block; }}
  .ch-title {{ font-family: 'Cormorant Garamond', serif; font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 300; line-height: 1.15; color: var(--star); margin-bottom: 0.8rem; }}
  .ch-title em {{ font-style: italic; color: #ec4899; text-shadow: 0 0 30px rgba(236,72,153,0.4); }}
  .ch-divider {{ display: flex; align-items: center; gap: 0.8rem; margin: 1.5rem auto 0; max-width: 160px; }}
  .ch-divider-line {{ flex: 1; height: 1px; background: linear-gradient(to right, transparent, rgba(236,72,153,0.5), transparent); }}
  .ch-divider-glyph {{ color: var(--accent); font-size: 0.8rem; }}
  .ch-content {{ font-family: 'Cormorant Garamond', serif; font-size: 1.18rem; color: var(--mist); line-height: 2; font-weight: 400; }}
  .ch-content p {{ margin-bottom: 1.5rem; }}
  .ch-content p.first::first-letter {{ font-family: 'Cinzel Decorative', cursive; font-size: 3.8rem; float: left; line-height: 1; margin: 0.05em 0.12em -0.1em 0; color: var(--accent); text-shadow: 0 0 20px var(--accent-glow); }}
  .ch-content em {{ color: #ec4899; font-style: italic; }}
  .ch-content .dialogue {{ color: var(--star); }}
  .ch-content .thought {{ color: #06b6d4; font-style: italic; }}
  .ch-content hr {{ border: none; text-align: center; margin: 2.5rem 0; }}
  .ch-content hr::after {{ content: '✦ ✦ ✦'; color: var(--accent); font-size: 0.7rem; letter-spacing: 0.5em; }}

  /* ═══ Chat / Text Message Bubbles ═══ */
  .chat-container {{
    position: relative;
    margin: 2rem 0;
    padding: 1.5rem 1.2rem;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(249, 115, 22, 0.12);
    border-radius: 16px;
    backdrop-filter: blur(6px);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.03);
  }}
  .chat-container::before {{
    content: '💬';
    position: absolute;
    top: -10px;
    left: 20px;
    font-size: 0.7rem;
    background: var(--midnight);
    padding: 0 0.5rem;
    color: rgba(249, 115, 22, 0.6);
    letter-spacing: 0.15em;
  }}
  .chat-bubble {{
    font-family: 'Raleway', sans-serif;
    font-size: 0.88rem;
    font-weight: 400;
    line-height: 1.6;
    padding: 0.7rem 1rem;
    border-radius: 14px;
    margin-bottom: 0.5rem;
    max-width: 80%;
    position: relative;
    animation: bubbleIn 0.3s ease forwards;
    word-wrap: break-word;
  }}
  @keyframes bubbleIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  .chat-received {{
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--mist);
    border-bottom-left-radius: 4px;
    margin-right: auto;
  }}
  .chat-sent {{
    background: linear-gradient(135deg, rgba(249, 115, 22, 0.15), rgba(236, 72, 153, 0.1));
    border: 1px solid rgba(249, 115, 22, 0.2);
    color: var(--star);
    border-bottom-right-radius: 4px;
    margin-left: auto;
    text-align: right;
  }}
  .chat-typing {{
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    color: rgba(200, 191, 224, 0.4);
    font-style: italic;
    padding: 0.3rem 0;
    margin-bottom: 0.3rem;
    letter-spacing: 0.05em;
  }}
  .author-note {{ background: rgba(0, 0, 0, 0.15); border: 1px solid rgba(236, 72, 153, 0.15); border-radius: 4px; padding: 2.5rem; margin-top: 4rem; }}
  .author-note .note-label {{ font-family: 'Raleway', sans-serif; font-size: 0.65rem; font-weight: 500; letter-spacing: 0.3em; text-transform: uppercase; color: #a67dd0; margin-bottom: 1.5rem; }}
  .author-note p {{ font-size: 1.15rem; color: var(--mist); line-height: 2; margin-bottom: 1rem; }}
  .author-note p:last-child {{ margin-bottom: 0; }}
  .ch-end {{ text-align: center; padding: 3rem 0 0; margin-top: 3rem; border-top: 1px solid rgba(236,72,153,0.2); }}
  .ch-end-text {{ font-family: 'Cormorant Garamond', serif; font-size: 0.85rem; font-style: italic; color: rgba(200,191,224,0.4); letter-spacing: 0.1em; margin-bottom: 2rem; }}
  .ch-nav {{ display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }}
  .ch-nav-btn {{ display: inline-flex; align-items: center; gap: 0.6rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(236,72,153,0.3); color: var(--star); padding: 0.8rem 1.8rem; font-family: 'Raleway', sans-serif; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none; transition: all 0.3s; border-radius: 2px; }}
  .ch-nav-btn:hover {{ background: rgba(236,72,153,0.15); border-color: rgba(249,115,22,0.5); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); }}
  .ch-nav-btn.disabled {{ opacity: 0.3; pointer-events: none; }}
  .ch-nav-toc {{ color: var(--accent); text-decoration: none; font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; transition: color 0.3s; }}
  .ch-nav-toc:hover {{ color: #ec4899; }}
  .progress-wrap {{ position: fixed; top: 0; left: 0; right: 0; height: 2px; z-index: 100; background: rgba(0,0,0,0.3); }}
  .progress-fill {{ height: 100%; width: 0; background: linear-gradient(to right, #ec4899, #f97316); transition: width 0.1s; }}
  .fade-in {{ opacity: 0; transform: translateY(20px); animation: fadeUp 0.8s ease forwards; }}
  @keyframes fadeUp {{ to {{ opacity: 1; transform: translateY(0); }} }}
  .delay-1 {{ animation-delay: 0.15s; }}
  .delay-2 {{ animation-delay: 0.3s; }}
  body {{ cursor: none; }}
  .cursor {{ position:fixed; width:8px; height:8px; background:#f97316; border-radius:50%; pointer-events:none; z-index:9999; transform:translate(-50%,-50%); transition:transform 0.1s, background 0.3s; box-shadow:0 0 12px rgba(249,115,22,0.6); }}
  .cursor-ring {{ position:fixed; width:32px; height:32px; border:1px solid rgba(249,115,22,0.4); border-radius:50%; pointer-events:none; z-index:9998; transform:translate(-50%,-50%); transition:all 0.18s ease; }}
</style>
</head>
<body>

<div class="cursor" id="cursor"></div>
<div class="cursor-ring" id="cursorRing"></div>

<div class="progress-wrap"><div class="progress-fill" id="progressFill"></div></div>
<div class="starfield" id="starfield"></div>

<nav class="top-nav">
  <a href="../index.html" class="logo">Luminae</a>
  <span class="nav-chapter-info">Chapter {ch_idx} of {total_chapters}</span>
  <a href="index.html" class="toc-link">☰ Chapters</a>
</nav>

<div class="reader-page">

  <header class="ch-header fade-in">
    <span class="ch-number">✦ Chapter {ch_idx} ✦</span>
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
    <p class="ch-end-text">— End of Chapter {ch_idx} —</p>
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

const cursor = document.getElementById('cursor'), cursorRing = document.getElementById('cursorRing');
let mx = 0, my = 0, rx = 0, ry = 0;
document.addEventListener('mousemove', e => {{ mx = e.clientX; my = e.clientY; cursor.style.left = mx + 'px'; cursor.style.top = my + 'px'; }});
function animRing() {{ rx += (mx - rx) * 0.12; ry += (my - ry) * 0.12; cursorRing.style.left = rx + 'px'; cursorRing.style.top = ry + 'px'; requestAnimationFrame(animRing); }}
animRing();
document.querySelectorAll('a, button, .ch-nav-btn').forEach(el => {{
  el.addEventListener('mouseenter', () => {{ cursor.style.transform = 'translate(-50%,-50%) scale(2)'; cursorRing.style.transform = 'translate(-50%,-50%) scale(1.5)'; cursorRing.style.borderColor = 'rgba(249,115,22,0.7)'; }});
  el.addEventListener('mouseleave', () => {{ cursor.style.transform = 'translate(-50%,-50%) scale(1)'; cursorRing.style.transform = 'translate(-50%,-50%) scale(1)'; cursorRing.style.borderColor = 'rgba(249,115,22,0.4)'; }});
}});
</script>
</body>
</html>
"""

def generate():
    files = sorted(glob.glob('AlwaysThere4U/*.docx'))
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
        in_chat = False
        ethan_is_sender = False
        
        for i, p in enumerate(paras):
            if not in_author_note and re.match(r'^Author[\'’]s\s*Note', p.strip(), re.IGNORECASE):
                in_author_note = True
                if in_chat:
                    content_html += '    </div>\n'
                    in_chat = False
                content_html += '    <div class="author-note">\n'
                content_html += '      <div class="note-label">AUTHOR\'S NOTE</div>\n'
                continue
            
            stripped = p.strip()
            # Handle lines with inline brackets like "He typed: [text]" or "[text] Ethan typed"
            # Extract all bracketed messages from a line
            inline_match = re.findall(r'\[([^\]]+)\]', stripped)
            
            if inline_match and not stripped.startswith('['):
                # This is a mixed line like "He typed: [text]" — render prose with embedded chat
                # First check if Ethan is the speaker
                line_lower = stripped.lower()
                is_ethan = any(kw in line_lower for kw in ['ethan typed', 'he typed', 'then typed', 'he replied'])
                
                # Remove the bracketed text to get the prose part
                prose_part = re.sub(r'\s*\[[^\]]+\]\s*', ' ', stripped).strip()
                if prose_part and prose_part not in ['.', ',']:
                    p_fmt = re.sub(r'([""].*?[""])', r'<span class="dialogue">\1</span>', prose_part)
                    content_html += f"    <p>{p_fmt}</p>\n"
                
                bubble_class = 'chat-sent' if is_ethan else 'chat-received'
                content_html += '    <div class="chat-container">\n'
                for msg in inline_match:
                    content_html += f'    <div class="chat-bubble {bubble_class}">{msg.strip()}</div>\n'
                content_html += '    </div>\n'
                continue
            
            # Detect pure chat messages: lines starting with [
            is_chat_start = stripped.startswith('[')
            has_closing = ']' in stripped
            
            if is_chat_start:
                # Determine sender from context
                prev_text = paras[i-1].strip().lower() if i > 0 else ''
                if any(kw in prev_text for kw in ['ethan typed', 'he typed', 'then typed', 'he replied', 'still, he replied', 'ethan sat', 'he typed honestly', 'ethan exhaled']):
                    ethan_is_sender = True
                elif any(kw in prev_text for kw in ['she replied', 'long pause', 'typing bubbles', 'typing…', 'three dots', 'message from', 'new notification', 'first unread', 'more messages', 'a breakup']):
                    ethan_is_sender = False
                elif not any(kw in prev_text for kw in ['ethan', 'he typed', 'he replied', 'then typed']):
                    ethan_is_sender = False
                
                if not in_chat:
                    in_chat = True
                    content_html += '    <div class="chat-container">\n'
                
                # Extract message text, handling ] that might have trailing text like "] Ethan typed"
                msg = stripped[1:]  # Remove leading [
                
                # Check if ] is in this line  
                if ']' in msg:
                    bracket_pos = msg.index(']')
                    msg_text = msg[:bracket_pos].strip()
                    trailing = msg[bracket_pos+1:].strip()
                    
                    if msg_text:
                        # Check if trailing text indicates sender
                        if trailing.lower().startswith('ethan typed') or trailing.lower().startswith('he typed'):
                            ethan_is_sender = True
                        
                        bubble_class = 'chat-sent' if ethan_is_sender else 'chat-received'
                        content_html += f'    <div class="chat-bubble {bubble_class}">{msg_text}</div>\n'
                    
                    # Close this chat group since we found ]
                    in_chat = False
                    ethan_is_sender = False
                    content_html += '    </div>\n'
                    
                    # If there's meaningful trailing prose, add it
                    if trailing and not trailing.lower().startswith('ethan typed') and not trailing.lower().startswith('he typed'):
                        p_fmt = re.sub(r'([""].*?[""])', r'<span class="dialogue">\1</span>', trailing)
                        content_html += f"    <p>{p_fmt}</p>\n"
                else:
                    # No ] on this line — multi-line message
                    msg_text = msg.strip()
                    if msg_text:
                        bubble_class = 'chat-sent' if ethan_is_sender else 'chat-received'
                        content_html += f'    <div class="chat-bubble {bubble_class}">{msg_text}</div>\n'
                continue
            
            # Continuation of a multi-line chat (in_chat but no leading [)
            if in_chat:
                if ']' in stripped:
                    bracket_pos = stripped.index(']')
                    msg_text = stripped[:bracket_pos].strip()
                    if msg_text:
                        bubble_class = 'chat-sent' if ethan_is_sender else 'chat-received'
                        content_html += f'    <div class="chat-bubble {bubble_class}">{msg_text}</div>\n'
                    in_chat = False
                    ethan_is_sender = False
                    content_html += '    </div>\n'
                else:
                    bubble_class = 'chat-sent' if ethan_is_sender else 'chat-received'
                    content_html += f'    <div class="chat-bubble {bubble_class}">{stripped}</div>\n'
                continue
            
            # Handle typing indicators and status lines
            if stripped.lower() in ['seen.', 'typing…', 'typing bubbles appeared instantly.', 'typing bubbles appeared, disappeared, appeared again.', 'three dots appeared again.', 'long pause.']:
                content_html += f'    <div class="chat-typing">{p}</div>\n'
                continue

            # Format dialogue
            p = re.sub(r'([""].*?[""])', r'<span class="dialogue">\1</span>', p)
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
        
        out_name = f'AlwaysThere4U/chapter{ch_idx}.html'
        with open(out_name, 'w', encoding='utf-8') as out_f:
            out_f.write(html)
            
        chapters_info.append((ch_idx, ch_number, ch_title.replace('<em>', '').replace('</em>', '')))
        
    # Generate index.html
    index_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Always There 4U — Chapters | Luminae</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Cinzel+Decorative:wght@400;700&family=Raleway:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --ink: #0d0a1a; --parchment: #fdf8f0; --cream: #f5ede0;
    --gold: #c9933a; --gold-light: #e8c97a; --gold-glow: #f0d898;
    --violet: #6b3fa0; --violet-dark: #3d1f6e; --violet-light: #a67dd0;
    --rose: #c45a7a; --midnight: #0f0820; --mist: #c8bfe0; --star: #f8f0e3;
    --accent: #f97316; --accent-glow: rgba(249,115,22,0.4);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body { background: var(--midnight); color: var(--star); font-family: 'Raleway', sans-serif; font-weight: 300; overflow-x: hidden; min-height: 100vh; }
  .starfield { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
  .star-dot { position: absolute; border-radius: 50%; background: white; animation: twinkle var(--d, 3s) ease-in-out infinite; animation-delay: var(--delay, 0s); opacity: 0; }
  @keyframes twinkle { 0%, 100% { opacity: 0; transform: scale(0.5); } 50% { opacity: var(--op, 0.7); transform: scale(1); } }
  .orb { position: fixed; border-radius: 50%; filter: blur(80px); pointer-events: none; z-index: 0; animation: drift var(--orb-d, 20s) ease-in-out infinite alternate; }
  .orb-1 { width: 400px; height: 400px; background: rgba(236,72,153,0.25); top: -10%; left: -10%; --orb-d: 18s; }
  .orb-2 { width: 300px; height: 300px; background: rgba(249,115,22,0.2); bottom: 20%; right: -5%; --orb-d: 23s; }
  @keyframes drift { from { transform: translate(0,0) scale(1); } to { transform: translate(30px,-20px) scale(1.1); } }
  .top-nav { position: relative; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 1.5rem 3rem; border-bottom: 1px solid rgba(236,72,153,0.2); }
  .logo { font-family: 'Cinzel Decorative', cursive; font-size: 1.3rem; color: var(--accent); letter-spacing: 0.08em; text-shadow: 0 0 20px var(--accent-glow); text-decoration: none; }
  .back-link { color: var(--mist); text-decoration: none; font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; transition: color 0.3s; display: flex; align-items: center; gap: 0.5rem; }
  .back-link:hover { color: var(--accent); }
  .page { position: relative; z-index: 1; max-width: 1280px; margin: 0 auto; padding: 0 2rem 5rem; }
  .book-hero { text-align: center; padding: 5rem 0 3rem; }
  .book-hero-tag { font-size: 0.65rem; letter-spacing: 0.4em; text-transform: uppercase; color: var(--accent); margin-bottom: 1.5rem; display: block; }
  .book-hero-title { font-family: 'Cormorant Garamond', serif; font-size: clamp(2.5rem, 6vw, 4.5rem); font-weight: 300; line-height: 1.1; color: var(--star); margin-bottom: 0.8rem; }
  .book-hero-title em { font-style: italic; color: #ec4899; text-shadow: 0 0 40px rgba(236,72,153,0.4); }
  .book-hero-author { font-size: 0.82rem; letter-spacing: 0.15em; color: var(--mist); text-transform: uppercase; margin-bottom: 1rem; }
  .book-hero-genre { font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: #06b6d4; }
  .hero-divider { display: flex; align-items: center; gap: 1rem; margin: 2.5rem auto; max-width: 240px; }
  .hero-divider-line { flex: 1; height: 1px; background: linear-gradient(to right, transparent, rgba(236,72,153,0.5), transparent); }
  .hero-divider-glyph { font-family: 'Cormorant Garamond', serif; color: var(--accent); font-size: 1.1rem; }
  .chapters-label { font-size: 0.68rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--accent); margin-bottom: 2rem; font-weight: 500; }
  .chapter-list { list-style: none; }
  .chapter-item { border-bottom: 1px solid rgba(236,72,153,0.15); }
  .chapter-item:first-child { border-top: 1px solid rgba(236,72,153,0.15); }
  .chapter-link { display: flex; align-items: center; justify-content: space-between; padding: 1.4rem 1.2rem; text-decoration: none; color: var(--star); transition: all 0.3s; position: relative; }
  .chapter-link::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(236,72,153,0.08), transparent); opacity: 0; transition: opacity 0.3s; }
  .chapter-link:hover { background: rgba(255,255,255,0.02); }
  .chapter-link:hover::before { opacity: 1; }
  .chapter-link:hover .chapter-arrow { transform: translateX(4px); color: var(--accent); }
  .chapter-left { display: flex; align-items: center; gap: 1.2rem; position: relative; z-index: 1; }
  .chapter-num { font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 300; color: #ec4899; min-width: 32px; }
  .chapter-name { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 400; margin-bottom: 0.2rem; }
  .chapter-meta { font-size: 0.7rem; color: var(--mist); letter-spacing: 0.05em; }
  .chapter-arrow { font-size: 0.9rem; color: var(--mist); transition: all 0.3s; position: relative; z-index: 1; }
  .toc-footer { border-top: 1px solid rgba(236,72,153,0.2); padding: 2rem 0; margin-top: 3rem; text-align: center; }
  .toc-footer-text { font-size: 0.7rem; color: rgba(200,191,224,0.35); letter-spacing: 0.1em; }
  .fade-in { opacity: 0; transform: translateY(20px); animation: fadeUp 0.8s ease forwards; }
  @keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }
  .delay-2 { animation-delay: 0.2s; }
  body { cursor: none; }
  .cursor { position:fixed; width:8px; height:8px; background:var(--accent); border-radius:50%; pointer-events:none; z-index:9999; transform:translate(-50%,-50%); transition:transform 0.1s, background 0.3s; box-shadow:0 0 12px var(--accent-glow); }
  .cursor-ring { position:fixed; width:32px; height:32px; border:1px solid rgba(249,115,22,0.4); border-radius:50%; pointer-events:none; z-index:9998; transform:translate(-50%,-50%); transition:all 0.18s ease; }

  /* ═══════════════════════════════════════════════════
     CHARACTERS SECTION
  ═══════════════════════════════════════════════════ */
  :root {
    --tl-a: #ec4899;
    --tl-a-glow: rgba(236,72,153,0.5);
    --tl-b: #f97316;
    --tl-b-glow: rgba(249,115,22,0.5);
  }
  .characters-section { position: relative; z-index: 2; padding: 1.5rem 0 4rem; overflow: visible; width: 100%; margin-bottom: 4rem; }
  .characters-header { text-align: center; margin-bottom: 3.5rem; }
  .characters-eyebrow { font-size: 0.55rem; letter-spacing: 0.5em; text-transform: uppercase; color: var(--accent); display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem; }
  .characters-eyebrow::before, .characters-eyebrow::after { content: ''; display: block; width: 40px; height: 1px; background: linear-gradient(to right, transparent, var(--accent)); opacity: 0.5; }
  .characters-eyebrow::after { transform: scaleX(-1); }
  .characters-title { font-family: 'Cormorant Garamond', serif; font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 300; color: var(--star); letter-spacing: 0.05em; margin-bottom: 0.6rem; }
  .characters-subtitle { font-size: 0.65rem; letter-spacing: 0.25em; text-transform: uppercase; color: rgba(200,191,224,0.4); }
  .char-particles { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
  .char-particle { position: absolute; border-radius: 50%; pointer-events: none; animation: float-particle var(--fp-d, 8s) ease-in-out infinite; animation-delay: var(--fp-delay, 0s); }
  @keyframes float-particle { 0%, 100% { transform: translateY(0) scale(1); opacity: var(--fp-op, 0.3); } 50% { transform: translateY(-20px) scale(1.2); opacity: calc(var(--fp-op, 0.3) * 1.6); } }
  .char-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.25rem; position: relative; z-index: 1; max-width: 700px; margin: 0 auto; padding: 0 1rem; }
  @media (max-width: 600px) { .char-grid { grid-template-columns: 1fr; max-width: 340px; } }
  .char-card { position: relative; aspect-ratio: 2/3; min-height: 320px; border-radius: 18px; overflow: hidden; cursor: pointer; transform-style: preserve-3d; transition: transform 0.08s linear; will-change: transform; background: #0a071a; box-shadow: 0 4px 30px rgba(0,0,0,0.5), 0 0 1px rgba(255,255,255,0.05); }
  .char-portrait { position: absolute; inset: 0; background-size: cover; background-position: center top; transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94), filter 0.5s ease; filter: saturate(0.7) brightness(0.65); will-change: transform, filter; }
  .char-card:hover .char-portrait { transform: scale(1.08); filter: saturate(1) brightness(0.5); }
  .char-overlay-base { position: absolute; inset: 0; background: linear-gradient(to top, rgba(7,4,15,0.98) 0%, rgba(7,4,15,0.85) 30%, rgba(7,4,15,0.4) 55%, transparent 100%); z-index: 1; transition: opacity 0.5s ease; }
  .char-card:hover .char-overlay-base { opacity: 0.9; }
  .char-frame { position: absolute; inset: 0; z-index: 2; border-radius: 18px; border: 1px solid rgba(255,255,255,0.08); transition: border-color 0.5s ease, box-shadow 0.5s ease; pointer-events: none; }
  .char-card[data-tl="A"]:hover .char-frame { border-color: rgba(236,72,153,0.35); box-shadow: inset 0 0 30px rgba(236,72,153,0.08), 0 0 40px rgba(236,72,153,0.25); }
  .char-card[data-tl="B"]:hover .char-frame { border-color: rgba(249,115,22,0.35); box-shadow: inset 0 0 30px rgba(249,115,22,0.08), 0 0 40px rgba(249,115,22,0.25); }
  .char-corners { position: absolute; inset: 0; z-index: 3; pointer-events: none; }
  .char-corners::before, .char-corners::after { content: ''; position: absolute; width: 24px; height: 24px; opacity: 0; transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
  .char-corners::before { top: 12px; left: 12px; border-top: 2px solid currentColor; border-left: 2px solid currentColor; transform: translate(-6px, -6px); }
  .char-corners::after { bottom: 12px; right: 12px; border-bottom: 2px solid currentColor; border-right: 2px solid currentColor; transform: translate(6px, 6px); }
  .char-card[data-tl="A"] .char-corners { color: var(--tl-a); }
  .char-card[data-tl="B"] .char-corners { color: var(--tl-b); }
  .char-card:hover .char-corners::before, .char-card:hover .char-corners::after { opacity: 1; transform: translate(0, 0); }
  .char-spotlight { position: absolute; inset: 0; z-index: 2; border-radius: 16px; opacity: 0; transition: opacity 0.3s ease; pointer-events: none; background: radial-gradient(circle 120px at var(--mx, 50%) var(--my, 30%), rgba(255,255,255,0.07) 0%, transparent 70%); }
  .char-card:hover .char-spotlight { opacity: 1; }
  .char-content { position: absolute; bottom: 0; left: 0; right: 0; z-index: 4; padding: 0 1.5rem 1.5rem; display: flex; flex-direction: column; gap: 0.5rem; transform: translateY(0); transition: transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
  .char-card:hover .char-content { transform: translateY(-12px); }
  .char-details { display: flex; flex-direction: column; gap: 0.45rem; max-height: 0; overflow: hidden; opacity: 0; transition: max-height 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.4s ease 0.1s; }
  .char-card:hover .char-details { max-height: 220px; opacity: 1; }
  .char-role-line { display: flex; align-items: center; gap: 0.5rem; opacity: 0; transform: translateY(6px); transition: opacity 0.35s ease 0.08s, transform 0.35s ease 0.08s; }
  .char-role-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
  .char-card[data-tl="A"] .char-role-dot { background: var(--tl-a); box-shadow: 0 0 6px var(--tl-a-glow); }
  .char-card[data-tl="B"] .char-role-dot { background: var(--tl-b); box-shadow: 0 0 6px var(--tl-b-glow); }
  .char-role-text { font-size: 0.58rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--mist); }
  .char-card:hover .char-role-line { opacity: 1; transform: translateY(0); }
  .char-name { font-family: 'Cormorant Garamond', serif; font-size: clamp(1.5rem, 3.5vw, 2rem); font-weight: 600; color: var(--star); line-height: 1.1; letter-spacing: 0.04em; text-shadow: 0 2px 20px rgba(0,0,0,0.95), 0 0 40px rgba(0,0,0,0.6); transition: text-shadow 0.4s ease, letter-spacing 0.4s ease; position: relative; padding-bottom: 0.5rem; }
  .char-name::after { content: ''; position: absolute; bottom: 0; left: 0; width: 32px; height: 2px; border-radius: 1px; transition: width 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94), box-shadow 0.4s ease; }
  .char-card[data-tl="A"] .char-name::after { background: var(--tl-a); box-shadow: 0 0 8px var(--tl-a-glow); }
  .char-card[data-tl="B"] .char-name::after { background: var(--tl-b); box-shadow: 0 0 8px var(--tl-b-glow); }
  .char-card:hover .char-name { text-shadow: 0 0 24px rgba(255,255,255,0.35), 0 2px 16px rgba(0,0,0,0.95); letter-spacing: 0.06em; }
  .char-card:hover .char-name::after { width: 60px; box-shadow: 0 0 14px currentColor; }
  .char-tagline { font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: clamp(0.8rem, 1.8vw, 1rem); font-weight: 300; opacity: 0; transform: translateY(8px); transition: opacity 0.4s ease 0.15s, transform 0.4s ease 0.15s; line-height: 1.3; color: var(--mist); }
  .char-card:hover .char-tagline { opacity: 1; transform: translateY(0); }
  .char-divider { height: 1px; background: linear-gradient(to right, transparent, currentColor, transparent); opacity: 0; transform: scaleX(0); transform-origin: left; transition: opacity 0.3s ease 0.2s, transform 0.4s ease 0.2s; margin: 0.15rem 0; }
  .char-card[data-tl="A"] .char-divider { color: rgba(236,72,153,0.3); }
  .char-card[data-tl="B"] .char-divider { color: rgba(249,115,22,0.3); }
  .char-card:hover .char-divider { opacity: 1; transform: scaleX(1); }
  .char-desc { font-size: clamp(0.7rem, 1.4vw, 0.82rem); font-weight: 300; color: rgba(200,191,224,0.8); line-height: 1.6; letter-spacing: 0.02em; opacity: 0; transform: translateY(8px); transition: opacity 0.4s ease 0.25s, transform 0.4s ease 0.25s; }
  .char-card:hover .char-desc { opacity: 1; transform: translateY(0); }
  .char-particle-canvas { position: absolute; inset: 0; z-index: 3; border-radius: 16px; pointer-events: none; opacity: 0; transition: opacity 0.4s ease; }
  .char-card:hover .char-particle-canvas { opacity: 1; }
  .char-aura { position: absolute; inset: -1px; border-radius: 17px; pointer-events: none; z-index: 0; opacity: 0; transition: opacity 0.4s ease; }
  .char-card[data-tl="A"] .char-aura { background: conic-gradient(from var(--aura-angle, 0deg), transparent 0%, rgba(236,72,153,0.5) 20%, transparent 40%, rgba(236,72,153,0.2) 60%, transparent 80%); animation: spin-aura 3s linear infinite; }
  .char-card[data-tl="B"] .char-aura { background: conic-gradient(from var(--aura-angle, 0deg), transparent 0%, rgba(249,115,22,0.5) 20%, transparent 40%, rgba(249,115,22,0.2) 60%, transparent 80%); animation: spin-aura 4s linear infinite reverse; }
  @property --aura-angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
  @keyframes spin-aura { from { --aura-angle: 0deg; } to { --aura-angle: 360deg; } }
  .char-card:hover .char-aura { opacity: 1; }

  @media (pointer: coarse) { body { cursor: auto; } .cursor, .cursor-ring { display: none !important; } }
</style>
</head>
<body>

<div class="cursor" id="cursor"></div>
<div class="cursor-ring" id="cursorRing"></div>

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
    <p class="book-hero-author">by Anonymous</p>
    <p class="book-hero-genre">Teen Drama · Romance · Contemporary</p>
    <div class="hero-divider">
      <div class="hero-divider-line"></div>
      <span class="hero-divider-glyph">✦</span>
      <div class="hero-divider-line"></div>
    </div>
  </section>


  <!-- ═══ CHARACTERS SECTION ═══ -->
  <section class="characters-section fade-in delay-1">
    <div class="char-particles" id="sectionParticles"></div>

    <div class="characters-header">
      <div class="characters-eyebrow">The Cast</div>
      <h2 class="characters-title">Souls In <em>The Hallways</em></h2>
      <p class="characters-subtitle">Finding connections where they least expect it.</p>
    </div>

    <div class="char-grid" id="charGrid">

      <!-- Chloe -->
      <div class="char-card" data-tl="A">
        <div class="char-aura"></div>
        <div class="char-portrait" style="background-image: url('Images/Chloe.png'); background-color: #1a0a14;"></div>
        <div class="char-overlay-base"></div>
        <div class="char-spotlight"></div>
        <div class="char-frame"></div>
        <div class="char-corners"></div>
        <canvas class="char-particle-canvas"></canvas>
        <div class="char-content">
          <div class="char-name">Chloe</div>
          <div class="char-details">
            <div class="char-role-line">
              <div class="char-role-dot"></div>
              <span class="char-role-text">Protagonist · Wallflower</span>
            </div>
            <div class="char-tagline">The Girl Who Hated Mornings</div>
            <div class="char-divider"></div>
            <div class="char-desc">Caught between the invisible lines of high school drama and trying to stay unnoticed. But staying unnoticed is hard when Ethan is around.</div>
          </div>
        </div>
      </div>

      <!-- Ethan -->
      <div class="char-card" data-tl="B">
        <div class="char-aura"></div>
        <div class="char-portrait" style="background-image: url('Images/Ethan.png'); background-color: #100a1a;"></div>
        <div class="char-overlay-base"></div>
        <div class="char-spotlight"></div>
        <div class="char-frame"></div>
        <div class="char-corners"></div>
        <canvas class="char-particle-canvas"></canvas>
        <div class="char-content">
          <div class="char-name">Ethan</div>
          <div class="char-details">
            <div class="char-role-line">
              <div class="char-role-dot"></div>
              <span class="char-role-text">Protagonist · New Guy</span>
            </div>
            <div class="char-tagline">The Unpredictable Spark</div>
            <div class="char-divider"></div>
            <div class="char-desc">Mysterious and effortlessly cool, he brings a storm into Chloe's quiet world, challenging everything she thought she wanted.</div>
          </div>
        </div>
      </div>
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
const cursor = document.getElementById('cursor'), cursorRing = document.getElementById('cursorRing');
let mx = 0, my = 0, rx = 0, ry = 0;
document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; cursor.style.left = mx + 'px'; cursor.style.top = my + 'px'; });
function animRing() { rx += (mx - rx) * 0.12; ry += (my - ry) * 0.12; cursorRing.style.left = rx + 'px'; cursorRing.style.top = ry + 'px'; requestAnimationFrame(animRing); }
animRing();
document.querySelectorAll('a, button, .chapter-link').forEach(el => {
  el.addEventListener('mouseenter', () => { cursor.style.transform = 'translate(-50%,-50%) scale(2)'; cursorRing.style.transform = 'translate(-50%,-50%) scale(1.5)'; cursorRing.style.borderColor = 'rgba(249,115,22,0.7)'; });
  el.addEventListener('mouseleave', () => { cursor.style.transform = 'translate(-50%,-50%) scale(1)'; cursorRing.style.transform = 'translate(-50%,-50%) scale(1)'; cursorRing.style.borderColor = 'rgba(249,115,22,0.4)'; });
});
</script>
</body>
</html>"""

    with open('AlwaysThere4U/index.html', 'w', encoding='utf-8') as out_f:
        out_f.write(index_template)

if __name__ == '__main__':
    generate()
