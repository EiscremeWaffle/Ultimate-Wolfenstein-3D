$path = 'xlat/O_Tst.txt'
$lines = Get-Content -LiteralPath $path
$inTiles = $false
$duplicate442 = 0
$output = foreach ($line in $lines) {
    if ($line -match '^\s*tiles\s*$') { $inTiles = $true }
    if ($line -match '^\s*things\s*$') { $inTiles = $false }
    if ($inTiles -and $line -match '^(\s*)(tile|trigger)(\s+)(\d+)(.*)$') {
        $old = [int]$Matches[4]
        $new = $old
        if ($old -ge 161 -and $old -le 201) { $new = $old - 17 }
        elseif ($old -ge 202 -and $old -le 218) { $new = $old - 17 }
        elseif ($old -ge 219 -and $old -le 226) { $new = $old - 17 }
        elseif ($old -eq 227) { $new = 212 }
        elseif ($old -ge 228 -and $old -le 229) { $new = $old - 18 }
        elseif ($old -ge 259 -and $old -le 272) { $new = $old - 46 }
        elseif ($old -ge 353 -and $old -le 441) { $new = $old - 126 }
        elseif ($old -eq 442) {
            $duplicate442++
            $new = if ($duplicate442 -eq 1) { 316 } else { 317 }
        }
        $line = $Matches[1] + $Matches[2] + $Matches[3] + $new + $Matches[5]
    }
    $line
}
[System.IO.File]::WriteAllLines((Resolve-Path $path), $output, [System.Text.UTF8Encoding]::new($false))
