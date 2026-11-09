@echo off
echo ========================================================
echo   WARPGATE - Cleaning All Previous Firewall Rules
echo ========================================================
netsh advfirewall firewall delete rule name="GAMESERV_BLOCK_OW2_NA_central_v4_0"
netsh advfirewall firewall delete rule name="GAMESERV_BLOCK_OW2_NA_central_v4_1"
netsh advfirewall firewall delete rule name="GAMESERV_BLOCK_OW2_NA_central_v6_0"
netsh advfirewall firewall delete rule name="BLOCK_ME_ONLY"
netsh advfirewall firewall delete rule name="OW2_BLOCK"
netsh advfirewall firewall delete rule name="_Overwatch"
powershell -NoProfile -Command "Get-NetFirewallRule | Where-Object { $_.DisplayName -like '*GAMESERV*' -or $_.DisplayName -like '*SELECTOR*' -or $_.DisplayName -like '*WARPGATE*' -or $_.DisplayName -like '*OW2*' -or $_.DisplayName -like '*_Overwatch*' -or $_.DisplayName -like '*BF_*' -or $_.DisplayName -like '*APEX_*' -or $_.DisplayName -like '*RIVALS_*' -or $_.DisplayName -like '*Overwatch-Server-Selector*' } | Remove-NetFirewallRule -ErrorAction SilentlyContinue"
echo.
echo All custom server selector firewall rules have been removed!
echo Default game connectivity and matchmaking have been 100%% restored.
echo ========================================================
pause
