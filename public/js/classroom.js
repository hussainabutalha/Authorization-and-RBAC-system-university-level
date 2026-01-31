// Classroom Management Functions

// Load classrooms based on user role
async function loadClassrooms() {
    try {
        const res = await fetch(`${API_URL}/classroom`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (!res.ok) throw new Error('Failed to load classrooms');

        const classrooms = await res.json();
        const list = document.getElementById('classroom-list');

        if (classrooms.length === 0) {
            list.innerHTML = '<div class="text-xs text-slate-500">No classrooms available</div>';
            return;
        }

        list.innerHTML = classrooms.map(classroom => `
            <div class="bg-white border border-slate-200 p-4 rounded-xl hover:shadow-md transition-all shadow-sm group">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-bold text-slate-800">${classroom.name}</h4>
                        <p class="text-xs text-slate-500 mt-1">${classroom.description || 'No description'}</p>
                        <div class="flex gap-2 mt-3 text-xs text-slate-400 font-medium">
                            <span class="bg-slate-50 px-2 py-1 rounded border border-slate-100">📍 ${classroom.department?.name || 'Unknown'}</span>
                            <span class="bg-slate-50 px-2 py-1 rounded border border-slate-100">👥 ${classroom.Members?.length || 0}/${classroom.max_students}</span>
                        </div>
                    </div>
                    <div class="flex gap-2 opacity-80 group-hover:opacity-100 transition-opacity">
                        <button onclick="viewClassroom(${classroom.id})" class="text-xs bg-cyan-50 text-cyan-700 hover:bg-cyan-100 border border-cyan-100 px-3 py-1.5 rounded-lg font-medium transition-colors">View</button>
                        ${canJoinClassroom(classroom) ? `<button onclick="joinClassroom(${classroom.id})" class="text-xs bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-100 px-3 py-1.5 rounded-lg font-medium transition-colors">Join</button>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading classrooms:', error);
        document.getElementById('classroom-list').innerHTML = '<div class="text-xs text-red-500">Error loading classrooms</div>';
    }
}

// Check if user can join a classroom
function canJoinClassroom(classroom) {
    if (!currentUser) return false;

    // Check if already a member
    const isMember = classroom.Members?.some(m => m.id === currentUser.id);
    if (isMember) return false;

    // Students and Faculty can join
    return currentUser.role === 'Student' || currentUser.role === 'Faculty';
}

// Show create classroom modal
function showCreateClassroomModal() {
    const modal = document.getElementById('create-classroom-modal');
    if (modal) {
        modal.classList.remove('hidden');

        // Show target department field for Admins/Directors
        const deptContainer = document.getElementById('classroom-target-dept-container');
        if (currentUser && currentUser.role === 'Admin' &&
            (currentUser.sub_role === 'ITAdmin' || currentUser.sub_role === 'Director')) {
            deptContainer.classList.remove('hidden');
        } else {
            deptContainer.classList.add('hidden');
        }
    }
}

// Close create classroom modal
function closeCreateClassroomModal() {
    const modal = document.getElementById('create-classroom-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('create-classroom-form').reset();
    }
}

// Create classroom
async function createClassroom(e) {
    e.preventDefault();

    const name = document.getElementById('classroom-name').value;
    const description = document.getElementById('classroom-description').value;
    const max_students = document.getElementById('classroom-max-students').value;
    const target_department_id = document.getElementById('classroom-target-dept').value;

    const payload = {
        name,
        description,
        max_students: parseInt(max_students)
    };

    if (target_department_id) {
        payload.target_department_id = parseInt(target_department_id);
    }

    try {
        const res = await fetch(`${API_URL}/classroom/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok) {
            alert('Classroom created successfully!');
            closeCreateClassroomModal();
            loadClassrooms();
        } else {
            alert(data.message || 'Failed to create classroom');
        }
    } catch (error) {
        console.error('Error creating classroom:', error);
        alert('Error creating classroom');
    }
}

// Join classroom
async function joinClassroom(classroomId) {
    try {
        const res = await fetch(`${API_URL}/classroom/${classroomId}/join`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const data = await res.json();

        if (res.ok) {
            alert(data.message);
            loadClassrooms();
        } else {
            alert(data.message || 'Failed to join classroom');
        }
    } catch (error) {
        console.error('Error joining classroom:', error);
        alert('Error joining classroom');
    }
}

// View classroom details
async function viewClassroom(classroomId) {
    try {
        const res = await fetch(`${API_URL}/classroom/${classroomId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (!res.ok) throw new Error('Failed to load classroom');

        const classroom = await res.json();

        // Store ID for post creation
        currentClassroomId = classroom.id;

        // Join Socket Room
        socket.emit('joinRoom', `classroom_${classroom.id}`);

        // Show classroom details modal
        showClassroomDetailsModal(classroom);
        loadClassroomPosts(classroom.id);
    } catch (error) {
        console.error('Error viewing classroom:', error);
        // alert('Error loading classroom details'); // Suppress alert on auto-refresh
    }
}

// Toggle Hand Raise
async function toggleHandRaise(classroomId) {
    try {
        const res = await fetch(`${API_URL}/classroom/${classroomId}/hand-raise`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const data = await res.json();

        if (res.ok) {
            // Refresh details
            viewClassroom(classroomId);
        } else {
            alert(data.message || 'Failed to toggle hand raise');
        }
    } catch (error) {
        console.error('Error toggling hand raise:', error);
        alert('Error toggling hand raise');
    }
}

// Show Create Post Form
function showCreatePostForm() {
    document.getElementById('create-post-form-container').classList.remove('hidden');
    document.getElementById('create-classroom-post-btn').classList.add('hidden');
}

// Hide Create Post Form
function hideCreatePostForm() {
    document.getElementById('create-post-form-container').classList.add('hidden');
    document.getElementById('create-classroom-post-btn').classList.remove('hidden');
    document.getElementById('post-title').value = '';
    document.getElementById('post-content').value = '';
}

// Create Classroom Post
async function createClassroomPost(e) {
    e.preventDefault();
    if (!currentClassroomId) return;

    const title = document.getElementById('post-title').value;
    const content = document.getElementById('post-content').value;

    try {
        const res = await fetch(`${API_URL}/posts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                title,
                content,
                scope: 'CLASSROOM',
                target_id: currentClassroomId
            })
        });

        const data = await res.json();

        if (res.ok) {
            hideCreatePostForm();
            loadClassroomPosts(currentClassroomId);
        } else {
            alert(data.message || 'Failed to create post');
        }
    } catch (error) {
        console.error('Error creating post:', error);
        alert('Error creating post');
    }
}

// Load Classroom Posts
async function loadClassroomPosts(classroomId) {
    const postsList = document.getElementById('classroom-posts-list');
    postsList.innerHTML = '<div class="text-xs text-slate-500">Loading posts...</div>';

    try {
        const res = await fetch(`${API_URL}/posts?scope=CLASSROOM&target_id=${classroomId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        const posts = await res.json();

        if (posts.length === 0) {
            postsList.innerHTML = '<div class="text-xs text-slate-500">No posts yet</div>';
            return;
        }

        postsList.innerHTML = posts.map(post => `
            <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h5 class="font-bold text-sm text-cyan-700">${post.title}</h5>
                <p class="text-sm mt-1 text-slate-600 leading-relaxed">${post.content}</p>
                <div class="mt-3 text-xs text-slate-400 flex justify-between border-t border-slate-100 pt-2">
                    <span>${new Date(post.createdAt).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading posts:', error);
        postsList.innerHTML = '<div class="text-xs text-red-500">Error loading posts</div>';
    }
}

// Show classroom details modal
function showClassroomDetailsModal(classroom) {
    const modal = document.getElementById('classroom-details-modal');
    if (!modal) return;

    document.getElementById('classroom-detail-name').textContent = classroom.name;
    document.getElementById('classroom-detail-description').textContent = classroom.description || 'No description';
    document.getElementById('classroom-detail-department').textContent = classroom.department?.name || 'Unknown';
    document.getElementById('classroom-detail-creator').textContent = classroom.Creator?.name || 'Unknown';

    // Check for current user membership
    console.log('Classroom Members:', classroom.Members);
    const currentMember = classroom.Members?.find(m => m.id === currentUser.id);
    console.log('Current Member:', currentMember);
    console.log('Is Hand Raised (DB):', currentMember?.ClassroomMember?.is_hand_raised);

    const isStudent = currentMember && currentMember.ClassroomMember.role === 'student';
    const isHandRaised = currentMember?.ClassroomMember?.is_hand_raised;

    // Show Raise Hand button for students
    const actionContainer = document.getElementById('classroom-details-actions');
    if (actionContainer) {
        if (isStudent) {
            actionContainer.innerHTML = `
                <button onclick="toggleHandRaise(${classroom.id})" 
                    class="px-4 py-2 rounded-lg text-sm font-medium transition-colors border shadow-sm flex items-center gap-2 ${isHandRaised ? 'bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'}">
                    ${isHandRaised
                    ? '<span class="animate-wave text-lg">✋</span> Lower Hand'
                    : '<span class="text-lg">✋</span> Raise Hand'}
                </button>
            `;
        } else {
            actionContainer.innerHTML = '';
        }
    }

    const membersList = document.getElementById('classroom-members-list');
    if (classroom.Members && classroom.Members.length > 0) {
        membersList.innerHTML = classroom.Members.map(member => {
            const handRaised = member.ClassroomMember?.is_hand_raised;
            return `
            <div class="flex justify-between items-center p-3 bg-white border border-slate-100 rounded-xl shadow-sm ${handRaised ? 'ring-2 ring-amber-200 bg-amber-50/50' : ''}">
                <div>
                    <span class="font-semibold text-sm text-slate-800">${member.name}</span>
                    <span class="text-xs text-slate-500 ml-2 bg-slate-100 px-2 py-0.5 rounded-full">(${member.ClassroomMember?.role || 'student'})</span>
                    ${handRaised ? '<span class="ml-2 text-amber-500 text-lg animate-wave" title="Hand Raised">✋</span>' : ''}
                </div>
                <span class="text-xs text-cyan-300 font-bold">${member.email}</span>
            </div>
        `}).join('');
    } else {
        membersList.innerHTML = '<div class="text-xs text-slate-500">No members yet</div>';
    }

    // Show Create Post button for non-students (Admins, Faculty)
    const createPostBtn = document.getElementById('create-classroom-post-btn');
    if (createPostBtn) {
        if (currentUser.role !== 'Student') {
            createPostBtn.classList.remove('hidden');
        } else {
            createPostBtn.classList.add('hidden');
        }
    }

    modal.classList.remove('hidden');

    // Default to Stream
    switchClassroomTab('stream');
}

let currentClassroomId = null; // Track current open classroom

// Listen for updates
socket.on('classroomUpdate', (data) => {
    console.log('Classroom Update:', data);
    if (!currentClassroomId) return;

    // If update belongs to current classroom (basic check, could be stricter)
    // Ideally check if data.classroomId matches, but for now we rely on room subscription

    // Refresh to show new state (Member Joined/Left, Hand Raised)
    if (document.getElementById('view-stream').classList.contains('hidden') === false) {
        viewClassroom(currentClassroomId, true);
    }
});

// Close classroom details modal
function closeClassroomDetailsModal() {
    const modal = document.getElementById('classroom-details-modal');
    if (modal) {
        modal.classList.add('hidden');
    }

    if (currentClassroomId) {
        socket.emit('leaveRoom', `classroom_${currentClassroomId}`);
        currentClassroomId = null;
    }
}

// Initialize classroom UI based on role
function initializeClassroomUI() {
    if (!currentUser) return;

    const createBtn = document.getElementById('create-classroom-btn');

    // Show create button for HOD, Campus Director, Director
    if (currentUser.role === 'Admin' &&
        ['Director', 'CampusDirector', 'ProgramCoordinator'].includes(currentUser.sub_role)) {
        if (createBtn) createBtn.classList.remove('hidden');
    }

    // Load classrooms
    loadClassrooms();
}

// Tab Switching
function switchClassroomTab(tab) {
    const streamView = document.getElementById('view-stream');
    const classworkView = document.getElementById('view-classwork');
    const tabStream = document.getElementById('tab-stream');
    const tabClasswork = document.getElementById('tab-classwork');

    if (tab === 'stream') {
        streamView.classList.remove('hidden');
        classworkView.classList.add('hidden');
        tabStream.className = "px-4 py-2 text-sm text-cyan-400 border-b-2 border-cyan-400 font-medium";
        tabClasswork.className = "px-4 py-2 text-sm text-gray-400 hover:text-gray-200 font-medium";
    } else {
        streamView.classList.add('hidden');
        classworkView.classList.remove('hidden');
        tabStream.className = "px-4 py-2 text-sm text-gray-400 hover:text-gray-200 font-medium";
        tabClasswork.className = "px-4 py-2 text-sm text-cyan-400 border-b-2 border-cyan-400 font-medium";

        loadAssignments(currentClassroomId);
    }
}

// Assignments Logic
async function loadAssignments(classroomId) {
    const list = document.getElementById('assignments-list');
    list.innerHTML = '<div class="text-center text-gray-500 mt-4">Loading assignments...</div>';

    // Show Create Button for Instructors/Admins
    const createBtn = document.getElementById('create-assignment-btn');
    // Simplified Role Check: Admin or Faculty
    if (currentUser.role === 'Admin' || currentUser.role === 'Faculty') {
        createBtn.classList.remove('hidden');
    } else {
        createBtn.classList.add('hidden');
    }

    try {
        const res = await fetch(`${API_URL}/assignments/${classroomId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const assignments = await res.json();

        if (assignments.length === 0) {
            list.innerHTML = '<div class="text-center text-gray-500 mt-4">No assignments yet.</div>';
            return;
        }

        list.innerHTML = assignments.map(a => `
            <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start">
                    <div>
                        <h5 class="font-bold text-slate-800 text-lg">${a.title}</h5>
                        <p class="text-sm text-slate-600 mt-1">${a.description || ''}</p>
                        <p class="text-xs text-slate-400 mt-2 font-medium">Due: ${a.due_date ? new Date(a.due_date).toLocaleDateString() : 'No due date'}</p>
                    </div>
                    <div>
                        ${currentUser.role === 'Student'
                ? `<button onclick="openSubmissionOverlay(${a.id}, '${a.title}', '${a.description || ''}')" class="text-xs bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 px-3 py-1.5 rounded-lg font-medium transition-colors">Turn In</button>`
                : `<button onclick="viewSubmissions(${a.id})" class="text-xs bg-slate-50 text-slate-600 hover:bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-lg font-medium transition-colors">View Submissions</button>`
            }
                    </div>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error(error);
        list.innerHTML = '<div class="text-red-500">Error loading assignments</div>';
    }
}

function showCreateAssignmentForm() {
    document.getElementById('create-assignment-form-container').classList.remove('hidden');
    document.getElementById('create-assignment-btn').classList.add('hidden');
}

function hideCreateAssignmentForm() {
    document.getElementById('create-assignment-form-container').classList.add('hidden');
    document.getElementById('create-assignment-btn').classList.remove('hidden');
}

async function createAssignment(e) {
    e.preventDefault();
    const title = document.getElementById('assign-title').value;
    const description = document.getElementById('assign-desc').value;
    const due_date = document.getElementById('assign-date').value;

    try {
        const res = await fetch(`${API_URL}/assignments/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                title,
                description,
                due_date,
                classroom_id: currentClassroomId
            })
        });

        if (res.ok) {
            hideCreateAssignmentForm();
            loadAssignments(currentClassroomId);
            document.getElementById('assign-title').value = '';
            document.getElementById('assign-desc').value = '';
        } else {
            alert('Failed to create assignment');
        }
    } catch (e) {
        alert('Error creating assignment');
    }
}

// Submission Logic
let currentAssignmentId = null;

function openSubmissionOverlay(assignId, title, desc) {
    currentAssignmentId = assignId;
    document.getElementById('submission-overlay').classList.remove('hidden');
    document.getElementById('sub-overlay-title').innerText = title;

    // Show Student View
    document.getElementById('student-submission-view').classList.remove('hidden');
    document.getElementById('instructor-submission-view').classList.add('hidden');
    document.getElementById('sub-overlay-desc').innerText = desc;
}

function closeSubmissionOverlay() {
    document.getElementById('submission-overlay').classList.add('hidden');
    currentAssignmentId = null;
}

async function submitWork(e) {
    e.preventDefault();
    const text = document.getElementById('sub-text').value;
    const fileInput = document.getElementById('sub-file');
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('assignment_id', currentAssignmentId);
    if (text) formData.append('text_content', text);
    if (file) formData.append('file', file);

    try {
        const res = await fetch(`${API_URL}/assignments/submit`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` },
            body: formData
        });

        if (res.ok) {
            alert('Submitted successfully!');
            closeSubmissionOverlay();
        } else {
            alert('Submission failed');
        }
    } catch (e) {
        alert('Error submitting');
    }
}

async function viewSubmissions(assignId) {
    currentAssignmentId = assignId;
    document.getElementById('submission-overlay').classList.remove('hidden');
    document.getElementById('sub-overlay-title').innerText = "Submissions";

    document.getElementById('student-submission-view').classList.add('hidden');
    document.getElementById('instructor-submission-view').classList.remove('hidden');

    const list = document.getElementById('submissions-list');
    list.innerHTML = 'Loading...';

    try {
        const res = await fetch(`${API_URL}/assignments/${assignId}/submissions`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const subs = await res.json();

        if (subs.length === 0) {
            list.innerHTML = 'No submissions yet.';
            return;
        }

        list.innerHTML = subs.map(s => `
            <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 mb-2">
                <div class="font-bold text-sm text-slate-800">${s.Student.name}</div>
                <div class="text-sm text-slate-600 mt-1">${s.text_content || ''}</div>
                ${s.file_url ? `<a href="${API_URL}${s.file_url}" target="_blank" class="text-xs text-cyan-600 hover:underline block mt-1 font-medium">View File</a>` : ''}
                <div class="mt-3 pt-3 border-t border-slate-200 flex gap-2 items-center">
                    <input type="text" placeholder="Grade" value="${s.grade || ''}" id="grade-${s.id}" class="w-16 bg-white border border-slate-300 rounded px-2 py-1 text-xs outline-none focus:border-cyan-500 text-slate-800">
                    <button onclick="gradeSubmission(${s.id})" class="text-xs bg-cyan-600 hover:bg-cyan-700 text-white px-3 py-1 rounded-lg">Save Grade</button>
                    <span id="grade-msg-${s.id}" class="text-xs text-emerald-600 font-medium"></span>
                </div>
            </div>
        `).join('');

    } catch (e) {
        list.innerHTML = 'Error loading submissions';
    }
}

async function gradeSubmission(subId) {
    const grade = document.getElementById(`grade-${subId}`).value;
    try {
        const res = await fetch(`${API_URL}/assignments/submission/${subId}/grade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ grade, feedback: 'Graded via UI' })
        });
        if (res.ok) {
            document.getElementById(`grade-msg-${subId}`).innerText = "Saved!";
            setTimeout(() => document.getElementById(`grade-msg-${subId}`).innerText = "", 2000);
        }
    } catch (e) {
        alert('Error grading');
    }
}

// Add event listener for create classroom form
document.addEventListener('DOMContentLoaded', () => {
    const createForm = document.getElementById('create-classroom-form');
    if (createForm) {
        createForm.addEventListener('submit', createClassroom);
    }
});
