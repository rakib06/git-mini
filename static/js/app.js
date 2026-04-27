/**
 * Mini GitHub LAN - Frontend JavaScript
 */

const API_BASE = '/api';

// ─── Repository Management ─────────────────────────────────────────

function openAddRepoDialog() {
    const dialog = document.getElementById('addRepoDialog');
    if (dialog) dialog.style.display = 'block';
}

function closeAddRepoDialog() {
    const dialog = document.getElementById('addRepoDialog');
    if (dialog) dialog.style.display = 'none';
    const nameInput = document.getElementById('repoName');
    const pathInput = document.getElementById('remotePath');
    if (nameInput) nameInput.value = '';
    if (pathInput) pathInput.value = '';
}

async function addRepository(event) {
    event.preventDefault();
    const name = document.getElementById('repoName')?.value?.trim();
    const remotePath = document.getElementById('remotePath')?.value?.trim();

    if (!name || !remotePath) {
        showNotification('Repository name and remote path are required', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/repositories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, remote_path: remotePath })
        });

        if (response.ok) {
            showNotification('Repository added successfully', 'success');
            closeAddRepoDialog();
            setTimeout(() => location.reload(), 1200);
        } else {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            showNotification(`Error: ${error.detail || 'Failed to add repository'}`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

async function deleteRepo(repoName) {
    if (!repoName) return;
    if (!confirm(`Delete repository "${repoName}"? This won't delete the remote repository.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/repositories/${encodeURIComponent(repoName)}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showNotification('Repository deleted', 'success');
            setTimeout(() => location.reload(), 1200);
        } else {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            showNotification(`Error: ${error.detail || 'Failed to delete'}`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

async function cloneRepo(repoName) {
    if (!repoName) return;

    const button = event?.target?.closest('button');
    const originalText = button?.innerHTML;

    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="icon">⏳</span> Syncing...';
    }

    try {
        const response = await fetch(`${API_BASE}/repositories/${encodeURIComponent(repoName)}/clone-or-fetch`, {
            method: 'POST'
        });

        if (response.ok) {
            showNotification('Repository synced successfully', 'success');
            setTimeout(() => location.reload(), 1200);
        } else {
            const error = await response.json().catch(() => ({ detail: 'Sync failed' }));
            showNotification(`Error: ${error.detail || 'Sync failed'}`, 'danger');
            if (button) {
                button.disabled = false;
                button.innerHTML = originalText || '<span class="icon">↓</span> Sync';
            }
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
        if (button) {
            button.disabled = false;
            button.innerHTML = originalText || '<span class="icon">↓</span> Sync';
        }
    }
}

// ─── Status & Commit Management ────────────────────────────────────

async function stageAll(repoName) {
    if (!repoName) return;

    try {
        const response = await fetch(`${API_BASE}/repositories/${encodeURIComponent(repoName)}/stage-all`, {
            method: 'POST'
        });

        if (response.ok) {
            showNotification('All changes staged', 'success');
            setTimeout(() => location.reload(), 800);
        } else {
            const error = await response.json().catch(() => ({ detail: 'Staging failed' }));
            showNotification(`Error: ${error.detail || 'Staging failed'}`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

function openCommitDialog() {
    const dialog = document.getElementById('commitDialog');
    if (dialog) dialog.style.display = 'block';
}

function closeCommitDialog() {
    const dialog = document.getElementById('commitDialog');
    if (dialog) dialog.style.display = 'none';
    const msgInput = document.getElementById('commitMessage');
    if (msgInput) msgInput.value = '';
}

async function createCommit(event, repoName) {
    event.preventDefault();
    if (!repoName) return;

    const message = document.getElementById('commitMessage')?.value?.trim();
    const authorName = document.getElementById('authorName')?.value?.trim() || 'User';
    const authorEmail = document.getElementById('authorEmail')?.value?.trim() || 'user@local';

    if (!message) {
        showNotification('Commit message is required', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/repositories/${encodeURIComponent(repoName)}/commit`, {
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
            setTimeout(() => location.reload(), 1200);
        } else {
            const error = await response.json().catch(() => ({ detail: 'Commit failed' }));
            showNotification(`Error: ${error.detail || 'Commit failed'}`, 'danger');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
    }
}

async function pushChanges(repoName) {
    if (!repoName) return;
    if (!confirm('Push changes to remote repository?')) {
        return;
    }

    const button = event?.target?.closest('button');
    const originalText = button?.innerHTML;

    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="icon">⏳</span> Pushing...';
    }

    try {
        const response = await fetch(`${API_BASE}/repositories/${encodeURIComponent(repoName)}/push`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ branch: 'main' })
        });

        if (response.ok) {
            showNotification('Changes pushed successfully', 'success');
            setTimeout(() => location.reload(), 1200);
        } else {
            const error = await response.json().catch(() => ({ detail: 'Push failed' }));
            showNotification(`Error: ${error.detail || 'Push failed'}`, 'danger');
            if (button) {
                button.disabled = false;
                button.innerHTML = originalText || '<span class="icon">↑</span> Push Changes';
            }
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'danger');
        if (button) {
            button.disabled = false;
            button.innerHTML = originalText || '<span class="icon">↑</span> Push Changes';
        }
    }
}

// ─── Notifications ─────────────────────────────────────────────────

function showNotification(message, type = 'info') {
    let alertsContainer = document.querySelector('.alerts');
    if (!alertsContainer) {
        alertsContainer = createAlertsContainer();
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span class="alert-message">${escapeHtml(message)}</span>
        <button class="alert-close" onclick="this.parentElement.remove();">&times;</button>
    `;

    alertsContainer.appendChild(alert);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s';
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

function createAlertsContainer() {
    const content = document.querySelector('.content-area') || document.querySelector('.content') || document.body;
    const alertsContainer = document.createElement('div');
    alertsContainer.className = 'alerts';
    content.insertBefore(alertsContainer, content.firstChild);
    return alertsContainer;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── Modal Management ──────────────────────────────────────────────

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
};

// Close modal on Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

// ─── Utilities ─────────────────────────────────────────────────────

function formatDate(isoString) {
    if (!isoString) return '';
    try {
        const date = new Date(isoString);
        return date.toLocaleString();
    } catch {
        return isoString;
    }
}

// ─── Initialize ────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function() {
    console.log('Mini GitHub LAN loaded');
});
