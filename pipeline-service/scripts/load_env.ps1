param(
    [string]$EnvFile = "..\.env"
)

$resolvedPath = Resolve-Path -Path $EnvFile -ErrorAction SilentlyContinue
if (-not $resolvedPath) {
    throw "Env file not found: $EnvFile"
}

Get-Content $resolvedPath | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) {
        return
    }

    $pair = $line -split "=", 2
    if ($pair.Count -ne 2) {
        return
    }

    $name = $pair[0].Trim()
    $value = $pair[1].Trim()
    if ($value.StartsWith('"') -and $value.EndsWith('"') -and $value.Length -ge 2) {
        $value = $value.Substring(1, $value.Length - 2)
    }
    Set-Item -Path ("Env:" + $name) -Value $value
}

Write-Host "Loaded env vars from $resolvedPath"
