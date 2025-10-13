# Auth storage modes

This app supports two frontend auth storage modes:

- LocalStorage mode (default): tokens are returned from the social callback in the URL fragment and saved in localStorage.
- HttpOnly Cookie mode (optional): tokens are set as HttpOnly cookies by the backend callback, and the frontend relies on cookies for authenticated API calls.

How to enable Cookie mode:

- Set environment variables on the server:
  - AUTH_COOKIE_MODE=true
  - AUTH_COOKIE_SECURE=true (recommended in production)
  - AUTH_COOKIE_SAMESITE=Lax (or Strict)
  - AUTH_COOKIE_DOMAIN=stock-chart-web-app.onrender.com (optional if needed)

Logout behavior:

- The frontend logout clears localStorage and calls /api/auth/social/logout/ to delete auth cookies when cookie mode is enabled.

Frontend header user display:

- The script frontend/js/auth-ui.js reads user from localStorage and updates header areas on common pages, also providing a visible Logout button.
