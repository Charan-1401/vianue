function setDashboardStatus(message, tone) {
    const node = document.querySelector("[data-dashboard-status]");
    if (!node) {
        return;
    }
    node.textContent = message;
    node.classList.remove("is-success", "is-error");
    if (tone) {
        node.classList.add(tone === "success" ? "is-success" : "is-error");
    }
}

function pluralize(count, label) {
    return `${count} ${label}${count === 1 ? "" : "s"} queued`;
}

function updateCounts(venues, services) {
    document.querySelector("[data-venues-count]").textContent = venues.length;
    document.querySelector("[data-services-count]").textContent = services.length;
    document.querySelector("[data-venues-count-pill]").textContent = pluralize(venues.length, "venue");
    document.querySelector("[data-services-count-pill]").textContent = pluralize(services.length, "service");
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function renderEmptyState(label) {
    return `<div class="empty-state">No pending ${label} right now.</div>`;
}

function renderVenueCard(item) {
    return `
        <article class="queue-item">
            <header>
                <div>
                    <h3>${escapeHtml(item.name)}</h3>
                    <div class="queue-meta">
                        <span>#${item.id}</span>
                        <span>Owner ${escapeHtml(item.owner)}</span>
                        <span>${escapeHtml(item.city)}</span>
                    </div>
                </div>
                <span class="pill">${escapeHtml(item.status)}</span>
            </header>
            <div class="queue-actions">
                <button class="button button-success" type="button" data-admin-action="approve" data-item-type="venue" data-item-id="${item.id}">Approve</button>
                <button class="button button-danger" type="button" data-admin-action="reject" data-item-type="venue" data-item-id="${item.id}">Reject</button>
            </div>
        </article>
    `;
}

function renderServiceCard(item) {
    return `
        <article class="queue-item">
            <header>
                <div>
                    <h3>${escapeHtml(item.title)}</h3>
                    <div class="queue-meta">
                        <span>#${item.id}</span>
                        <span>Vendor ${escapeHtml(item.vendor)}</span>
                    </div>
                </div>
                <span class="pill">${escapeHtml(item.status)}</span>
            </header>
            <div class="queue-actions">
                <button class="button button-success" type="button" data-admin-action="approve" data-item-type="service" data-item-id="${item.id}">Approve</button>
                <button class="button button-danger" type="button" data-admin-action="reject" data-item-type="service" data-item-id="${item.id}">Reject</button>
            </div>
        </article>
    `;
}

function renderList(type, items) {
    const node = document.querySelector(`[data-review-list="${type}"]`);
    if (!node) {
        return;
    }
    if (!items.length) {
        node.innerHTML = renderEmptyState(type);
        return;
    }
    node.innerHTML = items
        .map((item) => (type === "venues" ? renderVenueCard(item) : renderServiceCard(item)))
        .join("");
}

async function loadDashboard() {
    setDashboardStatus("Refreshing moderation queue.", null);

    try {
        const [me, venues, services] = await Promise.all([
            VianueSession.fetchMe(),
            VianueSession.fetchJson("/api/adminpanel/venues/pending", {
                headers: VianueSession.authHeaders(),
            }),
            VianueSession.fetchJson("/api/adminpanel/services/pending", {
                headers: VianueSession.authHeaders(),
            }),
        ]);

        document.querySelector("[data-user-label]").textContent = `${me.username} (${me.role})`;
        updateCounts(venues, services);
        renderList("venues", venues);
        renderList("services", services);
        setDashboardStatus("Queue synced with the API.", "success");
    } catch (error) {
        if (error.status === 401) {
            VianueSession.clearTokens();
            window.location.href = "/login/";
            return;
        }
        if (error.status === 403) {
            window.location.href = "/dashboard/";
            return;
        }
        setDashboardStatus(error.message || "Unable to load dashboard data.", "error");
    }
}

async function handleDecision(button) {
    const itemType = button.dataset.itemType;
    const action = button.dataset.adminAction;
    const itemId = button.dataset.itemId;
    const url = itemType === "venue"
        ? `/api/adminpanel/venues/${itemId}/${action}`
        : `/api/adminpanel/services/${itemId}/${action}`;

    button.disabled = true;
    setDashboardStatus(`Submitting ${action} decision.`, null);

    try {
        await VianueSession.fetchJson(url, {
            method: "POST",
            headers: VianueSession.authHeaders(),
            body: JSON.stringify({}),
        });
        setDashboardStatus(`Item ${action}d successfully.`, "success");
        await loadDashboard();
    } catch (error) {
        setDashboardStatus(error.message || "Unable to complete moderation action.", "error");
    } finally {
        button.disabled = false;
    }
}

document.querySelector("[data-refresh-dashboard]")?.addEventListener("click", () => {
    loadDashboard();
});

document.querySelector("[data-logout]")?.addEventListener("click", () => {
    VianueSession.clearTokens();
    window.location.href = "/login/";
});

document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-admin-action]");
    if (!button) {
        return;
    }
    handleDecision(button);
});

loadDashboard();
