function setStatus(element, message, tone) {
    element.textContent = message;
    element.classList.remove("is-success", "is-error");
    if (tone) {
        element.classList.add(tone === "success" ? "is-success" : "is-error");
    }
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function renderOrder(order) {
    const statusColors = {
        DRAFT: "pill-gray",
        PENDING_PAYMENT: "pill-yellow",
        CONFIRMED: "pill-green",
        CANCELLED: "pill-red",
        COMPLETED: "pill-blue",
        REFUNDED: "pill-purple",
    };
    const statusColor = statusColors[order.status] || "pill-gray";

    const itemsHtml = (order.items || [])
        .map((item) => {
            const type = item.item_type === "VENUE" ? "Venue" : "Service";
            const name = item.venue ? item.venue.name : item.service ? item.service.title : "Unknown";
            return `<div class="booking-item">
                <span class="item-type">${type}</span>
                <span class="item-name">${name}</span>
                <span class="item-status ${statusColor}">${item.fulfillment_status}</span>
            </div>`;
        })
        .join("");

    return `<div class="booking-card" data-order-id="${order.id}">
        <div class="booking-header">
            <div>
                <h3>Order #${order.id}</h3>
                <p class="booking-meta">
                    <i class="fa-regular fa-calendar"></i> ${formatDate(order.start_at)}
                    ${order.guest_count ? ` | <i class="fa-solid fa-users"></i> ${order.guest_count} guests` : ""}
                </p>
            </div>
            <span class="pill ${statusColor}">${order.status}</span>
        </div>
        <div class="booking-items">${itemsHtml}</div>
        <div class="booking-footer">
            <span class="booking-total">${order.currency} ${parseFloat(order.totals_snapshot?.total || 0).toFixed(2)}</span>
            <button class="button button-small" data-view-order="${order.id}">View details</button>
        </div>
    </div>`;
}

async function loadMyOrders() {
    const container = document.querySelector("[data-my-orders]");
    const statusNode = document.querySelector("[data-booking-status]");
    const countNode = document.querySelector("[data-booking-count]");
    const pendingNode = document.querySelector("[data-pending-count]");
    const confirmedNode = document.querySelector("[data-confirmed-count]");
    const emptyNode = document.querySelector("[data-no-orders]");

    try {
        const data = await VianueSession.fetchJson("/api/orders/my/", {
            headers: VianueSession.authHeaders(),
        });

        const orders = data.results || data;
        const pending = orders.filter((o) => o.status === "PENDING_PAYMENT" || o.status === "DRAFT");
        const confirmed = orders.filter((o) => o.status === "CONFIRMED" || o.status === "COMPLETED");

        if (countNode) countNode.textContent = orders.length;
        if (pendingNode) pendingNode.textContent = pending.length;
        if (confirmedNode) confirmedNode.textContent = confirmed.length;

        if (orders.length === 0) {
            if (emptyNode) emptyNode.style.display = "block";
            if (container) container.innerHTML = "";
            return;
        }

        if (container) {
            container.innerHTML = orders.map(renderOrder).join("");
        }

        setStatus(statusNode, `Loaded ${orders.length} booking(s).`, "success");
    } catch (error) {
        setStatus(statusNode, error.message || "Failed to load bookings.", "error");
    }
}

function initLogout() {
    const logoutBtn = document.querySelector("[data-logout]");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            VianueSession.clearTokens();
            window.location.href = "/login/";
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadMyOrders();
    initLogout();
});
