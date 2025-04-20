---
sidebar_position: 1
---

# Authentication API

The Authentication API handles user login, token refresh, logout, and password reset operations.

## Login

Authenticates a user and issues JWT tokens for accessing protected resources.

### Request

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Error Responses

- `401 Unauthorized` - Invalid credentials
- `400 Bad Request` - Missing username or password
- `403 Forbidden` - Account is inactive or locked

## Refresh Token

Refreshes an expired access token using a valid refresh token.

### Request

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Error Responses

- `401 Unauthorized` - Invalid or expired refresh token
- `400 Bad Request` - Missing refresh token

## Logout

Invalidates the user's refresh tokens.

### Request

```http
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{}
```

### Response

```json
{
  "message": "Successfully logged out"
}
```

## Password Reset Request

Initiates a password reset process by sending a reset link to the user's email.

### Request

```http
POST /api/v1/auth/password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### Response

```json
{
  "message": "Password reset email sent"
}
```

### Error Responses

- `404 Not Found` - Email not found
- `400 Bad Request` - Invalid email format

## Password Reset Confirmation

Resets the user's password using the token sent via email.

### Request

```http
POST /api/v1/auth/password-reset/confirm
Content-Type: application/json

{
  "token": "reset-token-from-email",
  "new_password": "new-password123"
}
```

### Response

```json
{
  "message": "Password successfully reset"
}
```

### Error Responses

- `401 Unauthorized` - Invalid or expired token
- `400 Bad Request` - Password doesn't meet requirements

## MFA Challenge

If MFA is enabled for the user, this endpoint is called after successful login to initiate the MFA verification process.

### Request

```http
POST /api/v1/auth/mfa/challenge
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "method": "totp"  // Options: "totp", "backup_code"
}
```

### Response

```json
{
  "mfa_challenge_id": "abc123",
  "message": "MFA challenge issued"
}
```

## MFA Verification

Verifies the MFA code provided by the user.

### Request

```http
POST /api/v1/auth/mfa/verify
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "mfa_challenge_id": "abc123",
  "code": "123456"
}
```

### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Error Responses

- `401 Unauthorized` - Invalid MFA code
- `400 Bad Request` - Missing or invalid challenge ID 