# Add custom cursor to all story HTML files
# Door To The Heart uses gold, Reality Entity uses cyan

$cursorCSS_gold = @"
  /* Custom cursor */
  body { cursor: none; }
  .cursor { position:fixed; width:8px; height:8px; background:#c9933a; border-radius:50%; pointer-events:none; z-index:9999; transform:translate(-50%,-50%); transition:transform 0.1s, background 0.3s; box-shadow:0 0 12px #f0d898; }
  .cursor-ring { position:fixed; width:32px; height:32px; border:1px solid rgba(201,147,58,0.4); border-radius:50%; pointer-events:none; z-index:9998; transform:translate(-50%,-50%); transition:all 0.18s ease; }
"@

$cursorCSS_cyan = @"
  /* Custom cursor */
  body { cursor: none; }
  .cursor { position:fixed; width:8px; height:8px; background:#0ea5e9; border-radius:50%; pointer-events:none; z-index:9999; transform:translate(-50%,-50%); transition:transform 0.1s, background 0.3s; box-shadow:0 0 12px rgba(14,165,233,0.6); }
  .cursor-ring { position:fixed; width:32px; height:32px; border:1px solid rgba(14,165,233,0.4); border-radius:50%; pointer-events:none; z-index:9998; transform:translate(-50%,-50%); transition:all 0.18s ease; }
"@

$cursorHTML = @"
<div class="cursor" id="cursor"></div>
<div class="cursor-ring" id="cursorRing"></div>
"@

$cursorJS_gold = @"
// Custom cursor
const cursor=document.getElementById('cursor'),cursorRing=document.getElementById('cursorRing');
let mx=0,my=0,rx=0,ry=0;
document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;cursor.style.left=mx+'px';cursor.style.top=my+'px';});
function animRing(){rx+=(mx-rx)*0.12;ry+=(my-ry)*0.12;cursorRing.style.left=rx+'px';cursorRing.style.top=ry+'px';requestAnimationFrame(animRing);}
animRing();
document.querySelectorAll('a, button, .ch-node, .story-card').forEach(el=>{
  el.addEventListener('mouseenter',()=>{cursor.style.transform='translate(-50%,-50%) scale(2)';cursorRing.style.transform='translate(-50%,-50%) scale(1.5)';cursorRing.style.borderColor='rgba(201,147,58,0.7)';});
  el.addEventListener('mouseleave',()=>{cursor.style.transform='translate(-50%,-50%) scale(1)';cursorRing.style.transform='translate(-50%,-50%) scale(1)';cursorRing.style.borderColor='rgba(201,147,58,0.4)';});
});
"@

$cursorJS_cyan = @"
// Custom cursor
const cursor=document.getElementById('cursor'),cursorRing=document.getElementById('cursorRing');
let mx=0,my=0,rx=0,ry=0;
document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;cursor.style.left=mx+'px';cursor.style.top=my+'px';});
function animRing(){rx+=(mx-rx)*0.12;ry+=(my-ry)*0.12;cursorRing.style.left=rx+'px';cursorRing.style.top=ry+'px';requestAnimationFrame(animRing);}
animRing();
document.querySelectorAll('a, button, .ch-node, .story-card').forEach(el=>{
  el.addEventListener('mouseenter',()=>{cursor.style.transform='translate(-50%,-50%) scale(2)';cursorRing.style.transform='translate(-50%,-50%) scale(1.5)';cursorRing.style.borderColor='rgba(14,165,233,0.7)';});
  el.addEventListener('mouseleave',()=>{cursor.style.transform='translate(-50%,-50%) scale(1)';cursorRing.style.transform='translate(-50%,-50%) scale(1)';cursorRing.style.borderColor='rgba(14,165,233,0.4)';});
});
"@

function Add-Cursor {
    param($file, $cssBlock, $jsBlock)
    
    $content = Get-Content $file -Raw
    
    # Skip if cursor already added
    if ($content -match 'class="cursor"') {
        Write-Host "SKIP (already has cursor): $file"
        return
    }
    
    # 1. Add CSS before </style>
    $content = $content -replace '</style>', "$cssBlock`n</style>"
    
    # 2. Add cursor HTML divs right after <body> (before first content)
    $content = $content -replace '<body>', "<body>`n$cursorHTML"
    
    # 3. Add cursor JS right before </script> (the LAST </script>)
    # Find the last </script> and insert before it
    $lastIdx = $content.LastIndexOf('</script>')
    if ($lastIdx -gt 0) {
        $content = $content.Substring(0, $lastIdx) + "$jsBlock`n" + $content.Substring($lastIdx)
    }
    
    Set-Content $file $content -NoNewline
    Write-Host "DONE: $file"
}

# Door To The Heart files (gold cursor)
$dthFiles = Get-ChildItem "d:\GitHub_Repository\Luminae\Door_To_The_Heart\*.html"
foreach ($f in $dthFiles) {
    Add-Cursor $f.FullName $cursorCSS_gold $cursorJS_gold
}

# The Reality Entity files (cyan cursor)
$treFiles = Get-ChildItem "d:\GitHub_Repository\Luminae\The_Reality_Entity\*.html"
foreach ($f in $treFiles) {
    Add-Cursor $f.FullName $cursorCSS_cyan $cursorJS_cyan
}

Write-Host "`nAll files processed!"
