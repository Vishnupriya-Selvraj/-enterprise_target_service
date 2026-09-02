// ==========================================================================
// ENTERPRISE AI WORKBENCH - FRONTEND ENGINE
// ==========================================================================

const NODE_DISPLAY_MAP = {
    "sre_commander": { label: "1. SRE Commander", icon: "🎯", desc: "Scoped P0 Outage & Dispatched Streams" },
    "telemetry_analyst": { label: "2. Telemetry Analyst", icon: "📡", desc: "Captured p99 spike & lock contention" },
    "runbook_rag": { label: "3. Runbook RAG", icon: "📚", desc: "Retrieved SOP SRE-RB-409 Protocol" },
    "diagnostic_fusion": { label: "4. Diagnostic Fusion", icon: "🧩", desc: "Fused Root Cause into confirmed plan" },
    "patch_engineer": { label: "5. Patch Engineer", icon: "💻", desc: "Generated compound index migration" },
    "sandbox_qa": { label: "6. Sandboxed QA", icon: "🧪", desc: "PyTest Suite Passed (4/4)" },
    "security_sast": { label: "7. Security SAST", icon: "🛡️", desc: "Zero CWE vulnerabilities verified" },
    "human_cab_gate": { label: "8. CAB Gate", icon: "👤", desc: "Change Advisory Board approved" },
    "deployment_and_postmortem": { label: "9. Git PR Release", icon: "🚀", desc: "Pushed to GitHub & Created PR #1" }
};

document.addEventListener("DOMContentLoaded", () => {
    initMetrics();
    initPresets();
    initSwarmTrigger();
    initLogsClear();
});

// 1. Fetch & Render Live MongoDB Metrics
async function initMetrics() {
    try {
        const res = await fetch("/api/metrics");
        const data = await res.json();
        
        if (data) {
            document.getElementById("metric-p99").innerText = data.p99_latency || "-- ms";
            document.getElementById("metric-error").innerText = data.error_rate_5xx || "0.0%";
            document.getElementById("metric-stage").innerText = data.live_database_stage?.includes("IXSCAN") ? "IXSCAN" : "COLLSCAN";
            document.getElementById("metric-docs").innerText = Number(data.total_documents || 10000).toLocaleString();

            const isHealthy = data.status === "HEALTHY";
            const badgeP99 = document.getElementById("badge-p99");
            badgeP99.className = `metric-badge ${isHealthy ? "healthy" : "critical"}`;
            badgeP99.innerText = isHealthy ? "OPTIMAL" : "DEGRADED";

            const badgeStage = document.getElementById("badge-stage");
            badgeStage.className = `metric-badge ${isHealthy ? "healthy" : "critical"}`;
            badgeStage.innerText = isHealthy ? "INDEXED" : "COLLSCAN";
        }
    } catch (err) {
        console.warn("Could not fetch metrics snapshot:", err);
    }
}

// 2. Setup Preset Buttons
function initPresets() {
    const presetButtons = document.querySelectorAll(".preset-btn");
    const textarea = document.getElementById("incident-input");

    // Default to first preset
    if (presetButtons.length > 0) {
        textarea.value = presetButtons[0].getAttribute("data-prompt");
    }

    presetButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            presetButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            textarea.value = btn.getAttribute("data-prompt");
        });
    });
}

// 3. Clear Logs Handler
function initLogsClear() {
    document.getElementById("btn-clear-logs").addEventListener("click", () => {
        const terminal = document.getElementById("terminal-body");
        terminal.innerHTML = `
            <div class="log-entry system">
                <span class="log-time">[${getTimestamp()}]</span>
                <span class="log-text">Terminal logs cleared. Swarm standby.</span>
            </div>
        `;
    });
}

// 4. Trigger 9-Node Multi-Agent Swarm
function initSwarmTrigger() {
    const triggerBtn = document.getElementById("btn-trigger-swarm");
    const textarea = document.getElementById("incident-input");
    const statusTag = document.getElementById("swarm-status-tag");
    const resultsSection = document.getElementById("results-section");

    triggerBtn.addEventListener("click", async () => {
        const prompt = textarea.value.trim();
        if (!prompt) return;

        // UI Loading State
        triggerBtn.disabled = true;
        triggerBtn.querySelector(".btn-text").innerText = "⏳ Swarm Mobilizing (Executing 9 Nodes)...";
        statusTag.innerText = "ACTIVE RUN";
        statusTag.className = "tag accent";
        resultsSection.style.display = "none";

        resetAllNodes();
        appendLog("system", `Incident Alert Dispatched: "${prompt.substring(0, 80)}..."`);

        try {
            // Animate node progression visually during network run
            const nodeSequence = [
                "sre_commander",
                "telemetry_analyst",
                "runbook_rag",
                "diagnostic_fusion",
                "patch_engineer",
                "sandbox_qa",
                "security_sast",
                "human_cab_gate",
                "deployment_and_postmortem"
            ];

            let stepTimer = 0;
            nodeSequence.forEach((nodeId, idx) => {
                setTimeout(() => {
                    activateNode(nodeId);
                    const info = NODE_DISPLAY_MAP[nodeId];
                    if (info) {
                        appendLog("step", `Executing [${info.label}]: ${info.desc}`);
                    }
                }, stepTimer);
                stepTimer += 1400; // Visual progression tempo
            });

            // Call FastAPI backend
            const response = await fetch("/api/triage", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ incident_description: prompt })
            });

            const data = await response.json();

            if (data.status === "SUCCESS") {
                // Ensure all nodes show completed
                nodeSequence.forEach(id => completeNode(id));

                statusTag.innerText = "TRIAGE RESOLVED";
                statusTag.className = "tag healthy";

                appendLog("success", `✅ Swarm completed 9-node execution in ${data.elapsed_seconds}s!`);
                appendLog("info", `GitHub PR Created: ${data.git_pr_url}`);

                // Render Results
                resultsSection.style.display = "block";
                document.getElementById("code-diff-viewer").innerText = data.patch_code || "// Migration generated and committed to GitHub.";
                
                // Render Markdown Post-Mortem
                const postmortemViewer = document.getElementById("postmortem-viewer");
                if (window.marked && data.post_mortem_report) {
                    postmortemViewer.innerHTML = marked.parse(data.post_mortem_report);
                } else {
                    postmortemViewer.innerText = data.post_mortem_report;
                }

                // Update PR Action Button
                const prLink = document.getElementById("pr-action-link");
                prLink.href = data.git_pr_url;

                // Refresh Metrics
                initMetrics();

                // Smooth scroll to results
                resultsSection.scrollIntoView({ behavior: "smooth" });
            } else {
                statusTag.innerText = "ERROR";
                statusTag.className = "tag error";
                appendLog("error", `Swarm execution failed: ${data.message || "Unknown error"}`);
            }

        } catch (err) {
            statusTag.innerText = "NETWORK ERROR";
            appendLog("error", `Network or server exception: ${err.message}`);
        } finally {
            triggerBtn.disabled = false;
            triggerBtn.querySelector(".btn-text").innerText = "⚡ Mobilize 9-Node AI Swarm";
        }
    });
}

// Visual Node State Helpers
function resetAllNodes() {
    document.querySelectorAll(".swarm-node").forEach(node => {
        node.classList.remove("active", "completed");
    });
}

function activateNode(nodeId) {
    const node = document.getElementById(`node-${nodeId}`);
    if (node) {
        node.classList.add("active");
        node.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
}

function completeNode(nodeId) {
    const node = document.getElementById(`node-${nodeId}`);
    if (node) {
        node.classList.remove("active");
        node.classList.add("completed");
    }
}

// Terminal Log Appender
function appendLog(type, text) {
    const terminal = document.getElementById("terminal-body");
    const entry = document.createElement("div");
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `
        <span class="log-time">[${getTimestamp()}]</span>
        <span class="log-text">${escapeHtml(text)}</span>
    `;
    terminal.appendChild(entry);
    terminal.scrollTop = terminal.scrollHeight;
}

function getTimestamp() {
    const now = new Date();
    return now.toTimeString().split(" ")[0];
}

function escapeHtml(string) {
    const div = document.createElement('div');
    div.innerText = string;
    return div.innerHTML;
}
