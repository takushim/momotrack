# get/set parameters from command line arguments
Param([Switch]$help = $false,
      [String]$file = "")

if (($help -eq $true) -or ($file.length -eq 0)) {
      Write-Host ("Example: {0} -file IMAGE_FILE" -f $MyInvocation.MyCommand.Name)
      return 0
}

# default values
$ErrorActionPreference = 'Stop'
$script = (Get-Command "mmtrack.py").Path
$stem = "{0}" -f (get-item $file).basename
$record = "{0}_track.json" -f $stem

# process!
if (Test-Path $record) {
      $parameters = @{
            FilePath = (Get-command "python.exe")
            ArgumentList = @($script, "-f", $record, $file)
      }
}
else {
      $parameters = @{
            FilePath = (Get-command "python.exe")
            ArgumentList = @($script, $file)
      }
}

Start-Process -NoNewWindow -Wait @parameters

