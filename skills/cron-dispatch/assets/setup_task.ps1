<#
.SYNOPSIS
  Register, list, or remove a Windows Task Scheduler job that runs a script on a timer.
.DESCRIPTION
  No secrets live in this file. Pass the command and arguments at call time.
  Examples:
    # register a daily 09:00 task
    .\setup_task.ps1 -TaskName "scraper-daily" -Command "python" -Arguments "C:\proj\scraper.py" -Time "09:00"
    # list matching tasks
    .\setup_task.ps1 -TaskName "scraper" -Action list
    # remove a task
    .\setup_task.ps1 -TaskName "scraper-daily" -Action remove
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $TaskName,
    [string] $Command = "python",
    [string] $Arguments = "",
    [string] $Time = "09:00",
    [string] $WorkingDir = (Get-Location).Path,
    [ValidateSet("register", "list", "remove")] [string] $Action = "register"
)

switch ($Action) {
    "list" {
        Get-ScheduledTask |
            Where-Object { $_.TaskName -like "*$TaskName*" } |
            Format-Table TaskName, State
        return
    }
    "remove" {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed task '$TaskName'."
        return
    }
}

# register (idempotent: -Force overwrites an existing task of the same name)
$taskAction = New-ScheduledTaskAction -Execute $Command -Argument $Arguments -WorkingDirectory $WorkingDir
$trigger    = New-ScheduledTaskTrigger -Daily -At $Time
$settings   = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $taskAction -Trigger $trigger `
    -Settings $settings -Force | Out-Null

Write-Host "Registered '$TaskName' to run '$Command $Arguments' daily at $Time (cwd: $WorkingDir)."
