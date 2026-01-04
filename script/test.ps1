# --- Paths
$proj = "/home/atari-monk/atari-monk/project/access-guard"

snippet clear

# --- Project structure
if (Test-Path $proj) {
    fstree $proj -c
    snippet -d 'Project Structure:' -t context
}

# --- Prompt for Swagger
$prompt = "Test only"
snippet -c $prompt -t prompt

snippet pop
