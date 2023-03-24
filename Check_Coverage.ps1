param (
    [string]$module='',
    [switch]$append=$false,
    [switch]$blank=$false,
    [string]$path="."
)

Set-Location $path

$testLog = ".\TEST_LOG.log"
if (Test-Path $testLog) {
    Remove-Item $testLog
}

$coverage = ".\.coverage"
if ((Test-Path $coverage) -and $blank) {
    Remove-Item $coverage
}

Write-Output @"
======================================================================
Discovering and running unit tests
----------------------------------------------------------------------
"@
if ($module -eq '') {
    if ($append) {
        coverage run --source=uofi_gui,utilityFunctions --append -m unittest discover -v -b -s .\unittests\ -p test_*.py
    } else {
        coverage run --source=uofi_gui,utilityFunctions -m unittest discover -v -b -s .\unittests\ -p test_*.py
    }
} elseif ($module -eq 'utilityFunctions') {
    if ($append) {
        coverage run --source=utilityFunctions --append -m unittest discover -v -b -s .\unittests\ -p test_utilityFunctions*.py
    } else {
        coverage run --source=utilityFunctions -m unittest discover -v -b -s .\unittests\ -p test_utilityFunctions*.py
    }
} else {
    if ($append) {
        coverage run --source=uofi_gui.$module --append --context=$module -m unittest discover -v -b -s .\unittests\ -p test_uofi_$module*.py
    } else {
        coverage run --source=uofi_gui.$module --context=$module -m unittest discover -v -b -s .\unittests\ -p test_uofi_$module*.py
    }
}
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