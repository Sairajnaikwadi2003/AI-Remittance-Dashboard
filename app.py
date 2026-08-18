import streamlit as st
from datetime import datetime

# =========================================================
# PAGE / GLOBAL CONFIG
# =========================================================
st.set_page_config(
    page_title="Money2India Smart",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# MOCK DATA — deliberately deterministic for the prototype
# =========================================================
TRANSFERS = [
    {
        "beneficiary": "Mom",
        "amount": "₹50,000",
        "amount_num": 50000,
        "date": "12 Aug 2026",
        "status": "Processing",
        "tracking": "M2I-839274",
        "purpose": "Family maintenance",
        "initials": "M",
    },
    {
        "beneficiary": "Dad",
        "amount": "₹40,000",
        "amount_num": 40000,
        "date": "31 Jul 2026",
        "status": "Completed",
        "tracking": "M2I-838721",
        "purpose": "Family maintenance",
        "initials": "D",
    },
    {
        "beneficiary": "ABC Supplies",
        "amount": "₹1,20,000",
        "amount_num": 120000,
        "date": "18 Jul 2026",
        "status": "Completed",
        "tracking": "M2I-836904",
        "purpose": "Business payment",
        "initials": "A",
    },
    {
        "beneficiary": "Mom",
        "amount": "₹50,000",
        "amount_num": 50000,
        "date": "12 Jun 2026",
        "status": "Completed",
        "tracking": "M2I-833110",
        "purpose": "Family maintenance",
        "initials": "M",
    },
    {
        "beneficiary": "Dad",
        "amount": "₹40,000",
        "amount_num": 40000,
        "date": "30 May 2026",
        "status": "Completed",
        "tracking": "M2I-831002",
        "purpose": "Family maintenance",
        "initials": "D",
    },
]

# =========================================================
# MOCK M2I TOOLS
# =========================================================
def get_recent_transfers():
    return TRANSFERS[:5]


def get_transfer_status(tracking_id):
    return next(
        (transfer for transfer in TRANSFERS if transfer["tracking"] == tracking_id),
        None,
    )


def get_annual_remittance_summary():
    return {"total": "₹8.42L", "transfers": 11}


def get_usual_transfer_pattern():
    return {"beneficiary": "Mom", "amount": "₹50,000", "purpose": "Family maintenance"}


def get_declaration_status(name):
    return {"beneficiary": name, "valid_until": "31 Mar 2027"}


def prepare_transfer():
    return get_usual_transfer_pattern()


# =========================================================
# DETERMINISTIC INTENT ROUTER
# =========================================================
def route_prompt(prompt):
    query = prompt.lower().strip()

    if not query:
        return "unsupported", None

    if any(
        phrase in query
        for phrase in (
            "exact usd",
            "today's rate",
            "today rate",
            "live fx",
            "live rate",
            "live exchange",
        )
    ):
        return "fx_guardrail", None

    if any(
        phrase in query
        for phrase in (
            "transfer ₹5 lakh",
            "transfer 5 lakh",
            "send ₹5 lakh",
            "send 5 lakh",
            "transfer now",
        )
    ):
        return "execution_guardrail", None

    if "eligible" in query and any(
        word in query for word in ("rbi", "regulatory", "rules", "amount")
    ):
        return "compliance_guardrail", None

    if "pending" in query or (
        "latest transfer" in query and "why" in query
    ):
        return "pending", TRANSFERS[0]

    if any(
        phrase in query
        for phrase in ("how much", "sent this year", "this year")
    ):
        return "annual", get_annual_remittance_summary()

    if any(
        phrase in query
        for phrase in (
            "recent transfers",
            "last 5",
            "last five",
            "transfer history",
            "show recent",
        )
    ):
        return "recent", get_recent_transfers()

    if (
        "usual monthly" in query
        or "monthly transfer" in query
        or ("prepare" in query and "transfer" in query)
    ):
        return "prepare", prepare_transfer()

    if "declaration" in query or "document" in query:
        return "declaration", get_declaration_status("Mom")

    if "business" in query and ("lakh" in query or "1 lakh" in query):
        data = [
            t for t in TRANSFERS
            if t["purpose"] == "Business payment" and t["amount_num"] > 100000
        ]
        return "business", data

    if "family" in query:
        data = [t for t in TRANSFERS if t["purpose"] == "Family maintenance"]
        return "family", data

    if "track" in query:
        return "track", TRANSFERS[0]

    return "unsupported", None


# =========================================================
# DESIGN SYSTEM
# =========================================================
st.markdown(
    """
<style>
/*
 M2I DESIGN SYSTEM
 ------------------------------------------------------------
 Palette
   Brand:       #B32635  (ICICI/M2I-inspired red)
   Brand dark:  #8E1C29
   Ink:         #17202B  (primary text)
   Ink 2:       #3D4652  (secondary text)
   Muted:       #687381
   Canvas:      #F5F6F8
   Surface:     #FFFFFF
   Surface 2:   #FBFCFD
   Border:      #D9DEE5
   Success:     #167A5B
   Warning:     #9A640E
   Danger:      #B32635

 Typography
   Display:     32px / 700
   H1:          28px / 700
   H2:          20px / 700
   H3:          15px / 700
   Body:        14px / 400
   Small:       12px / 500
   Caption:     11px / 500

 Layout
   4px base spacing
   12px standard radius
   16px major surface radius
   1px borders
   shadows only on elevated surfaces
*/

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --brand: #B32635;
    --brand-dark: #8E1C29;
    --brand-hover: #9F202E;
    --brand-50: #FFF4F5;
    --brand-100: #FBE5E8;

    --ink: #17202B;
    --ink-2: #3D4652;
    --muted: #687381;
    --muted-2: #8A94A1;

    --canvas: #F5F6F8;
    --surface: #FFFFFF;
    --surface-2: #FBFCFD;

    --border: #D9DEE5;
    --border-strong: #C7CDD5;

    --success: #167A5B;
    --success-bg: #EAF7F2;
    --warning: #9A640E;
    --warning-bg: #FFF6E5;
    --danger: #B32635;
    --danger-bg: #FFF0F2;

    --radius-sm: 8px;
    --radius: 12px;
    --radius-lg: 16px;

    --shadow-sm: 0 1px 3px rgba(23,32,43,.06);
    --shadow-md: 0 8px 24px rgba(23,32,43,.08);
}

/* ================= APP FOUNDATION ================= */

html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", Arial, sans-serif !important;
    color: var(--ink) !important;
}

.stApp {
    background: var(--canvas) !important;
}

.block-container {
    max-width: 1440px !important;
    padding: 28px 42px 64px !important;
}

/* Remove Streamlit development chrome */
#MainMenu, footer {
    visibility: hidden !important;
}
header {
    background: transparent !important;
}

/* ================= SIDEBAR ================= */

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 20px 14px !important;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 4px 8px 22px;
}

.sidebar-logo {
    width: 38px;
    height: 38px;
    display: grid;
    place-items: center;
    border-radius: 10px;
    background: var(--brand);
    color: #FFFFFF !important;
    font-size: 19px;
    font-weight: 700;
}

.sidebar-brand-name {
    color: var(--ink) !important;
    font-size: 15px;
    line-height: 1.2;
    font-weight: 700;
}

.sidebar-brand-sub {
    color: var(--muted-2) !important;
    font-size: 10px;
    margin-top: 3px;
}

.side-section {
    color: var(--muted-2) !important;
    font-size: 10px;
    letter-spacing: .08em;
    text-transform: uppercase;
    font-weight: 700;
    padding: 14px 9px 7px;
}

/* Sidebar buttons: readable, no invisible text */
[data-testid="stSidebar"] .stButton {
    margin: 2px 0 !important;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    min-height: 42px !important;
    padding: 9px 12px !important;
    border: 1px solid transparent !important;
    border-radius: 9px !important;
    background: transparent !important;
    color: var(--ink-2) !important;
    text-align: left !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--brand-50) !important;
    color: var(--brand) !important;
    border-color: var(--brand-100) !important;
}

.side-footer {
    margin-top: 80px;
    padding: 14px 10px;
    border-top: 1px solid var(--border);
    color: var(--muted-2) !important;
    font-size: 10px;
    line-height: 1.6;
}

/* ================= TOP BAR ================= */

.top-header {
    height: 52px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 0 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 34px;
}

.top-title {
    color: var(--ink) !important;
    font-size: 15px;
    font-weight: 700;
}

.top-subtitle {
    color: var(--muted) !important;
    font-size: 11px;
    margin-top: 3px;
}

.profile {
    display: flex;
    align-items: center;
    gap: 9px;
    color: var(--ink-2) !important;
    font-size: 12px;
    font-weight: 500;
}

.profile-avatar {
    width: 32px;
    height: 32px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: var(--brand-100);
    color: var(--brand) !important;
    font-weight: 700;
}

/* ================= TYPOGRAPHY ================= */

.eyebrow {
    color: var(--brand) !important;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .09em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

h1 {
    color: var(--ink) !important;
    font-size: 30px !important;
    line-height: 1.15 !important;
    letter-spacing: -.035em !important;
    font-weight: 700 !important;
    margin: 0 !important;
}

h2 {
    color: var(--ink) !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}

h3 {
    color: var(--ink) !important;
    font-size: 15px !important;
    font-weight: 700 !important;
}

p, label, .stMarkdown {
    color: var(--ink-2);
}

.hero-copy {
    color: var(--muted) !important;
    font-size: 14px;
    line-height: 1.55;
    margin-top: 8px;
}

/* ================= SECTION HEADERS ================= */

.section-label {
    margin: 30px 0 12px;
    color: var(--ink) !important;
    font-size: 15px;
    font-weight: 700;
}

.section-meta {
    color: var(--muted-2) !important;
    font-size: 11px;
    font-weight: 500;
    margin-left: 5px;
}

/* ================= PRIMARY AGENT SURFACE ================= */

.agent-shell {
    margin-top: 24px;
    padding: 18px 20px;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: 3px solid var(--brand) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-sm) !important;
}

.agent-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}

.agent-badge {
    background: var(--brand) !important;
    color: #FFFFFF !important;
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: .06em;
}

.agent-heading {
    color: var(--ink) !important;
    font-size: 14px;
    font-weight: 700;
}

.agent-caption {
    color: var(--muted) !important;
    font-size: 12px;
    line-height: 1.45;
}

/* ================= INPUTS ================= */

[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label {
    color: var(--ink-2) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 9px !important;
    min-height: 42px !important;
    font-size: 13px !important;
    box-shadow: none !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: var(--muted-2) !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(179,38,53,.10) !important;
}

/* Selectbox text */
[data-baseweb="select"] * {
    color: var(--ink) !important;
}

/* ================= BUTTON STANDARD ================= */

.stButton > button,
[data-testid="stFormSubmitButton"] button {
    min-height: 40px !important;
    padding: 8px 14px !important;
    border-radius: 9px !important;
    border: 1px solid var(--border-strong) !important;
    background: var(--surface) !important;
    color: var(--ink-2) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    border-color: var(--brand) !important;
    color: var(--brand) !important;
    background: var(--brand-50) !important;
}

.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
    background: var(--brand) !important;
    border-color: var(--brand) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
    background: var(--brand-dark) !important;
    border-color: var(--brand-dark) !important;
    color: #FFFFFF !important;
}

/* ================= KPI CARDS ================= */

.stat-card {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 18px !important;
    min-height: 112px;
    box-shadow: var(--shadow-sm);
}

.stat-label {
    color: var(--muted) !important;
    font-size: 11px;
    font-weight: 600;
}

.stat-value {
    color: var(--ink) !important;
    font-size: 22px;
    line-height: 1.2;
    font-weight: 700;
    margin-top: 8px;
}

.stat-sub {
    color: var(--muted-2) !important;
    font-size: 10px;
    margin-top: 6px;
}

/* Native metric */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 14px 16px !important;
    box-shadow: var(--shadow-sm);
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 11px !important;
}

[data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-size: 21px !important;
    font-weight: 700 !important;
}

/* ================= ACTIVITY / INSIGHTS ================= */

.activity-panel,
.insight-card,
.response-shell {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-sm) !important;
}

.activity-panel {
    padding: 8px 18px;
}

.activity-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 0;
    border-bottom: 1px solid #EEF0F3;
}

.activity-row:last-child {
    border-bottom: 0;
}

.activity-main {
    display: flex;
    align-items: center;
    gap: 11px;
}

.avatar {
    width: 36px;
    height: 36px;
    display: grid;
    place-items: center;
    border-radius: 9px;
    background: var(--brand-100);
    color: var(--brand) !important;
    font-size: 11px;
    font-weight: 700;
}

.activity-name {
    color: var(--ink) !important;
    font-size: 13px;
    font-weight: 650;
}

.activity-meta {
    color: var(--muted) !important;
    font-size: 10px;
    margin-top: 3px;
}

.activity-amount {
    color: var(--ink) !important;
    text-align: right;
    font-size: 13px;
    font-weight: 700;
}

.status {
    display: inline-block;
    border-radius: 999px;
    padding: 4px 8px;
    margin-top: 4px;
    font-size: 9px;
    font-weight: 700;
}

.status-processing {
    color: var(--warning) !important;
    background: var(--warning-bg);
}

.status-completed {
    color: var(--success) !important;
    background: var(--success-bg);
}

.insight-card {
    padding: 16px;
    margin-bottom: 10px;
}

.insight-head {
    color: var(--ink) !important;
    font-size: 13px;
    font-weight: 700;
}

.insight-copy {
    color: var(--muted) !important;
    font-size: 11px;
    line-height: 1.55;
    margin-top: 5px;
}

.insight-accent {
    color: var(--brand) !important;
    font-weight: 700;
}

/* ================= RESPONSE ================= */

.response-shell {
    padding: 18px;
    margin-top: 18px;
}

.response-heading {
    color: var(--ink) !important;
    font-size: 14px;
    font-weight: 700;
}

.source-pill {
    color: var(--muted) !important;
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 4px 8px;
    font-size: 9px;
}

/* Native alerts: enforce readable contrast */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}

[data-testid="stAlert"] p {
    color: var(--ink-2) !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
}

/* ================= TABLE ================= */

[data-testid="stDataFrame"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}

/* ================= DIVIDER / CAPTION ================= */

hr {
    border-color: var(--border) !important;
}

[data-testid="stCaptionContainer"] p {
    color: var(--muted) !important;
    font-size: 11px !important;
}

/* ================= EXPANDER ================= */

[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

[data-testid="stExpander"] summary {
    color: var(--ink) !important;
    font-weight: 600 !important;
}

/* ================= RESPONSIVE ================= */

@media (max-width: 900px) {
    .block-container {
        padding: 20px 18px 48px !important;
    }

    h1 {
        font-size: 26px !important;
    }

    .top-header {
        margin-bottom: 24px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================
if "response" not in st.session_state:
    st.session_state.response = None
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "handoff" not in st.session_state:
    st.session_state.handoff = False


def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def run_prompt(prompt):
    st.session_state.prompt = prompt
    st.session_state.response = route_prompt(prompt)
    st.session_state.handoff = False


# =========================================================
# SIDEBAR — functional navigation
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "Home"

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">₹</div>
            <div>
                <div class="sidebar-brand-name">Money2India</div>
                <div class="sidebar-brand-sub">Smart remittance</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-section">Navigate</div>', unsafe_allow_html=True)

    nav_items = [
        ("Home", "⌂  Home"),
        ("Send Money", "↗  Send money"),
        ("Track Transfer", "⌁  Track transfer"),
        ("Beneficiaries", "◉  Beneficiaries"),
        ("Statements", "▤  Statements"),
        ("Declarations", "✓  Declarations"),
        ("Support", "?  Support"),
    ]

    for page_name, label in nav_items:
        prefix = "● " if st.session_state.page == page_name else "○ "
        if st.button(
            prefix + label,
            key=f"nav_{page_name}",
            use_container_width=True,
        ):
            st.session_state.page = page_name
            st.session_state.response = None
            st.session_state.handoff = False
            safe_rerun()

    st.markdown(
        """
        <div class="side-footer">
            <b>Prototype environment</b><br>
            M2I demo data only.<br><br>
            No live account, FX, compliance or payment APIs are connected.
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# TOP HEADER
# =========================================================
st.markdown(
    """
    <div class="top-header">
        <div>
            <div class="top-title">Money2India Smart</div>
            <div class="top-subtitle">International remittance · prototype</div>
        </div>
        <div class="profile">
            <div class="profile-avatar">AS</div>
            <span>A. Sharma</span>
            <span style="color:#a1a6ad">⌄</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PAGE SURFACE HELPERS
# =========================================================
def render_page_header(title, subtitle):
    st.markdown('<div class="eyebrow">Money2India</div>', unsafe_allow_html=True)
    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f'<div class="hero-copy">{subtitle}</div>', unsafe_allow_html=True)


# =========================================================
# PAGE FUNCTIONS
# =========================================================

def render_send_money():
    render_page_header("Send money", "Prepare a remittance using a clear, guided flow.")
    st.markdown("#### Recipient")
    beneficiary = st.selectbox("Beneficiary", ["Mom", "Dad", "ABC Supplies"])
    amount = st.number_input("Amount in INR", min_value=1000, max_value=1000000, value=50000, step=5000)
    purpose = st.selectbox(
        "Purpose",
        ["Family maintenance", "Education", "Business payment", "Other"],
    )
    st.divider()
    st.markdown("#### Review")
    c1, c2, c3 = st.columns(3)
    c1.metric("Beneficiary", beneficiary)
    c2.metric("Amount", f"₹{amount:,.0f}")
    c3.metric("Purpose", purpose)

    if st.button("Prepare transfer", type="primary", use_container_width=True):
        st.session_state.response = (
            "prepare",
            {"beneficiary": beneficiary, "amount": f"₹{amount:,.0f}", "purpose": purpose},
        )
        st.session_state.handoff = False
        safe_rerun()

    st.caption("Prototype only. The final action would hand off to authenticated bank confirmation.")


def render_track_transfer():
    render_page_header("Track transfer", "View the latest status from the M2I demo transaction set.")
    tracking = st.selectbox(
        "Select tracking ID",
        [t["tracking"] for t in TRANSFERS],
        format_func=lambda x: f"{x} · {get_transfer_status(x)['beneficiary']}",
    )
    data = get_transfer_status(tracking)
    if data:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Beneficiary", data["beneficiary"])
        c2.metric("Amount", data["amount"])
        c3.metric("Status", data["status"])
        c4.metric("Date", data["date"])
        if data["status"] == "Processing":
            st.warning("→ Awaiting beneficiary-bank credit")
        else:
            st.success("✓ Transfer completed")
        st.caption(f"Tracking ID: {data['tracking']} · Demo data")


def render_beneficiaries():
    render_page_header("Beneficiaries", "Manage recipients used for international remittances.")
    st.dataframe(
        [
            {"Beneficiary": "Mom", "Type": "Individual", "Relationship": "Parent", "Status": "Active"},
            {"Beneficiary": "Dad", "Type": "Individual", "Relationship": "Parent", "Status": "Active"},
            {"Beneficiary": "ABC Supplies", "Type": "Business", "Relationship": "Vendor", "Status": "Active"},
        ],
        use_container_width=True,
        hide_index=True,
    )
    if st.button("Add beneficiary", type="primary"):
        st.info("Prototype: this would open the authenticated beneficiary-registration journey.")


def render_statements():
    render_page_header("Statements", "Review your remittance activity and download account records.")
    st.metric("Transfers this year", 11)
    st.dataframe(
        [
            {
                "Date": t["date"],
                "Beneficiary": t["beneficiary"],
                "Amount": t["amount"],
                "Status": t["status"],
                "Tracking ID": t["tracking"],
            }
            for t in TRANSFERS
        ],
        use_container_width=True,
        hide_index=True,
    )
    if st.button("Prepare statement download", type="primary"):
        st.success("Statement prepared for download — demo only.")


def render_declarations():
    render_page_header("Declarations", "Review declarations associated with your remittance beneficiaries.")
    st.info("Mom · Valid until 31 Mar 2027 · Demo declaration")
    st.info("Dad · Valid until 31 Mar 2027 · Demo declaration")
    st.caption(
        "Production eligibility and documentation requirements would come from authoritative compliance services."
    )


def render_support():
    render_page_header("Support", "Get contextual help without leaving your remittance journey.")
    issue = st.selectbox(
        "What do you need help with?",
        ["Transfer pending", "Beneficiary issue", "Declaration/document", "Something else"],
    )
    if st.button("Get help", type="primary", use_container_width=True):
        answers = {
            "Transfer pending": "Start with the transfer status timeline. If it is awaiting beneficiary-bank credit, no customer action may be required.",
            "Beneficiary issue": "Check the beneficiary details and registration status before attempting another transfer.",
            "Declaration/document": "The prototype cannot make compliance decisions. Production help would use authoritative bank requirements.",
            "Something else": "Please describe the issue in Ask M2I.",
        }
        st.info(answers[issue])


# =========================================================
# PAGE ROUTER
# =========================================================
if st.session_state.page == "Home":
    # =========================================================
    # HERO
    # =========================================================
    st.markdown('<div class="eyebrow">Your remittance cockpit</div>', unsafe_allow_html=True)
    st.markdown("<h1>Good evening</h1>", unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-copy">Your remittance overview, with a smarter way to get things done.</div>',
        unsafe_allow_html=True,
    )

    # =========================================================
    # ASK M2I
    # =========================================================
    st.markdown(
        """
        <div class="agent-shell">
            <div class="agent-row">
                <span class="agent-badge">ASK M2I</span>
                <span class="agent-heading">Talk to your remittance data</span>
            </div>
            <div class="agent-caption">
                Ask about transfers, beneficiaries, declarations or your remittance patterns.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("ask_form", clear_on_submit=False):
        c1, c2 = st.columns([6, 1])
        with c1:
            prompt = st.text_input(
                "Ask M2I",
                value=st.session_state.prompt,
                label_visibility="collapsed",
                placeholder="Try: Why is my latest transfer pending?",
            )
        with c2:
            submitted = st.form_submit_button("Ask M2I →", use_container_width=True)

    if submitted and prompt.strip():
        run_prompt(prompt)

    st.markdown('<div class="prompt-label">Suggested</div>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    suggestions = [
        "Why is my transfer pending?",
        "How much have I sent this year?",
        "Prepare my monthly transfer",
        "Show recent transfers",
    ]

    for col, suggestion in zip((s1, s2, s3, s4), suggestions):
        with col:
            if st.button(suggestion, key=f"s_{suggestion}", use_container_width=True):
                run_prompt(suggestion)
                safe_rerun()

    # =========================================================
    # AGENT RESPONSE — native Streamlit components
    # =========================================================
    if st.session_state.response:
        response_type, data = st.session_state.response

        st.markdown("### M2I response")
        st.caption("M2I demo data")

        if response_type == "pending":
            st.info(
                f"Your {data['amount']} transfer to {data['beneficiary']} "
                f"is currently **processing**."
            )
            st.write("No action is required from you right now.")

            c1, c2 = st.columns(2)
            with c1:
                st.success("✓ Transfer initiated")
                st.success("✓ Initial validation completed")
            with c2:
                st.success("✓ Processing completed")
                st.warning("→ Awaiting beneficiary-bank credit")

            st.caption(
                f"Tracking ID: {data['tracking']} · Status: {data['status']} · Demo data"
            )

        elif response_type == "track":
            st.info(
                f"Transfer **{data['tracking']}** for **{data['beneficiary']}** "
                f"is currently **{data['status']}**."
            )
            for label, completed in (
                ("Transfer initiated", True),
                ("Initial validation completed", True),
                ("Processing completed", True),
                ("Awaiting beneficiary-bank credit", False),
            ):
                if completed:
                    st.success(f"✓ {label}")
                else:
                    st.warning(f"→ {label}")

            st.caption("In production this would be driven by the authoritative M2I tracking service.")

        elif response_type == "annual":
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Sent this financial year", data["total"])
            with c2:
                st.metric("Transfers made", data["transfers"])
            st.caption("Mock summary for demonstration; not connected to a live account.")

        elif response_type in {"recent", "family", "business"}:
            title = {
                "recent": "Recent transfers",
                "family": "Family transfers",
                "business": "Business payments above ₹1 lakh",
            }[response_type]
            st.write(f"**{title}**")
            st.dataframe(
                [
                    {
                        "Beneficiary": t["beneficiary"],
                        "Amount": t["amount"],
                        "Date": t["date"],
                        "Status": t["status"],
                        "Tracking ID": t["tracking"],
                    }
                    for t in data
                ],
                use_container_width=True,
                hide_index=True,
            )

        elif response_type == "prepare":
            st.info("Transfer prepared for review — it has **not** been submitted.")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Beneficiary", data["beneficiary"])
            with c2:
                st.metric("Amount", data["amount"])
            with c3:
                st.metric("Purpose", data["purpose"])

            review, cancel = st.columns(2)
            with review:
                if st.button("Continue to secure review", type="primary", use_container_width=True):
                    st.session_state.handoff = True
            with cancel:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.response = None
                    st.session_state.handoff = False
                    safe_rerun()

            if st.session_state.handoff:
                st.warning(
                    "Secure handoff: this prototype would now transfer control to "
                    "the bank's authenticated confirmation journey. No money movement "
                    "is performed by the agent."
                )

        elif response_type == "declaration":
            st.info(
                f"Mock declaration status for **{data['beneficiary']}**: "
                f"valid until **{data['valid_until']}**."
            )
            st.warning(
                "Compliance decisions are never made by the AI alone. Production "
                "requirements would come from the authoritative M2I/compliance service."
            )

        elif response_type == "fx_guardrail":
            st.warning(
                "Live-data boundary: this prototype does not have access to live FX data. "
                "Any rate shown here is demo data only."
            )

        elif response_type == "execution_guardrail":
            st.warning(
                "Financial-action boundary: I can prepare a transaction for review, "
                "but this prototype cannot execute money movement."
            )

        elif response_type == "compliance_guardrail":
            st.warning(
                "Compliance boundary: this prototype does not determine regulatory "
                "eligibility. Production decisions would come from authoritative "
                "bank/compliance services."
            )

        else:
            st.info(
                "I don’t have verified data for that in this prototype, "
                "so I won’t invent an answer."
            )

    # =========================================================
    # SNAPSHOT
    # =========================================================
    st.markdown(
        '<div class="section-label">Your remittance snapshot <span class="section-meta">Mock data</span></div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)

    for col, label, value, sub in (
        (m1, "Sent this financial year", "₹8.42L", "11 transfers"),
        (m2, "Typical monthly transfer", "₹75,000", "Based on demo history"),
        (m3, "Active beneficiaries", "3", "Available for transfer"),
        (m4, "Indicative rate", "₹85.29", "Demo value only"),
    ):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{value}</div>
                    <div class="stat-sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================
    # ACTIVITY + PERSONALIZED INSIGHTS
    # =========================================================
    st.markdown('<div class="section-label">Your activity & next best actions</div>', unsafe_allow_html=True)

    left, right = st.columns([1.65, 1])

    with left:
        activity_html = ['<div class="activity-panel">']
        for t in TRANSFERS[:4]:
            status_class = "status-processing" if t["status"] == "Processing" else "status-completed"
            activity_html.append(
                f"""
                <div class="activity-row">
                    <div class="activity-main">
                        <div class="avatar">{t["initials"]}</div>
                        <div>
                            <div class="activity-name">{t["beneficiary"]}</div>
                            <div class="activity-meta">{t["date"]} · {t["tracking"]}</div>
                        </div>
                    </div>
                    <div>
                        <div class="activity-amount">{t["amount"]}</div>
                        <div class="status {status_class}">{t["status"]}</div>
                    </div>
                </div>
                """
            )
        activity_html.append("</div>")
        st.markdown("".join(activity_html), unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-head">Monthly pattern</div>
                <div class="insight-copy">
                    Your family transfers usually happen around the
                    <span class="insight-accent">5th–10th</span> of the month.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Prepare usual transfer", key="prepare_side", use_container_width=True):
            run_prompt("Prepare my monthly transfer")
            safe_rerun()

        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-head">Declaration</div>
                <div class="insight-copy">
                    Mom's demo declaration is valid until
                    <span class="insight-accent">31 Mar 2027</span>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Check declaration", key="decl_side", use_container_width=True):
            run_prompt("Do I need a declaration for Mom?")
            safe_rerun()

    # =========================================================
    # COMING NEXT
    # =========================================================
    st.markdown('<div class="section-label">Concepts for the next iteration</div>', unsafe_allow_html=True)

    features = [
        ("Smart FX timing", "Compare today's indicative quote with the customer's historical transfer pattern."),
        ("Family dashboard", "See recurring remittance commitments and upcoming transfers in one place."),
        ("AI document assistant", "Explain what document is needed without becoming the compliance decision-maker."),
        ("Business workspace", "Search vendor payments, exceptions and reconciliation status conversationally."),
        ("Proactive alerts", "Surface unusual delays, expiring declarations and recurring transfer reminders."),
        ("Fee explanation", "Explain exactly how a transfer amount reached the beneficiary using authoritative transaction data."),
    ]

    fc = st.columns(3)
    for i, (title, desc) in enumerate(features):
        with fc[i % 3]:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-head">{title}</div>
                    <div class="insight-copy">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================
    # DEMO ARCHITECTURE — hidden inside a collapsed developer note
    # =========================================================
    with st.expander("Prototype notes", expanded=False):
        st.caption(
            "UI → deterministic intent router → mock M2I tools → mock data. "
            "READ and PREPARE are demonstrated. EXECUTE is intentionally unavailable."
        )

elif st.session_state.page == "Send Money":
    render_send_money()
elif st.session_state.page == "Track Transfer":
    render_track_transfer()
elif st.session_state.page == "Beneficiaries":
    render_beneficiaries()
elif st.session_state.page == "Statements":
    render_statements()
elif st.session_state.page == "Declarations":
    render_declarations()
elif st.session_state.page == "Support":
    render_support()