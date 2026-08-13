console.log("LOGIN JS LOADED");
document.querySelector('#login-form').addEventListener('submit', async(event) => {
    event.preventDefault();
    const tokenResponse = await fetch('/api/csrf-token', { credentials: 'same-origin' });
    const { csrf_token: csrfToken } = await tokenResponse.json();
    const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        credentials: 'same-origin',
        body: JSON.stringify({
            email: document.querySelector('#email').value,
            password: document.querySelector('#password').value
        })
    });
    if (response.ok) {
        window.location.assign('/dashboard');
        return;
    }
    document.querySelector('#login-error').textContent =
        (await response.json()).error || 'Unable to sign in.';
});