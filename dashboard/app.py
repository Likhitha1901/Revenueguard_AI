from pathlib import Path
import os
import json
import pandas as pd
import plotly.express as px
import streamlit as st

# RevenueGuard AI — Premium Gold financial investigation workspace
ROOT = Path(__file__).resolve().parent.parent
SCENARIO_FILE = ROOT / "data" / "synthetic_scenarios" / "controlled_leakage_scenarios.csv"
COMPARISON_FILE = ROOT / "reports" / "model_comparison.csv"
RECOVERY_FILE = ROOT / "data" / "processed" / "recovery_case_register.csv"

st.set_page_config(page_title="RevenueGuard AI | Financial Investigation", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# --------------------------- DESIGN SYSTEM ---------------------------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--paper:#111111;--surface:#1b1b1b;--surface2:#202020;--ink:#f5f0e5;--muted:#b8b0a1;--line:#39352d;--gold:#d6b46a;--bronze:#b98a45;--pale:#e5c77b;--sidebar:#0b0b0b;}
html,body,[class*="css"],[data-testid="stAppViewContainer"]{font-family:'Manrope',sans-serif}
.stApp{background:var(--paper);color:var(--ink)}
[data-testid="stHeader"]{background:rgba(17,17,17,.96)}
[data-testid="stAppViewContainer"]>.main{background:radial-gradient(circle at 90% 2%,rgba(214,180,106,.12),transparent 25%),var(--paper)}
.block-container{max-width:1580px;padding-top:1.6rem!important;padding-bottom:2.5rem!important}
[data-testid="stSidebar"]{background:var(--sidebar);border-right:1px solid #393329}
[data-testid="stSidebar"]>div:first-child{background:var(--sidebar)}
[data-testid="stSidebar"] *{color:#f5f0e5}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] .stCaption,[data-testid="stSidebar"] small{color:#b8b0a1!important}
[data-testid="stSidebar"] hr{border-color:#393329}
[data-testid="stSidebar"] [data-testid="stRadio"] label{color:#f5f0e5!important;font-weight:650;border-radius:8px;padding:8px 10px}
[data-testid="stSidebar"] [data-testid="stRadio"]>div{gap:.25rem}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){background:#27231b;border-left:4px solid var(--gold);padding-left:12px}
.brand-lockup{display:flex;align-items:center;gap:10px;color:#fff;font-size:21px;font-weight:800;letter-spacing:-.7px;white-space:nowrap}
.brand-mark{display:inline-flex;width:32px;height:32px;align-items:center;justify-content:center;background:linear-gradient(145deg,#e5c77b,#8f6b34);color:#17130c;border-radius:9px;font-size:20px;font-weight:900}
.eyebrow{color:var(--gold);text-transform:uppercase;letter-spacing:2px;font-size:10px;font-weight:800;margin-bottom:7px}
.hero-title{color:var(--ink);font-size:clamp(28px,3vw,40px);line-height:1.15;font-weight:800;letter-spacing:-1.5px;margin:0 0 8px;overflow-wrap:anywhere}
.hero-subtitle{color:var(--muted);font-size:14px;line-height:1.7;max-width:900px;margin-bottom:14px}
.hero-rule{height:4px;width:72px;background:linear-gradient(90deg,#8f6b34,#e5c77b);border-radius:99px;margin:14px 0 22px}
.section-heading{color:var(--ink);font-size:17px;font-weight:800;letter-spacing:-.3px;margin:12px 0}
.section-kicker{color:var(--muted);font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px}
.metric-card{background:linear-gradient(145deg,#202020,#171717);border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:13px;padding:17px;min-height:125px;box-shadow:0 10px 28px rgba(0,0,0,.2)}
.metric-card.bronze{border-top-color:var(--bronze)}.metric-card.pale{border-top-color:var(--pale)}.metric-card.muted{border-top-color:#8d7a58}
.metric-label{color:var(--muted);font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.6px;line-height:1.5;margin-bottom:11px;text-transform:uppercase}
.metric-value{color:var(--ink);font-size:clamp(20px,2vw,29px);font-weight:800;line-height:1.18;letter-spacing:-.7px;overflow-wrap:anywhere}
.metric-note{color:var(--muted);font-size:11px;margin-top:8px;line-height:1.5}
.pill{display:inline-block;border-radius:5px;background:#30291c;color:var(--gold);padding:4px 8px;font-family:'DM Mono',monospace;font-size:10px}
.research-note{background:#292219;border:1px solid #5d4930;border-left:4px solid var(--gold);border-radius:10px;padding:12px 14px;color:#e4d6b7;font-size:12px;line-height:1.65}
.sidebar-status{background:#191919;border:1px solid #393329;border-radius:10px;padding:12px;margin-top:8px}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--gold);margin-right:7px}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input{background:#191919!important;color:#f5f0e5!important;border-color:#514735!important;border-radius:8px!important}
[data-testid="stSelectbox"]>div>div,[data-testid="stMultiSelect"]>div>div{background:#191919!important;color:#f5f0e5!important;border-color:#514735!important;border-radius:8px!important}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;overflow:hidden}
.stButton>button,.stDownloadButton>button{background:linear-gradient(135deg,#e5c77b,#b98a45);color:#17130c;border:0;border-radius:8px;font-weight:800;padding:.55rem 1rem}
.stButton>button:hover,.stDownloadButton>button:hover{background:#f0d79b;color:#111}
[data-testid="stMetric"]{background:#1b1b1b;border:1px solid #39352d;border-radius:12px;padding:12px}
[data-testid="stChatMessage"]{background:#1b1b1b;border:1px solid #39352d;border-radius:12px}
hr{border-color:#39352d} ::selection{background:#8f6b34;color:#fff} footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

# --------------------------- DATA LOADING ---------------------------
@st.cache_data
def load_data(path, modified_time):
    data = pd.read_csv(path)
    for col in ["item_total", "freight_total", "expected_total", "payment_total", "simulated_payment", "simulated_difference", "is_synthetic_leakage"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    for col in ["order_purchase_timestamp", "order_approved_at", "order_delivered_customer_date"]:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors="coerce")
    return data

def money(value):
    return f"{float(value or 0):,.2f}"

def add_shortfall(frame):
    result = frame.copy()
    if "expected_total" in result and "simulated_payment" in result:
        result["simulated_shortfall"] = (result["expected_total"] - result["simulated_payment"]).clip(lower=0).fillna(0)
    else:
        result["simulated_shortfall"] = 0.0
    return result

def metric_card(label, value, note, accent=""):
    st.markdown(f'<div class="metric-card {accent}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

def load_register():
    RECOVERY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if RECOVERY_FILE.exists():
        try:
            return pd.read_csv(RECOVERY_FILE).fillna("")
        except Exception:
            pass
    return pd.DataFrame(columns=["order_id", "review_status", "finding", "verified_recoverable_amount", "recovered_amount", "owner", "notes"])

def save_register(register):
    RECOVERY_FILE.parent.mkdir(parents=True, exist_ok=True)
    register.to_csv(RECOVERY_FILE, index=False)

if not SCENARIO_FILE.exists():
    st.error(f"Scenario dataset not found. Expected file: {SCENARIO_FILE}")
    st.stop()
df = load_data(str(SCENARIO_FILE), SCENARIO_FILE.stat().st_mtime)
required = {"order_id", "scenario_type", "is_synthetic_leakage", "expected_total", "simulated_payment", "simulated_difference"}
missing = required - set(df.columns)
if missing:
    st.error(f"Dataset is missing columns: {sorted(missing)}")
    st.stop()
df = add_shortfall(df)

# --------------------------- SIDEBAR / NAVIGATION ---------------------------
pages = ["Executive Overview", "Leakage Investigation", "Recovery Management", "Model Performance", "AI Analyst"]
with st.sidebar:
    st.markdown('<div class="brand-lockup"><span class="brand-mark">◈</span> REVENUEGUARD</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#b8b0a1;font-size:10px;letter-spacing:2px;font-weight:700;margin:8px 0 22px 2px;">FINANCIAL INVESTIGATION INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="color:#b8b0a1;font-size:10px;letter-spacing:1.7px;font-weight:800;margin:12px 0 8px;">WORKSPACE</div>', unsafe_allow_html=True)
    page = st.radio("Navigation", pages, label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div style="color:#b8b0a1;font-size:10px;letter-spacing:1.7px;font-weight:800;margin:12px 0 8px;">DATA CONNECTION</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-status"><div style="font-weight:750;font-size:13px;"><span class="status-dot"></span>Olist e-commerce</div><div style="color:#b8b0a1;font-size:11px;margin-top:7px;">{len(df):,} scenario records loaded</div><div style="color:#b8b0a1;font-size:10px;margin-top:4px;">CSV · Local research dataset</div></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div style="background:#292219;border:1px solid #5d4930;border-radius:10px;padding:12px;color:#e4d6b7;font-size:11px;line-height:1.65;"><b style="color:#e5c77b;">EXPERIMENTAL MODE</b><br>Leakage labels are simulated scenarios, not confirmed business losses.</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div style="color:#8d8679;font-size:10px;line-height:1.8;">DETECTION → INVESTIGATION → RECOVERY<br>REVENUEGUARD AI · RESEARCH BUILD</div>', unsafe_allow_html=True)

# --------------------------- SHARED HEADER + FILTERS ---------------------------
st.markdown('<div class="eyebrow">REVENUE ASSURANCE / RESEARCH CONSOLE</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Revenue leakage,<br>made visible.</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">A financial investigation workspace connecting anomaly detection, case review, recovery tracking and model evidence.</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-rule"></div>', unsafe_allow_html=True)

scenario_options = sorted(df["scenario_type"].dropna().astype(str).unique().tolist())
with st.expander("Global filters", expanded=(page in ["Executive Overview", "Leakage Investigation"])):
    f1, f2, f3 = st.columns([1.2, 1, 1])
    with f1:
        selected_scenarios = st.multiselect("Leakage / scenario type", scenario_options, default=scenario_options)
    with f2:
        search_id = st.text_input("Order ID contains", placeholder="Enter full or partial order ID")
    with f3:
        min_shortfall_global = st.number_input("Minimum simulated amount", min_value=0.0, value=0.0, step=10.0)
filtered = df[df["scenario_type"].astype(str).isin(selected_scenarios)].copy()
if search_id.strip():
    filtered = filtered[filtered["order_id"].astype(str).str.contains(search_id.strip(), case=False, na=False)]
filtered = add_shortfall(filtered)
filtered = filtered[filtered["simulated_shortfall"] >= min_shortfall_global]
flagged = filtered[filtered["is_synthetic_leakage"] == 1].copy()

# --------------------------- PAGE 1: EXECUTIVE OVERVIEW ---------------------------
if page == "Executive Overview":
    st.markdown('<div class="section-heading">01 / Executive overview</div>', unsafe_allow_html=True)
    potential = float(flagged["simulated_shortfall"].sum())
    baseline_count = int((filtered["is_synthetic_leakage"] == 0).sum())
    # Avoid implying these are actual verified losses or recoveries.
    cards = [("TRANSACTIONS ANALYZED", f"{len(filtered):,}", "Orders in current filter", ""), ("SUSPECTED SCENARIOS", f"{len(flagged):,}", "Synthetic candidates for review", "bronze"), ("VERIFIED LEAKAGE", "Not yet verified", "Requires source-record investigation", "muted"), ("SIMULATED SHORTFALL", money(potential), "Experimental monetary units", "pale")]
    cols = st.columns(4)
    for col, (label, value, note, accent) in zip(cols, cards):
        with col:
            metric_card(label, value, note, accent)
    st.write("")
    left, right = st.columns([1, 1.2], gap="large")
    with left:
        st.markdown('<div class="section-heading">Scenario composition</div>', unsafe_allow_html=True)
        counts = filtered["scenario_type"].value_counts().rename_axis("Scenario").reset_index(name="Orders")
        if not counts.empty:
            fig = px.pie(counts, names="Scenario", values="Orders", hole=.68, color_discrete_sequence=["#D6B46A", "#B98A45", "#E5C77B", "#8D7A58", "#F0D79B"])
            fig.update_traces(textposition="inside", textinfo="percent", marker=dict(line=dict(color="#1B1B1B", width=3)))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Manrope", color="#E9E0CD"), margin=dict(t=10,b=10,l=8,r=8), legend=dict(font=dict(size=11,color="#E9E0CD")))
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("No records match the selected filters.")
    with right:
        st.markdown('<div class="section-heading">Simulated amount by scenario</div>', unsafe_allow_html=True)
        amounts = filtered.groupby("scenario_type", as_index=False)["simulated_shortfall"].sum().sort_values("simulated_shortfall")
        if not amounts.empty:
            fig = px.bar(amounts, x="simulated_shortfall", y="scenario_type", orientation="h", color="scenario_type", color_discrete_sequence=["#D6B46A", "#B98A45", "#E5C77B", "#8D7A58", "#F0D79B"], labels={"simulated_shortfall":"Simulated shortfall","scenario_type":"Scenario"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="Manrope",color="#E9E0CD"),showlegend=False,margin=dict(t=10,b=10,l=5,r=10),xaxis=dict(showgrid=True,gridcolor="#39352D",zeroline=False),yaxis=dict(showgrid=False))
            st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="section-heading">Audit sample</div>', unsafe_allow_html=True)
    show_cols = [c for c in ["order_id","scenario_type","expected_total","simulated_payment","simulated_shortfall","simulated_difference","is_synthetic_leakage"] if c in filtered.columns]
    st.dataframe(filtered[show_cols].head(15), use_container_width=True, hide_index=True)
    st.markdown('<div class="research-note"><b>Evidence boundary:</b> simulated shortfall is not verified leakage, actual recovery, or confirmed financial impact. Validate against source order, payment, refund and settlement records before operational conclusions.</div>', unsafe_allow_html=True)

# --------------------------- PAGE 2: LEAKAGE INVESTIGATION ---------------------------
elif page == "Leakage Investigation":
    st.markdown('<div class="section-heading">02 / Leakage investigation</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Filter candidates, inspect the underlying order-level evidence available in the dataset, and export a focused investigation queue.</div>', unsafe_allow_html=True)
    q = flagged.copy()
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("OPEN CANDIDATES", f"{len(q):,}", "Synthetic label = positive", "bronze")
    with c2: metric_card("SIMULATED SHORTFALL", money(q["simulated_shortfall"].sum()), "Not yet verified", "pale")
    with c3: metric_card("AVERAGE PER CASE", money(q["simulated_shortfall"].mean() if len(q) else 0), "Across filtered candidates", "")
    with c4: metric_card("SCENARIO TYPES", f"{q['scenario_type'].nunique() if len(q) else 0}", "Present in queue", "muted")
    f1,f2,f3 = st.columns(3)
    with f1:
        sort_mode = st.selectbox("Sort candidates", ["Largest amount first", "Smallest amount first", "Order ID"])
    with f2:
        scenario_focus = st.selectbox("Focused scenario", ["All selected"] + sorted(q["scenario_type"].dropna().astype(str).unique().tolist()))
    with f3:
        top_n = st.selectbox("Rows to display", [50,100,250,500,1000], index=1)
    if scenario_focus != "All selected": q = q[q["scenario_type"].astype(str) == scenario_focus]
    if sort_mode == "Largest amount first": q = q.sort_values("simulated_shortfall", ascending=False)
    elif sort_mode == "Smallest amount first": q = q.sort_values("simulated_shortfall", ascending=True)
    else: q = q.sort_values("order_id")
    display = [c for c in ["order_id","scenario_type","expected_total","simulated_payment","simulated_shortfall","simulated_difference","order_status","seller_id","order_purchase_timestamp"] if c in q.columns]
    st.dataframe(q[display].head(int(top_n)), use_container_width=True, hide_index=True, height=430)
    st.download_button("Export investigation queue (.csv)", q.to_csv(index=False).encode("utf-8"), "revenueguard_investigation_queue.csv", "text/csv")
    st.markdown('<div class="research-note"><b>Investigation checklist:</b> compare the order total with payment/settlement records; inspect order status; account for cancellations, refunds, discounts, freight and settlement timing; document the evidence before marking a case verified.</div>', unsafe_allow_html=True)
    order_choices = q["order_id"].astype(str).head(500).tolist()
    if order_choices:
        st.markdown('<div class="section-heading">Order evidence panel</div>', unsafe_allow_html=True)
        chosen = st.selectbox("Inspect an order", order_choices)
        record = q[q["order_id"].astype(str) == chosen].head(1)
        if not record.empty:
            a,b = st.columns(2)
            with a: st.json({str(k): (None if pd.isna(v) else (v.isoformat() if hasattr(v,"isoformat") else v.item() if hasattr(v,"item") else v)) for k,v in record.iloc[0].to_dict().items()})
            with b: st.info("This panel displays only fields present in the local dataset. It does not connect to a live payment gateway or accounting system.")
    st.markdown('<div class="section-heading">Record investigation decision</div>', unsafe_allow_html=True)
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(0,str(project_root))
    from src.investigation_store import( save_investigation, get_investigation)
    existing = get_investigation(chosen) or {}
    with st.form("investigation_decision_form"):
        review_status= st.selectbox("Investigation status", ["Under Review", "Verified Leakage", "False Positive", "Resolved"], index=( ["Under Review", "Verified Leakage", "False Positive", "Resolved"].index(existing.get("status","Under Review"))))
        confirmed_amount = st.number_input("Confirmed leakage amount", min_value=0.0, value=float(existing.get("confirmed_amount",0)), step=10.0)
        evidence_notes = st.text_area("Investigation and Evidence notes", value=str(existing.get("evidence_notes","")), placeholder="Record source system, payment reference, refund checks, timestamps and conclusion…")
        submitted = st.form_submit_button("Save investigation record",use_container_width=True)
    if submitted:
        try:
            save_investigation(chosen, review_status, confirmed_amount, evidence_notes)
            st.success(f"Investigation decision saved for order {chosen}.")
        except (ValueError,TypeError) as exc:
            st.error(f"Error saving investigation record: {exc}")
# --------------------------- PAGE 3: RECOVERY MANAGEMENT ---------------------------
elif page == "Recovery Management":

    st.markdown(
        '<div class="section-heading">03 / Recovery management</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-subtitle">Track investigation outcomes, '
        'verified recoverable amounts and confirmed cash recovery.</div>',
        unsafe_allow_html=True
    )

    register = load_register()

# Load Experiment 2 financial case classifications
    try:
        financial_cases = pd.read_csv(
            "reports/financial_case_classification.csv"
        )

        # Exclude normal transactions
        candidates = financial_cases[
            financial_cases["financial_case_type"] != "Normal"
        ].copy()

    except FileNotFoundError:
        st.warning(
            "Financial classification file not found. "
            "Using the existing investigation candidates."
        )
        candidates = flagged.copy()

# Remove cases that are already registered
    if not register.empty:
        tracked_ids = set(register["order_id"].astype(str))

        candidates = candidates[
            ~candidates["order_id"].astype(str).isin(tracked_ids)
        ]
    # Recovery investigation filters
    filtered_candidates = candidates.copy()

    if not filtered_candidates.empty:
        f1, f2 = st.columns(2)

        with f1:
            case_types = ["All"] + sorted(
                filtered_candidates["financial_case_type"].dropna().unique().tolist()
            )

            selected_type = st.selectbox(
                "Filter by case type",
                case_types
            )

        with f2:
            priorities = ["All", "High", "Medium", "Low"]

            selected_priority = st.selectbox(
                "Filter by priority",
                priorities
            )

        if selected_type != "All":
            filtered_candidates = filtered_candidates[
                filtered_candidates["financial_case_type"] == selected_type
            ]

        if selected_priority != "All":
            filtered_candidates = filtered_candidates[
                filtered_candidates["investigation_priority"] == selected_priority
            ]
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("TRACKED CASES", f"{len(register):,}",
                    "Saved recovery records", "")

    with c2:
        verified = pd.to_numeric(
            register.get("verified_recoverable_amount",
                        pd.Series(dtype=float)),
            errors="coerce"
        ).fillna(0).sum()

        metric_card("VERIFIED RECOVERABLE", money(verified),
                    "Evidence-based amount", "pale")

    with c3:
        recovered = pd.to_numeric(
            register.get("recovered_amount",
                        pd.Series(dtype=float)),
            errors="coerce"
        ).fillna(0).sum()

        metric_card("RECOVERED AMOUNT", money(recovered),
                    "Confirmed cash recovered", "bronze")

    with c4:
        metric_card("NEW CANDIDATES", f"{len(candidates):,}",
                    "Not yet registered", "muted")

    st.markdown(
        '<div class="section-heading">Create / update recovery case</div>',
        unsafe_allow_html=True
    )

    if candidates.empty and register.empty:
        st.info("No new candidates or saved recovery cases Available.")

    else:
        # Show High priority cases first
        priority_order = {
            "High": 0,
            "Medium": 1,
            "Low": 2
        }

        filtered_candidates = filtered_candidates.copy()

        if not filtered_candidates.empty:
            filtered_candidates["_priority_order"] = (
                filtered_candidates["investigation_priority"]
                .map(priority_order)
                .fillna(3)
            )

            filtered_candidates = filtered_candidates.sort_values(
                "_priority_order"
            )

        candidate_ids = (
            filtered_candidates["order_id"].astype(str).tolist()
        )

        registered_ids = (
            register["order_id"].astype(str).tolist()
            if not register.empty else []
        )

        case_ids = list(dict.fromkeys(candidate_ids + registered_ids))

        case_labels = {}

# Labels for new filtered candidates
        for _, row in filtered_candidates.iterrows():
            order_id = str(row["order_id"])

            case_labels[order_id] = (
                f'{row["investigation_priority"]} Priority | '
                f'{row["financial_case_type"]} | {order_id}'
            )

        selected_case = st.selectbox(
            "Select order to register",
            case_ids,
            format_func=lambda x: case_labels.get(
                str(x), f"Registered Case | {x}"
            )
        )
        # Display Experiment 2 classification details
        selected_candidate = financial_cases[
            financial_cases["order_id"].astype(str) == selected_case
        ] if "financial_cases" in locals() else pd.DataFrame()

        if not selected_candidate.empty:
            case_info = selected_candidate.iloc[0]

            st.markdown("#### Financial investigation insights")

            info1, info2 = st.columns(2)

            with info1:
                st.metric(
                    "Case type",
                    case_info["financial_case_type"]
                )

            with info2:
                st.metric(
                    "Investigation priority",
                    case_info["investigation_priority"]
                )
            st.markdown("#### Financial evidence")

            expected_amount = pd.to_numeric(
                pd.Series([case_info.get("item_plus_freight", 0)]),
                errors="coerce"
            ).fillna(0).iloc[0]

            actual_payment = pd.to_numeric(
                pd.Series([case_info.get("payment_total", 0)]),
                errors="coerce"
            ).fillna(0).iloc[0]

            payment_difference = pd.to_numeric(
                pd.Series([case_info.get("payment_difference", 0)]),
                errors="coerce"
            ).fillna(0).iloc[0]

            e1, e2, e3 = st.columns(3)

            with e1:
                st.metric("Expected amount", money(expected_amount))

            with e2:
                st.metric("Actual payment", money(actual_payment))

            with e3:
                st.metric(
                    "Payment difference",
                    money(payment_difference),
                    delta="Overpayment" if payment_difference > 1
                    else "Underpayment" if payment_difference < -1
                    else "Within tolerance",
                    delta_color="off"
                )
            st.markdown("#### Investigation reason")

            case_type = case_info["financial_case_type"]

            if case_type == "Potential Underpayment":
                reason = (
                    f"Payment is lower than the expected amount by "
                    f"{money(abs(payment_difference))}. "
                    "Review payment records, discounts, refunds and "
                    "other adjustments."
                )

            elif case_type == "Potential Overpayment":
                reason = (
                    f"Payment exceeds the expected amount by "
                    f"{money(abs(payment_difference))}. "
                    "Investigate additional charges, payment adjustments "
                    "and possible reconciliation errors."
                )

            elif case_type == "Behavioural Anomaly":
                reason = (
                    "The transaction was flagged by the Isolation Forest "
                    "model because of an unusual financial or transaction "
                    "pattern. The payment difference is within the "
                    "₹1 tolerance. Further investigation is required."
                )

            else:
                reason = "Review the transaction and supporting financial records."

            st.info(reason)
        existing = register[
            register["order_id"].astype(str) == selected_case
        ]

        old = existing.iloc[0].to_dict() if not existing.empty else {}

        statuses = [
            "New", "Under investigation", "Awaiting evidence",
            "Verified leakage", "No leakage found",
            "Recovery in progress", "Recovered", "Closed"
        ]

        findings = [
            "Not reviewed", "Payment mismatch confirmed",
            "Freight under-recovery confirmed",
            "Missing payment confirmed",
            "Refund / cancellation explained",
            "No discrepancy", "Other"
        ]

        with st.form("recovery_case_form"):

            s1, s2 = st.columns(2)

            with s1:
                status = st.selectbox(
                    "Review status",
                    statuses,
                    index=statuses.index(old["review_status"])
                    if old.get("review_status") in statuses else 0
                )

            with s2:
                finding = st.selectbox(
                    "Investigation finding",
                    findings,
                    index=findings.index(old["finding"])
                    if old.get("finding") in findings else 0
                )

            owner = st.text_input(
                "Assigned investigator",
                value=str(old.get("owner", ""))
            )

            a1, a2 = st.columns(2)

            with a1:
                verified_amount = st.number_input(
                    "Verified recoverable amount",
                    min_value=0.0,
                    value=float(pd.to_numeric(
                        pd.Series([old.get("verified_recoverable_amount", 0)]),
                        errors="coerce"
                    ).fillna(0).iloc[0]),
                    step=10.0
                )

            with a2:
                recovered_amount = st.number_input(
                    "Amount recovered",
                    min_value=0.0,
                    value=float(pd.to_numeric(
                        pd.Series([old.get("recovered_amount", 0)]),
                        errors="coerce"
                    ).fillna(0).iloc[0]),
                    step=10.0
                )

            notes = st.text_area(
                "Evidence / investigation notes",
                value=str(old.get("notes", ""))
            )

            submitted = st.form_submit_button("Save recovery case")

        if submitted:

            if recovered_amount > verified_amount:
                st.error(
                    "Recovered amount cannot exceed verified recoverable amount."
                )

            else:
                row = {
                    "order_id": selected_case,
                    "review_status": status,
                    "finding": finding,
                    "verified_recoverable_amount": verified_amount,
                    "recovered_amount": recovered_amount,
                    "owner": owner.strip(),
                    "notes": notes.strip()
                }

                if existing.empty:
                    register = pd.concat(
                        [register, pd.DataFrame([row])],
                        ignore_index=True
                    )
                else:
                    for key, value in row.items():
                        register.loc[
                            register["order_id"].astype(str) == selected_case,
                            key
                        ] = value

                save_register(register)

                st.success("Recovery case saved successfully!")
                st.rerun()

    st.markdown(
        '<div class="section-heading">Recovery case register</div>',
        unsafe_allow_html=True
    )

    if register.empty:
        st.info("No recovery cases registered yet.")

    else:
        st.dataframe(
            register,
            use_container_width=True,
            hide_index=True,
            height=350
        )

        st.download_button(
            "Export recovery register (.csv)",
            register.to_csv(index=False).encode("utf-8"),
            "revenueguard_recovery_register.csv",
            "text/csv"
        )

    st.markdown(
        '<div class="research-note"><b>Governance:</b> '
        'Only record verified recoverable amounts after checking '
        'financial evidence. Recovered amount means confirmed collection, '
        'not a model estimate.</div>',
        unsafe_allow_html=True
    )
# --------------------------- PAGE 4: MODEL PERFORMANCE ---------------------------
elif page == "Model Performance":
    st.markdown('<div class="section-heading">04 / Model performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Compare the current rule-based baseline and Random Forest results, inspect the metrics report and document the limitations of synthetic evaluation.</div>', unsafe_allow_html=True)
    if COMPARISON_FILE.exists():
        comparison = pd.read_csv(COMPARISON_FILE)
        needed = {"method", "precision", "recall", "f1_score"}
        if needed.issubset(comparison.columns):
            for col in ["precision", "recall", "f1_score"]: comparison[col] = pd.to_numeric(comparison[col], errors="coerce")
            wide = comparison.melt(id_vars="method", value_vars=["precision","recall","f1_score"], var_name="metric", value_name="score")
            fig = px.bar(wide, x="metric", y="score", color="method", barmode="group", color_discrete_sequence=["#B98A45","#D6B46A"], labels={"metric":"Evaluation metric","score":"Score","method":"Method"}, text_auto=".3f")
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="Manrope",color="#E9E0CD"),margin=dict(t=35,b=10,l=5,r=15),yaxis=dict(range=[0,1.12],gridcolor="#39352D",title="Score"),xaxis=dict(showgrid=False),legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('<div class="section-heading">Metric detail</div>', unsafe_allow_html=True)
            st.dataframe(comparison, use_container_width=True, hide_index=True)
            st.download_button("Download model comparison (.csv)", comparison.to_csv(index=False).encode("utf-8"), "model_comparison.csv", "text/csv")
        else:
            st.error("model_comparison.csv must contain method, precision, recall and f1_score columns.")
            st.dataframe(comparison, use_container_width=True, hide_index=True)
    else:
        st.warning("Model comparison report not found. Run `python src\\compared_models.py` from the project root, then refresh this page.")
    metrics_file = ROOT / "reports" / "initial_model_metrics.json"
    if metrics_file.exists():
        st.markdown('<div class="section-heading">First model report</div>', unsafe_allow_html=True)
        try: st.json(json.loads(metrics_file.read_text(encoding="utf-8")))
        except Exception: st.caption("Initial model metrics file exists but could not be parsed as JSON.")
    st.markdown('<div class="research-note"><b>Research limitation:</b> synthetic features may reveal the label-generation logic. High scores are not evidence of production readiness. Next evaluate temporal/group splits, remove label-defining shortcuts, measure precision-recall under realistic class imbalance, and validate with independently constructed scenarios.</div>', unsafe_allow_html=True)

# --------------------------- AI ANALYST ---------------------------
else:
    st.markdown('<div class="section-heading">05 / AI analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Ask questions about the current filtered portfolio, investigation candidates, model comparison and recovery register. Answers are grounded in the local project data; no live payment or accounting system is connected.</div>', unsafe_allow_html=True)
    register = load_register()
    # Load Experiment 2 financial classifications
    try:
        financial_cases = pd.read_csv(
            "reports/financial_case_classification.csv"
        )
    except FileNotFoundError:
        financial_cases = pd.DataFrame()
    total_shortfall = float(flagged["simulated_shortfall"].sum())
    scenario_summary = flagged.groupby("scenario_type")["simulated_shortfall"].agg(["count","sum"]).sort_values("sum", ascending=False) if len(flagged) else pd.DataFrame()
    suggestions = [
        "Summarize the current leakage candidates", 
        "Which scenario has the largest simulated shortfall?",
        "What are the Experiment 2 anomaly detection results?",
        "Summarize potential underpayments and overpayments",
        "What should an investigator verify before confirming leakage?",
        "Explain the current model comparison and its limitations",
        "Summarize recovery progress"]
    selected_question = st.selectbox("Suggested investigation question", ["Choose a question…"] + suggestions)
    question = st.text_input("Ask RevenueGuard Analyst", value="" if selected_question == "Choose a question…" else selected_question, placeholder="e.g., What are the highest-priority cases and why?")

    def analyst_answer(q):
        text = q.lower()
        lines = []
        lines.append(f"Current filter contains **{len(filtered):,} records**, including **{len(flagged):,} synthetic positive candidates**.")
        lines.append(f"The summed simulated shortfall is **{money(total_shortfall)}** monetary units. This is a simulation estimate, not verified leakage or actual recoverable cash.")
        if "scenario" in text or "largest" in text or "type" in text:
            if not scenario_summary.empty:
                name = str(scenario_summary.index[0]); amount = float(scenario_summary.iloc[0]["sum"]); count = int(scenario_summary.iloc[0]["count"])
                lines.append(f"The largest current scenario by summed simulated shortfall is **{name}** ({money(amount)} across {count:,} flagged records).")
                lines.append("Use the investigation queue to inspect individual order IDs and validate against payment, refund, freight, discount and status evidence.")
            else: lines.append("No positive candidates match the current filters.")
        if "verify" in text or "investigat" in text or "priority" in text or "before" in text:
            lines.append("Recommended review sequence: (1) match order ID and item totals, (2) reconcile payment/settlement references, (3) check cancellations and refunds, (4) include freight, discount and tax rules where available, (5) review timing differences, and (6) record the evidence and reviewer before setting a verified outcome.")
        if any(k in text for k in [
            "experiment 2", "anomaly", "underpayment", "overpayment"
        ]):
            if not financial_cases.empty:

                counts = financial_cases[
                    "financial_case_type"
                ].value_counts()

                lines.append("**Experiment 2 — Financial Anomaly Analysis**")

                for case_type, count in counts.items():
                    lines.append(
                        f"- {case_type}: **{count:,} transactions**"
                    )

                lines.append(
                    "The system uses Isolation Forest to prioritize "
                    "unusual financial transactions for investigation."
                )

                lines.append(
                    "These classifications are not confirmed leakage. "
                    "Financial evidence and business explanations must "
                    "be checked before confirming a recovery."
                )

            else:
                lines.append(
                    "Experiment 2 classification report is unavailable."
                )
        if "model" in text or "performance" in text or "precision" in text or "recall" in text or "limitation" in text:
            if COMPARISON_FILE.exists():
                try:
                    comp = pd.read_csv(COMPARISON_FILE)
                    if {"method","precision","recall","f1_score"}.issubset(comp.columns):
                        lines.append("Current model comparison report:\n" + comp[["method","precision","recall","f1_score"]].to_markdown(index=False))
                except Exception: pass
            lines.append("Important: the positive labels are synthetically generated. Possible feature/label shortcuts can inflate metrics; use group or time-based splits and an independently designed validation set before making generalisation claims.")
        if "recover" in text or "progress" in text or "case" in text:
            if register.empty:
                lines.append("No recovery cases have been saved in the register yet. Use Recovery Management to assign a status and record investigation evidence.")
            else:
                statuses = register.get("review_status", pd.Series(dtype=str)).astype(str).value_counts().to_dict()
                verified = pd.to_numeric(register.get("verified_recoverable_amount", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
                recovered = pd.to_numeric(register.get("recovered_amount", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
                lines.append(f"The register contains **{len(register):,} cases**. Status counts: `{statuses}`. Verified recoverable amount entered: **{money(verified)}**; recovered amount entered: **{money(recovered)}**.")
        if not any(k in text for k in ["scenario","largest","type","verify","investigat","priority","before","model","performance","precision","recall","limitation","recover","progress","case"]):
            lines.append("I can summarize current candidates, compare scenario amounts, explain model metrics, outline investigation checks, or report the saved recovery register. Choose one of the suggested questions for a focused response.")
        return "\n\n".join(lines)

    if "analyst_history" not in st.session_state: st.session_state.analyst_history = []
    for item in st.session_state.analyst_history:
        with st.chat_message(item["role"]): st.markdown(item["content"])
    if st.button("Analyze question", type="primary") and question.strip():
        answer = analyst_answer(question.strip())
        st.session_state.analyst_history.append({"role":"user","content":question.strip()})
        st.session_state.analyst_history.append({"role":"assistant","content":answer})
        st.rerun()
    if st.button("Clear analyst conversation"):
        st.session_state.analyst_history = []
        st.rerun()
    st.markdown('<div class="research-note"><b>Analyst scope:</b> this built-in analyst generates data-grounded summaries from the local CSV reports and case register. It is not an external LLM connection and does not verify financial transactions. An LLM provider can be integrated later with approved credentials and additional privacy controls.</div>', unsafe_allow_html=True)
