# --- Get blog files (skip index.md)
function Get-BlogFiles {
    param (
        [Parameter(Mandatory=$true)]
        [string]$BlogPath
    )

    if (-not (Test-Path $BlogPath)) {
        Write-Error "Blog path does not exist: $BlogPath"
        return @()
    }

    $posts = Get-ChildItem -Path $BlogPath -Recurse -File -Filter "*.md" |
             Where-Object { $_.Name -ne "index.md" } |
             ForEach-Object { $_.FullName }

    return $posts
}

# --- Get project files
function Get-PyProjFiles {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        Write-Error "Path does not exist: $Path"
        return @()
    }

    $patterns = @("*.py", "*.json", "*.ini", "*.txt", ".gitignore")

    $allFiles = Get-ChildItem -Path $Path -Recurse -File |
                Where-Object {
                    $matched = $false
                    foreach ($pattern in $patterns) {
                        if ($_.Name -like $pattern) {
                            $matched = $true
                            break
                        }
                    }
                    $matched
                } |
                ForEach-Object { $_.FullName }

    return $allFiles
}
