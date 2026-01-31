# Email Configuration Guide

## Setup Gmail for Sending OTP Emails

### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to your Google Account: https://myaccount.google.com/
2. Click "Security" in the left sidebar
3. Under "Signing in to Google", enable "2-Step Verification"

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" as the app
3. Select "Other (Custom name)" as the device
4. Enter "RBAC System" as the name
5. Click "Generate"
6. Copy the 16-character password (remove spaces)

### Step 3: Update .env File
Open `d:\Authorization and RBAC\.env` and update:

```
EMAIL_SERVICE=gmail
EMAIL_USER=your-actual-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_FROM=RBAC System <your-actual-email@gmail.com>
```

### Step 4: Restart Server
```bash
npm run dev
```

### Alternative Email Services

#### SendGrid
```
EMAIL_SERVICE=SendGrid
EMAIL_USER=apikey
EMAIL_PASSWORD=your-sendgrid-api-key
```

#### Outlook/Hotmail
```
EMAIL_SERVICE=hotmail
EMAIL_USER=your-email@outlook.com
EMAIL_PASSWORD=your-password
```

#### Custom SMTP
```
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_SECURE=false
EMAIL_USER=your-email@example.com
EMAIL_PASSWORD=your-password
```

## Testing

After configuration, test with:
```bash
node test_forgot_password.js
```

You should receive an actual email with the OTP!
