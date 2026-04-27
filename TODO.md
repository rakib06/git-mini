# TODO: GitHub-style Usability Upgrade

## Feature 1: Add Existing Local Repository
- [x] GitService: `link_local_repo(repo_name, local_path)` method
- [x] API: `POST /api/repositories/{repo_name}/link-local` endpoint
- [x] UI: Dialog to input local path (index.html already has dialog)
- [x] UI: JS functions for Link Local dialog (`openLinkLocalDialog`, `closeLinkLocalDialog`, `linkLocalRepository`)

## Feature 2: Clone Button
- [x] Ensure clone button works on repo cards (API + JS `cloneRepo` exist)
- [x] Fix `is_cloned` badge on repo cards (web.py index uses raw storage without `is_cloned`)

## Feature 3: Push Button
- [x] Add Push button to repo page (repo.html has it)
- [x] JS `pushRepo()` function missing for index cards (calls non-existent function)

## Feature 4: Empty Repo Detection
- [x] GitService: `is_empty_repo(remote_path)` method
- [x] Web: Pass `is_empty` flag to repo template
- [x] Template: Show "Empty Repository" badge

## Feature 5: GitHub-style Command Boxes
- [x] Template: Command boxes for empty repos with LAN_PATH
- [x] CSS: Style command boxes like GitHub (`.command-box`, `.command-header`, `.btn-copy`, etc.)
- [x] JS: Copy-to-clipboard functionality (`copyToClipboard` function)
