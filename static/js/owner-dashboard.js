function ownerStatus(message, tone) {
    const node = document.querySelector("[data-owner-status]");
    node.textContent = message;
    node.classList.remove("is-success", "is-error");
    if (tone) {
        node.classList.add(tone === "success" ? "is-success" : "is-error");
    }
}

function ownerEscape(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function ownerPayload(form) {
    return {
        name: form.name.value.trim(),
        venue_type: form.venue_type.value.trim(),
        description: form.description.value.trim(),
        address: form.address.value.trim(),
        city: form.city.value.trim(),
        state: form.state.value.trim(),
        country: form.country.value.trim(),
        pincode: form.pincode.value.trim(),
        capacity_min: Number(form.capacity_min.value || 1),
        capacity_max: Number(form.capacity_max.value || 100),
        base_price: form.base_price.value || "0.00",
    };
}

function resetOwnerForm() {
    const form = document.querySelector("[data-owner-form]");
    form.reset();
    form.venue_id.value = "";
    form.capacity_min.value = "1";
    form.capacity_max.value = "100";
    form.base_price.value = "0";
    document.querySelector("[data-owner-form-mode]").textContent = "Create";
}

function fillOwnerForm(item) {
    const form = document.querySelector("[data-owner-form]");
    form.venue_id.value = item.id;
    form.name.value = item.name || "";
    form.venue_type.value = item.venue_type || "";
    form.description.value = item.description || "";
    form.address.value = item.address || "";
    form.city.value = item.city || "";
    form.state.value = item.state || "";
    form.country.value = item.country || "";
    form.pincode.value = item.pincode || "";
    form.capacity_min.value = item.capacity_min || 1;
    form.capacity_max.value = item.capacity_max || 100;
    form.base_price.value = item.base_price || 0;
    document.querySelector("[data-owner-form-mode]").textContent = `Edit #${item.id}`;
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderOwnerItems(items) {
    const node = document.querySelector("[data-owner-venues]");
    const pendingCount = items.filter((item) => item.status === "PENDING").length;

    document.querySelector("[data-owner-venue-count]").textContent = items.length;
    document.querySelector("[data-owner-pending-count]").textContent = pendingCount;
    document.querySelector("[data-owner-list-pill]").textContent = `${items.length} venue${items.length === 1 ? "" : "s"}`;

    if (!items.length) {
        node.innerHTML = '<div class="empty-state">You have not created any venues yet.</div>';
        return;
    }

    node.innerHTML = items.map((item) => `
        <article class="queue-item">
            <header>
                <div>
                    <h3>${ownerEscape(item.name)}</h3>
                    <div class="queue-meta">
                        <span>${ownerEscape(item.venue_type || "Venue")}</span>
                        <span>${ownerEscape(item.city)}</span>
                        <span>${ownerEscape(item.capacity_min)}-${ownerEscape(item.capacity_max)} guests</span>
                    </div>
                </div>
                <span class="pill">${ownerEscape(item.status)}</span>
            </header>
            <p class="queue-description">${ownerEscape(item.address)}</p>
            <div class="queue-actions">
                <button class="button button-secondary" type="button" data-owner-edit="${item.id}">Edit</button>
                <button class="button button-primary" type="button" data-owner-submit="${item.id}">Submit for review</button>
                <button class="button button-danger" type="button" data-owner-delete="${item.id}">Delete</button>
            </div>
        </article>
    `).join("");
}

async function loadOwnerDashboard() {
    ownerStatus("Loading venues.", null);

    try {
        const [me, venues] = await Promise.all([
            VianueSession.fetchMe(),
            VianueSession.fetchJson("/api/venues/owner/", {
                headers: VianueSession.authHeaders(),
            }),
        ]);
        document.querySelector("[data-owner-user]").textContent = me.username;
        renderOwnerItems(venues);
        ownerStatus("Venue list synced.", "success");
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
        ownerStatus(error.message || "Unable to load venues.", "error");
    }
}

async function saveOwnerVenue(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const venueId = form.venue_id.value;
    const isEdit = Boolean(venueId);
    const url = isEdit ? `/api/venues/owner/${venueId}/` : "/api/venues/owner/";
    const method = isEdit ? "PATCH" : "POST";

    ownerStatus(isEdit ? "Updating venue." : "Creating venue.", null);

    try {
        await VianueSession.fetchJson(url, {
            method,
            headers: VianueSession.authHeaders(),
            body: JSON.stringify(ownerPayload(form)),
        });
        resetOwnerForm();
        await loadOwnerDashboard();
    } catch (error) {
        ownerStatus(error.message || "Unable to save venue.", "error");
    }
}

async function submitOwnerVenue(id) {
    ownerStatus("Submitting venue for review.", null);
    try {
        await VianueSession.fetchJson(`/api/venues/owner/${id}/submit/`, {
            method: "POST",
            headers: VianueSession.authHeaders(),
            body: JSON.stringify({}),
        });
        await loadOwnerDashboard();
    } catch (error) {
        ownerStatus(error.message || "Unable to submit venue.", "error");
    }
}

async function deleteOwnerVenue(id) {
    ownerStatus("Deleting venue.", null);
    try {
        await VianueSession.fetchJson(`/api/venues/owner/${id}/`, {
            method: "DELETE",
            headers: VianueSession.authHeaders(),
        });
        await loadOwnerDashboard();
    } catch (error) {
        ownerStatus(error.message || "Unable to delete venue.", "error");
    }
}

document.querySelector("[data-owner-form]")?.addEventListener("submit", saveOwnerVenue);
document.querySelector("[data-owner-reset]")?.addEventListener("click", resetOwnerForm);
document.querySelector("[data-refresh-owner]")?.addEventListener("click", loadOwnerDashboard);
document.querySelector("[data-logout]")?.addEventListener("click", () => {
    VianueSession.clearTokens();
    window.location.href = "/login/";
});

document.addEventListener("click", async (event) => {
    const editButton = event.target.closest("[data-owner-edit]");
    if (editButton) {
        const venues = await VianueSession.fetchJson("/api/venues/owner/", {
            headers: VianueSession.authHeaders(),
        });
        const item = venues.find((venue) => String(venue.id) === editButton.dataset.ownerEdit);
        if (item) {
            fillOwnerForm(item);
        }
        return;
    }

    const submitButton = event.target.closest("[data-owner-submit]");
    if (submitButton) {
        submitOwnerVenue(submitButton.dataset.ownerSubmit);
        return;
    }

    const deleteButton = event.target.closest("[data-owner-delete]");
    if (deleteButton) {
        deleteOwnerVenue(deleteButton.dataset.ownerDelete);
    }
});

resetOwnerForm();
loadOwnerDashboard();
