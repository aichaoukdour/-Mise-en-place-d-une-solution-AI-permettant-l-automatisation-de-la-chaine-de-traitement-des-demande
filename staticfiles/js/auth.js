// static/js/auth.js
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function refreshToken() {
    return fetch('/api/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Refresh token failed');
        }
        return response.json();
    })
    .then(data => {
        localStorage.setItem('access_token', data.access);
        return data.access;
    })
    .catch(error => {
        console.error('Error refreshing token:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
        throw error;
    });
}

async function fetchWithToken(url, options = {}) {
    options.headers = {
        ...options.headers,
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'X-CSRFToken': getCookie('csrftoken')
    };

    let response = await fetch(url, options);
    if (response.status === 401) {
        try {
            await refreshToken();
            options.headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
            response = await fetch(url, options);
        } catch (error) {
            return Promise.reject(error);
        }
    }
    return response;
}