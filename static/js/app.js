/**
 * Mini GitHub LAN - Frontend JavaScript
 */

const API_BASE = '/api';

// Repository Management
function openAddRepoDialog() {
    document.getElementById('addRepoDialog').style.display = 'block';
}

function closeAddRepoDialog() {
    document.getElementById('addRepoDialog').style.display = 'none';
    document.getElementById('repoName').value = '';
    document.getElementById('remotePath').value = '';
}

async function addRepository(event) {
    event.preventDefault();
    const name = document.getElementById('repoName').value;
    const remotePath = document.getElementById('remotePath').value;
    
    try {
        const response = await fetch(`${API_BASE}/repositories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, remote_path: remotePath })
        });
        
        if (response.ok) {
            showNotification('Repository added successfully', 'success');
            closeAddRepoDialog();
            setTimeout(() => location.reload(), 1500);
        } else {
            const error = await response.json();
            showNotification(`Error: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

async function deleteRepo(repoName) {
    if (!confirm(`Delete repository "${repoName}"? This won't delete the remote repository.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/repositories/${repoName}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Repository deleted', 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            const error = await response.json();
            showNotification(`Error: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

async function cloneRepo(repoName) {
    const button = event.target;
    button.disabled = true;
    button.innerText = 'Cloning...';
    
    try {
        const response = await fetch(`${API_BASE}/repositories/${repoName}/clone-or-fetch`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Repository cloned/fetched successfully', 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            const error = await response.json();
            showNotification(`Error: ${error.detail}`, 'danger');
            button.disabled = false;
            button.innerText = 'Clone/Fetch';
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
        button.disabled = false;
        button.innerText = 'Clone/Fetch';
    }
}

// Status Management
async function stageAll(repoName) {
    try {
        const response = await fetch(`${API_BASE}/repositories/${repoName}/stage-all`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('All changes staged', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            const error = await response.json();
            showNotification(`Error: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

function openCommitDialog() {
    document.getElementById('commitDialog').style.display = 'block';
}

function closeCommitDialog() {
    document.getElementById('commitDialog').style.display = 'none';
    document.getElementById('commitMessage').value = '';
}

async function createCommit(event, repoName) {
    event.preventDefault();
    const message = document.getElementById('commitMessage').value;
    const authorName = document.getElementById('authorName').value;
    const authorEmail = document.getElementById('authorEmail').value;
    
    try {
        const response = await fetch(`${API_BASE}/repositories/${repoName}/commit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                author_name: authorName,
                author_email: authorEmail
            })
        });
        
        if (response.ok) {
            showNotification('Commit created successfully', 'success');
            closeCommitDialog();
            setTimeout(() => location.reload(), 1500);
        } else {
            const error = await response.json();
            showNotification(`Error: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

async function pushChanges(repoName) {
    if (!confirm('Push changes to remote repository?')) {
        return;
    }
    
    const button = event.target;
    button.disabled = true;
    button.innerText = 'Pushing...';
    
    try {
        const response = await fetch(`${API_BASE}/repositories/${repoName}/push`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ branch: 'main' })
        });
        
        if (response.ok) {
            showNotification('Changes pushed successfully', 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            const error = await response.json();
            showNotification(`Error: ${error.detail}`, 'danger');
            button.disabled = false;
            button.innerText = 'Push';
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
        button.disabled = false;
        button.innerText = 'Push';
    }
}

// Notifications
function showNotification(message, type = 'info') {
    const alertsContainer = document.querySelector('.alerts') || createAlertsContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span class="alert-message">${message}</span>
        <button class="alert-close" onclick="this.parentElement.style.display='none';">&times;</button>
    `;
    
    alertsContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.style.display = 'none';
    }, 5000);
}

function createAlertsContainer() {
    const content = document.querySelector('.content');
    const alertsContainer = document.createElement('div');
    alertsContainer.className = 'alerts';
    content.insertBefore(alertsContainer, content.firstChild);
    return alertsContainer;
}

// Modal Management
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
};

// Format time for display
function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Mini GitHub LAN loaded');
});
