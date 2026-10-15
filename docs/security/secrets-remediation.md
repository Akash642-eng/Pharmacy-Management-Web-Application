# Secrets Remediation Record

## Scope
Maruti Pharmacy application security cleanup.

## Configuration review
- SMTP server defaults to smtp.gmail.com.
- SMTP username and password are read from environment variables.
- Docker Compose passes SMTP credentials through environment variables.
- The local `.env` file is ignored by Git.

## Credential rotation
- A replacement Gmail App Password was created and stored locally.
- SMTP SSL authentication on port 465 succeeded.
- Any app password disclosed in chat must be revoked.
- Final rotation closure remains pending until exposed credentials are revoked and the active replacement is verified.

## Repository and Git history scan
- Scanner: Gitleaks 8.18.2 (local).
- Scan scope: local repository and Git history reachable through local references.
- Commits scanned: 29.
- Result: no leaks found.
- Limitation: this result does not guarantee that all secrets are absent or cover remote refs not present locally.

## CI secret scanning
- Workflow: `.github/workflows/ci.yml`.
- A Gitleaks job is configured to scan the full Git history.
- The Docker publishing job depends on both tests and secret scanning.
- CI closure remains pending until the workflow runs successfully in GitHub Actions.

## Remaining actions
1. Revoke every app password disclosed outside the trusted local environment.
2. Verify the active replacement credential and SMTP authentication.
3. Review Gitleaks findings if future scans report any.
4. Confirm the Gitleaks job passes in GitHub Actions.
5. Re-run the repository and history scan after remediation.
6. Keep this record free of passwords, tokens, and other secret values.

