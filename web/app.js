// ==========================================================================
// ENTERPRISE AI WORKBENCH - ADVANCED MULTI-AGENT FRONTEND ENGINE v3.0
// ==========================================================================

const NODE_DISPLAY_MAP = {
    "sre_commander": { step: 1, label: "1. SRE Incident Commander", icon: "🎯", desc: "Supervisory Triage & Stream Dispatch" },
    "telemetry_analyst": { step: 2, label: "2. Telemetry & Log Analyst", icon: "📡", desc: "OpenTelemetry Spans & MongoDB Explain Plan" },
    "runbook_rag": { step: 3, label: "3. Runbook RAG Agent", icon: "📚", desc: "SRE Knowledge Base SOP Retrieval" },
    "diagnostic_fusion": { step: 4, label: "4. Diagnostic Fusion Engine", icon: "🧩", desc: "Cross-Stream RCA Convergence" },
    "patch_engineer": { step: 5, label: "5. Principal Patch Engineer", icon: "💻", desc: "Remediation Patch & Reflection Engine" },
    "sandbox_qa": { step: 6, label: "6. Sandboxed QA Runner", icon: "🧪", desc: "Live PyUnit Test Runner (localhost:27017)" },
    "security_sast": { step: 7, label: "7. DevSecOps SAST Auditor", icon: "🛡️", desc: "CWE-89 & NoSQL Injection Auditor" },
    "human_cab_gate": { step: 8, label: "8. CAB Governance Gate", icon: "👤", desc: "Cryptographic Governance Authorization" },
    "deployment_and_postmortem": { step: 9, label: "9. Git PR Deployment", icon: "🚀", desc: "Live GitHub Push & PR Deployment" }
};

const NODE_ORDER = [
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

// 2. Setup 5 Preset Buttons
function initPresets() {
    const presetButtons = document.querySelectorAll(".preset-btn");
    const textarea = document.getElementById("incident-input");

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

// 4. Trigger 9-Node Multi-Agent Swarm with Live Progress Pipeline
function initSwarmTrigger() {
    const triggerBtn = document.getElementById("btn-trigger-swarm");
    const textarea = document.getElementById("incident-input");
    const statusTag = document.getElementById("swarm-status-tag");
    const resultsSection = document.getElementById("results-section");
    const progressContainer = document.getElementById("pipeline-progress-bar");
    const progressFill = document.getElementById("progress-fill");
    const statusLabel = document.getElementById("pipeline-status-label");
    const stepCounter = document.getElementById("pipeline-step-counter");
    const percentLabel = document.getElementById("pipeline-percent");

    triggerBtn.addEventListener("click", async () => {
        const prompt = textarea.value.trim();
        if (!prompt) return;

        // UI Loading State
        triggerBtn.disabled = true;
        triggerBtn.querySelector(".btn-text").innerText = "⏳ Swarm Mobilized: Executing 9 Nodes in Parallel...";
        statusTag.innerText = "ACTIVE RUN";
        statusTag.className = "tag accent";
        resultsSection.style.display = "none";
        progressContainer.classList.add("running");

        resetAllNodes();
        updateProgress(0, "Mobilizing SRE Swarm: Initializing State Machine...");
        appendLog("system", `🚨 Incident Alert Mobilized: "${prompt.substring(0, 80)}..."`);

        try {
            // Animate node progression visually during execution
            let currentStepIdx = 0;
            const stepInterval = 1200;

            const timer = setInterval(() => {
                if (currentStepIdx < NODE_ORDER.length) {
                    const nodeId = NODE_ORDER[currentStepIdx];
                    const info = NODE_DISPLAY_MAP[nodeId];
                    
                    activateNode(nodeId);
                    activateStepPill(nodeId);
                    
                    const pct = Math.round(((currentStepIdx + 1) / NODE_ORDER.length) * 100);
                    updateProgress(pct, `Executing Node ${currentStepIdx + 1}/9: ${info.label} (${info.desc})`);
                    appendLog("step", `⚡ [Node ${currentStepIdx + 1}/9] ${info.label}: ${info.desc}`);

                    currentStepIdx++;
                }
            }, stepInterval);

            // Call FastAPI backend
            const response = await fetch("/api/triage", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ incident_description: prompt })
            });

            const data = await response.json();
            clearInterval(timer);

            if (data.status === "SUCCESS") {
                // Complete all steps and nodes
                NODE_ORDER.forEach(id => {
                    completeNode(id);
                    completeStepPill(id);
                });

                updateProgress(100, `✅ Incident Remediated: 9/9 Nodes Verified in ${data.elapsed_seconds}s`);
                statusTag.innerText = "TRIAGE RESOLVED";
                statusTag.className = "tag healthy";

                // Print Agent Thoughts and Tool Audits to Terminal
                if (data.agent_thoughts && data.agent_thoughts.length > 0) {
                    data.agent_thoughts.forEach(th => appendLog("info", th));
                }

                if (data.tool_audit_trail && data.tool_audit_trail.length > 0) {
                    data.tool_audit_trail.forEach(tool => {
                        appendLog("tool", `🔧 Tool Executed: ${tool.tool} (${tool.latency_ms}ms) -> Status: ${tool.status}`);
                    });
                }

                appendLog("success", `✅ Swarm completed 9-node execution in ${data.elapsed_seconds}s!`);
                if (data.cab_token) {
                    appendLog("info", `👤 CAB Authorization Issued: ${data.cab_token}`);
                }
                appendLog("info", `🐙 GitHub PR Deployed: ${data.git_pr_url}`);

                // Render Results
                resultsSection.style.display = "block";
                document.getElementById("code-diff-viewer").innerText = data.patch_code || "// Remediation patch generated and committed to GitHub.";
                
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
            progressContainer.classList.remove("running");
        }
    });

    function updateProgress(percent, label) {
        progressFill.style.width = `${percent}%`;
        percentLabel.innerText = `${percent}%`;
        statusLabel.innerText = label;
        
        const activeCount = Math.round((percent / 100) * 9);
        stepCounter.innerText = `${activeCount} / 9 Nodes Complete`;
    }
}

// Visual Node State Helpers
function resetAllNodes() {
    document.querySelectorAll(".swarm-node").forEach(node => {
        node.classList.remove("active", "completed");
    });
    document.querySelectorAll(".step-pill").forEach(pill => {
        pill.classList.remove("active", "completed");
    });
}

function activateNode(nodeId) {
    const node = document.getElementById(`node-${nodeId}`);
    if (node) {
        node.classList.add("active");
    }
}

function completeNode(nodeId) {
    const node = document.getElementById(`node-${nodeId}`);
    if (node) {
        node.classList.remove("active");
        node.classList.add("completed");
    }
}

function activateStepPill(nodeId) {
    const pill = document.getElementById(`step-${nodeId}`);
    if (pill) {
        pill.classList.add("active");
    }
}

function completeStepPill(nodeId) {
    const pill = document.getElementById(`step-${nodeId}`);
    if (pill) {
        pill.classList.remove("active");
        pill.classList.add("completed");
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
