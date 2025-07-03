document.addEventListener("DOMContentLoaded", () => {
    const connectBtn = document.getElementById("connect-calendar");
    const eventsTable = document.getElementById("events-table");
    const eventsContainer = document.querySelector("#events-container tbody");

    if (connectBtn) {
        connectBtn.addEventListener("click", () => {
            fetch('/fetch_events')
                .then(response => response.json())
                .then(data => {
                    if (data && data.length > 0) {
                        eventsContainer.innerHTML = "";
                        data.forEach(event => {
                            const row = document.createElement("tr");
                            row.innerHTML = `
                                <td>${event.summary}</td>
                                <td>${formatDateTime(event.start)}</td>
                                <td>${formatDateTime(event.end)}</td>

                            `;
                            eventsContainer.appendChild(row);
                        });
                        eventsTable.style.display = "table";
                    } else {
                        eventsContainer.innerHTML = `<tr><td colspan="3">No upcoming events found.</td></tr>`;
                        eventsTable.style.display = "table";
                    }
                })
                .catch(error => {
                    console.error("Error fetching calendar events:", error);
                    eventsContainer.innerHTML = `<tr><td colspan="3">Failed to load events.</td></tr>`;
                    eventsTable.style.display = "table";
                });
        });
    }
});
function formatDateTime(isoString) {
    const date = new Date(isoString);
    const options = {
        weekday: 'short',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    };
    return date.toLocaleString('en-IN', options); 
}

