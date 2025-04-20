---
sidebar_position: 2
---

# Multi-Factor Authentication API

This section documents the API endpoints for setting up and managing multi-factor authentication.

## MFA Setup

### Enable MFA for a User

```http
POST /api/v1/mfa/enable
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "mfa_type": "totp"
}
```

Response:

```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code_url": "data:image/png;base64,iVBOR...",
  "setup_status": "pending"
}
```

### Verify MFA Setup

```http
POST /api/v1/mfa/verify-setup
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "verification_code": "123456"
}
```

Response:

```json
{
  "setup_status": "completed",
  "recovery_codes": [
    "ABCD-EFGH-IJKL",
    "MNOP-QRST-UVWX",
    "YZAB-CDEF-GHIJ"
  ]
}
```

## MFA Verification

### Verify MFA Code

```http
POST /api/v1/mfa/verify
Content-Type: application/json

{
  "username": "user@example.com",
  "mfa_code": "123456",
  "request_id": "abcd1234"
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Recovery Options

### Use Recovery Code

```http
POST /api/v1/mfa/recover
Content-Type: application/json

{
  "username": "user@example.com",
  "recovery_code": "ABCD-EFGH-IJKL",
  "request_id": "abcd1234"
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "remaining_recovery_codes": 4
}
```

### Disable MFA

```http
DELETE /api/v1/mfa
Content-Type: application/json
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "MFA has been disabled for user"
}
``` 