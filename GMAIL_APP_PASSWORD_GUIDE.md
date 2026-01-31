# Gmail App Password Setup - Quick Guide

## ⚠️ IMPORTANT: You CANNOT use your regular Gmail password!

Gmail blocks third-party apps from using your regular password for security reasons.
You need to create an **App Password** instead.

## Step-by-Step Instructions:

### 1. Enable 2-Factor Authentication (if not already enabled)
   - Go to: https://myaccount.google.com/security
   - Find "2-Step Verification" and turn it ON
   - Follow the prompts to set it up with your phone

### 2. Generate App Password
   - Go to: https://myaccount.google.com/apppasswords
   - You might need to sign in again
   - Select "Mail" for the app
   - Select "Other (Custom name)" for the device
   - Type: "RBAC System"
   - Click "Generate"

### 3. Copy the 16-Character Password
   - You'll see something like: `abcd efgh ijkl mnop`
   - Copy this ENTIRE password (you can include or remove spaces)

### 4. Update Your .env File
   Open: `d:\Authorization and RBAC\.env`
   
   Replace line 14 with:
   ```
   EMAIL_PASSWORD=abcdefghijklmnop
   ```
   (Use the actual 16-character password you got from step 3)

### 5. Restart Server
   ```bash
   npm run dev
   ```

### 6. Test Again
   ```bash
   node test_email_config.js
   ```

## Current Status:
- ✅ Email address configured: abutalha112020@gmail.com
- ❌ Using regular password (won't work)
- ⏳ Need App Password

## Alternative: Use a Different Email Service

If you don't want to use Gmail, you can use:
- **Outlook/Hotmail** (simpler, no app password needed)
- **SendGrid** (free tier available)
- **Mailtrap** (for testing only)

Let me know if you need help with any of these alternatives!
