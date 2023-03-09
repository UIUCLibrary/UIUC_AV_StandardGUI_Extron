Set-Location "C:\Users\feuerhe1\OneDrive - University of Illinois - Urbana\Documents - Library IT AV Projects\General\Standards Documents\01 - Library Standards\Extron GUI Port\Code\"
Remove-Item .\.coverage
Remove-Item .\TEST_LOG.log

Write-Output @"
======================================================================
Discovering and running unit tests
----------------------------------------------------------------------
"@
coverage run --source=uofi_gui,utilityFunctions -m unittest discover -v -b -s .\unittests\ -p test_*.py

Write-Output @"
======================================================================
Generating coverage report
----------------------------------------------------------------------
"@
coverage html

Write-Output @"
======================================================================
Opening coverage report
----------------------------------------------------------------------
"@
Invoke-Item .\htmlcov\index.html