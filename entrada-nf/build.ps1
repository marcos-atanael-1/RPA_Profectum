$exclude = @("venv", "entrada-nf.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "entrada-nf.zip" -Force