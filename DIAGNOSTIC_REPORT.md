# Diagnostic Report: CineScore Movie Search & Loading Failure

This report outlines the diagnostics, root cause analysis, and fixes applied to resolve the movie search and dynamic loading issues in the production deployment of CineScore.

---

## 1. Diagnostics Summary

### Exact Failing Endpoint
* **Client-side Request URL**: `https://cine-score-three.vercel.app/movies?query=...` (falling back to relative routing due to missing env variable configuration) or `https://cinescore-production-0e22.up.railway.app//movies?query=...` (trailing slash double-slash conflict).
* **Target Backend Endpoint**: `GET /movies?query=...` (defined in `rest.py`).

### Exact Frontend Exception
1. **JSON Parsing Exception**:
   ```javascript
   SyntaxError: Unexpected token '<', "<!doctype html>..." is not valid JSON
   ```
   * *Occurs when*: `BACKEND_URL` is blank on Vercel. Fetching `/movies?query=...` targets the frontend Vercel server, which intercepts the route and serves the static HTML SPA wrapper (`index.html`) with a `200 OK` status. The frontend `res.json()` parser fails to parse HTML text as JSON, throwing a syntax exception.
2. **TypeError on Ratings formatting**:
   ```javascript
   TypeError: Cannot read properties of null (reading 'toFixed')
   ```
   * *Occurs when*: Rendering movie comparisons or chart datasets for dynamic search results that are missing IMDb, Metacritic, or YouTube rating scores.

### Exact Backend Response
* **Status**: `200 OK`
* **Response Body**:
  * For correct calls: A valid JSON matching the `MovieListResponse` schema.
  * For relative routing on Vercel: The contents of the frontend `index.html` file (HTML document).

---

## 2. Root Cause Analysis

We identified three primary factors that caused search and dynamic movie loading to fail in production:

1. **Missing or Untrimmed Environment Variable**:
   The Vercel deployment lacked the `VITE_API_URL` environment variable, or it was configured with a trailing slash (`https://cinescore-production-0e22.up.railway.app/`). This caused:
   - Relative request routing that fetched HTML from Vercel instead of JSON from Railway.
   - Dual slash URL structures (`//movies`) which can result in redirection or route mismatches.
2. **Missing Local Fallback Archive Cache**:
   When the client failed to retrieve results, the app fell back to the `FALLBACK_MOVIES` mock dataset. This made preloaded movies (Inception, Interstellar, Dark Knight) visible and clickable (via local detail mock caching), but searching for any new title (which does not exist in the mock dataset) resulted in search failure messages.
3. **Rating Type Vulnerability**:
   Dynamic search results returned from TMDb often miss IMDb or Metacritic scores. In such cases, these attributes are returned as `null` or empty values. Attempting to call `.toFixed(1)` or similar methods directly on these fields caused silent JavaScript rendering crashes in component mapping loops.

---

## 3. Code Fixes Applied

To fix the search pipeline and make the application robust, we implemented the following changes:

### A. Trailing Slash Sanitization & Global Backend URL
In [App.jsx](file:///c:/Users/ACER/Downloads/movie-ai-rating%20%282%29%20%281%29/movie-ai-rating/movie-ai-rating/frontend/src/App.jsx), we sanitized the backend URL to remove any trailing slashes, avoiding path rewriting issues:
```javascript
const sanitizeUrl = (url) => {
  if (!url) return '';
  const trimmed = url.trim();
  return trimmed.endsWith('/') ? trimmed.slice(0, -1) : trimmed;
};
const BACKEND_URL = sanitizeUrl(import.meta.env.VITE_API_URL || '');
```

### B. Verbose Console Logging
We updated the `fetchWithTimeout` wrapper to log request metrics, response status codes, and cloned response bodies to the console. This allows you to inspect the exact endpoint payloads in the browser's developer console:
```javascript
console.log(`[API Request] URL: ${resource} | Method: ${options.method || 'GET'}`);
// ...
const responseClone = response.clone();
console.log(`[API Response] URL: ${resource} | Status: ${response.status} ${response.statusText}`);
// ... logs JSON or text body safely
```

### C. Safe Score Parsing Utility
We implemented a `parseRating` utility to safely cast scores to floats. All gauges, compare bars, and charts now use this utility to prevent runtime `.toFixed()` TypeErrors:
```javascript
const parseRating = (val, fallback = 0) => {
  if (val === null || val === undefined) return fallback;
  const num = parseFloat(val);
  return isNaN(num) ? fallback : num;
};
```

### D. Graceful UI Fallbacks
We added fallback values for missing metadata to prevent layouts from breaking:
- **Overview fallback**: `{featured.overview || 'No synopsis available.'}`
- **Empty results / poster paths / null ratings**: Fully resolved by mapping through safe defaults.

### E. Explicit Catch-Block Error Toast Notifications
We replaced generic catch statements with detailed error handlers. The user-facing toast alerts will now show the exact exception message (`err.message`), highlighting whether a request failed due to connection timeouts, CORS, or JSON syntax parsing errors:
```javascript
.catch(err => {
  console.error("[Search Pipeline] Search failed explicitly:", err);
  addToast(`Search failed: ${err.message || 'Server connection issue.'}`, "SEARCH ERROR", "rose");
  setIsLoading(false);
});
```
