import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from inventory_bar_chart import render_horizontal_device_chart

API_BASE_URL = "http://127.0.0.1:8000/api"
REQUEST_TIMEOUT = 30
MAX_PDF_SIZE_MB = 20

# Page Configuration
st.set_page_config(
    page_title="Mobile Models Manager",
    page_icon="📱",
    layout="wide",
)

# Dynamic Theme Detection (Light vs Dark Mode)
is_dark_theme = False
try:
    theme_base = st.get_option("theme.base")
    if theme_base == "dark":
        is_dark_theme = True
except Exception:
    pass

# Dynamic Color Scheme Variables
bg_color = "#0F172A" if is_dark_theme else "#F8FAFC"
card_bg = "#1E293B" if is_dark_theme else "#FFFFFF"
text_color = "#F8FAFC" if is_dark_theme else "#0F172A"
subtext_color = "#94A3B8" if is_dark_theme else "#64748B"
border_color = "#334155" if is_dark_theme else "#E2E8F0"
inner_box_bg = "#0F172A" if is_dark_theme else "#F8FAFC"

# Custom CSS Injection supporting Light & Dark Mode seamlessly
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color};
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: {text_color} !important;
        }}
        p, span, label {{
            color: {text_color};
        }}
        .custom-card {{
            background-color: {card_bg};
            padding: 20px 24px;
            border-radius: 12px;
            border: 1px solid {border_color};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 16px;
        }}
        .stButton>button {{
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease-in-out;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-weight: 600;
            font-size: 15px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# App Main Title Header
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); padding: 24px 32px; border-radius: 16px; color: white; margin-bottom: 24px; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);">
        <h1 style="color: white !important; margin: 0; font-size: 28px; font-weight: 800;">📱 Mobile Models Management</h1>
        <p style="margin: 6px 0 0 0; color: #DBEAFE !important; font-size: 15px;">Enterprise dashboard with cataloging, document management, and store mapping workflows.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def api_error_message(response):
    try:
        detail = response.json().get("detail", response.text)
    except (ValueError, AttributeError):
        detail = response.text or "Unknown API error"
    return f"HTTP {response.status_code}: {detail}"


def get_models():
    response = requests.get(f"{API_BASE_URL}/models", timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict):
        return payload.get("data", [])
    return payload if isinstance(payload, list) else []


def validate_pdf(uploaded_file):
    if uploaded_file is None:
        return False, "Choose a PDF file first."
    if not uploaded_file.name.lower().endswith(".pdf"):
        return False, "Only PDF files are allowed."
    pdf_bytes = uploaded_file.getvalue()
    if not pdf_bytes.startswith(b"%PDF-"):
        return False, "The selected file does not appear to be a valid PDF."
    if len(pdf_bytes) > MAX_PDF_SIZE_MB * 1024 * 1024:
        return False, f"PDF must be {MAX_PDF_SIZE_MB} MB or smaller."
    return True, pdf_bytes


# Navigation Tabs including Maps Tab
view_tab, add_tab, delete_tab, file_tab, map_tab, report_tab = st.tabs(
    [
        "📋 View Models",
        "➕ Add Model",
        "🗑️ Delete Model",
        "📤 PDF Management",
        "🗺️ Store Locations (Maps)",
        "📄 Generated PDF Report",
    ]
)


def select_table_view():
    st.session_state["view_table"] = True
    st.session_state["view_line_chart"] = False
    st.session_state["view_pie_chart"] = False


def select_line_chart_view():
    st.session_state["view_table"] = False
    st.session_state["view_line_chart"] = True
    st.session_state["view_pie_chart"] = False


def select_pie_chart_view():
    st.session_state["view_table"] = False
    st.session_state["view_line_chart"] = False
    st.session_state["view_pie_chart"] = True


if "view_table" not in st.session_state:
    st.session_state["view_table"] = True
if "view_line_chart" not in st.session_state:
    st.session_state["view_line_chart"] = False
if "view_pie_chart" not in st.session_state:
    st.session_state["view_pie_chart"] = False

with view_tab:
    st.markdown(
        f"""
        <div style="background-color: {card_bg}; padding: 16px 20px; border-radius: 12px; border: 1px solid {border_color}; margin-bottom: 20px; display: flex; align-items: center;">
            <span style="font-weight: 700; color: {text_color}; font-size: 15px; margin-right: 24px;">🎛️ Select Display Layout:</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.checkbox("View Table Form", key="view_table", on_change=select_table_view)
    with col_c2:
        st.checkbox("View Bar Graph", key="view_line_chart", on_change=select_line_chart_view)
    with col_c3:
        st.checkbox("View Pie Chart", key="view_pie_chart", on_change=select_pie_chart_view)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    col_header, col_btn = st.columns([4, 1])
    with col_header:
        st.subheader("All Mobile Models Catalogue")
    with col_btn:
        if st.button("🔄 Refresh Data", key="refresh_models", use_container_width=True):
            st.rerun()

    try:
        models = get_models()
        if not models:
            st.info("No mobile models found in the database.")
        elif st.session_state["view_line_chart"]:
            chart_data = [{"name": m.get("name", "Unknown"), "device_count": len(m.get("device_names") or [])} for m in
                          models]
            render_horizontal_device_chart(models_data=chart_data, title="Inventory Status Matrix",
                                           subtitle="Stock levels by category")
        elif st.session_state["view_pie_chart"]:
            pie_df = pd.DataFrame(
                [{"Model Name": m.get("name", "Unknown"), "Number of Devices": len(m.get("device_names") or [])} for m
                 in models])
            st.markdown(
                f'<div class="custom-card"><h3 style="margin-top:0; color:{text_color};">Inventory Share Distribution</h3></div>',
                unsafe_allow_html=True)
            fig_pie = px.pie(pie_df, names="Model Name", values="Number of Devices", hole=0.4)
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font={"color": text_color})
            st.plotly_chart(fig_pie, use_container_width=True)
            st.dataframe(pie_df, use_container_width=True, hide_index=True)
        else:
            display_models = [{"ID": m["id"], "Name": m["name"], "Price": f"₹ {m['price']:,}"} for m in models]
            left_column, right_column = st.columns([2, 1], gap="medium")
            with left_column:
                st.markdown("##### Companies Directory")
                event = st.dataframe(pd.DataFrame(display_models), use_container_width=True, hide_index=True,
                                     on_select="rerun", selection_mode="single-row", key="company_table")

            selected_rows = event.selection.rows
            selected_company = models[selected_rows[0]] if selected_rows else models[0]

            with right_column:
                st.markdown("##### Device Models Spec")
                device_names = selected_company.get("device_names") or []
                devices_html = "".join([
                                           f'<div style="background-color: {inner_box_bg}; padding: 10px; border-radius: 8px; border: 1px solid {border_color}; margin-bottom: 8px;"><b>#{i}</b> {d}</div>'
                                           for i, d in enumerate(device_names, 1)]) or "No devices found."
                st.markdown(
                    f'<div class="custom-card"><div style="font-size: 20px; font-weight: 800; color: #60A5FA; margin-bottom: 8px;">{selected_company["name"]}</div>{devices_html}</div>',
                    unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading models: {e}")

with add_tab:
    st.subheader("Add New Mobile Model")
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("add_model_form", clear_on_submit=True):
            model_id = st.number_input("Model ID", min_value=1, step=1)
            model_name = st.text_input("Model Name", max_chars=15)
            model_price = st.number_input("Price (₹)", min_value=1, step=1)
            submitted = st.form_submit_button("➕ Submit & Add Model", use_container_width=True)
        if submitted:
            try:
                res = requests.post(f"{API_BASE_URL}/model",
                                    json={"id": int(model_id), "name": model_name.strip(), "price": int(model_price)},
                                    timeout=REQUEST_TIMEOUT)
                if res.ok:
                    st.success("Added successfully.")
                else:
                    st.error(res.text)
            except Exception as ex:
                st.error(ex)
        st.markdown('</div>', unsafe_allow_html=True)

with delete_tab:
    st.subheader("Delete Mobile Model")
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("delete_form"):
            del_id = st.number_input("Model ID to delete", min_value=1, step=1)
            del_sub = st.form_submit_button("🗑️ Confirm Deletion", use_container_width=True)
        if del_sub:
            res = requests.delete(f"{API_BASE_URL}/model/{int(del_id)}/delete", timeout=REQUEST_TIMEOUT)
            if res.ok:
                st.success("Deleted.")
            else:
                st.error(res.text)
        st.markdown('</div>', unsafe_allow_html=True)

with file_tab:
    st.subheader("PDF Document Management")
    col_up, col_down = st.columns(2, gap="medium")
    with col_up:
        st.markdown('<div class="custom-card"><h4>Upload PDF</h4>', unsafe_allow_html=True)
        with st.form("pdf_up"):
            u_id = st.number_input("Model ID", min_value=1, step=1, key="up_id")
            u_file = st.file_uploader("PDF file", type=["pdf"])
            u_sub = st.form_submit_button("Upload", use_container_width=True)
        if u_sub and u_file:
            valid, res = validate_pdf(u_file)
            if valid:
                r = requests.post(f"{API_BASE_URL}/models/{int(u_id)}/pdf",
                                  files={"file": (u_file.name, res, "application/pdf")})
                if r.ok: st.success("Uploaded successfully.")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_down:
        st.markdown('<div class="custom-card"><h4>Download PDF</h4>', unsafe_allow_html=True)
        with st.form("pdf_down"):
            d_id = st.number_input("Model ID", min_value=1, step=1, key="down_id")
            d_sub = st.form_submit_button("Find PDF", use_container_width=True)
        if d_sub:
            r = requests.get(f"{API_BASE_URL}/models/{int(d_id)}/pdf")
            if r.ok:
                st.session_state["pdf_bytes"] = r.content
                st.success("Ready.")
        if "pdf_bytes" in st.session_state:
            st.download_button("Download PDF", data=st.session_state["pdf_bytes"], file_name="model.pdf",
                               use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# 🗺️ New Store Locations (Google Maps Integration Tab)
with map_tab:
    st.subheader("🗺️ Official Store & Service Centers Map")
    st.caption("Explore our authorized retail locations and service hubs across the region.")

    # Sample store coordinates data (Replace or pull dynamically from your database/API)
    stores_data = pd.DataFrame({
        "name": ["Connaught Place Hub", "Cyber City Store", "Bandra West Center", "Koramangala Outlet", "Miyapur Store"],
        "lat": [28.6280, 28.4595, 19.0596, 12.9352, 17.4968],
        "lon": [77.2090, 77.0266, 72.8295, 77.6144,78.3614],
        "city": ["New Delhi", "Gurugram", "Mumbai", "Bengaluru", "Hyderabad"]
    })

    # Interactive Streamlit Native Map View
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("##### Interactive Regional Store Distribution")
    st.map(stores_data, latitude="lat", longitude="lon", size=30, color="#2563EB")
    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed Table of Store Locations
    st.markdown("##### Location Directory")
    st.dataframe(stores_data, use_container_width=True, hide_index=True)

with report_tab:
    st.subheader("Global Catalog PDF Report")
    st.markdown('<div class="custom-card" style="text-align: center;">', unsafe_allow_html=True)
    if st.button("📊 Fetch Compiled PDF Report", use_container_width=True):
        res = requests.get(f"{API_BASE_URL}/reports/pdf")
        if res.ok:
            st.session_state["report_bytes"] = res.content
            st.success("Ready.")
    if "report_bytes" in st.session_state:
        st.download_button("⬇️ Download Report", data=st.session_state["report_bytes"],
                           file_name="mobile_models_report.pdf", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)