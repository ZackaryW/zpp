# Validate a message file or existing commit against the zmem commit grammar.
$ErrorActionPreference = 'Stop'

$CanonicalEvents = @('DECISION', 'LESSON_LEARNT', 'REFACTOR', 'DEBT', 'CONTEXT')
$RequireZmem = $false
$RemainingArgs = @($args)
if ($RemainingArgs.Count -ge 1 -and $RemainingArgs[0] -eq '--require-zmem') {
    $RequireZmem = $true
    $RemainingArgs = @($RemainingArgs | Select-Object -Skip 1)
}

function Emit-Result {
    param([bool]$Ok, [int]$Code, [string]$Message, [string]$CcType, [int]$Annotations)
    [pscustomobject]@{
        ok = $Ok; code = $Code; message = $Message
        cc_type = $CcType; annotations = $Annotations
    } | ConvertTo-Json -Compress
}

if ($RemainingArgs.Count -ge 1 -and $RemainingArgs[0] -eq '--file') {
    if (-not (Test-Path -LiteralPath $RemainingArgs[1])) {
        Emit-Result $false 1 "message file not found: $($RemainingArgs[1])" '' 0; exit 1
    }
    $Msg = Get-Content -LiteralPath $RemainingArgs[1] -Raw
} else {
    $Ref = if ($RemainingArgs.Count -ge 1) { $RemainingArgs[0] } else { 'HEAD' }
    $Msg = git log -1 --format=%B $Ref 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $Msg) {
        Emit-Result $false 1 "cannot read commit: $Ref" '' 0; exit 1
    }
    if ($Msg -is [array]) { $Msg = $Msg -join "`n" }
}

$Lines = $Msg -split "`r?`n"
$Subject = $Lines[0].Trim()
if ($Subject -notmatch '^[a-z]+(\([^)]*\))?!?: .+$') {
    Emit-Result $false 20 "subject is not a conventional commit: $Subject" '' 0; exit 20
}
if ($Subject.Length -gt 72) {
    Emit-Result $false 21 'subject exceeds 72 chars' '' 0; exit 21
}

$CcType = [regex]::Match($Subject, '^([a-z]+)').Groups[1].Value
$Annotations = 0
for ($i = 1; $i -lt $Lines.Count; $i++) {
    $Stripped = $Lines[$i].Trim()
    if (-not $Stripped) { continue }
    if ($Stripped -match '^(?:[-*]\s+)?zmem\(([^)]+)\): .+$') {
        $Annotations++
        $Event = $Matches[1]
        if ($CanonicalEvents -notcontains $Event) {
            Emit-Result $false 24 "non-canonical event: $Event (allowed: $($CanonicalEvents -join ' '))" $CcType $Annotations
            exit 24
        }
        continue
    }
    if ($Stripped -match '^[-*] .+$') { continue }
    Emit-Result $false 22 "body line $($i + 1) is prose (must be zmem() or bullet): $Stripped" $CcType $Annotations
    exit 22
}
if ($RequireZmem -and $Annotations -eq 0) {
    Emit-Result $false 23 "memory-bearing validation requires a zmem() annotation" $CcType 0
    exit 23
}
Emit-Result $true 0 'ok' $CcType $Annotations
exit 0
