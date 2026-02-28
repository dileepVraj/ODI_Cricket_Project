python core/utils/compliance-bouncer.py --root .
if ($LASTEXITCODE -ne 0) {
    Write-Host "[COMPLIANCE BOUNCER] FAIL: Commit blocked."
    exit $LASTEXITCODE
}
exit 0
