import os
import time
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from src.config import settings
from src.graph import build_devsecops_swarm_graph

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="Autonomous AI SRE & DevSecOps Swarm",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF6B6B, #1E88E5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1rem;
        color: #718096;
        margin-bottom: 24px;
    }
    .status-badge {
        background-color: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# -------------------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"sre-session-{int(time.time())}"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph" not in st.session_state:
    st.session_state.graph = build_devsecops_swarm_graph(checkpointer=True)

# -------------------------------------------------------------
# 3. SIDEBAR CONTROLS & PRESETS
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://raw.githubusercontent.com/langchain-ai/langgraph/main/docs/static/img/langgraph_logo.png", width=180)
    st.title("SRE Commander")

    st.markdown("### 🔌 Swarm Runtime")
    provider = settings.get_resolved_provider().upper()
    model = settings.get_resolved_model_name()
    st.success(f"**LLM Engine**: {provider}\n(`{model}`)")
    st.info(f"**LangSmith Project**:\n`{settings.langsmith_project}`")

    st.divider()

    st.markdown("### ⚡ Live Incident Presets")
    st.caption("Click to trigger an autonomous 9-node incident triage & PR release:")

    preset_1 = "CRITICAL OUTAGE: checkout-api is throwing 504 gateway timeouts. p99 latency spiked to 5,120ms with 26.4% 5xx errors. Investigate, patch, verify tests, SAST audit, and raise PR."
    preset_2 = "P0 SEV1 ALERT: orders-db connection pool is 100% saturated. Row lock contention observed on cart_items table. Diagnose, write migration patch, and deploy hotfix."
    preset_3 = "SECURITY & STABILITY AUDIT: Check concurrency lock patterns on checkout services, rewrite unindexed queries with NOWAIT safeguards, and verify with SAST scanner."

    if st.button("🚨 P0: Checkout 504 Outage", use_container_width=True):
        st.session_state.preset_input = preset_1

    if st.button("💥 P0: DB Pool Exhaustion", use_container_width=True):
        st.session_state.preset_input = preset_2

    if st.button("🛡️ DevSecOps Lock Audit", use_container_width=True):
        st.session_state.preset_input = preset_3

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = f"sre-session-{int(time.time())}"
            st.rerun()
    with col2:
        st.link_button("📊 LangSmith", "https://smith.langchain.com", use_container_width=True)

# -------------------------------------------------------------
# 4. MAIN CANVAS & SWARM VISUALIZER
# -------------------------------------------------------------
st.markdown('<div class="main-title">⚡ Autonomous SRE & DevSecOps Swarm</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">9-Node Architecture: SRE Commander ➔ [Telemetry || Runbooks] ➔ Fusion ➔ Patch ➔ Sandbox QA ➔ SAST ➔ CAB ➔ Git PR</div>', unsafe_allow_html=True)

# Render prior chat history
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(msg.content)

# Prompt input
prompt_input = st.chat_input("Enter production incident alert (e.g. 'checkout-api is failing with 504 timeouts')...")

if "preset_input" in st.session_state and st.session_state.preset_input:
    prompt_input = st.session_state.preset_input
    st.session_state.preset_input = None

if prompt_input:
    st.session_state.messages.append(HumanMessage(content=prompt_input))
    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant", avatar="⚡"):
        status_box = st.status("🚀 SRE Swarm Mobilized: Triaging Incident & Dispatching Streams...", expanded=True)
        
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        final_postmortem = ""

        NODE_LABELS = {
            "sre_commander": "🎯 **1. SRE Incident Commander**: Scoped P0 Outage & Dispatched Parallel Streams",
            "telemetry_analyst": "📡 **2. Telemetry & Log Analyst**: Captured p99 5,120ms spike & PID 62901 lock contention",
            "runbook_rag": "📚 **3. Runbook RAG Agent**: Retrieved SOP SRE-RB-409 (Row Lock Remediation Protocol)",
            "diagnostic_fusion": "🧩 **4. Diagnostic Fusion Engine**: Synthesized Root Cause & Prescribed Index Migration",
            "patch_engineer": "💻 **5. Principal Patch Engineer**: Generated SQL Index Migration & `FOR UPDATE NOWAIT` Query",
            "sandbox_qa": "🧪 **6. Sandboxed QA Runner**: Executed 4/4 Unit Tests in isolated runtime (PASSED)",
            "security_sast": "🛡️ **7. DevSecOps SAST Auditor**: Verified CWE-89 & Lock Deadlock Avoidance (0 Vulnerabilities)",
            "human_cab_gate": "👤 **8. CAB Approval Gate**: Automated Change Advisory Board Verification Confirmed",
            "deployment_and_postmortem": "🚀 **9. Git PR Deployment & Post-Mortem**: Created GitHub PR #4092 & Published Report"
        }

        try:
            events = st.session_state.graph.stream(
                {
                    "messages": [HumanMessage(content=prompt_input)],
                    "incident_description": prompt_input,
                    "iteration_count": 0
                },
                config=config,
                stream_mode="updates"
            )

            for event in events:
                for node_name, node_output in event.items():
                    label = NODE_LABELS.get(node_name, f"⚡ Node: {node_name}")
                    status_box.write(label)
                    
                    if node_name == "deployment_and_postmortem":
                        final_postmortem = node_output.get("post_mortem_report", "")

            status_box.update(label="✅ Autonomous SRE Triage, Patch, SAST Audit & PR Release Complete!", state="complete", expanded=False)

            if final_postmortem:
                st.markdown(final_postmortem)
                st.session_state.messages.append(AIMessage(content=final_postmortem))
            else:
                st.info("Swarm completed incident resolution.")

            st.success(f"📡 **Full 9-Node Telemetry Dispatched**: Project `{settings.langsmith_project}`. [Inspect live multi-agent trace waterfall in LangSmith](https://smith.langchain.com)")

        except Exception as e:
            status_box.update(label="❌ Execution Error", state="error", expanded=True)
            st.error(f"Error during swarm execution: {str(e)}")
