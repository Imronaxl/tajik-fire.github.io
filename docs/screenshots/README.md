# Screenshots

This directory holds UI screenshots referenced from the project README.
Each file below corresponds to a screen in DevStudio Pro. Replace the
placeholder with a real `.png` once you've captured the screen.

## How to capture

```bash
cd fastapi_app
uvicorn main:app --reload
```

Open <http://localhost:8000>, log in as `demo / Demo1234`, then capture
each screen at **1440×900** (or wider) in the browser's dark mode.

## Naming convention

Files use `kebab-case.png`. Save them next to this `README.md` so the
relative paths in the project README (`docs/screenshots/01-home.png`)
resolve correctly on GitHub.

## Required screenshots

| #   | Filename                       | URL                                  | What it shows                                                                 |
|-----|--------------------------------|--------------------------------------|-------------------------------------------------------------------------------|
| 01  | `01-home.png`                  | `/`                                  | Landing hero with live platform stats and animated code preview                |
| 02  | `02-auth.png`                  | `/login`                             | Sign-in / register / reset tabs with the demo account hint                    |
| 03  | `03-problems.png`              | `/problems`                          | Problem archive with difficulty pills, category filters and search            |
| 04  | `04-problem-modal.png`         | `/problems` → click any problem       | Problem detail modal with statement and sample tests                          |
| 05  | `05-editor.png`                | `/problems/1/solve`                   | Split-view code editor with statement on the left, code on the right          |
| 06  | `06-verdict-accepted.png`      | `/problems/1/solve` after submit      | "Accepted · 4/4 tests" verdict card with timing and memory stats            |
| 07  | `07-verdict-wrong-answer.png`  | submit a wrong solution               | "Wrong answer on test 1" verdict card with the diff hint                     |
| 08  | `08-leaderboard.png`           | `/leaderboard`                       | Top-3 podium + ranked list with rating, solved count and attempts            |
| 09  | `09-submissions.png`           | `/submissions`                       | Global submission feed with verdict filters                                  |
| 10  | `10-learning.png`              | `/learning`                          | Learning track cards with module numbers and progress bars                   |
| 11  | `11-learning-detail.png`       | `/learning/intro-to-algorithms`      | Module detail: theory on the left, linked problems on the right              |
| 12  | `12-tasks.png`                 | `/tasks`                             | Kanban board with to-do / in-progress / done columns                          |
| 13  | `13-messenger.png`             | `/messenger`                         | Chat list on the left, conversation on the right with bubble layout          |
| 14  | `14-profile.png`               | `/profile`                           | Profile header, stats cards, recent submissions feed and password change     |
| 15  | `15-news.png`                  | `/news`                              | News feed with author avatars and publication dates                           |
| 16  | `16-contests.png`              | `/olympiads`                         | Contest grid with live / upcoming badges and date ranges                      |
| 17  | `17-swagger-docs.png`          | `/docs`                              | FastAPI Swagger UI showing all 49 endpoints                                  |
| 18  | `18-mobile-home.png`           | `/` at 375×812 (iPhone 13 viewport)   | Mobile-responsive landing and navbar drawer                                   |

## Tips for clean captures

- Use a clean browser profile — no extension icons, no bookmark bar.
- Hide the cursor where possible.
- Keep the dark theme. Light theme support is on the roadmap but not yet shipped.
- For wide pages (submissions feed, leaderboard), capture the full viewport;
  don't trim.
- For modals (problem detail, edit profile), make sure the overlay is visible.

## Replacing the placeholders

After capturing, replace this `README.md` is not needed — keep the PNG files
next to it. The project root README references them via
`docs/screenshots/01-home.png` etc., which resolves on GitHub.

If you remove a screenshot, also remove its reference in
`README.md` to avoid broken images in the rendered README.
