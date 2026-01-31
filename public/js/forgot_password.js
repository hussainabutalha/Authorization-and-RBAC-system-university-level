// Forgot Password Flow
let forgotPasswordEmail = '';

function showForgotPasswordModal() {
    document.getElementById('forgot-password-modal').classList.remove('hidden');
    document.getElementById('forgot-step-1').classList.remove('hidden');
    document.getElementById('forgot-step-2').classList.add('hidden');
    document.getElementById('forgot-step-3').classList.add('hidden');
}

function closeForgotPasswordModal() {
    document.getElementById('forgot-password-modal').classList.add('hidden');
    forgotPasswordEmail = '';
}

async function sendOTP() {
    const email = document.getElementById('forgot-email').value;
    if (!email) {
        alert('Please enter your email');
        return;
    }

    try {
        const res = await fetch('/auth/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        const data = await res.json();

        if (res.ok) {
            forgotPasswordEmail = email;
            alert('OTP sent! Check the server console for the OTP code.');
            document.getElementById('forgot-step-1').classList.add('hidden');
            document.getElementById('forgot-step-2').classList.remove('hidden');
        } else {
            alert(data.message || 'Failed to send OTP');
        }
    } catch (e) {
        console.error(e);
        alert('Error sending OTP: ' + e.message);
    }
}

async function verifyOTP() {
    const otp = document.getElementById('otp-code').value;
    if (!otp) {
        alert('Please enter the OTP');
        return;
    }

    try {
        const res = await fetch('/auth/verify-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: forgotPasswordEmail, otp })
        });

        const data = await res.json();

        if (res.ok) {
            alert('OTP verified! Now set your new password.');
            document.getElementById('forgot-step-2').classList.add('hidden');
            document.getElementById('forgot-step-3').classList.remove('hidden');
        } else {
            alert(data.message || 'Invalid OTP');
        }
    } catch (e) {
        alert('Error verifying OTP');
    }
}

async function resetPassword() {
    const newPassword = document.getElementById('new-password').value;
    const otp = document.getElementById('otp-code').value;

    if (!newPassword) {
        alert('Please enter a new password');
        return;
    }

    try {
        const res = await fetch('/auth/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: forgotPasswordEmail,
                otp,
                newPassword
            })
        });

        const data = await res.json();

        if (res.ok) {
            alert('Password reset successfully! You can now login with your new password.');
            closeForgotPasswordModal();
        } else {
            alert(data.message || 'Failed to reset password');
        }
    } catch (e) {
        alert('Error resetting password');
    }
}
