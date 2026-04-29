function setStatus(element, message, tone) {
    element.textContent = message;
    element.classList.remove("is-success", "is-error");
    if (tone) {
        element.classList.add(tone === "success" ? "is-success" : "is-error");
    }
}

function formatDateTimeLocal(dateStr) {
    const d = new Date(dateStr);
    return d.toISOString().slice(0, 16);
}

async function getQuote(params) {
    const quoteDisplay = document.querySelector("[data-quote-display]");
    const quoteLoading = document.querySelector("[data-quote-loading]");
    const quoteItems = document.querySelector("[data-quote-items]");
    const quoteTotal = document.querySelector("[data-quote-total]");

    if (quoteLoading) quoteLoading.style.display = "block";
    if (quoteDisplay) quoteDisplay.style.display = "none";

    try {
        const response = await fetch("/api/orders/quote/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(params),
        });
        const data = await response.json();

        if (quoteItems) {
            quoteItems.innerHTML = (data.items || [])
                .map((item) => `<div class="quote-item">
                    <span>${item.type === "VENUE" ? "Venue" : "Service"}</span>
                    <span>${parseFloat(item.price).toFixed(2)}</span>
                </div>`)
                .join("");
        }
        if (quoteTotal) quoteTotal.textContent = parseFloat(data.total).toFixed(2);
        if (quoteDisplay) quoteDisplay.style.display = "block";
        if (quoteLoading) quoteLoading.style.display = "none";

        return data;
    } catch (error) {
        if (quoteLoading) quoteLoading.style.display = "none";
        return null;
    }
}

async function loadItemDetails() {
    const params = new URLSearchParams(window.location.search);
    const venueId = params.get("venue_id");
    const serviceId = params.get("service_id");
    const titleNode = document.querySelector("[data-booking-title]");

    if (venueId) {
        document.querySelector("#booking-item-type").value = "VENUE";
        document.querySelector("#booking-venue-id").value = venueId;
        if (titleNode) titleNode.textContent = "Book Venue";

        try {
            const data = await VianueSession.fetchJson(`/api/venues/${venueId}/`, {
                headers: VianueSession.authHeaders(),
            });
            if (titleNode) titleNode.textContent = `Book ${data.name}`;
        } catch {}
    } else if (serviceId) {
        document.querySelector("#booking-item-type").value = "SERVICE";
        document.querySelector("#booking-service-id").value = serviceId;
        if (titleNode) titleNode.textContent = "Book Service";

        try {
            const data = await VianueSession.fetchJson(`/api/services/${serviceId}/`, {
                headers: VianueSession.authHeaders(),
            });
            if (titleNode) titleNode.textContent = `Book ${data.title}`;
        } catch {}
    }
}

async function handleBookingSubmit(form, statusNode, submitBtn) {
    const itemType = form.item_type.value;
    const venueId = form.venue_id.value;
    const serviceId = form.service_id.value;

    if (!itemType || (!venueId && !serviceId)) {
        setStatus(statusNode, "Missing venue or service information.", "error");
        return;
    }

    const orderPayload = {
        start_at: form.start_at.value,
        end_at: form.end_at.value,
        event_type: form.event_type.value,
        guest_count: parseInt(form.guest_count.value),
        event_city: form.event_city.value,
        event_address: form.event_address.value,
    };

    try {
        submitBtn.disabled = true;
        setStatus(statusNode, "Creating order...", null);

        const order = await VianueSession.fetchJson("/api/orders/", {
            method: "POST",
            headers: VianueSession.authHeaders(),
            body: JSON.stringify(orderPayload),
        });

        const itemPayload = {
            item_type: itemType,
            start_at: form.start_at.value,
            end_at: form.end_at.value,
            quantity: 1,
        };
        if (itemType === "VENUE") {
            itemPayload.venue = venueId;
        } else {
            itemPayload.service = serviceId;
        }

        await VianueSession.fetchJson(`/api/orders/${order.id}/items/`, {
            method: "POST",
            headers: VianueSession.authHeaders(),
            body: JSON.stringify(itemPayload),
        });

        setStatus(statusNode, "Booking created successfully! Redirecting...", "success");
        setTimeout(() => {
            window.location.href = "/dashboard/customer/";
        }, 1000);
    } catch (error) {
        const detail = error.payload || error.message || "Booking failed.";
        setStatus(statusNode, typeof detail === "string" ? detail : JSON.stringify(detail), "error");
    } finally {
        submitBtn.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("[data-booking-form]");
    if (!form) return;

    loadItemDetails();

    const statusNode = document.querySelector("[data-booking-status]");
    const submitBtn = form.querySelector("[data-submit-btn]");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        await handleBookingSubmit(form, statusNode, submitBtn);
    });
});
