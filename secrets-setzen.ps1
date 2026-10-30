# Überträgt die API-Schlüssel als GitHub-Secrets ins Repo ki-trader-arena.
# Anthropic-Schlüssel wird verdeckt abgefragt; die übrigen kommen aus OpenCodes auth.json.
# Kein Schlüssel wird angezeigt, gespeichert oder geloggt. Start: Doppelklick auf secrets-setzen.cmd
$ErrorActionPreference = 'Stop'
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)   # kein BOM in der Pipe zu gh (sonst landet U+FEFF im Secret)
$repo = 'rouvenwieland/ki-trader-arena'

function Setze($name, $wert) {
  if (-not $wert) { return }
  $wert.Trim() | gh secret set $name -R $repo | Out-Null
  Write-Host "  gesetzt: $name"
}

Write-Host "Anthropic-API-Schlüssel einfügen (Rechtsklick fügt ein, die Eingabe bleibt unsichtbar), dann Enter."
Write-Host "Leer lassen, um ihn zu überspringen."
$sicher = Read-Host -AsSecureString 'Schlüssel'
$klar = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sicher))
Setze 'ARENA_ANTHROPIC_KEY' $klar.Trim()
$klar = $null

$auth = "$env:USERPROFILE\.local\share\opencode\auth.json"
if (Test-Path $auth) {
  $a = Get-Content $auth -Raw | ConvertFrom-Json
  $karte = @{ google = 'GEMINI_API_KEY'; openrouter = 'OPENROUTER_API_KEY'; deepseek = 'DEEPSEEK_API_KEY'; moonshot = 'MOONSHOT_API_KEY';
              groq = 'GROQ_API_KEY'; cerebras = 'CEREBRAS_API_KEY'; mistral = 'MISTRAL_API_KEY'; openai = 'OPENAI_API_KEY' }
  foreach ($p in $a.PSObject.Properties) {
    if ($karte.ContainsKey($p.Name) -and $p.Value.type -eq 'api') { Setze $karte[$p.Name] $p.Value.key }
  }
}
Write-Host "`nFertig. Vorhandene Secrets:"
gh secret list -R $repo
