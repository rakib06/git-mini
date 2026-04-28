# Implementation Plan

## Task 1a — Hide `.git` from File Browser
- [x] Update `app/services/git_service.py` — skip `.git` in `list_directory()`

## Task 1b — Colorful File Display & Syntax Highlighting
- [x] Update `app/services/git_service.py` — add `ext` and `lang_class` to entries
- [x] Update `templates/files.html` — add language badge & color classes
- [x] Update `templates/view.html` — add Prism.js syntax highlighting
- [x] Update `static/css/style.css` — add `.ext-xxx` colors & `.language-badge` styles
- [x] Update `app/routers/web.py` — pass `language_class` to view template

## Task 2 — `temp_local` as Always-Synced Mirror
- [x] Update `app/services/git_service.py` — true mirror sync (`reset --hard`, `clean -fd`)
- [x] Update `templates/repo.html` — remove push/fetch buttons, add mirror info
- [x] Update `templates/status.html` — remove stage/commit/push buttons, add mirror banner
- [x] Update `static/css/style.css` — add `.mirror-banner` / `.info-panel` styles

## Task 3 — Centered Modal Message Box for Alerts & Confirmations
- [x] Update `templates/base.html` — add generic message-box modal markup
- [x] Update `static/css/style.css` — add centered modal overlay & button styles
- [x] Update `static/js/app.js` — add `showModalAlert()` and `showModalConfirm()`
- [x] Replace native `confirm()` in `deleteRepo()` and `pushChanges()`

## Task 4 — Full UI/UX Overhaul (User Feedback)

### 4.1 Replace all toasts with centered modals
- [x] Update `showModalAlert()` to accept optional `onClose` callback
- [x] Replace ALL `showNotification()` calls in `app.js` with `showModalAlert()`
- [x] Update `copyToClipboard()` to show "Copied" modal with OK

### 4.2 Repo Details page layout improvements
- [x] Update `app/routers/web.py` — pass `has_files`, `root_entries` to repo template
- [x] Update `templates/repo.html`:
  - [x] Show Files section first (if has_files), then Overview below
  - [x] Add Git Clone button that shows clone command in modal
  - [x] Add Delete button to repo header
  - [x] Update Copy buttons to use modal

### 4.3 Empty repo logic fix
- [x] Update `app/routers/web.py` — `is_empty` = false if local clone has files
- [x] Update `templates/repo.html` — show "&#10003; Repository synced" instead of "Empty Repository"

### 4.4 Landing page repo card cleanup
- [x] Update `templates/index.html`:
  - [x] Remove Delete button from cards
  - [x] Rename "Clone" &#8594; "Sync"
  - [x] Add "Clone / Copy" button (shows git clone command modal)
  - [x] Keep "Open" button

### 4.5 Add `showCloneModal()` helper
- [x] Update `static/js/app.js` — add `showCloneModal(repoName, remotePath)`

### 4.6 UX polish
- [x] Update `static/css/style.css` — responsive buttons, smooth transitions, consistent spacing

## Task 5 — Clone Button Redesign (User Feedback)

### 5.1 Inline clone command on repo cards
- [x] Update `templates/index.html` — show `git clone "LAN_PATH"` text + Clone button in bottom row
- [x] Update `static/css/style.css` — add `.card-clone-row` and `.clone-command` styles
- [x] Move Clone button from `card-actions` to new `.card-clone-row`
- [x] Keep "Open" and "Sync" as top action buttons

### 5.2 Reusable helpers
- [x] Update `static/js/app.js` — add `getCloneCommand(remotePath)` helper
- [x] Update `static/js/app.js` — add `copyCloneCommand(remotePath)` helper
- [x] Refactor `showCloneModal()` to use reusable helpers

### 5.3 Functional behavior
- [x] Clicking "Clone" button copies full `git clone "LAN_PATH"` command to clipboard
- [x] Shows centered modal: "Clone command copied" with OK button
- [x] Graceful truncation for long paths on small screens

## Followup
- [ ] Test app to verify all changes
- [ ] Verify modal alerts/confirmations appear centered with OK/Cancel
- [ ] Verify repo cards show only Open/Sync/Clone
- [ ] Verify Delete moved to repo details
- [ ] Verify Files section shows first on Overview when repo has files
- [ ] Verify empty repo logic fixed

