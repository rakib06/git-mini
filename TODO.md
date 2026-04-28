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

## Followup
- [ ] Test app to verify `.git` hidden
- [ ] Verify file browser colors & syntax highlighting
- [ ] Verify UI no longer shows stage/commit/push buttons
- [ ] Verify auto-sync behavior
