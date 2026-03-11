const VianueSession = (() => {
    const ACCESS_TOKEN_KEY = "vianue.access_token";
    const REFRESH_TOKEN_KEY = "vianue.refresh_token";
    const ACCESS_COOKIE = "vianue_access_token";
    const REFRESH_COOKIE = "vianue_refresh_token";

    function setCookie(name, value, maxAgeSeconds) {
        document.cookie = `${name}=${encodeURIComponent(value)}; Max-Age=${maxAgeSeconds}; Path=/; SameSite=Lax`;
    }

    function clearCookie(name) {
        document.cookie = `${name}=; Max-Age=0; Path=/; SameSite=Lax`;
    }

    function saveTokens(payload) {
        localStorage.setItem(ACCESS_TOKEN_KEY, payload.access);
        localStorage.setItem(REFRESH_TOKEN_KEY, payload.refresh);
        setCookie(ACCESS_COOKIE, payload.access, 60 * 60);
        setCookie(REFRESH_COOKIE, payload.refresh, 24 * 60 * 60);
    }

    function clearTokens() {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        clearCookie(ACCESS_COOKIE);
        clearCookie(REFRESH_COOKIE);
    }

    function getAccessToken() {
        return localStorage.getItem(ACCESS_TOKEN_KEY);
    }

    function authHeaders(options = {}) {
        const { json = true } = options;
        const headers = {
            Authorization: `Bearer ${getAccessToken()}`,
        };
        if (json) {
            headers["Content-Type"] = "application/json";
        }
        return headers;
    }

    async function fetchJson(url, options = {}) {
        const response = await fetch(url, options);
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            const detail = data.detail || "Request failed.";
            const error = new Error(detail);
            error.status = response.status;
            error.payload = data;
            throw error;
        }
        return data;
    }

    async function fetchMe() {
        return fetchJson("/api/auth/me", {
            headers: authHeaders(),
        });
    }

    function resolveDashboardPath(user) {
        if (user.is_staff) {
            return "/dashboard/admin/";
        }
        if (user.role === "OWNER") {
            return "/dashboard/owner/";
        }
        if (user.role === "VENDOR") {
            return "/dashboard/vendor/";
        }
        return "/";
    }

    return {
        saveTokens,
        clearTokens,
        getAccessToken,
        authHeaders,
        fetchJson,
        fetchMe,
        resolveDashboardPath,
    };
})();
