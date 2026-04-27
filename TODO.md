# File Browser Feature Implementation

## Plan
- [x] Analyze codebase and confirm plan with user
- [x] Update `app/utils/path_security.py` - add `validate_repo_file_path`
- [x] Update `app/services/git_service.py` - add `list_directory`, `is_text_file`, `get_safe_mime_type`
- [x] Update `app/routers/web.py` - add `/files`, `/download`, `/view` routes
- [x] Create `templates/files.html` - GitHub-style file explorer
- [x] Create `templates/view.html` - text/code preview
- [x] Update `templates/repo.html` - add Files tab
- [x] Update `static/css/style.css` - file browser and preview styles
- [x] Update `static/js/app.js` - format bytes and dates
- [x] Verify implementation completeness

## Summary of Changes

### Backend
- `app/utils/path_security.py`: Added `validate_repo_file_path()` for secure file path validation inside `temp_local/{repo_name}`. Blocks `..`, absolute paths, and path escapes.
- `app/services/git_service.py`: Added `list_directory()`, `is_text_file()`, `get_safe_mime_type()` helpers.
- `app/routers/web.py`: Added three new routes:
  - `GET /repo/{name}/files?path=...` — File browser with breadcrumbs, folder navigation, back button
  - `GET /repo/{name}/download?path=...` — Safe file streaming download
  - `GET /repo/{name}/view?path=...` — Text/code preview with binary rejection

### Frontend
- `templates/files.html`: GitHub-style file explorer table with folders first, file sizes, modified times, icons, and actions (Open/View/Download).
- `templates/view.html`: Clean text preview page with breadcrumbs, file metadata, and download/back actions.
- `templates/repo.html`: Added "Files" tab to the repo navigation.
- `static/css/style.css`: Added `.file-browser`, `.file-table`, `.file-view-header`, `.file-view-container` styles.
- `static/js/app.js`: Added `formatBytes()` and `enhanceFileBrowser()` for human-readable sizes and dates.

### Security
- Path traversal blocked (`../`, absolute paths)
- Only paths inside `temp_local/{repo_name}` are allowed
- Binary files rejected from text preview (415 response)
- Safe MIME type handling for downloads

