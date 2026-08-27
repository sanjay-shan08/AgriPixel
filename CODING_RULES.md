# Coding Rules & Guidelines

## 1. Python (Backend & ML)
*   **Formatting:** Use standard PEP8 formatting. Tools like `ruff` or `black` are recommended.
*   **Typing:** Use Python type hints (`def process_data(data: list) -> dict:`) extensively for all function definitions.
*   **Naming:** 
    *   Variables and functions: `snake_case`
    *   Classes: `PascalCase`
    *   Constants: `UPPER_SNAKE_CASE`
*   **Documentation:** Use Google-style docstrings for all complex ML modules and API endpoints.

## 2. React (Frontend)
*   **Framework:** Functional components with React Hooks only. No class components.
*   **Styling:** Use Vanilla CSS (modules or global `index.css`). **Do not use TailwindCSS**. Prioritize premium, modern design aesthetics (glassmorphism, clean typography, smooth transitions).
*   **Naming:**
    *   Components: `PascalCase.jsx` (e.g., `WeatherMap.jsx`)
    *   Functions/Hooks: `camelCase` (e.g., `useWeatherData`)
    *   CSS Files: `ComponentName.css` or `ComponentName.module.css`
*   **Structure:** Keep components small, focused, and reusable.

## 3. General Practices
*   **API Responses:** Standardize JSON responses from FastAPI (e.g., always include `status`, `data`, and `message` fields).
*   **Error Handling:** Use `try/except` blocks gracefully. FastAPI should return appropriate HTTP status codes (400, 404, 500) rather than crashing.
*   **Hardcoding:** Avoid hardcoding API keys, DB credentials, or URLs. Always use `.env` files.

## 4. Git & Commit Conventions
*   Write clear, descriptive commit messages.
*   Track all major feature additions in `FEATURE_LOG.md`.
