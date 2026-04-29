const TOKEN_KEY = "is601.jwt";

function getTokenPreview(token) {
    if (!token) {
        return "No token stored yet.";
    }

    if (token.length <= 32) {
        return token;
    }

    return `${token.slice(0, 18)}...${token.slice(-12)}`;
}

function setMessage(messageElement, text, state) {
    if (!messageElement) {
        return;
    }

    messageElement.textContent = text;
    messageElement.dataset.state = state;
}

function normalizeEmail(value) {
    return value.trim().toLowerCase();
}

function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function bindStoredToken() {
    const tokenElement = document.querySelector("[data-token-value]");
    if (!tokenElement) {
        return;
    }

    const token = window.localStorage.getItem(TOKEN_KEY);
    tokenElement.textContent = getTokenPreview(token);
}

async function handleSubmit(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const messageElement = document.querySelector("[data-message]");
    const pageMode = form.dataset.authMode;
    const emailField = form.elements.email;
    const passwordField = form.elements.password;
    const confirmField = form.elements.confirmPassword;

    const email = normalizeEmail(emailField.value);
    const password = passwordField.value;
    const confirmPassword = confirmField ? confirmField.value : "";

    if (!isValidEmail(email)) {
        setMessage(messageElement, "Enter a valid email address.", "error");
        return;
    }

    if (password.length < 8) {
        setMessage(messageElement, "Password must be at least 8 characters.", "error");
        return;
    }

    if (pageMode === "register" && confirmPassword && confirmPassword !== password) {
        setMessage(messageElement, "Passwords do not match.", "error");
        return;
    }

    setMessage(messageElement, "Submitting...", "loading");

    const response = await fetch(`/${pageMode}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
    });

    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
        const errorText = Array.isArray(payload.detail)
            ? payload.detail[0]?.msg || "Unable to complete request."
            : payload.detail || payload.message || "Unable to complete request.";
        setMessage(messageElement, errorText, "error");
        return;
    }

    window.localStorage.setItem(TOKEN_KEY, payload.access_token);
    bindStoredToken();
    form.reset();
    setMessage(messageElement, payload.message || "Success.", "success");
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form[data-auth-mode]").forEach((form) => {
        form.addEventListener("submit", handleSubmit);
    });

    bindStoredToken();
});