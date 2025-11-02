
# 📱 User API Documentation (Django + Knox Auth)

## ✅ 1. Send OTP (Phone Verification)
- **Endpoint:** `POST /api/user/send-otp/`
- **Description:** Sends an OTP to the phone number if it doesn't exist already.

### Request Body
```json
{
  "phone": "171234567"
}
```

### Success Response
```json
{
  "status": true,
  "detail": "OTP sent successfully."
}
```

### Failure Response
```json
{
  "status": false,
  "detail": "Phone Number already exists."
}
```

---

## 🔐 2. Verify OTP
- **Endpoint:** `POST /api/user/validate-otp/`
- **Description:** Verifies the OTP sent to the user.

### Request Body
```json
{
  "phone": "0171234567",
  "otp": "1234"
}
```

### Success Response
```json
{
  "status": true,
  "detail": "OTP MATCHED, Please proceed for registration."
}
```

### Failure Response
```json
{
  "status": false,
  "detail": "OTP INCORRECT"
}
```

---

## 👤 3. Register User
- **Endpoint:** `POST /api/user/register/`
- **Description:** Creates a new user after OTP verification.

### Request Body
```json
{
  "phone": "171234567",
  "password": "your_secure_password",
  "role": "user"
}
```

### Success Response
```json
{
  "status": true,
  "detail": "Account created successfully.",
  "user": {
    "phone": "0171234567",
    "role": "user",
    "first_login": false
  }
}
```

### Failure Response
```json
{
  "status": false,
  "detail": "OTP not verified."
}
```

---

## 🔐 4. Login
- **Endpoint:** `POST /api/user/login/`
- **Description:** Logs in the user and returns Knox token and user data.

### Request Body
```json
{
  "phone": "0171234567",
  "password": "your_secure_password"
}
```

### Success Response
```json
{
  "expiry": "2025-08-06T17:00:00Z",
  "token": "knox-auth-token",
  "user": {
    "id": 1,
    "phone": "0171234567",
    "name": "John",
    "role": "user",
    "is_active": true
  }
}
```

### Failure Response
```json
{
  "detail": "Invalid credentials",
  "user_exists": true
}
```

---

## 👁️ 5. Get Current User Info
- **Endpoint:** `GET /api/user/me/`
- **Description:** Returns the currently authenticated user's information.

### Headers
```
Authorization: Token <your_knox_token>
```

### Response
```json
{
  "id": 1,
  "phone": "0171234567",
  "role": "user",
  "first_login": true
}
```

---

## 🛠️ DASHBOARD ENDPOINTS (Role-Based)

### 🛡️ 6. Admin Dashboard
- **Endpoint:** `GET /api/user/admin-dashboard/`
- **Permission:** `admin`

### Response
```json
{
  "message": "Welcome Admin",
  "user_count": 15,
  "admin_count": 2
}
```

---

### 🎯 7. Agent Dashboard
- **Endpoint:** `GET /api/user/agent-dashboard/`
- **Permission:** `agent`

### Response
```json
{
  "message": "Welcome Agent",
  "assigned_tasks": []
}
```

---

### 🧾 8. Staff Dashboard
- **Endpoint:** `GET /api/user/staff-dashboard/`
- **Permission:** `staff`

### Response
```json
{
  "message": "Welcome Staff Member",
  "pending_approvals": []
}
```

---

## 📋 9. List All Users (Admin Only)
- **Endpoint:** `GET /api/user/list/`
- **Permission:** `admin`

### Response
```json
[
  {
    "id": 1,
    "phone": "0171234567",
    "role": "user",
    "first_login": false
  },
  {
    "id": 2,
    "phone": "0171234589",
    "role": "agent",
    "first_login": true
  }
]
```
