# Phase 17 — Object Storage Closure

Date: 2026-10-10
Project: Maruti Pharmacy
Status: TECHNICAL OBJECTIVES VERIFIED

## Objective
Move product images to private object storage rather than relying on
application pod filesystems.

## Verified results
- MinIO health endpoint returned HTTP 200.
- Root credential rotation completed; new credentials authenticated
  successfully with the MinIO admin API.
- MinIO application user `maruti-pharmacy-app` is enabled.
- Policy `maruti-pharmacy-images` is attached to the application user.
- Bucket `maruti-pharmacy-products` exists.
- Both Kubernetes application pods reached the MinIO health endpoint.
- Flask storage integration test passed:
  - Upload: PASS
  - Retrieval: PASS
  - Exact byte comparison: PASS
  - MIME type validation: PASS
  - Temporary object cleanup: PASS

## Recovery and security
- Replacement container: `maruti-minio`
- Data volume: `maruti-minio-data-clean`
- Rollback container retained: `maruti-minio-root-rotation-backup`
- Sensitive container-inspect JSON must not be committed or shared.
- Keep the new root password in a password manager.
- The rollback container and volumes are retained until recovery
  requirements are reviewed.

## Phase gate
Core Phase 17 technical objectives are verified. Review the Git status,
confirm the sensitive JSON is not tracked, and retain the rollback
container until its removal is explicitly approved.
