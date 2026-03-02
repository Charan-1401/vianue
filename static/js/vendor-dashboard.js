function vendorStatus(message, tone) {
    const node = document.querySelector("[data-vendor-status]");
    node.textContent = message;
    node.classList.remove("is-success", "is-error");
    if (tone) {
        node.classList.add(tone === "success" ? "is-success" : "is-error");
    }
}

function vendorEscape(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function vendorPayload(form) {
    const maxGuests = form.max_guests_supported.value.trim();
    return {
        title: form.title.value.trim(),
        description: form.description.value.trim(),
        pricing_model: form.pricing_model.value,
        base_price: form.base_price.value || "0.00",
        min_order_value: form.min_order_value.value || "0.00",
        max_guests_supported: maxGuests ? Number(maxGuests) : null,
        travel_fee_rule: {},
        cancellation_policy: {},
    };
}

function resetVendorForm() {
    const form = document.querySelector("[data-vendor-form]");
    form.reset();
    form.service_id.value = "";
    form.base_price.value = "0";
    form.min_order_value.value = "0";
    document.querySelector("[data-vendor-form-mode]").textContent = "Create";
}

function fillVendorForm(item) {
    const form = document.querySelector("[data-vendor-form]");
    form.service_id.value = item.id;
    form.title.value = item.title || "";
    form.description.value = item.description || "";
    form.pricing_model.value = item.pricing_model || "FIXED";
    form.base_price.value = item.base_price || 0;
    form.min_order_value.value = item.min_order_value || 0;
    form.max_guests_supported.value = item.max_guests_supported || "";
    document.querySelector("[data-vendor-form-mode]").textContent = `Edit #${item.id}`;
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderVendorServices(items) {
    const node = document.querySelector("[data-vendor-services]");
    document.querySelector("[data-vendor-service-count]").textContent = items.length;
    document.querySelector("[data-vendor-list-pill]").textContent = `${items.length} service${items.length === 1 ? "" : "s"}`;

    if (!items.length) {
        node.innerHTML = '<div class="empty-state">You have not created any services yet.</div>';
        return;
    }

    node.innerHTML = items.map((item) => `
        <article class="queue-item">
            <header>
                <div>
                    <h3>${vendorEscape(item.title)}</h3>
                    <div class="queue-meta">
                        <span>${vendorEscape(item.pricing_model)}</span>
                        <span>Base ${vendorEscape(item.base_price)}</span>
                        <span>Min order ${vendorEscape(item.min_order_value)}</span>
                    </div>
                </div>
                <span class="pill">${vendorEscape(item.status)}</span>
            </header>
            <p class="queue-description">${vendorEscape(item.description || "No description provided.")}</p>
            <div class="queue-actions">
                <button class="button button-secondary" type="button" data-vendor-edit="${item.id}">Edit</button>
                <button class="button button-primary" type="button" data-vendor-submit="${item.id}">Submit for review</button>
                <button class="button button-danger" type="button" data-vendor-delete="${item.id}">Delete</button>
            </div>
        </article>
    `).join("");
}

function renderVendorRequests(items) {
    const node = document.querySelector("[data-vendor-requests]");
    document.querySelector("[data-vendor-request-count]").textContent = items.length;
    document.querySelector("[data-vendor-request-pill]").textContent = `${items.length} request${items.length === 1 ? "" : "s"}`;

    if (!items.length) {
        node.innerHTML = '<div class="empty-state">No pending booking requests right now.</div>';
        return;
    }

    node.innerHTML = items.map((item) => `
        <article class="queue-item">
            <header>
                <div>
                    <h3>${vendorEscape(item.service)}</h3>
                    <div class="queue-meta">
                        <span>Request #${vendorEscape(item.id)}</span>
                        <span>Order #${vendorEscape(item.order_id)}</span>
                    </div>
                </div>
                <span class="pill">Pending</span>
            </header>
            <pre class="request-snapshot">${vendorEscape(JSON.stringify(item.pricing, null, 2))}</pre>
            <div class="queue-actions">
                <button class="button button-success" type="button" data-vendor-accept="${item.id}">Accept</button>
                <button class="button button-danger" type="button" data-vendor-reject="${item.id}">Reject</button>
            </div>
        </article>
    `).join("");
}

async function loadVendorDashboard() {
    vendorStatus("Loading services.", null);

    try {
        const [me, services, requests] = await Promise.all([
            VianueSession.fetchMe(),
            VianueSession.fetchJson("/api/services/vendor/", {
                headers: VianueSession.authHeaders(),
            }),
            VianueSession.fetchJson("/api/services/vendor/requests/", {
                headers: VianueSession.authHeaders(),
            }),
        ]);
        document.querySelector("[data-vendor-user]").textContent = me.username;
        renderVendorServices(services);
        renderVendorRequests(requests);
        vendorStatus("Vendor workspace synced.", "success");
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
        vendorStatus(error.message || "Unable to load vendor dashboard.", "error");
    }
}

async function saveVendorService(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const serviceId = form.service_id.value;
    const isEdit = Boolean(serviceId);
    const url = isEdit ? `/api/services/vendor/${serviceId}/` : "/api/services/vendor/";
    const method = isEdit ? "PATCH" : "POST";

    vendorStatus(isEdit ? "Updating service." : "Creating service.", null);

    try {
        await VianueSession.fetchJson(url, {
            method,
            headers: VianueSession.authHeaders(),
            body: JSON.stringify(vendorPayload(form)),
        });
        resetVendorForm();
        await loadVendorDashboard();
    } catch (error) {
        vendorStatus(error.message || "Unable to save service.", "error");
    }
}

async function submitVendorService(id) {
    vendorStatus("Submitting service for review.", null);
    try {
        await VianueSession.fetchJson(`/api/services/vendor/${id}/submit/`, {
            method: "POST",
            headers: VianueSession.authHeaders(),
            body: JSON.stringify({}),
        });
        await loadVendorDashboard();
    } catch (error) {
        vendorStatus(error.message || "Unable to submit service.", "error");
    }
}

async function deleteVendorService(id) {
    vendorStatus("Deleting service.", null);
    try {
        await VianueSession.fetchJson(`/api/services/vendor/${id}/`, {
            method: "DELETE",
            headers: VianueSession.authHeaders(),
        });
        await loadVendorDashboard();
    } catch (error) {
        vendorStatus(error.message || "Unable to delete service.", "error");
    }
}

async function vendorDecision(id, action) {
    vendorStatus(`Submitting ${action} decision.`, null);
    try {
        await VianueSession.fetchJson(`/api/services/vendor/requests/${id}/${action}`, {
            method: "POST",
            headers: VianueSession.authHeaders(),
            body: JSON.stringify({}),
        });
        await loadVendorDashboard();
    } catch (error) {
        vendorStatus(error.message || "Unable to process request.", "error");
    }
}

document.querySelector("[data-vendor-form]")?.addEventListener("submit", saveVendorService);
document.querySelector("[data-vendor-reset]")?.addEventListener("click", resetVendorForm);
document.querySelector("[data-refresh-vendor]")?.addEventListener("click", loadVendorDashboard);
document.querySelector("[data-logout]")?.addEventListener("click", () => {
    VianueSession.clearTokens();
    window.location.href = "/login/";
});

document.addEventListener("click", async (event) => {
    const editButton = event.target.closest("[data-vendor-edit]");
    if (editButton) {
        const services = await VianueSession.fetchJson("/api/services/vendor/", {
            headers: VianueSession.authHeaders(),
        });
        const item = services.find((service) => String(service.id) === editButton.dataset.vendorEdit);
        if (item) {
            fillVendorForm(item);
        }
        return;
    }

    const submitButton = event.target.closest("[data-vendor-submit]");
    if (submitButton) {
        submitVendorService(submitButton.dataset.vendorSubmit);
        return;
    }

    const deleteButton = event.target.closest("[data-vendor-delete]");
    if (deleteButton) {
        deleteVendorService(deleteButton.dataset.vendorDelete);
        return;
    }

    const acceptButton = event.target.closest("[data-vendor-accept]");
    if (acceptButton) {
        vendorDecision(acceptButton.dataset.vendorAccept, "accept");
        return;
    }

    const rejectButton = event.target.closest("[data-vendor-reject]");
    if (rejectButton) {
        vendorDecision(rejectButton.dataset.vendorReject, "reject");
    }
});

resetVendorForm();
loadVendorDashboard();
