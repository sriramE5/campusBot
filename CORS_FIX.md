# CORS Fix for Backend

The backend CORS configuration needs to be updated to allow all origins.

## Quick Fix:

1. Open terminal/command prompt
2. Navigate to your project folder
3. Run:

```bash
git add .
git commit -m "Fix CORS to allow all origins"
git push
```

## What this fixes:
- CORS error when testing locally
- Allows frontend to connect to backend
- Fixes "Access-Control-Allow-Origin" error

## After pushing:
- Wait 2-3 minutes for redeploy
- Test your login again
- Should work without CORS errors

## Current Status:
- Backend: LIVE but CORS blocked
- Frontend: Ready to connect
- Fix: Ready to deploy

## Test after fix:
- Username: admin
- Password: campusbot123
- Should login successfully!
