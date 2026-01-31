// JS Helper for dynamic role options
function updateCreateUserFormOptions() {
    const roleSelect = document.getElementById('new-user-role');
    const subRoleSelect = document.getElementById('new-user-subrole');

    if (!currentUser) return;

    // Clear options
    roleSelect.innerHTML = '<option value="">Select Role</option>';
    subRoleSelect.innerHTML = '<option value="None">No Sub-Role</option>';

    // Define hierarchy logic for UI
    const options = [];
    const subOptions = [];

    // IT Admin (100) & Director (90) - Can create everything
    if (currentUser.sub_role === 'ITAdmin' || currentUser.sub_role === 'Director') {
        options.push('Student', 'Faculty', 'Admin');
        subOptions.push('Director', 'CampusDirector', 'ProgramCoordinator', 'ITAdmin');
    }
    // Campus Director (80) - Can create HOD (70), Faculty (50), Student (10)
    else if (currentUser.sub_role === 'CampusDirector') {
        options.push('Student', 'Faculty', 'Admin'); // Admin for HOD
        subOptions.push('ProgramCoordinator'); // Only HOD sub-role allowed
    }
    // HOD (70) - Can create Faculty (50), Student (10)
    else if (currentUser.sub_role === 'ProgramCoordinator') {
        options.push('Student', 'Faculty');
    }
    // Faculty (50) - Can create Student (10)
    else if (currentUser.role === 'Faculty') {
        options.push('Student');
    }

    // Populate Roles
    options.forEach(role => {
        const opt = document.createElement('option');
        opt.value = role;
        opt.textContent = role;
        roleSelect.appendChild(opt);
    });

    // Populate Sub-Roles
    subOptions.forEach(sub => {
        const opt = document.createElement('option');
        opt.value = sub;
        opt.textContent = sub;
        subRoleSelect.appendChild(opt);
    });

    // Hide/Show Department & Campus Selectors based on Scope
    const deptDiv = document.getElementById('new-user-dept').parentElement;
    const campusDiv = document.getElementById('new-user-campus').parentElement;

    // Default: Show all
    deptDiv.style.display = 'block';
    campusDiv.style.display = 'block';

    // 1. Campus Director: Fixed Campus, Can choose Department
    if (currentUser.sub_role === 'CampusDirector') {
        campusDiv.style.display = 'none'; // Auto-filled by backend/client.js
    }
    // 2. HOD & Faculty: Fixed Campus AND Department
    else if (currentUser.sub_role === 'ProgramCoordinator' || currentUser.role === 'Faculty') {
        campusDiv.style.display = 'none';
        deptDiv.style.display = 'none';
    }
}

// Ensure this runs when opening the modal or dashboard
document.addEventListener('DOMContentLoaded', () => {
    // We'll call this from showDashboard in client.js
});
