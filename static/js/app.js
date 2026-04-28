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
        showModalAlert('Repository name and remote path are required', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/repositories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, remote_path: remotePath })
        });

        if (response.ok) {
            showModalAlert('Repository added successfully', 'success', () => location.reload());
        } else {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            showModalAlert(`Error: ${error.detail || 'Failed to add repository'}`, 'danger');
        }
    } catch (error) {
        showModalAlert(`Error: ${error.message}`, 'danger');
    }
}

async function deleteRepo(repoName) {
    if (!repoName) return;
    showModalConfirm(
        `Delete repository "${repoName}"? This won't delete the remote repository.`,
        async () => {
            try {
                const response = await fetch(`${API_BASE}/repositories/${encodeURIComponent(repoName)}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    showModalAlert('Repository deleted', 'success', () => location.reload());
                } else {
                    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                    showModalAlert(`Error: ${error.detail || 'Failed to delete'}`, 'danger');
                }
            } catch (error) {
                showModalAlert(`Error: ${error.message}`, 'danger');
            }
        }
    );
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
            showModalAlert('Repository synced successfully', 'success', () => location.reload());
        } else {
            const error = await response.json().catch(() => ({ detail: 'Sync failed' }));
            showModalAlert(`Error: ${error.detail || 'Sync failed'}`, 'danger');
            if (button) {
                button.disabled = false;
                button.innerHTML = originalText || '<span class="icon">↓</span> Sync';
            }
        }
    } catch (error) {
        showModalAlert(`Error: ${error.message}`, 'danger');
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
            showModalAlert('All changes staged', 'success', () => location.reload());
        } else {
            const error = await response.json().catch(() => ({ detail: 'Staging failed' }));
            showModalAlert(`Error: ${error.detail || 'Staging failed'}`, 'danger');
        }
    } catch (error) {
        showModalAlert(`Error: ${error.message}`, 'danger');
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
        showModalAlert('Commit message is required', 'warning');
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
            showModalAlert('Commit created successfully', 'success', () => location.reload());
        } else {
            const error = await response.json().catch(() => ({ detail: 'Commit failed' }));
            showModalAlert(`Error: ${error.detail || 'Commit failed'}`, 'danger');
        }
    } catch (error) {
        showModalAlert(`Error: ${error.message}`, 'danger');
    }
}

async function pushChanges(repoName) {
    if (!repoName) return;
    showModalConfirm(
        'Push changes to remote repository?',
        async () => {
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
                    showModalAlert('Changes pushed successfully', 'success', () => location.reload());
                } else {
                    const error = await response.json().catch(() => ({ detail: 'Push failed' }));
                    showModalAlert(`Error: ${error.detail || 'Push failed'}`, 'danger');
                    if (button) {
                        button.disabled = false;
                        button.innerHTML = originalText || '<span class="icon">↑</span> Push Changes';
                    }
                }
            } catch (error) {
                showModalAlert(`Error: ${error.message}`, 'danger');
                if (button) {
                    button.disabled = false;
                    button.innerHTML = originalText || '<span class="icon">↑</span> Push Changes';
                }
            }
        }
    );
}

// ─── Notifications (deprecated, use showModalAlert) ────────────────

function showNotification(message, type = 'info') {
    // Fallback: delegate to modal alert
    showModalAlert(message, type);
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

// ─── Message Box Modal ─────────────────────────────────────────────

function showModalAlert(message, type = 'info', onClose = null) {
    const modal = document.getElementById('msgboxModal');
    const titleEl = document.getElementById('msgboxTitle');
    const msgEl = document.getElementById('msgboxMessage');
    const cancelBtn = document.getElementById('msgboxCancel');
    const okBtn = document.getElementById('msgboxOk');

    if (!modal || !titleEl || !msgEl || !okBtn) return;

    const titles = {
        info: 'Information',
        success: 'Success',
        warning: 'Warning',
        danger: 'Error'
    };

    titleEl.textContent = titles[type] || titles.info;
    msgEl.textContent = message;

    if (cancelBtn) cancelBtn.style.display = 'none';
    okBtn.textContent = 'OK';
    okBtn.className = 'btn btn-primary';

    const cleanup = () => {
        modal.classList.remove('active');
        okBtn.removeEventListener('click', onOk);
        document.removeEventListener('keydown', onKey);
    };

    const onOk = () => {
        cleanup();
        if (typeof onClose === 'function') onClose();
    };
    const onKey = (e) => {
        if (e.key === 'Escape' || e.key === 'Enter') {
            e.preventDefault();
            onOk();
        }
    };

    okBtn.addEventListener('click', onOk);
    document.addEventListener('keydown', onKey);

    modal.classList.add('active');
    okBtn.focus();
}

function showModalConfirm(message, onConfirm, onCancel = null) {
    const modal = document.getElementById('msgboxModal');
    const titleEl = document.getElementById('msgboxTitle');
    const msgEl = document.getElementById('msgboxMessage');
    const cancelBtn = document.getElementById('msgboxCancel');
    const okBtn = document.getElementById('msgboxOk');

    if (!modal || !titleEl || !msgEl || !okBtn || !cancelBtn) return;

    titleEl.textContent = 'Confirm';
    msgEl.textContent = message;

    cancelBtn.style.display = '';
    cancelBtn.textContent = 'Cancel';
    okBtn.textContent = 'OK';
    okBtn.className = 'btn btn-primary';

    const cleanup = () => {
        modal.classList.remove('active');
        okBtn.removeEventListener('click', onOk);
        cancelBtn.removeEventListener('click', onCancelClick);
        document.removeEventListener('keydown', onKey);
    };

    const onOk = () => {
        cleanup();
        if (typeof onConfirm === 'function') onConfirm();
    };

    const onCancelClick = () => {
        cleanup();
        if (typeof onCancel === 'function') onCancel();
    };

    const onKey = (e) => {
        if (e.key === 'Escape') {
            e.preventDefault();
            onCancelClick();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            onOk();
        }
    };

    okBtn.addEventListener('click', onOk);
    cancelBtn.addEventListener('click', onCancelClick);
    document.addEventListener('keydown', onKey);

    modal.classList.add('active');
    okBtn.focus();
}

// ─── Toast Notifications ─────────────────────────────────────────

const activeToasts = new Map();

function showToast(message, type = 'success', duration = 2500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    // Deduplication: if same message is already showing, don't stack
    const key = `${type}:${message}`;
    if (activeToasts.has(key)) {
        // Reset timer on existing toast
        const existing = activeToasts.get(key);
        clearTimeout(existing.timer);
        existing.timer = setTimeout(() => hideToast(existing.element, key), duration);
        return;
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? '✓' : '✕';
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span>${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);

    const timer = setTimeout(() => hideToast(toast, key), duration);
    activeToasts.set(key, { element: toast, timer });
}

function hideToast(toast, key) {
    if (!toast || !toast.parentElement) {
        activeToasts.delete(key);
        return;
    }
    toast.classList.add('hiding');
    setTimeout(() => {
        if (toast.parentElement) toast.remove();
        activeToasts.delete(key);
    }, 300);
}

function showSuccessToast(message) {
    showToast(message, 'success', 2500);
}

function showErrorToast(message) {
    showToast(message, 'error', 4000);
}

// ─── File Type Helpers ───────────────────────────────────────────

const PREVIEWABLE_EXTS = new Set([
    'md', 'txt', 'py', 'js', 'ts', 'json', 'html', 'css',
    'yml', 'yaml', 'xml', 'sh', 'env', 'bash', 'zsh',
    'jsx', 'tsx', 'scss', 'sass', 'java', 'kt', 'c', 'cpp',
    'h', 'hpp', 'cs', 'go', 'rs', 'rb', 'php', 'swift',
    'r', 'dart', 'lua', 'sql', 'dockerfile', 'tf', 'ini',
    'cfg', 'toml', 'vue', 'svelte', 'ps1'
]);

const BINARY_EXTS = new Set([
    'pdf', 'docx', 'xlsx', 'zip', 'exe', 'png', 'jpg',
    'jpeg', 'gif', 'mp4', 'bin', 'dll', 'so', 'dylib',
    'wav', 'mp3', 'avi', 'mov', 'wmv', 'flv', 'webm',
    'ico', 'svg', 'woff', 'woff2', 'ttf', 'eot', 'otf'
]);

const FILE_TYPE_LABELS = {
    'md': 'Markdown', 'txt': 'Text', 'py': 'Python', 'js': 'JavaScript',
    'ts': 'TypeScript', 'json': 'JSON', 'html': 'HTML', 'css': 'CSS',
    'yml': 'YAML', 'yaml': 'YAML', 'xml': 'XML', 'sh': 'Shell',
    'env': 'Env', 'bash': 'Bash', 'zsh': 'Zsh', 'jsx': 'JSX',
    'tsx': 'TSX', 'scss': 'SCSS', 'sass': 'Sass', 'java': 'Java',
    'kt': 'Kotlin', 'c': 'C', 'cpp': 'C++', 'h': 'C Header',
    'hpp': 'C++ Header', 'cs': 'C#', 'go': 'Go', 'rs': 'Rust',
    'rb': 'Ruby', 'php': 'PHP', 'swift': 'Swift', 'r': 'R',
    'dart': 'Dart', 'lua': 'Lua', 'sql': 'SQL', 'dockerfile': 'Docker',
    'tf': 'Terraform', 'ini': 'INI', 'cfg': 'Config', 'toml': 'TOML',
    'vue': 'Vue', 'svelte': 'Svelte', 'ps1': 'PowerShell'
};

function isPreviewableFile(filename) {
    if (!filename) return false;
    const base = filename.toLowerCase();
    if (base.startsWith('readme')) return true;
    const ext = base.split('.').pop();
    return PREVIEWABLE_EXTS.has(ext);
}

function isBinaryFile(filename) {
    if (!filename) return false;
    const ext = filename.toLowerCase().split('.').pop();
    return BINARY_EXTS.has(ext);
}

function getFileTypeLabel(filename) {
    if (!filename) return 'File';
    const base = filename.toLowerCase();
    if (base.startsWith('readme')) return 'Markdown';
    const ext = base.split('.').pop();
    return FILE_TYPE_LABELS[ext] || ext.toUpperCase();
}

// ─── Kebab Menu ──────────────────────────────────────────────────

function toggleKebabMenu(menuId) {
    const menu = document.getElementById(menuId);
    if (!menu) return;

    // Close all other kebab menus
    document.querySelectorAll('.kebab-dropdown').forEach(m => {
        if (m.id !== menuId) m.classList.remove('active');
    });

    menu.classList.toggle('active');
}

// Close kebab menus when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.kebab-menu-wrapper')) {
        document.querySelectorAll('.kebab-dropdown').forEach(menu => {
            menu.classList.remove('active');
        });
    }
});

// ─── Copy to Clipboard ─────────────────────────────────────────────

async function copyTextToClipboard(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            throw new Error('Clipboard API unavailable');
        }
    } catch (err) {
        // Fallback for older browsers or non-secure contexts
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        textarea.style.top = '0';
        textarea.setAttribute('readonly', '');
        document.body.appendChild(textarea);
        textarea.select();
        textarea.setSelectionRange(0, textarea.value.length);
        const success = document.execCommand('copy');
        document.body.removeChild(textarea);
        if (!success) throw new Error('execCommand copy failed');
    }
}

// ─── Clone Helpers ─────────────────────────────────────────────────

function getCloneCommand(remotePath) {
    return `git clone "${remotePath}"`;
}

function copyCloneCommand(remotePath) {
    const command = getCloneCommand(remotePath);
    copyTextToClipboard(command).then(() => {
        showToast('Copied!', 'success', 2000);
    }).catch(() => {
        showToast('Failed to copy', 'error', 3000);
    });
}

function showCloneModal(repoName, remotePath) {
    const command = getCloneCommand(remotePath);
    showModalConfirm(
        `Clone this repository with:\n\n${command}\n\nClick OK to copy to clipboard.`,
        () => {
            copyCloneCommand(remotePath);
        }
    );
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

// Msgbox modal backdrop click: close only non-destructive (alert) dialogs
(function setupMsgboxBackdrop() {
    const modal = document.getElementById('msgboxModal');
    if (!modal) return;

    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            const cancelBtn = document.getElementById('msgboxCancel');
            // If cancel button is hidden, this is an alert (non-destructive)
            if (cancelBtn && cancelBtn.style.display === 'none') {
                modal.classList.remove('active');
            }
        }
    });
})();

// ─── Create Bare Repository ──────────────────────────────────────

function openCreateRepoDialog() {
    const dialog = document.getElementById('createRepoDialog');
    if (dialog) dialog.style.display = 'block';
}

function closeCreateRepoDialog() {
    const dialog = document.getElementById('createRepoDialog');
    if (dialog) dialog.style.display = 'none';
    const nameInput = document.getElementById('createRepoName');
    const readmeCheckbox = document.getElementById('initWithReadme');
    if (nameInput) nameInput.value = '';
    if (readmeCheckbox) readmeCheckbox.checked = true;
}

async function createBareRepo(event) {
    event.preventDefault();
    const name = document.getElementById('createRepoName')?.value?.trim();
    const initWithReadme = document.getElementById('initWithReadme')?.checked ?? true;

    if (!name) {
        showModalAlert('Repository name is required', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/repositories/create-bare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, initialize_with_readme: initWithReadme })
        });

        if (response.ok) {
            showModalAlert('Repository created successfully', 'success', () => location.reload());
        } else {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            showModalAlert(`Error: ${error.detail || 'Failed to create repository'}`, 'danger');
        }
    } catch (error) {
        showModalAlert(`Error: ${error.message}`, 'danger');
    }
}

// ─── Link Local Repository ───────────────────────────────────────

function openLinkLocalDialog() {
    const dialog = document.getElementById('linkLocalDialog');
    if (dialog) dialog.style.display = 'block';
}

function closeLinkLocalDialog() {
    const dialog = document.getElementById('linkLocalDialog');
    if (dialog) dialog.style.display = 'none';
    const nameInput = document.getElementById('linkRepoName');
    const pathInput = document.getElementById('localPath');
    if (nameInput) nameInput.value = '';
    if (pathInput) pathInput.value = '';
}

async function linkLocalRepository(event) {
    event.preventDefault();
    const repoName = document.getElementById('linkRepoName')?.value?.trim();
    const localPath = document.getElementById('localPath')?.value?.trim();

    if (!repoName || !localPath) {
        showModalAlert('Repository name and local path are required', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/repositories/link-local`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repo_name: repoName, local_path: localPath })
        });

        if (response.ok) {
            showModalAlert('Local repository linked and pushed successfully', 'success', () => location.reload());
        } else {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            showModalAlert(`Error: ${error.detail || 'Failed to link repository'}`, 'danger');
        }
    } catch (error) {
        showModalAlert(`Error: ${error.message}`, 'danger');
    }
}

// ─── Push Repo (wrapper for index cards) ───────────────────────────

async function pushRepo(repoName) {
    return pushChanges(repoName);
}

// ─── Copy to Clipboard ─────────────────────────────────────────────

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const text = element.innerText;
    copyTextToClipboard(text).then(() => {
        showToast('Copied!', 'success', 2000);
    }).catch(() => {
        showToast('Failed to copy', 'error', 3000);
    });
}

// ─── Utilities ─────────────────────────────────────────────────────

function formatBytes(bytes, decimals = 2) {
    if (bytes === null || bytes === undefined || bytes === '') return '—';
    if (bytes === 0) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDate(isoString) {
    if (!isoString) return '';
    try {
        const date = new Date(isoString);
        return date.toLocaleString();
    } catch {
        return isoString;
    }
}

// ─── File Browser Enhancements ─────────────────────────────────────

function enhanceFileBrowser() {
    // Format file sizes
    document.querySelectorAll('.file-table .col-size').forEach(cell => {
        const raw = cell.textContent.trim();
        if (raw && raw !== '—' && !isNaN(parseInt(raw))) {
            cell.textContent = formatBytes(parseInt(raw));
        }
    });

    // Format dates
    document.querySelectorAll('.file-table .col-modified time').forEach(time => {
        const raw = time.getAttribute('datetime');
        if (raw) {
            time.textContent = formatDate(raw);
        }
    });
}

// ─── Initialize ────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function() {
    console.log('Mini GitHub LAN loaded');
    enhanceFileBrowser();
});

