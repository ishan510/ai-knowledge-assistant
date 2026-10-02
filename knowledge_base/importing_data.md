# Importing Data into Northstar

Document ID: KB-009
Last updated: 2026-09-30
Owner: Customer Onboarding

## Who can import data
Workspace owners and admins can import data.
Members cannot run imports.

Imports are unavailable while a workspace is read-only.

## Supported files
Northstar accepts CSV files encoded in UTF-8.
Each file must be no larger than 10 MB and contain no more
than 5,000 data rows, excluding the header row.

Excel files must be exported to CSV before uploading.

## Required columns
Each file must contain these column headers:
- external_id
- title
- description

Every row must have a non-empty external_id and title.
The description may be blank.

## Running an import
1. Open Settings → Import data.
2. Upload the CSV file.
3. Review the validation results.
4. Fix any reported errors and upload the corrected file.
5. Select "Confirm import."

Uploading a file does not create records until you confirm.

## Validation errors
If any row fails validation, the entire import is blocked.
No records are created or changed.

Duplicate external_id values within the same file are
validation errors.

## Existing records
If an external_id matches an existing workspace record,
the import updates that record's title and description.
A blank description clears the existing description.

New external_id values create new records.

## After importing
The completion screen shows the number of records created
and updated.

Imports cannot be automatically undone. Export a backup
of existing records before importing updates.

## Import failures
If a confirmed import reports a processing failure,
contact Northstar Support with the import ID before retrying.
Do not attach confidential customer data to the request.