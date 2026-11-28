$ErrorActionPreference = "Stop"

$reportDir = $PSScriptRoot
$sourcePath = Join-Path $reportDir "technical-report.md"
$htmlPath = Join-Path $reportDir "technical-report.html"
$pdfPath = Join-Path $reportDir "technical-report.pdf"

if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    throw "Pandoc is required to build the report. Install it from https://pandoc.org/installing.html."
}

& pandoc $sourcePath `
    --from "markdown+yaml_metadata_block+header_attributes" `
    --to html5 `
    --standalone `
    --toc `
    --toc-depth=2 `
    --css=style.css `
    --output $htmlPath

if ($LASTEXITCODE -ne 0) {
    throw "Pandoc failed to generate the report HTML (exit code $LASTEXITCODE)."
}

$browserCandidates = @(
    (Join-Path ${env:ProgramFiles(x86)} "Microsoft\Edge\Application\msedge.exe"),
    (Join-Path $env:ProgramFiles "Microsoft\Edge\Application\msedge.exe"),
    (Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe")
)

$browser = $browserCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $browser) {
    throw "Microsoft Edge or Google Chrome is required to print the report PDF."
}

$htmlUri = (New-Object System.Uri((Resolve-Path $htmlPath).Path)).AbsoluteUri
& $browser --headless --disable-gpu --no-pdf-header-footer "--print-to-pdf=$pdfPath" $htmlUri

if ($LASTEXITCODE -ne 0 -or -not (Test-Path $pdfPath)) {
    throw "Browser PDF export failed (exit code $LASTEXITCODE)."
}

Write-Host "Report generated:"
Write-Host "  $htmlPath"
Write-Host "  $pdfPath"
