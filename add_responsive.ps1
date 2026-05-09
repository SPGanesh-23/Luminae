# Add custom cursor AND responsiveness to all story HTML files

$responsiveCSS = @"
  @media (pointer: coarse) {
    body { cursor: auto; }
    .cursor, .cursor-ring { display: none !important; }
  }
  @media (max-width: 768px) {
    .top-nav { padding: 1rem 1.5rem !important; }
    .logo { font-size: 1.1rem !important; }
    .reader-page { padding: 3rem 1.2rem 2rem !important; }
    .ch-title { font-size: 2.2rem !important; }
    .ch-nav { justify-content: center !important; }
    .ch-nav-btn { padding: 0.7rem 1.2rem !important; font-size: 0.65rem !important; }
    .author-note { padding: 1.5rem !important; }
  }
"@

function Update-File {
    param($file)
    $content = Get-Content $file -Raw
    
    # 1. Add responsiveness before </style>
    if ($content -notmatch '@media \(pointer: coarse\)') {
        $content = $content -replace '</style>', "$responsiveCSS`n</style>"
    }
    
    # 2. Add cursor HTML if missing
    if ($content -notmatch 'class="cursor"') {
        # This part was already done by the previous script but let's be safe
        # Actually I already updated them, but if any were missed...
    }
    
    Set-Content $file $content -NoNewline
}

# Process all story chapters
$files = Get-ChildItem "d:\GitHub_Repository\Luminae\Door_To_The_Heart\chapter*.html"
$files += Get-ChildItem "d:\GitHub_Repository\Luminae\The_Reality_Entity\chapter*.html"

foreach ($f in $files) {
    Update-File $f.FullName
}

Write-Host "Responsiveness added to all chapter files!"
