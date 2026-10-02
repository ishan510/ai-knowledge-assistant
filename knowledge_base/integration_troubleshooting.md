# Troubleshooting Northstar Integrations

Document ID: KB-010
Last updated: 2026-09-30
Owner: Technical Support

## Who can manage integrations
Workspace owners and admins can connect, reconnect, and
disconnect integrations. Members can view integration status
but cannot change connection settings.

## Checking integration status
Open Settings → Integrations and select the connection.

The status panel shows:
- Connection status
- Time of the last successful sync
- Most recent error, if any

Enabled integrations normally sync every 15 minutes.

## Authentication errors
If the status shows "Authentication required":
1. Select "Reconnect."
2. Sign in to the connected service.
3. Approve the requested permissions.
4. Check the status after the next scheduled sync.

The person reconnecting must have permission to authorize
access in the connected service.

## Missing records
If the connection is healthy but records are missing:
1. Confirm the records exist in the connected service.
2. Check whether the integration's filters exclude them.
3. Confirm the last successful sync occurred after the
   records were created or updated.

If records remain missing after two successful syncs,
contact Northstar Support.

## Rate limit errors
A "Rate limited" status means the connected service is
temporarily limiting requests.

Northstar automatically retries at the next scheduled sync.
Do not repeatedly disconnect and reconnect the integration.

If rate limiting continues for more than one hour,
contact Northstar Support.

## What to include in a support request
- Workspace name
- Integration name
- Last successful sync time
- Exact error message, with any sensitive values removed

Never include passwords, API keys, or access tokens.

## Scope
This guide does not list supported third-party services
or specify which record types each integration syncs.