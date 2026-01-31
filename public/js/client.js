const API_URL = ''; // Relative path handled by same origin
const socket = io(API_URL);

let currentUser = null;
let authToken = localStorage.getItem('token');

// Elements
const loginScreen = document.getElementById('login-screen');
const dashboard = document.getElementById('dashboard');
const loginForm = document.getElementById('login-form');
const userRoleDisplay = document.getElementById('user-role');
const feedContainer = document.getElementById('feed-container');
const postForm = document.getElementById('post-form');

// Init
if (authToken) {
    fetchProfile();
} else {
    showLogin();
}

// Event Listeners
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (res.ok) {
            authToken = data.token;
            localStorage.setItem('token', authToken);
            fetchProfile();
        } else {
            alert(data.message || 'Login failed');
        }
    } catch (error) {
        console.error("Login Error:", error);
        alert('Network error: ' + error.message);
    }
});

postForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!authToken) return;

    const title = document.getElementById('post-title').value;
    const content = document.getElementById('post-content').value;
    const scope = document.getElementById('post-scope').value;
    const target_id = document.getElementById('post-target').value;

    try {
        const res = await fetch(`${API_URL}/posts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ title, content, scope, target_id })
        });

        if (res.ok) {
            alert('Post created!');
            loadPosts();
            postForm.reset();
        } else {
            const data = await res.json();
            alert(`Failed: ${data.message} \n(Check your Role/Scope permissions)`);
        }
    } catch (error) {
        console.error(error);
    }
});

// Functions
async function fetchProfile() {
    try {
        const res = await fetch(`${API_URL}/auth/profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (res.ok) {
            currentUser = await res.json();
            showDashboard();
            loadPosts();
        } else {
            logout();
        }
    } catch (e) {
        logout();
    }
}

function showLogin() {
    loginScreen.classList.remove('hidden');
    dashboard.classList.add('hidden');
}

function showDashboard() {
    loginScreen.classList.add('hidden');
    dashboard.classList.remove('hidden');

    // Update User Info with Department Names
    let roleDisplay = currentUser.role;
    let deptInfo = '';

    // Show sub-role for admins
    if (currentUser.sub_role && currentUser.sub_role !== 'None') {
        roleDisplay = currentUser.sub_role;
    }

    // Add department/campus information based on hierarchy
    if (currentUser.role === 'Admin') {
        if (currentUser.sub_role === 'ITAdmin') {
            deptInfo = ' | System-wide';
        } else if (currentUser.sub_role === 'Director') {
            deptInfo = ' | All Departments';
        } else if (currentUser.sub_role === 'CampusDirector') {
            deptInfo = currentUser.Campus ? ` | ${currentUser.Campus.name}` : ' | Campus';
        } else if (currentUser.sub_role === 'ProgramCoordinator') {
            deptInfo = currentUser.Department ? ` | ${currentUser.Department.name} Dept.` : ' | Department';
        }
    } else if (currentUser.Department) {
        // Faculty and Students show their department
        deptInfo = ` | ${currentUser.Department.name} Dept.`;
    }

    userRoleDisplay.innerText = `${currentUser.name} | ${roleDisplay}${deptInfo}`;

    // Hide Create Post form for Students
    const createPostSection = document.getElementById('create-post-section');
    if (currentUser.role === 'Student') {
        createPostSection.classList.add('hidden');
    } else {
        createPostSection.classList.remove('hidden');
    }

    renderQuickActions();

    // Initialize Classroom System (if script loaded)
    if (typeof initializeClassroomUI === 'function') {
        initializeClassroomUI();
    }
}

function renderQuickActions() {
    const container = document.getElementById('quick-actions-container');
    container.innerHTML = '';

    // Commons Actions
    container.innerHTML += `
        <button onclick="showRoomsModal()"
            class="w-full text-left px-4 py-3 bg-cyan-50 hover:bg-cyan-100 border border-cyan-100 rounded-lg text-sm transition-colors flex items-center justify-between group shadow-sm">
            <span class="text-cyan-700 font-medium">📂 My Chats</span>
            <span class="opacity-0 group-hover:opacity-100 transition-opacity text-cyan-600">→</span>
        </button>
    `;

    // Role Specific
    if (currentUser.role === 'Admin' || currentUser.role === 'Faculty') {
        container.innerHTML += `
            <button onclick="showUserModal()"
                class="w-full text-left px-4 py-3 bg-cyan-50 hover:bg-cyan-100 border border-cyan-100 rounded-lg text-sm transition-colors flex items-center justify-between group shadow-sm">
                <span class="text-cyan-700 font-medium">📩 New Message (DM)</span>
                <span class="opacity-0 group-hover:opacity-100 transition-opacity text-cyan-600">→</span>
            </button>
            <button onclick="createChat()"
                class="w-full text-left px-4 py-3 bg-slate-50 hover:bg-slate-100 border border-slate-100 rounded-lg text-sm transition-colors flex items-center justify-between group shadow-sm">
                <span class="text-slate-700 font-medium">💬 Create Group Chat</span>
                <span class="opacity-0 group-hover:opacity-100 transition-opacity text-slate-600">→</span>
            </button>
        `;
    }

    if (currentUser.role === 'Admin') {
        container.innerHTML += `
            <button onclick="toggleCreateUserForm()"
                class="w-full text-left px-4 py-3 bg-emerald-50 hover:bg-emerald-100 border border-emerald-100 rounded-lg text-sm transition-colors flex items-center justify-between group shadow-sm">
                <span class="text-emerald-700 font-medium">👤 Create New User</span>
                <span class="opacity-0 group-hover:opacity-100 transition-opacity text-emerald-600">→</span>
            </button>
        `;

        // Setup create user form handler
        setTimeout(() => {
            const form = document.getElementById('create-user-form');
            if (form && !form.dataset.listenerAdded) {
                form.addEventListener('submit', handleCreateUser);
                form.dataset.listenerAdded = 'true';
            }
        }, 100);
    }
}

// ROOMS LOGIC
const roomsModal = document.getElementById('rooms-modal');
const roomsList = document.getElementById('rooms-list');

async function showRoomsModal() {
    roomsModal.classList.remove('hidden');
    roomsList.innerHTML = '<div class="text-center text-gray-500">Loading rooms...</div>';

    try {
        const res = await fetch(`${API_URL}/chat`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const rooms = await res.json();

        roomsList.innerHTML = '';
        if (rooms.length === 0) {
            roomsList.innerHTML = '<div class="text-center text-slate-500">No active conversations.</div>';
            return;
        }

        rooms.forEach(room => {
            const div = document.createElement('div');
            div.className = 'flex justify-between items-center p-3 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer group border border-slate-100 shadow-sm mb-2';
            div.onclick = () => { closeRoomsModal(); openChat(room.id, room.name); };
            div.innerHTML = `
                <div>
                    <div class="font-semibold text-slate-800">${room.name}</div>
                    <div class="text-xs text-slate-500">${room.type}</div>
                </div>
                <span class="text-slate-400 group-hover:text-cyan-600">→</span>
            `;
            roomsList.appendChild(div);
        });
    } catch (e) {
        roomsList.innerHTML = '<div class="text-red-400">Error loading rooms</div>';
    }
}

function closeRoomsModal() {
    roomsModal.classList.add('hidden');
}

function logout() {
    localStorage.removeItem('token');
    authToken = null;
    currentUser = null;
    showLogin();
}

async function loadPosts() {
    feedContainer.innerHTML = '<div class="text-center text-slate-400">Refresh to see posts...</div>';

    try {
        const res = await fetch(`${API_URL}/posts`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const posts = await res.json();

        feedContainer.innerHTML = '';
        if (posts.length === 0) {
            feedContainer.innerHTML = '<div class="text-center text-slate-400 py-4">No posts found.</div>';
            return;
        }

        posts.forEach(post => {
            const card = document.createElement('div');
            card.className = 'bg-white border border-slate-200 p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow space-y-2 relative group';

            // Format ID for display
            const targetDisplay = post.target_id ? `(Target: ${post.target_id})` : '';

            // Delete Button Logic (Author or Admin)
            let deleteBtn = '';
            if (currentUser.id === post.author_id || currentUser.role === 'Admin') {
                deleteBtn = `
                    <button onclick="deletePost(${post.id})" class="absolute top-4 right-4 text-slate-300 hover:text-red-500 transition-colors p-1 rounded-full hover:bg-red-50" title="Delete Post">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                `;
            }

            card.innerHTML = `
                ${deleteBtn}
                <div class="flex justify-between items-start pr-8">
                    <h4 class="font-bold text-cyan-700">${post.title}</h4>
                    <span class="text-xs px-2 py-1 rounded bg-slate-100 text-slate-600 border border-slate-200 font-medium">
                        ${post.scope} ${targetDisplay}
                    </span>
                </div>
                <p class="text-slate-700 text-sm leading-relaxed">${post.content}</p>
                <div class="text-xs text-slate-400 mt-2 flex items-center gap-1">
                    <span class="font-medium text-slate-500">Author ID: ${post.author_id}</span> • ${new Date(post.createdAt).toLocaleString()}
                </div>
            `;
            feedContainer.appendChild(card);
        });

    } catch (error) {
        feedContainer.innerHTML = '<div class="text-red-400">Error loading posts</div>';
    }
}

async function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post?')) return;

    try {
        const res = await fetch(`${API_URL}/posts/${postId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (res.ok) {
            // Remove element visually or reload
            loadPosts();
        } else {
            const data = await res.json();
            alert(data.message || 'Failed to delete');
        }
    } catch (error) {
        alert('Network error');
    }
}

const userModal = document.getElementById('user-modal');
const userList = document.getElementById('user-list');

async function showUserModal() {
    userModal.classList.remove('hidden');
    userList.innerHTML = '<div class="text-center text-slate-500">Loading users...</div>';

    try {
        const res = await fetch(`${API_URL}/auth/users`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const users = await res.json();

        userList.innerHTML = '';
        users.forEach(user => {
            if (user.id === currentUser.id) return; // Don't show self

            const div = document.createElement('div');
            div.className = 'flex justify-between items-center p-3 bg-white border border-slate-100 hover:border-cyan-200 rounded-xl transition-all shadow-sm group';
            div.innerHTML = `
                <div>
                    <div class="font-semibold text-slate-800">${user.name}</div>
                    <div class="text-xs text-slate-500">${user.role}</div>
                </div>
                <button onclick="startDM(${user.id}, '${user.name}')" class="px-3 py-1.5 bg-cyan-50 text-cyan-600 hover:bg-cyan-600 hover:text-white rounded-lg text-xs font-medium transition-all">
                    Message
                </button>
            `;
            userList.appendChild(div);
        });
    } catch (e) {
        userList.innerHTML = '<div class="text-red-400">Error loading users</div>';
    }
}

function closeUserModal() {
    userModal.classList.add('hidden');
}

async function startDM(userId, userName) {
    try {
        const res = await fetch(`${API_URL}/chat/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                name: `DM with ${userName}`,
                type: 'PERSONAL',
                participant_ids: [userId]
            })
        });
        const data = await res.json();

        closeUserModal();
        openChat(data.room.id, data.room.name);
    } catch (e) {
        alert('Error starting DM');
    }
}

function toggleCreateUserForm() {
    const section = document.getElementById('create-user-section');
    if (section.classList.contains('hidden')) {
        section.classList.remove('hidden');
        // Dynamic UI update for hierarchy
        if (typeof updateCreateUserFormOptions === 'function') {
            updateCreateUserFormOptions();
        }
        // Scroll to section
        setTimeout(() => section.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
    } else {
        section.classList.add('hidden');
    }
}

async function handleCreateUser(e) {
    e.preventDefault();

    const name = document.getElementById('new-user-name').value;
    const email = document.getElementById('new-user-email').value;
    const password = document.getElementById('new-user-password').value;
    const role = document.getElementById('new-user-role').value;
    const sub_role = document.getElementById('new-user-subrole').value;

    try {
        const res = await fetch(`${API_URL}/auth/create-user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ name, email, password, role, sub_role })
        });

        const data = await res.json();

        if (res.ok) {
            alert(`User created successfully! Email: ${email}`);
            document.getElementById('create-user-form').reset();
            toggleCreateUserForm();
        } else {
            alert(data.message || 'Failed to create user');
        }
    } catch (e) {
        alert('Error creating user');
    }
}

// CHAT LOGIC
const chatModal = document.getElementById('chat-modal');
const messagesArea = document.getElementById('messages-area');
const chatTitle = document.getElementById('chat-title');
const chatForm = document.getElementById('chat-form');
let currentRoomId = null;
let chatPollInterval = null;

async function openChat(roomId, roomName) {
    currentRoomId = roomId;
    chatTitle.innerText = roomName;
    chatModal.classList.remove('hidden');
    messagesArea.innerHTML = '<div class="text-center text-slate-500 mt-10">Loading history...</div>';

    await fetchMessages();
    await fetchMessages();
    startPolling();

    // Join Socket Room
    socket.emit('joinRoom', roomId);
}

function closeChatModal() {
    chatModal.classList.add('hidden');
    if (currentRoomId) {
        socket.emit('leaveRoom', currentRoomId);
    }
    currentRoomId = null;
    stopPolling();
}

async function fetchMessages() {
    if (!currentRoomId) return;
    try {
        const res = await fetch(`${API_URL}/chat/messages/${currentRoomId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const messages = await res.json();
        renderMessages(messages);
    } catch (e) {
        console.error(e);
    }
}

function renderMessages(messages) {
    messagesArea.innerHTML = '';
    if (messages.length === 0) {
        messagesArea.innerHTML = '<div class="text-center text-slate-500 mt-10">No messages yet. Say hi! 👋</div>';
        return;
    }

    messages.forEach(msg => {
        const isMe = msg.sender_id === currentUser.id;
        const div = document.createElement('div');
        div.className = `flex ${isMe ? 'justify-end' : 'justify-start'}`;

        div.innerHTML = `
            <div class="max-w-[70%] ${isMe ? 'bg-cyan-600 text-white shadow-md shadow-cyan-500/20' : 'bg-white border border-slate-200 text-slate-700 shadow-sm'} rounded-2xl px-4 py-2 text-sm">
                ${!isMe ? `<div class="text-xs text-cyan-700 font-bold mb-0.5">${msg.Sender.name}</div>` : ''}
                <div class="leading-relaxed">${msg.content}</div>
            </div>
        `;
        messagesArea.appendChild(div);
    });

    messagesArea.scrollTop = messagesArea.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    if (!content || !currentRoomId) return;

    try {
        input.value = ''; // Optimistic clear
        await fetch(`${API_URL}/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ room_id: currentRoomId, content })
        });
        fetchMessages();
    } catch (e) {
        alert('Failed to send');
    }
});

function startPolling() {
    stopPolling();
    chatPollInterval = setInterval(fetchMessages, 3000); // Poll every 3s
}

function stopPolling() {
    if (chatPollInterval) clearInterval(chatPollInterval);
}

async function createChat() {
    const name = prompt("Enter Chat Room Name:");
    if (!name) return;

    try {
        const res = await fetch(`${API_URL}/chat/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ name, type: 'GROUP' })
        });
        const data = await res.json();
        alert(data.message);
    } catch (e) {
        alert('Err');
    }
}


// Profile Management Functions
function showProfileModal() {
    if (!currentUser) return;

    // Populate Fields
    document.getElementById('profile-initials').textContent = currentUser.name.charAt(0).toUpperCase();
    document.getElementById('profile-role-badge').textContent = currentUser.role;
    document.getElementById('profile-name').value = currentUser.name;
    document.getElementById('profile-email').value = currentUser.email;
    document.getElementById('profile-role').value = currentUser.role;
    document.getElementById('profile-dept').value = currentUser.department_id ? `Dept ID: ${currentUser.department_id}` : 'General';

    // Reset State
    cancelEditProfile();

    // Show Modal
    document.getElementById('profile-modal').classList.remove('hidden');
}

function closeProfileModal() {
    document.getElementById('profile-modal').classList.add('hidden');
}

function enableEditProfile() {
    document.getElementById('profile-name').disabled = false;
    document.getElementById('profile-email').disabled = false;

    document.getElementById('btn-edit-profile').classList.add('hidden');
    document.getElementById('edit-actions').classList.remove('hidden');
}

function cancelEditProfile() {
    document.getElementById('profile-name').disabled = true;
    document.getElementById('profile-email').disabled = true;

    // Reset Values
    if (currentUser) {
        document.getElementById('profile-name').value = currentUser.name;
        document.getElementById('profile-email').value = currentUser.email;
    }

    document.getElementById('btn-edit-profile').classList.remove('hidden');
    document.getElementById('edit-actions').classList.add('hidden');
}

async function saveProfile() {
    const name = document.getElementById('profile-name').value;
    const email = document.getElementById('profile-email').value;

    try {
        const res = await fetch(`${API_URL}/auth/profile/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ name, email })
        });

        const data = await res.json();

        if (res.ok) {
            if (data.verificationRequired) {
                // Show Verification Modal
                showEmailVerificationModal(data.oldEmail, data.newEmail);
                return; // Stop further execution (don't update local state yet)
            }

            alert('Profile updated successfully!');
            // Update Local State
            currentUser.name = name;
            currentUser.email = email;

            // Refresh Header
            showDashboard();

            // Close Edit Mode
            cancelEditProfile();
        } else {
            alert(data.message || 'Update failed');
        }
    } catch (error) {
        console.error(error);
        alert('Network error updating profile');
    }
}

// EMAIL VERIFICATION LOGIC
const emailVerificationModal = document.getElementById('email-verification-modal');
const emailVerificationForm = document.getElementById('email-verification-form');

function showEmailVerificationModal(oldEmail, newEmail) {
    emailVerificationModal.classList.remove('hidden');
    // document.getElementById('verify-msg').innerText = `Verifying change from ${oldEmail} to ${newEmail}`;
}

function closeEmailVerificationModal() {
    emailVerificationModal.classList.add('hidden');
    emailVerificationForm.reset();
}

emailVerificationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const otpOld = document.getElementById('otp-old-email').value;
    const otpNew = document.getElementById('otp-new-email').value;

    try {
        const res = await fetch(`${API_URL}/auth/profile/verify-email-update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ otpOld, otpNew })
        });

        const data = await res.json();

        if (res.ok) {
            alert('Email updated successfully!');
            closeEmailVerificationModal();

            // Update local user email
            // Note: In a real app we might want to fetchProfile() again to be sure
            // but we can also just update the local state if the server confirmed it.
            // However, the previous "pending" email is now official. 
            // We need to know what that email was if we want to update UI without refetch.
            // Simplest is to just refetch profile:
            fetchProfile();

            cancelEditProfile();
        } else {
            alert(data.message || 'Verification failed');
        }
    } catch (error) {
        alert('Error during verification');
    }
});
socket.on('newMessage', (msg) => {
    // Only append if we are in the same room
    if (currentRoomId && msg.room_id === currentRoomId) {
        // Append message
        const isMe = msg.sender_id === currentUser.id;
        const div = document.createElement('div');
        div.className = `flex ${isMe ? 'justify-end' : 'justify-start'} animate-fade-in`;

        div.innerHTML = `
            <div class="max-w-[70%] ${isMe ? 'bg-cyan-600 text-white shadow-md shadow-cyan-500/20' : 'bg-white border border-slate-200 text-slate-700 shadow-sm'} rounded-2xl px-4 py-2 text-sm">
                ${!isMe ? `<div class="text-xs text-cyan-700 font-bold mb-0.5">${msg.Sender ? msg.Sender.name : 'User'}</div>` : ''}
                <div class="leading-relaxed">${msg.content}</div>
            </div>
        `;
        messagesArea.appendChild(div);
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
});

socket.on('connect', () => {
    console.log('Connected to socket server');
});
