import requests
import pandas as pd
import streamlit as st

API_BASE_URL = "https://amplifier-daisy-flood-varying.trycloudflare.com/api"
REQUEST_TIMEOUT = 30
MAX_PDF_SIZE_MB = 20

st.set_page_config(
    page_title="Mobile Models",
    page_icon="Mobile",
    layout="wide",
)

st.title("Mobile Models Management")


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

    # The API may return {"data": [...]} or a direct list.
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


view_tab, add_tab, delete_tab, file_tab, report_tab = st.tabs(
    [
        "View Models",
        "Add Model",
        "Delete Model",
        "PDF Upload and Download",
        "Generated PDF Report",
    ]
)



with view_tab:
    st.subheader("All Mobile Models")

    if st.button("Refresh Models", key="refresh_models"):
        st.rerun()

    try:
        models = get_models()

        if not models:
            st.info("No mobile models found.")

        else:
            # Build the company table.
            display_models = [
                {
                    "ID": model["id"],
                    "Name": model["name"],
                    "Price": model["price"]
                }
                for model in models
            ]

            # Two-column layout.
            left_column, right_column = st.columns([2, 1])

            with left_column:
                st.subheader("Companies")
                st.caption("Click a row to view its device models.")

                # Enable single-row selection.
                event = st.dataframe(
                    pd.DataFrame(display_models),
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="company_table"
                )

            # Read the currently selected row.
            selected_rows = event.selection.rows

            if selected_rows:
                selected_index = selected_rows[0]
                selected_company = models[selected_index]

                # Store the selection for other Streamlit reruns.
                st.session_state["selected_company_id"] = (
                    selected_company["id"]
                )

            else:
                # Preserve the last selection if the user clicks elsewhere.
                selected_company_id = st.session_state.get(
                    "selected_company_id"
                )

                selected_company = next(
                    (
                        model for model in models
                        if model["id"] == selected_company_id
                    ),
                    models[0]
                )

                st.session_state["selected_company_id"] = (
                    selected_company["id"]
                )

            # Display devices in the right-hand column.
            with right_column:
                st.subheader("Device Models")

                st.markdown(
                    f"**Company:** {selected_company['name']}"
                )

                device_names = selected_company.get("device_names", [])

                if device_names:
                    st.caption(f"Total devices: {len(device_names)}")

                    for index, device_name in enumerate(
                        device_names, start=1
                    ):
                        st.write(f"{index}. {device_name}")

                else:
                    st.info(
                        "No device models found for this company."
                    )

    except (requests.RequestException, ValueError, KeyError) as error:
        show_api_error(error)



with add_tab:
    st.subheader("Add a Mobile Model")

    with st.form("add_model_form", clear_on_submit=True):
        model_id = st.number_input(
            "Model ID",
            min_value=1,
            step=1,
        )
        model_name = st.text_input(
            "Model Name",
            max_chars=15,
        )
        model_price = st.number_input(
            "Price",
            min_value=1,
            step=1,
        )

        submitted = st.form_submit_button("Add Model")

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

with delete_tab:
    st.subheader("Delete a Mobile Model")

    with st.form("delete_model_form"):
        delete_id = st.number_input(
            "Model ID to delete",
            min_value=1,
            step=1,
        )

        delete_submitted = st.form_submit_button("Delete Model")

    if delete_submitted:
        try:
            response = requests.delete(
                f"{API_BASE_URL}/model/{int(delete_id)}/delete",
                timeout=REQUEST_TIMEOUT,
            )

            if response.ok:
                st.success("Delete request completed.")

                try:
                    st.json(response.json())
                except ValueError:
                    st.write(response.text)
            else:
                st.error(api_error_message(response))

        except requests.RequestException as error:
            show_api_error(error)

with file_tab:
    st.subheader("Upload a PDF for a Mobile Model")

    st.caption(
        "The PDF is stored in the database against the selected model ID. "
        f"Maximum upload size: {MAX_PDF_SIZE_MB} MB."
    )

    with st.form("pdf_upload_form"):
        upload_model_id = st.number_input(
            "Mobile Model ID",
            min_value=1,
            step=1,
            key="upload_model_id",
        )

        uploaded_pdf = st.file_uploader(
            "Choose PDF",
            type=["pdf"],
            key="uploaded_model_pdf",
        )

        upload_submitted = st.form_submit_button("Upload PDF")

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

    st.divider()
    st.subheader("Download a Stored PDF")

    with st.form("pdf_download_form"):
        download_model_id = st.number_input(
            "Mobile Model ID",
            min_value=1,
            step=1,
            key="download_model_id",
        )

        download_submitted = st.form_submit_button("Find PDF")

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
                st.session_state["stored_pdf_model_id"] = int(
                    download_model_id
                )

                st.success("PDF is ready to download.")
            else:
                st.session_state.pop("stored_pdf_bytes", None)
                st.session_state.pop("stored_pdf_name", None)
                st.error(api_error_message(response))

        except requests.RequestException as error:
            show_api_error(error)

    if "stored_pdf_bytes" in st.session_state:
        st.download_button(
            label="Download Stored PDF",
            data=st.session_state["stored_pdf_bytes"],
            file_name=st.session_state["stored_pdf_name"],
            mime="application/pdf",
            key="download_stored_pdf",
        )

with report_tab:
    st.subheader("Download the Generated PDF Report")

    st.write(
        "Generate or download the PDF report exposed by the FastAPI backend."
    )

    if st.button("Fetch PDF Report", key="fetch_pdf_report"):
        try:
            response = requests.get(
                f"{API_BASE_URL}/reports/pdf",
                timeout=REQUEST_TIMEOUT,
            )

            if response.ok:
                st.session_state["report_pdf_bytes"] = response.content
                st.success("PDF report is ready.")
            else:
                st.session_state.pop("report_pdf_bytes", None)
                st.error(api_error_message(response))

        except requests.RequestException as error:
            show_api_error(error)

    if "report_pdf_bytes" in st.session_state:
        st.download_button(
            label="Download mobile_models_report.pdf",
            data=st.session_state["report_pdf_bytes"],
            file_name="mobile_models_report.pdf",
            mime="application/pdf",
            key="download_generated_report",
        )
