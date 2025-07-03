document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");

    window.sendMessage = function () {
        const text = userInput.value.trim();
        if (!text) return;

        appendMessage("You", text, "user-msg");
        userInput.value = "";

        fetch("/guest_schedule", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        })
        .then(response => response.json())
        .then(schedule => {
            appendSchedule(schedule);
            document.getElementById("download-buttons").style.display = "block";
        })
        .catch(error => {
            appendMessage("Bot", "An error occurred while generating the schedule.", "bot-msg");
            console.error(error);
        });
    };

    function appendMessage(sender, text, className) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `chat-message ${className}`;
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendSchedule(schedule) {
        const messageDiv = document.createElement("div");
        messageDiv.className = "chat-message bot-msg";
    
        if (schedule.length === 1 && schedule[0].start_time === '' && schedule[0].end_time === '') {
            messageDiv.innerHTML = `<strong>Bot:</strong> ${schedule[0].task}`;
        } else if (schedule.length === 0) {
            messageDiv.innerHTML = `<strong>Bot:</strong> I didn't catch any valid tasks. Could you please rephrase?`;
        } else {
            messageDiv.innerHTML = `<strong>Bot:</strong> Here's your optimized schedule:<br>${generateTable(schedule)}`;
            document.getElementById("download-buttons").style.display = "block";
        }
    
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    

    function generateTable(schedule) {
        let table = "<table><thead><tr><th>Task</th><th>Date</th><th>Start</th><th>End</th></tr></thead><tbody>";
        schedule.forEach(item => {
            table += `<tr><td>${item.task}</td><td>${item.date}</td><td>${item.start_time}</td><td>${item.end_time}</td></tr>`;
        });
        table += "</tbody></table>";
        return table;
    }

    window.printSchedule = function () {
        const printContent = document.getElementById("chat-box").innerHTML;
        const w = window.open();
        w.document.write('<html><head><title>Schedule</title></head><body>' + printContent + '</body></html>');
        w.document.close();
        w.print();
    };

    window.downloadSchedule = function () {
        const table = document.querySelector("#chat-box table");
        if (!table) return;

        let csv = "Task,Date,Start,End\n";
        for (const row of table.rows) {
            const cols = Array.from(row.cells).map(cell => cell.innerText);
            if (cols.length === 4) csv += cols.join(",") + "\n";
        }

        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "schedule.csv";
        a.click();
        URL.revokeObjectURL(url);
    };
});
