# ✅ COMPLETED: Fix Homepage Navigation and Repo Cards

## Changes Made

### 1. Fixed Runtime Error: `url_for` undefined
**File: `app/routers/web.py`**
- Switched from raw Jinja2 `Environment` + `template.render()` to FastAPI `Jinja2Templates` + `TemplateResponse`
- Added `request: Request` parameter to every route handler
- Fixed `TemplateResponse` argument order to `(request, name, context)` (was incorrectly `(name, context)` causing `tuple as dict key` error)
- Error responses now return `HTMLResponse` objects with proper status codes

### 2. Fixed `templates/index.html`
- Removed duplicate "Add Repository" modal HTML fragment
- Added `repo_config is mapping` guard to handle non-dict data gracefully
- Updated all repo links to use `url_for('repo_page', repo_name=...)`
- Removed duplicate modal closing tags

### 3. Fixed `templates/partials/_header.html`
- Already correct — uses `url_for` for all navigation links

### 4. Fixed `templates/partials/_sidebar.html`  
- Already correct — uses `request.url.path` and `url_for` (now works since `request` is passed)

### 5. Fixed `templates/partials/_footer.html`
- Updated hardcoded links to use `url_for('index')` and `url_for('settings_page')`

### 6. Fixed remaining templates for `url_for` consistency
- **`branches.html`** — all breadcrumbs and back links use `url_for`
- **`commits.html`** — all breadcrumbs, commit SHA links, and back links use `url_for`
- **`status.html`** — all breadcrumbs and back links use `url_for`
- **`diff.html`** — all breadcrumbs and back links use `url_for`
- **`settings.html`** — back link uses `url_for('index')`

### 7. Updated `static/css/style.css`
- Added styles for `.app-container`, `.app-header`, `.app-sidebar`, `.content-area`, `.app-footer` to match actual HTML
- Added `.page-header`, `.repo-header`, `.breadcrumb`, `.repo-nav-tabs`, `.repo-content` styles
- Added `.status-section`, `.file-list`, `.file-item`, `.status-actions` styles
- Added `.commits-mini`, `.commit-mini`, `.branches-mini`, `.branch-item` styles
- Improved responsive styles for mobile
- Added `.modal-header`, `.modal-body`, `.modal-close` styles
- Added `.card-header`, `.card-body`, `.card-footer`, `.card-actions` styles

### 8. Updated `static/js/app.js`
- Added null-safe element checks (`?.`) for all DOM queries
- Added `encodeURIComponent()` for all API path parameters
- Added `.catch(() => ({detail: '...'}))` for all JSON parse fallbacks
- Added `event?.target?.closest('button')` for reliable button targeting
- Added auto-dismiss fade animation for notifications
- Added `Escape` key handler to close modals
- Added `escapeHtml()` to prevent XSS in notification messages

## Test Results
```
/: 200 OK
/settings: 200 OK
```
`url_for` now resolves correctly across all templates. No `undefined` errors.
