import streamlit as st
import pandas as pd
import os

# Set wide layout
st.set_page_config(page_title="Control VS Treatment", layout="wide")

st.title("Control VS Treatment")

# Data source dropdown
DATA_SOURCES = ["AUTD.tsv", "AUTD_Serp.tsv", "AUTD_Copilot.tsv"]
selected_file = st.selectbox("Select Data Source", DATA_SOURCES)

# Check if file exists
if not os.path.exists(selected_file):
    st.error(f"{selected_file} not found. Please place the TSV file in the project root directory.")
    st.stop()

# Read TSV
df = pd.read_csv(selected_file, sep="\t")

required_cols = {"Query", "MUrl", "PUrl", "Fidelity_Control", "Fidelity_Treatment",
                 "InL1WithoutSpaceV", "Experiment_InL1WithoutSpaceV"}

if not set(df.columns).issuperset(required_cols):
    st.error(f"The TSV is missing required columns: {', '.join(required_cols)}")
    st.stop()

# Group by Query
grouped = df.groupby("Query")
query_list = list(grouped.groups.keys())

# Initialize current Query index
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "current_file" not in st.session_state:
    st.session_state.current_file = selected_file

# Reset index if data source changed
if st.session_state.current_file != selected_file:
    st.session_state.idx = 0
    st.session_state.current_file = selected_file

# Previous / Next Query buttons
col_prev, col_next = st.columns([1, 1])
with col_prev:
    if st.button("⬅ Previous") and st.session_state.idx > 0:
        st.session_state.idx -= 1
with col_next:
    if st.button("Next ➡") and st.session_state.idx < len(query_list) - 1:
        st.session_state.idx += 1

# Current Query data
current_query = query_list[st.session_state.idx]
qdf = grouped.get_group(current_query)

st.subheader(f"Query: {current_query}  ({st.session_state.idx + 1}/{len(query_list)})")

# Display Fidelity
fidelity_control = qdf["Fidelity_Control"].iloc[0]
fidelity_treatment = qdf["Fidelity_Treatment"].iloc[0]
st.write(f"**Fidelity_Control:** {fidelity_control}")
st.write(f"**Fidelity_Treatment:** {fidelity_treatment}")

# Categorize for three columns
left = qdf[(qdf["InL1WithoutSpaceV"] == True) & (qdf["Experiment_InL1WithoutSpaceV"] == False)]
middle = qdf[(qdf["InL1WithoutSpaceV"] == True) & (qdf["Experiment_InL1WithoutSpaceV"] == True)]
right = qdf[(qdf["InL1WithoutSpaceV"] == False) & (qdf["Experiment_InL1WithoutSpaceV"] == True)]

# === Replace column + show_images logic with a single HTML flex container ===

def build_images_html(df, title, images_per_row=3, img_height=108):
    """返回单列（title + 网格图片）的 HTML 字符串"""
    html = f"<div style='padding-left:6px; padding-top:4px; padding-bottom:4px;'>"
    html += f"<h3 style='margin:4px 0 8px 0; font-size:16px;'>{title} ({len(df)})</h3>"

    # 按行切分
    rows = [df[i:i + images_per_row] for i in range(0, len(df), images_per_row)]
    for row in rows:
        html += "<div style='display:flex; gap:2px; margin-bottom:6px;'>"
        for _, r in row.iterrows():
            # 每个缩略图块
            html += (
                "<div style='flex:1; text-align:center; line-height:1; overflow:hidden;'>"
                f"<a href='{r['MUrl']}' target='_blank' style='display:inline-block'>"
                f"<img src='{r['MUrl']}' style='height:{img_height}px; width:auto; max-width:100%; border-radius:3px; display:block; margin:0 auto;' />"
                "</a>"
                f"<div style='font-size:11px; margin-top:4px; word-break:break-all;'>"
                f"<a href='{r['PUrl']}' target='_blank' style='font-size:11px; text-decoration:none;'>PUrl of Image</a>"
                "</div>"
                "</div>"
            )
        html += "</div>"

    html += "</div>"
    return html

# 生成三列各自的 HTML
col0_html = build_images_html(left, "Control", images_per_row=3, img_height=108)
col1_html = build_images_html(middle, "Control & Treatment", images_per_row=3, img_height=108)
col2_html = build_images_html(right, "Treatment", images_per_row=3, img_height=108)

# 最外层 flex 容器：三等分，每列前两列带右边框
full_html = (
    "<div style='display:flex; gap:8px; align-items:flex-start;'>"
    f"<div style='width:33%; box-sizing:border-box; border-right:2px solid #dcdcdc; padding-right:8px;'>{col0_html}</div>"
    f"<div style='width:33%; box-sizing:border-box; border-right:2px solid #dcdcdc; padding-right:8px;'>{col1_html}</div>"
    f"<div style='width:34%; box-sizing:border-box;'>{col2_html}</div>"
    "</div>"
)

st.markdown(full_html, unsafe_allow_html=True)
