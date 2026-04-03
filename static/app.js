// Chart instance
let engagementChart = null;

// ========== START MONITORING BUTTON ==========
document.getElementById("startBtn").addEventListener("click", function () {
    const monitoringSection = document.getElementById("monitoringSection");
    if (monitoringSection) {
        monitoringSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
});

// ========== LOAD STATISTICS ==========
async function loadStats() {
    try {
        const response = await fetch("/api/stats");
        const data = await response.json();

        // Update main content stats
        document.getElementById("score").textContent = data.score.toFixed(1) + "%";
        document.getElementById("faces").textContent = data.faces;
        document.getElementById("engaged").textContent = data.engaged;
        document.getElementById("status").textContent = data.status;

        // Update sidebar stats
        document.getElementById("sidebarScore").textContent = data.score.toFixed(1) + "%";
        document.getElementById("sidebarFaces").textContent = data.faces;
        document.getElementById("sidebarStatus").textContent = data.status;

        // Load students table
        const studentsTable = document.getElementById("studentsTable");
        studentsTable.innerHTML = "";

        if (data.students.length === 0) {
            studentsTable.innerHTML = "<tr><td colspan='4'>No students found</td></tr>";
        } else {
            data.students.forEach(student => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${student.id}</td>
                    <td>${student.name}</td>
                    <td>${student.roll_no || "-"}</td>
                    <td>${student.attendance}</td>
                `;
                studentsTable.appendChild(row);
            });
        }

        // Load engagement logs table
        const logsTable = document.getElementById("logsTable");
        logsTable.innerHTML = "";

        if (data.logs.length === 0) {
            logsTable.innerHTML = "<tr><td colspan='5'>No logs found</td></tr>";
        } else {
            data.logs.forEach(log => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${log.timestamp}</td>
                    <td>${log.score}%</td>
                    <td>${log.faces_detected}</td>
                    <td>${log.engaged_faces}</td>
                    <td>${log.status}</td>
                `;
                logsTable.appendChild(row);
            });
        }
    } catch (error) {
        console.error("Error loading stats:", error);
    }
}

// ========== LOAD CHART DATA ==========
async function loadChartData() {
    try {
        const response = await fetch("/api/chart-data");
        const data = await response.json();

        if (!data.ok) {
            console.error("Failed to fetch chart data:", data.error);
            return;
        }

        // Format timestamps to show only time (HH:MM:SS)
        const labels = data.labels.map(timestamp => {
            const time = timestamp.split(" ")[1];
            return time || timestamp;
        });

        // Create or update chart
        const ctx = document.getElementById("engagementChart").getContext("2d");

        if (engagementChart) {
            engagementChart.data.labels = labels;
            engagementChart.data.datasets[0].data = data.data;
            engagementChart.update();
        } else {
            engagementChart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Engagement Score (%)",
                            data: data.data,
                            borderColor: "rgb(6, 182, 212)",
                            backgroundColor: "rgba(6, 182, 212, 0.1)",
                            borderWidth: 3,
                            tension: 0.4,
                            fill: true,
                            pointBackgroundColor: "rgb(6, 182, 212)",
                            pointBorderColor: "#fff",
                            pointBorderWidth: 2,
                            pointRadius: 5,
                            pointHoverRadius: 7
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            labels: {
                                font: { size: 14 },
                                color: "#1e293b",
                                usePointStyle: true
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function (value) {
                                    return value + "%";
                                },
                                color: "#64748b"
                            },
                            grid: {
                                color: "rgba(0, 0, 0, 0.05)"
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: "#64748b"
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error("Error loading chart data:", error);
    }
}

// ========== ADD STUDENT FORM ==========
document.getElementById("studentForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const roll_no = document.getElementById("roll_no").value.trim();
    const message = document.getElementById("message");

    try {
        const response = await fetch("/api/add_student", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name, roll_no })
        });

        const result = await response.json();

        if (result.ok) {
            message.style.color = "#10b981";
            message.textContent = "✓ " + result.message;
            document.getElementById("studentForm").reset();
            loadStats();
        } else {
            message.style.color = "#ef4444";
            message.textContent = "✗ " + result.message;
        }
    } catch (error) {
        message.style.color = "#ef4444";
        message.textContent = "✗ Something went wrong";
        console.error("Error:", error);
    }
});

// ========== INITIALIZE ==========
// Load initial data
loadStats();
loadChartData();

// Update stats every 2 seconds
setInterval(loadStats, 2000);

// Update chart every 10 seconds
setInterval(loadChartData, 10000);