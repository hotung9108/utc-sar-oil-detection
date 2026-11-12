<# Export the editable defense deck using locally installed PowerPoint.
   Reads/writes this project only. Does not close any user presentation.
#>
param([switch]$Preview)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$deckPath = Join-Path $projectRoot 'docs\slides\v2\BAO_VE_BTL_XLA_V2.pptx'
$pdfPath = Join-Path $projectRoot 'docs\slides\v2\BAO_VE_BTL_XLA_V2.pdf'
$previewPath = Join-Path $projectRoot '.cache\slides_v2_preview'
$slideApp = New-Object -ComObject PowerPoint.Application
$slideDeck = $null
try {
    $slideDeck = $slideApp.Presentations.Open($deckPath, -1, 0, 0)
    $slideDeck.SaveAs($pdfPath, 32)
    if ($Preview) {
        New-Item -ItemType Directory -Path $previewPath -Force | Out-Null
        $slideDeck.Export($previewPath, 'PNG', 1600, 900)
    }
    $overflows = @()
    foreach ($slideItem in $slideDeck.Slides) {
        foreach ($shape in $slideItem.Shapes) {
            if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
                if ($shape.TextFrame2.TextRange.BoundHeight -gt ($shape.Height + 2)) {
                    $overflows += [pscustomobject]@{Slide=$slideItem.SlideIndex; Text=$shape.TextFrame.TextRange.Text}
                }
            }
        }
    }
    $audit = [ordered]@{renderer='Microsoft PowerPoint'; slides=$slideDeck.Slides.Count; overflow_count=$overflows.Count; overflows=$overflows}
    $audit | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $projectRoot '.cache\slides_v2_render_audit.json') -Encoding UTF8
    if ($overflows.Count -gt 0) { throw 'Slide text overflows; see .cache/slides_v2_render_audit.json' }
    Write-Output "Exported $($slideDeck.Slides.Count) slides to $pdfPath"
} finally {
    if ($null -ne $slideDeck) { $slideDeck.Close() }
    if ($slideApp.Presentations.Count -eq 0) { $slideApp.Quit() }
}

