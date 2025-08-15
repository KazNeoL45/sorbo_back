# CORS Troubleshooting Guide

This guide helps you resolve CORS (Cross-Origin Resource Sharing) issues when connecting your frontend to the SorboBackend API.

## What is CORS?

CORS is a security feature implemented by browsers that restricts web pages from making requests to a different domain than the one that served the original page. This is a browser security feature, not a server-side restriction.

## Current CORS Configuration

The Django backend is configured with the following CORS settings:

```python
# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True  # Allows all origins in development
CORS_ALLOW_CREDENTIALS = True

# Allowed origins for specific frontend frameworks
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React default port
    "http://localhost:4200",  # Angular default port
    "http://localhost:8080",  # Vue default port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4200",
    "http://127.0.0.1:8080",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
]

# Regex patterns for localhost development
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",
    r"^http://127.0.0.1:\d+$",
]
```

## Testing CORS

### 1. Test the CORS endpoint

Visit this URL in your browser to test if CORS is working:
```
http://localhost:8000/api/cors-test/
```

You should see:
```json
{
    "message": "CORS is working!",
    "status": "success",
    "origin": "No origin header",
    "method": "GET"
}
```

### 2. Test from your frontend

Add this JavaScript code to your frontend to test CORS:

```javascript
// Test GET request
fetch('http://localhost:8000/api/cors-test/', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
    },
})
.then(response => response.json())
.then(data => console.log('CORS GET test:', data))
.catch(error => console.error('CORS GET error:', error));

// Test POST request
fetch('http://localhost:8000/api/cors-test/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ test: 'data' })
})
.then(response => response.json())
.then(data => console.log('CORS POST test:', data))
.catch(error => console.error('CORS POST error:', error));
```

## Common CORS Issues and Solutions

### 1. "strict-origin-when-cross-origin" Error

**Problem**: Browser is blocking requests due to CORS policy.

**Solutions**:
- Ensure your frontend is running on one of the allowed origins
- Check that the Django server is running on `http://localhost:8000`
- Verify that `CORS_ALLOW_ALL_ORIGINS = True` is set in settings.py

### 2. Preflight Request Failing

**Problem**: OPTIONS requests are being blocked.

**Solution**: The backend is configured to handle OPTIONS requests. Make sure your frontend includes the correct headers:

```javascript
fetch('http://localhost:8000/api/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    body: JSON.stringify({
        username: 's0rb0mx24',
        password: 's0rb0s0rb1t0'
    })
})
```

### 3. Credentials Not Being Sent

**Problem**: Cookies or authorization headers not being sent.

**Solution**: Include `credentials: 'include'` in your fetch requests:

```javascript
fetch('http://localhost:8000/api/products/', {
    method: 'GET',
    credentials: 'include',
    headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    },
})
```

## Frontend Framework Specific Solutions

### React

```javascript
// Using fetch
const login = async () => {
    try {
        const response = await fetch('http://localhost:8000/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: 's0rb0mx24',
                password: 's0rb0s0rb1t0'
            })
        });
        const data = await response.json();
        console.log('Login response:', data);
    } catch (error) {
        console.error('Login error:', error);
    }
};

// Using axios
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

const login = async () => {
    try {
        const response = await api.post('/login/', {
            username: 's0rb0mx24',
            password: 's0rb0s0rb1t0'
        });
        console.log('Login response:', response.data);
    } catch (error) {
        console.error('Login error:', error);
    }
};
```

### Angular

```typescript
// In your service
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  login(username: string, password: string) {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return this.http.post(`${this.baseUrl}/login/`, {
      username,
      password
    }, { headers });
  }
}
```

### Vue.js

```javascript
// Using axios
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const login = async (username, password) => {
    try {
        const response = await api.post('/login/', {
            username,
            password
        });
        return response.data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
};
```

## Debugging Steps

1. **Check Browser Console**: Look for CORS errors in the browser's developer tools console.

2. **Check Network Tab**: In browser dev tools, check the Network tab to see if requests are being made and what responses are received.

3. **Test with curl**: Use curl to test if the API is working:
   ```bash
   curl -X GET http://localhost:8000/api/cors-test/
   ```

4. **Check Django Logs**: Look at the Django server console for any error messages.

5. **Verify URLs**: Make sure you're using the correct API URLs:
   - Base URL: `http://localhost:8000/api`
   - Login: `http://localhost:8000/api/login/`
   - Products: `http://localhost:8000/api/products/`

## Production Considerations

For production, you should:

1. **Remove `CORS_ALLOW_ALL_ORIGINS = True`**
2. **Set specific allowed origins**:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://yourdomain.com",
       "https://www.yourdomain.com",
   ]
   ```
3. **Use HTTPS** for all communications
4. **Configure proper security headers**

## Still Having Issues?

If you're still experiencing CORS issues:

1. **Restart the Django server** after making CORS configuration changes
2. **Clear browser cache** and try again
3. **Check if your frontend is running on the expected port**
4. **Verify that the Django server is running on port 8000**
5. **Test with the CORS test endpoint first**

## Quick Test Commands

```bash
# Test if Django server is running
curl http://localhost:8000/api/cors-test/

# Test login endpoint
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "s0rb0mx24", "password": "s0rb0s0rb1t0"}'

# Test products endpoint
curl http://localhost:8000/api/products/
```
