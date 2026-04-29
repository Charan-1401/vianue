let ownerVenueCache = [];

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

function normalizeOptionalUrl(value) {
    const trimmed = value.trim();
    if (!trimmed) {
        return "";
    }
    return /^[a-z]+:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
}

function appendFormValue(formData, key, value) {
    if (value === null || value === undefined) {
        formData.append(key, "");
        return;
    }
    formData.append(key, String(value));
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
        instagram_url: normalizeOptionalUrl(form.instagram_url.value),
        facebook_url: normalizeOptionalUrl(form.facebook_url.value),
        youtube_url: normalizeOptionalUrl(form.youtube_url.value),
        website_url: normalizeOptionalUrl(form.website_url.value),
    };
}

function ownerFormData(form) {
    const payload = ownerPayload(form);
    const formData = new FormData();
    Object.entries(payload).forEach(([key, value]) => appendFormValue(formData, key, value));
    Array.from(form.media_uploads.files).forEach((file) => {
        formData.append("media_uploads", file);
    });
    return formData;
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
    form.instagram_url.value = item.instagram_url || "";
    form.facebook_url.value = item.facebook_url || "";
    form.youtube_url.value = item.youtube_url || "";
    form.website_url.value = item.website_url || "";
    document.querySelector("[data-owner-form-mode]").textContent = `Edit #${item.id}`;
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function ownerSocialMarkup(item) {
    const links = [
        ["Instagram", item.instagram_url],
        ["Facebook", item.facebook_url],
        ["YouTube", item.youtube_url],
        ["Website", item.website_url],
    ].filter(([, url]) => url);

    if (!links.length) {
        return "";
    }

    return `
        <div class="social-links">
            ${links.map(([label, url]) => `
                <a class="social-link" href="${ownerEscape(url)}" target="_blank" rel="noreferrer">
                    ${ownerEscape(label)}
                </a>
            `).join("")}
        </div>
    `;
}

function ownerMediaMarkup(item) {
    if (!item.media?.length) {
        return "";
    }

    return `
        <div class="media-grid">
            ${item.media.map((media) => `
                <figure class="media-card">
                    ${media.is_video
                        ? `<video src="${ownerEscape(media.file)}" controls preload="metadata"></video>`
                        : `<img src="${ownerEscape(media.file)}" alt="${ownerEscape(item.name)} media" loading="lazy">`
                    }
                    <figcaption>
                        <span>${media.is_video ? "Video" : "Photo"}</span>
                        <button
                            class="button button-danger button-compact"
                            type="button"
                            data-owner-media-delete="${item.id}:${media.id}"
                        >
                            Remove
                        </button>
                    </figcaption>
                </figure>
            `).join("")}
        </div>
    `;
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
                        <span>${item.media?.length || 0} uploads</span>
                    </div>
                </div>
                <span class="pill">${ownerEscape(item.status)}</span>
            </header>
            <p class="queue-description">${ownerEscape(item.address)}</p>
            ${ownerSocialMarkup(item)}
            ${ownerMediaMarkup(item)}
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
        ownerVenueCache = venues;
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
            headers: VianueSession.authHeaders({ json: false }),
            body: ownerFormData(form),
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

async function deleteOwnerMedia(venueId, mediaId) {
    ownerStatus("Removing media.", null);
    try {
        await VianueSession.fetchJson(`/api/venues/owner/${venueId}/media/${mediaId}/`, {
            method: "DELETE",
            headers: VianueSession.authHeaders(),
        });
        await loadOwnerDashboard();
    } catch (error) {
        ownerStatus(error.message || "Unable to delete media.", "error");
    }
}

document.querySelector("[data-owner-form]")?.addEventListener("submit", saveOwnerVenue);
document.querySelector("[data-owner-reset]")?.addEventListener("click", resetOwnerForm);
document.querySelector("[data-refresh-owner]")?.addEventListener("click", loadOwnerDashboard);
document.querySelector("[data-logout]")?.addEventListener("click", () => {
    VianueSession.clearTokens();
    window.location.href = "/login/";
});

document.addEventListener("click", (event) => {
    const editButton = event.target.closest("[data-owner-edit]");
    if (editButton) {
        const item = ownerVenueCache.find((venue) => String(venue.id) === editButton.dataset.ownerEdit);
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
        return;
    }

    const mediaDeleteButton = event.target.closest("[data-owner-media-delete]");
    if (mediaDeleteButton) {
        const [venueId, mediaId] = mediaDeleteButton.dataset.ownerMediaDelete.split(":");
        deleteOwnerMedia(venueId, mediaId);
    }
});

resetOwnerForm();
loadOwnerDashboard();
loadOwnerBookings();

async function loadOwnerBookings() {
    const container = document.querySelector("[data-owner-bookings]");
    const countNode = document.querySelector("[data-owner-booking-count]");
    const pillNode = document.querySelector("[data-owner-booking-pill]");
    const emptyNode = document.querySelector("[data-no-owner-bookings]");

    try {
        const data = await VianueSession.fetchJson("/api/orders/venue-bookings/", {
            headers: VianueSession.authHeaders(),
        });

        const bookings = data.results || data;
        if (countNode) countNode.textContent = bookings.length;
        if (pillNode) pillNode.textContent = `${bookings.length} booking${bookings.length === 1 ? "" : "s"}`;

        if (bookings.length === 0) {
            if (emptyNode) emptyNode.style.display = "block";
            if (container) container.innerHTML = "";
            return;
        }

        if (container) {
            container.innerHTML = bookings.map(renderBooking).join("");
        }
    } catch (error) {
        console.error("Failed to load bookings:", error);
    }
}

function renderBooking(booking) {
    const statusColors = {
        PENDING_ACCEPTANCE: "pill-yellow",
        ACCEPTED: "pill-green",
        REJECTED: "pill-red",
        SCHEDULED: "pill-blue",
        DELIVERED: "pill-purple",
    };
    const statusColor = statusColors[booking.fulfillment_status] || "pill-gray";

    return `<div class="queue-item" data-booking-id="${booking.id}">
        <header>
            <div>
                <h3>Order #${booking.order}</h3>
                <div class="queue-meta">
                    <span>${booking.item_type}</span>
                    <span>${new Date(booking.start_at).toLocaleDateString()}</span>
                    <span>${booking.quantity} unit(s)</span>
                </div>
            </div>
            <span class="pill ${statusColor}">${booking.fulfillment_status}</span>
        </header>
        <div class="queue-actions">
            ${booking.fulfillment_status === "PENDING_ACCEPTANCE" ? `
                <button class="button button-primary" data-accept-booking="${booking.id}">Accept</button>
                <button class="button button-danger" data-reject-booking="${booking.id}">Reject</button>
            ` : ""}
            ${booking.fulfillment_status === "ACCEPTED" ? `
                <button class="button button-secondary" data-schedule-booking="${booking.id}">Mark Scheduled</button>
            ` : ""}
            ${booking.fulfillment_status === "SCHEDULED" ? `
                <button class="button button-primary" data-deliver-booking="${booking.id}">Mark Delivered</button>
            ` : ""}
        </div>
    </div>`;
}

document.addEventListener("click", async (event) => {
    const acceptBtn = event.target.closest("[data-accept-booking]");
    if (acceptBtn) {
        await updateBookingStatus(acceptBtn.dataset.acceptBooking, "accept");
        return;
    }

    const rejectBtn = event.target.closest("[data-reject-booking]");
    if (rejectBtn) {
        await updateBookingStatus(rejectBtn.dataset.rejectBooking, "reject");
        return;
    }

    const scheduleBtn = event.target.closest("[data-schedule-booking]");
    if (scheduleBtn) {
        await updateBookingStatus(scheduleBtn.dataset.scheduleBooking, "schedule");
        return;
    }

    const deliverBtn = event.target.closest("[data-deliver-booking]");
    if (deliverBtn) {
        await updateBookingStatus(deliverBtn.dataset.deliverBooking, "deliver");
        return;
    }
});

async function updateBookingStatus(itemId, action) {
    try {
        await VianueSession.fetchJson(`/api/orders/booking-management/${itemId}/`, {
            method: "POST",
            headers: VianueSession.authHeaders(),
            body: JSON.stringify({ action }),
        });
        ownerStatus("Booking updated successfully.", "success");
        await loadOwnerBookings();
    } catch (error) {
        ownerStatus(error.message || "Failed to update booking.", "error");
    }
}
