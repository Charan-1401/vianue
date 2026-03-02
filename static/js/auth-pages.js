function setStatus(element, message, tone) {
    element.textContent = message;
    element.classList.remove("is-success", "is-error");
    if (tone) {
        element.classList.add(tone === "success" ? "is-success" : "is-error");
    }
}

function redirectAfterLogin(user) {
    const nextParam = new URLSearchParams(window.location.search).get("next");
    const fallback = VianueSession.resolveDashboardPath(user);

    if (nextParam && nextParam.startsWith("/")) {
        window.location.href = nextParam;
        return;
    }
    window.location.href = fallback;
}

async function handleLogin(form, statusNode) {
    const payload = {
        username: form.username.value.trim(),
        password: form.password.value,
    };

    const data = await VianueSession.fetchJson("/api/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    VianueSession.saveTokens(data);
    const user = await VianueSession.fetchMe();
    setStatus(statusNode, "Session created. Redirecting to your dashboard.", "success");
    window.setTimeout(() => {
        redirectAfterLogin(user);
    }, 400);
}

async function handleRegister(form, statusNode) {
    const payload = {
        username: form.username.value.trim(),
        email: form.email.value.trim(),
        phone: form.phone.value.trim(),
        role: form.role.value,
        password: form.password.value,
    };

    await VianueSession.fetchJson("/api/auth/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    form.reset();
    setStatus(statusNode, "Account created. Continue to login.", "success");
    window.setTimeout(() => {
        window.location.href = "/login/?registered=1";
    }, 700);
}

function hydrateQueryStatus(statusNode) {
    const params = new URLSearchParams(window.location.search);
    if (params.get("registered") === "1") {
        setStatus(statusNode, "Registration complete. Sign in with the new account.", "success");
    }
}

const form = document.querySelector("[data-auth-form]");

if (form) {
    const statusNode = form.querySelector("[data-form-status]");
    hydrateQueryStatus(statusNode);

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const submitButton = form.querySelector("button[type='submit']");
        submitButton.disabled = true;
        setStatus(statusNode, "Submitting request.", null);

        try {
            if (form.dataset.mode === "login") {
                await handleLogin(form, statusNode);
            } else {
                await handleRegister(form, statusNode);
            }
        } catch (error) {
            const payload = error.payload || {};
            const firstError = Object.values(payload)[0];
            const detail = Array.isArray(firstError) ? firstError[0] : error.message;
            setStatus(statusNode, detail || "Request failed.", "error");
        } finally {
            submitButton.disabled = false;
        }
    });
}
