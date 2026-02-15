# Excel Import QA Checklist (Customer Management)

This checklist is for real-user validation focused on customer safety.

## Goal
- New customers are inserted correctly.
- Existing customers are never overwritten.
- Errors are clearly identifiable and actionable.

## Pre-check
1. Launch app with test DB.
2. Confirm `Excel Import` button is visible in footer.
3. Prepare 3 files:
   - `success.xlsx` (all valid new customers)
   - `mixed.xlsx` (new + existing + invalid rows)
   - `invalid.xlsx` (missing name/phone, wrong formats)

## Scenario A: Success only
1. Open `success.xlsx`.
2. Click `Preview`.
3. Expected:
   - `success > 0`, `skip = 0`, `fail = 0`
4. Click `Commit`.
5. Expected:
   - same counts as preview
   - new customers visible in list/search

## Scenario B: Existing customers must be preserved
1. Pick one existing customer and note key fields (memo/address/payment method).
2. Put same `phone+name` in `mixed.xlsx` with changed values.
3. Preview + Commit.
4. Expected:
   - row is `skip` with code `E202`
   - original customer data remains unchanged

## Scenario C: Error identification quality
1. Use `invalid.xlsx`.
2. Preview.
3. Expected error columns in grid:
   - `sheet`, `row`, `column`, `error_code`, `message`, `action_hint`
4. Export error report.
5. Expected:
   - CSV contains `ERROR`/`SKIP` rows
   - each row has enough data to fix quickly

## Scenario D: Duplicate handling
1. Add duplicate `phone+name` rows in same file.
2. Preview.
3. Expected:
   - duplicate row marked `E201`
   - only one valid row can proceed

## Safety checks
1. Existing customer count before/after should not decrease.
2. Existing customer details should not be modified by import.
3. App should not crash on malformed files.

## Exit criteria
1. All scenarios pass.
2. No unexpected overwrite.
3. Error report is understandable by non-technical user.

