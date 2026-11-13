# Update fields on a task-owned copy using Word; never edit the user's template.
$ErrorActionPreference = 'Stop'
$reportRoot = Split-Path -Parent $PSScriptRoot
$reportSource = Join-Path $reportRoot '.cache/report/Bao_cao_SAR_SOS.docx'
$reportTarget = Join-Path $reportRoot '.cache/report/Bao_cao_SAR_SOS_word.docx'
Copy-Item -LiteralPath $reportSource -Destination $reportTarget -Force
$reportWord = $null
$reportDocument = $null
try {
    $reportWord = New-Object -ComObject Word.Application
    $reportWord.Visible = $false
    $reportWord.DisplayAlerts = 0
    $reportDocument = $reportWord.Documents.Open($reportTarget, $false, $false)
    $null = $reportDocument.Fields.Update()
    foreach ($reportToc in $reportDocument.TablesOfContents) { $reportToc.Update() }
    foreach ($reportFigures in $reportDocument.TablesOfFigures) { $reportFigures.Update() }
    $reportDocument.Repaginate()
    foreach ($reportToc in $reportDocument.TablesOfContents) { $reportToc.UpdatePageNumbers() }
    foreach ($reportFigures in $reportDocument.TablesOfFigures) { $reportFigures.UpdatePageNumbers() }
    $reportDocument.Save()
    Write-Output 'Updated Word fields in the report copy.'
} finally {
    if ($null -ne $reportDocument) { $reportDocument.Close(0) }
    if ($null -ne $reportWord) { $reportWord.Quit() }
}
@{
    source_sha256 = (Get-FileHash -LiteralPath $reportSource -Algorithm SHA256).Hash.ToLowerInvariant()
    refreshed_sha256 = (Get-FileHash -LiteralPath $reportTarget -Algorithm SHA256).Hash.ToLowerInvariant()
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $reportRoot '.cache/report/word_refresh.json') -Encoding UTF8
