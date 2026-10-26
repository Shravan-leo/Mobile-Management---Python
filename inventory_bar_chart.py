import streamlit as st
import streamlit.components.v1 as components

# Distinct color palette matching your design reference (Amber, Green, Dark Slate, Red, Blue)
BAR_COLORS = [
    "#F59E0B",  # Amber / Orange
    "#10B981",  # Emerald Green
    "#1E293B",  # Dark Slate
    "#EF4444",  # Coral Red
    "#3B82F6",  # Royal Blue
    "#8B5CF6",  # Vivid Purple
]

def render_horizontal_device_chart(
    models_data: list[dict],
    title: str = "Inventory Status",
    subtitle: str = "Stock levels by category",
    max_capacity: int = 10,
):
    """
    Renders a styled container where each model name is a sub-heading
    and a horizontal colored bar below shows the device count ratio.
    """
    if not models_data:
        st.info("No models found to display chart.")
        return

    highest = max([int(m.get("device_count", 0)) for m in models_data] + [1])
    denominator = max(max_capacity, highest)

    rows_html = ""
    for idx, item in enumerate(models_data):
        name = str(item.get("name", "UNKNOWN")).upper()
        count = int(item.get("device_count", 0))
        pct = min(max((count / denominator) * 100, 0), 100)
        color = BAR_COLORS[idx % len(BAR_COLORS)]

        rows_html += f"""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
                <span style="font-size: 15px; font-weight: 600; color: #1E293B;">{name}</span>
                <span style="font-size: 14px; font-weight: 500; color: #64748B;">{count}/{denominator}</span>
            </div>
            <div style="width: 100%; background-color: #EEF2F6; border-radius: 9999px; height: 10px; overflow: hidden;">
                <div style="width: {pct:.1f}%; background-color: {color}; height: 100%; border-radius: 9999px;"></div>
            </div>
        </div>
        """

    card_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 4px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: transparent;
            }}
            .card {{
                background-color: #FFFFFF;
                padding: 24px 28px;
                border-radius: 14px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div style="font-size: 20px; font-weight: 700; color: #0F172A; margin-bottom: 4px;">{title}</div>
            <div style="font-size: 14px; color: #64748B; margin-bottom: 24px;">{subtitle}</div>
            {rows_html}
        </div>
    </body>
    </html>
    """

    dynamic_height = 120 + (len(models_data) * 64)
    components.html(card_html, height=dynamic_height, scrolling=False)