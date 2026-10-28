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
        /* Main Theme & Background */
        .stApp {{
            background-color: {bg_color};
        }}

        /* Headers styling */
        h1, h2, h3, h4, h5, h6 {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: {text_color} !important;
        }}

        p, span, label {{
            color: {text_color};
        }}

        /* Card Container styling */
        .custom-card {{
            background-color: {card_bg};
            padding: 20px 24px;
            border-radius: 12px;
            border: 1px solid {border_color};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 16px;
        }}

        /* Custom buttons styling enhancement */
        .stButton>button {{
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease-in-out;
        }}

        /* Tabs typography */
        .stTabs [data-baseweb="tab"] {{
            font-weight: 600;
            font-size: 15px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# App Main Title Header with Accent Card
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); padding: 24px 32px; border-radius: 16px; color: white; margin-bottom: 24px; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);">
        <h1 style="color: white !important; margin: 0; font-size: 28px; font-weight: 800;">📱 Mobile Models Management</h1>
        <p style="margin: 6px 0 0 0; color: #DBEAFE !important; font-size: 15px;">Enterprise dashboard for mobile catalogue, inventory tracking, and document workflows.</p>
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
    response = requests.get(
        f"{API_BASE_URL}/models",
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict):
        return payload.get("data", [])
    return payload if isinstance(payload, list) else []


def show_api_error(error):
    if isinstance(error, requests.HTTPError) and error.response is not None:
        st.error(api_error_message(error.response))
    else:
        st.error(f"Could not connect to the API: {error}")


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


# Navigation Tabs
view_tab, add_tab, delete_tab, file_tab, report_tab = st.tabs(
    [
        "📋 View Models",
        "➕ Add Model",
        "🗑️ Delete Model",
        "📤 PDF Upload & Download",
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


# Initialize session state flags
if "view_table" not in st.session_state:
    st.session_state["view_table"] = True
if "view_line_chart" not in st.session_state:
    st.session_state["view_line_chart"] = False
if "view_pie_chart" not in st.session_state:
    st.session_state["view_pie_chart"] = False

with view_tab:
    # Styled Toggle View Box Container
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
        st.checkbox(
            "View Table Form",
            key="view_table",
            on_change=select_table_view,
        )
    with col_c2:
        st.checkbox(
            "View Line Chart (Inventory Status)",
            key="view_line_chart",
            on_change=select_line_chart_view,
        )
    with col_c3:
        st.checkbox(
            "View Pie Chart (Inventory Share)",
            key="view_pie_chart",
            on_change=select_pie_chart_view,
        )

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
            chart_data = []
            for model in models:
                device_names = model.get("device_names") or []
                chart_data.append({
                    "name": model.get("name", "Unknown"),
                    "device_count": len(device_names),
                })

            render_horizontal_device_chart(
                models_data=chart_data,
                title="Inventory Status Matrix",
                subtitle="Stock levels and catalog device availability by category",
                max_capacity=10,
            )

        elif st.session_state["view_pie_chart"]:
            pie_data = []
            for model in models:
                device_names = model.get("device_names") or []
                pie_data.append({
                    "Model Name": model.get("name", "Unknown"),
                    "Number of Devices": len(device_names),
                })

            pie_df = pd.DataFrame(pie_data)

            st.markdown(
                f"""
                <div class="custom-card">
                    <h3 style="margin-top: 0; color: {text_color};">Inventory Share Distribution</h3>
                    <p style="color: {subtext_color}; font-size: 14px;">Proportion of available device models per company category.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            fig_pie = px.pie(
                pie_df,
                names="Model Name",
                values="Number of Devices",
                hole=0.4,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": text_color},
                margin={"l": 20, "r": 20, "t": 20, "b": 20},
                legend={"title": "Models"},
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.dataframe(pie_df, use_container_width=True, hide_index=True)

        else:
            display_models = [
                {
                    "ID": model["id"],
                    "Name": model["name"],
                    "Price": f"₹ {model['price']:,}",
                }
                for model in models
            ]

            left_column, right_column = st.columns([2, 1], gap="medium")

            with left_column:
                st.markdown("##### Companies Directory")
                st.caption("Click any row entry below to inspect associated device models.")

                event = st.dataframe(
                    pd.DataFrame(display_models),
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="company_table",
                )

            selected_rows = event.selection.rows

            if selected_rows:
                selected_index = selected_rows[0]
                selected_company = models[selected_index]
                st.session_state["selected_company_id"] = selected_company["id"]
            else:
                selected_company_id = st.session_state.get("selected_company_id")
                selected_company = next(
                    (
                        model for model in models
                        if model["id"] == selected_company_id
                    ),
                    models[0],
                )
                st.session_state["selected_company_id"] = selected_company["id"]

            with right_column:
                st.markdown("##### Device Models Spec")

                device_names = selected_company.get("device_names") or []
                devices_html = ""
                if device_names:
                    for index, device_name in enumerate(device_names, start=1):
                        devices_html += (
                            f'<div style="background-color: {inner_box_bg}; padding: 10px 14px; '
                            f'border-radius: 8px; border: 1px solid {border_color}; margin-bottom: 8px; '
                            f'font-size: 13.5px; font-weight: 500; color: {text_color};">'
                            f'<span style="color: #60A5FA; font-weight: 600; margin-right: 8px;">#{index}</span> '
                            f'{device_name}</div>'
                        )
                else:
                    devices_html = f"<p style='color: {subtext_color}; font-size: 13px;'>No device models found for this company.</p>"

                card_content = (
                    f'<div style="background-color: {card_bg}; padding: 20px; border-radius: 12px; border: 1px solid {border_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">'
                    f'<div style="font-size: 12px; text-transform: uppercase; font-weight: 700; color: {subtext_color}; letter-spacing: 0.5px;">Selected Company</div>'
                    f'<div style="font-size: 22px; font-weight: 800; color: #60A5FA; margin-top: 4px; margin-bottom: 12px;">{selected_company["name"]}</div>'
                    f'<div style="font-size: 13px; color: {subtext_color}; margin-bottom: 14px;">Total catalog entries: <b style="color: {text_color};">{len(device_names)}</b></div>'
                    f'<hr style="border: none; border-top: 1px solid {border_color}; margin-bottom: 14px;" />'
                    f'{devices_html}'
                    f'</div>'
                )
                st.markdown(card_content, unsafe_allow_html=True)

    except (requests.RequestException, ValueError, KeyError) as error:
        show_api_error(error)

with add_tab:
    st.subheader("Add New Mobile Model")
    st.caption("Register a brand new mobile model entry into the core backend repository.")

    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("add_model_form", clear_on_submit=True):
            model_id = st.number_input("Model ID", min_value=1, step=1)
            model_name = st.text_input("Model Name", max_chars=15, placeholder="e.g., SAMSUNG")
            model_price = st.number_input("Price (₹)", min_value=1, step=1)

            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("➕ Submit & Add Model", use_container_width=True)

        if submitted:
            if len(model_name.strip()) < 3:
                st.error("Model name must contain at least 3 characters.")
            else:
                payload = {
                    "id": int(model_id),
                    "name": model_name.strip(),
                    "price": int(model_price),
                }
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/model",
                        json=payload,
                        timeout=REQUEST_TIMEOUT,
                    )
                    if response.ok:
                        st.success("Mobile model added successfully.")
                        st.json(response.json())
                    else:
                        st.error(api_error_message(response))
                except requests.RequestException as error:
                    show_api_error(error)
        st.markdown('</div>', unsafe_allow_html=True)

with delete_tab:
    st.subheader("Delete Mobile Model")
    st.caption("Permanently remove an existing mobile model record using its unique identifier ID.")

    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("delete_model_form"):
            delete_id = st.number_input("Model ID to delete", min_value=1, step=1)
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            delete_submitted = st.form_submit_button("🗑️ Confirm Deletion", use_container_width=True)

        if delete_submitted:
            try:
                response = requests.delete(
                    f"{API_BASE_URL}/model/{int(delete_id)}/delete",
                    timeout=REQUEST_TIMEOUT,
                )
                if response.ok:
                    st.success("Delete request completed successfully.")
                    try:
                        st.json(response.json())
                    except ValueError:
                        st.write(response.text)
                else:
                    st.error(api_error_message(response))
            except requests.RequestException as error:
                show_api_error(error)
        st.markdown('</div>', unsafe_allow_html=True)

with file_tab:
    st.subheader("PDF Document Management")
    st.caption("Upload or retrieve model-specific specification sheets stored directly in database blobs.")

    col_up, col_down = st.columns(2, gap="medium")

    with col_up:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### 📤 Upload PDF Spec")
        with st.form("pdf_upload_form"):
            upload_model_id = st.number_input(
                "Mobile Model ID", min_value=1, step=1, key="upload_model_id"
            )
            uploaded_pdf = st.file_uploader(
                "Choose PDF document", type=["pdf"], key="uploaded_model_pdf"
            )
            upload_submitted = st.form_submit_button("Upload PDF File", use_container_width=True)

        if upload_submitted:
            is_valid, result = validate_pdf(uploaded_pdf)
            if not is_valid:
                st.error(result)
            else:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/models/{int(upload_model_id)}/pdf",
                        files={
                            "file": (
                                uploaded_pdf.name,
                                result,
                                "application/pdf",
                            )
                        },
                        timeout=REQUEST_TIMEOUT,
                    )
                    if response.ok:
                        st.success("PDF uploaded and stored successfully.")
                        st.json(response.json())
                    else:
                        st.error(api_error_message(response))
                except requests.RequestException as error:
                    show_api_error(error)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_down:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### 📥 Download Stored PDF")
        with st.form("pdf_download_form"):
            download_model_id = st.number_input(
                "Mobile Model ID", min_value=1, step=1, key="download_model_id"
            )
            st.markdown("<div style='margin-top: 36px;'></div>", unsafe_allow_html=True)
            download_submitted = st.form_submit_button("Find & Prepare PDF", use_container_width=True)

        if download_submitted:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/models/{int(download_model_id)}/pdf",
                    timeout=REQUEST_TIMEOUT,
                )
                if response.ok:
                    st.session_state["stored_pdf_bytes"] = response.content
                    st.session_state["stored_pdf_name"] = (
                        f"model_{int(download_model_id)}.pdf"
                    )
                    st.session_state["stored_pdf_model_id"] = int(download_model_id)
                    st.success("PDF is ready to download below.")
                else:
                    st.session_state.pop("stored_pdf_bytes", None)
                    st.session_state.pop("stored_pdf_name", None)
                    st.error(api_error_message(response))
            except requests.RequestException as error:
                show_api_error(error)

        if "stored_pdf_bytes" in st.session_state:
            st.download_button(
                label="⬇️ Download Stored PDF Now",
                data=st.session_state["stored_pdf_bytes"],
                file_name=st.session_state["stored_pdf_name"],
                mime="application/pdf",
                key="download_stored_pdf",
                use_container_width=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

with report_tab:
    st.subheader("Global Catalog PDF Report")
    st.caption("Generate or download a complete compiled PDF report directly from the backend reporting engine.")

    st.markdown(
        f"""
        <div class="custom-card" style="text-align: center; padding: 32px;">
            <h3 style="color: {text_color}; margin-bottom: 8px;">Ready to Compile Report</h3>
            <p style="color: {subtext_color}; font-size: 14px; margin-bottom: 24px;">Click the button below to query the FastAPI reporting service and compile the latest analytics report file.</p>
        """,
        unsafe_allow_html=True,
    )

    if st.button("📊 Fetch Compiled PDF Report", key="fetch_pdf_report", use_container_width=True):
        try:
            response = requests.get(
                f"{API_BASE_URL}/reports/pdf",
                timeout=REQUEST_TIMEOUT,
            )
            if response.ok:
                st.session_state["report_pdf_bytes"] = response.content
                st.success("PDF report generated successfully.")
            else:
                st.session_state.pop("report_pdf_bytes", None)
                st.error(api_error_message(response))
        except requests.RequestException as error:
            show_api_error(error)

    if "report_pdf_bytes" in st.session_state:
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Download mobile_models_report.pdf",
            data=st.session_state["report_pdf_bytes"],
            file_name="mobile_models_report.pdf",
            mime="application/pdf",
            key="download_generated_report",
            use_container_width=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)