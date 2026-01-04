# --- Import utility functions
$utilsPath = "/home/atari-monk/atari-monk/project/access-guard/script/utils.ps1"
if (Test-Path $utilsPath) {
    . $utilsPath  # dot-source the script to load functions
} else {
    Write-Error "Utils script not found at $utilsPath"
}

# --- Paths
$blog = "/home/atari-monk/atari-monk/project/dev-blog/post/access-guard"

snippet clear

# --- Blog posts
snippet -c 'dev-blog of project access-guard:' -t context
$posts = Get-BlogFiles $blog | Sort-Object Name 
foreach ($post in $posts) {
    snippet -f $post -t context    
}

# --- Prompt
$prompt = ""
snippet -c $prompt -t prompt

snippet pop
