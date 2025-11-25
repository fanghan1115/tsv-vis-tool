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

col1, col2, col3 = st.columns(3)

def show_images(df, col, title):
    col.markdown(f"### {title} ({len(df)})")
    for _, r in df.iterrows():
        # Image clickable to open MUrl
        col.markdown(f"[![image]({r['MUrl']})]({r['MUrl']})")
        # Display PUrl as hyperlink
        col.markdown(f"[PUrl of Image]({r['PUrl']})")

show_images(left, col1, "Control")
show_images(middle, col2, "Control & Treatment")
show_images(right, col3, "Treatment")