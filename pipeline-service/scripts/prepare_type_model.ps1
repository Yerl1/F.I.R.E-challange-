param(
  [string]$SourceDir = "..\type_recognition",
  [string]$TargetDir = ".\models\type_recognition"
)

$ErrorActionPreference = "Stop"

function Ensure-Dir([string]$PathValue) {
  if (-not (Test-Path -LiteralPath $PathValue)) {
    New-Item -ItemType Directory -Path $PathValue | Out-Null
  }
}

function Copy-IfExists([string]$From, [string]$To) {
  if (Test-Path -LiteralPath $From) {
    Copy-Item -LiteralPath $From -Destination $To -Force
  }
}

$src = (Resolve-Path -LiteralPath $SourceDir).Path
Ensure-Dir $TargetDir
$dst = (Resolve-Path -LiteralPath $TargetDir).Path

# Required inference artifacts
Copy-IfExists "$src\best_model.pt" "$dst\best_model.pt"
Copy-IfExists "$src\xlmr_final.pt" "$dst\xlmr_final.pt"
Copy-IfExists "$src\label_encoder.pkl" "$dst\label_encoder.pkl"

# Tokenizer directory
$srcTokenizerDir = "$src\xlmr_model"
$dstTokenizerDir = "$dst\xlmr_model"
if (Test-Path -LiteralPath $srcTokenizerDir) {
  Ensure-Dir $dstTokenizerDir
  Copy-IfExists "$srcTokenizerDir\tokenizer.json" "$dstTokenizerDir\tokenizer.json"
  Copy-IfExists "$srcTokenizerDir\tokenizer_config.json" "$dstTokenizerDir\tokenizer_config.json"
}

# Remove obvious training/dataset artifacts from destination if present
$garbage = @(
  "labeled_dataset_combined.csv",
  "labeled_dataset_combined_full.csv",
  "synthetic.csv",
  "inference.py",
  "train.py",
  "note.py",
  "xml_roberta.py",
  "en_type_classifier_best.joblib",
  "kz_type_classifier_best.joblib",
  "ru_type_classifier_best.joblib"
)

foreach ($name in $garbage) {
  $path = Join-Path $dst $name
  if (Test-Path -LiteralPath $path) {
    Remove-Item -LiteralPath $path -Force
  }
}

Write-Host "Type model prepared for inference:" -ForegroundColor Green
Write-Host "  Source: $src"
Write-Host "  Target: $dst"
Write-Host ""
Write-Host "Set env (optional):" -ForegroundColor Yellow
Write-Host "  `$env:TYPE_MODEL_PATH=""$dst"""

