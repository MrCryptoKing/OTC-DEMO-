"""A local-only paper-trading and operations workflow demo.

This application intentionally does not accept payments, store KYC documents,
connect to wallets/banks, or execute trades. All balances and review records
are fictional session data.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import streamlit as st


DISPLAY_CURRENCIES = ("USD", "EUR", "GBP", "INR", "AED", "JPY", "BRL", "NGN")
FX_TO_USD = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27, "INR": 0.012, "AED": 0.272, "JPY": 0.0064, "BRL": 0.19, "NGN": 0.00066}


def seed_records() -> list[dict[str, object]]:
    return [
        {"id": "SIM-1042", "user": "Aarav Sharma", "account_name": "Aarav Sharma", "payer_name": "Aarav Sharma", "currency": "INR", "amount": 2500.0, "proof": "Reference supplied", "status": "Pending review", "risk": "Low", "note": "Fictional demo record"},
        {"id": "SIM-1043", "user": "Maya Patel", "account_name": "Maya Patel", "payer_name": "Karan Patel", "currency": "USD", "amount": 75.0, "proof": "Reference supplied", "status": "Name mismatch", "risk": "High", "note": "Third-party payer: request clarification"},
        {"id": "SIM-1044", "user": "Sofia Khan", "account_name": "Sofia Khan", "payer_name": "Sofia Khan", "currency": "EUR", "amount": 120.0, "proof": "No reference", "status": "Needs evidence", "risk": "Medium", "note": "Do not credit until verified"},
        {"id": "SIM-1045", "user": "Daniel Okafor", "account_name": "Daniel Okafor", "payer_name": "Daniel Okafor", "currency": "NGN", "amount": 30000.0, "proof": "Reference supplied", "status": "Verified", "risk": "Low", "note": "Demo only"},
    ]


def usd_value(amount: float, currency: str) -> float:
    return amount * FX_TO_USD[currency]


st.set_page_config(page_title="Orbit Paper Trading", page_icon="◈", layout="wide")

if "records" not in st.session_state:
    st.session_state.records = seed_records()
if "virtual_balance" not in st.session_state:
    st.session_state.virtual_balance = 10_000.0

st.title("Orbit — Paper Trading Operations Demo")
st.caption("Simulation only. No deposits, withdrawals, payment proofs, KYC data, or real trades are processed by this app.")

with st.sidebar:
    st.header("Demo controls")
    currency = st.selectbox("Display currency", DISPLAY_CURRENCIES)
    st.metric("Virtual balance", f"{st.session_state.virtual_balance * FX_TO_USD[currency]:,.2f} {currency}")
    st.divider()
    st.info("For a production financial service, use licensed payment partners and obtain legal/compliance approval before handling customer funds.")

overview, review_queue, simulator, policy = st.tabs(["Overview", "Review queue", "Trade simulator", "Controls"])

with overview:
    frame = pd.DataFrame(st.session_state.records)
    pending = int((frame["status"] != "Verified").sum())
    high_risk = int((frame["risk"] == "High").sum())
    total_usd = frame.apply(lambda row: usd_value(float(row.amount), str(row.currency)), axis=1).sum()
    a, b, c, d = st.columns(4)
    a.metric("Fictional requests", len(frame))
    b.metric("Awaiting action", pending)
    c.metric("High-risk flags", high_risk)
    d.metric("Simulated request value", f"${total_usd:,.2f}")
    st.subheader("Review principles")
    st.write("Match account-holder and payer details; require a verifiable reference through an approved provider; keep an audit trail; and hold/reject mismatches under a documented policy. Never make a final fraud decision from a screenshot alone.")

with review_queue:
    st.subheader("Fictional verification queue")
    queue = pd.DataFrame(st.session_state.records)
    st.dataframe(queue, use_container_width=True, hide_index=True)
    request_ids = queue["id"].tolist()
    selected_id = st.selectbox("Select a fictional request", request_ids)
    selected = next(item for item in st.session_state.records if item["id"] == selected_id)
    st.write(f"**Account holder:** {selected['account_name']}  ")
    st.write(f"**Payer shown:** {selected['payer_name']}  ")
    st.warning("This demo does not accept screenshots, UTRs, bank details, identity documents, or real payment data.")
    action = st.selectbox("Demo reviewer action", ("No change", "Mark verified (simulation)", "Request clarification (simulation)", "Flag for compliance review (simulation)"))
    if st.button("Apply demo action", type="primary") and action != "No change":
        if action.startswith("Mark"):
            selected["status"], selected["risk"], selected["note"] = "Verified", "Low", "Simulated approval — no funds credited"
        elif action.startswith("Request"):
            selected["status"], selected["note"] = "Needs evidence", "Simulated clarification request"
        else:
            selected["status"], selected["risk"], selected["note"] = "Compliance review", "High", "Simulated compliance escalation"
        st.success("Demo record updated locally for this browser session.")

with simulator:
    st.subheader("Virtual trade ticket")
    st.caption("This changes only a fictional practice balance; it does not place an order or create a financial obligation.")
    pair = st.selectbox("Practice market", ("EUR/USD", "GBP/USD", "USD/JPY", "BTC/USD (simulated)"))
    direction = st.radio("Direction", ("Up", "Down"), horizontal=True)
    stake = st.number_input("Virtual stake (USD)", min_value=1.0, max_value=1000.0, value=25.0, step=1.0)
    outcome = st.selectbox("Simulated outcome", ("Win", "Loss"))
    if st.button("Run simulated trade"):
        change = stake * 0.8 if outcome == "Win" else -stake
        st.session_state.virtual_balance += change
        st.success(f"Simulation recorded: {direction} on {pair}; virtual P/L ${change:,.2f}.")

with policy:
    st.subheader("Production-readiness checklist")
    st.markdown("""
    - Do not receive or custody funds until the relevant licences, legal entity, and payment-provider approvals are in place.
    - Obtain independent legal/compliance advice for every jurisdiction served.
    - Use provider-side webhooks and reconciliation—not screenshot/UTR-only approvals—to verify payments.
    - Apply KYC/AML, sanctions screening, transaction monitoring, privacy controls, role-based access, and immutable audit logs.
    - Give users clear appeal/review routes; avoid automatic accusations based solely on a name mismatch.
    """)
    st.caption(f"Demo session generated at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
