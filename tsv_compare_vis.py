import streamlit as st
import pandas as pd

# File upload function
def load_tsv(file):
    return pd.read_csv(file, sep='\t')

# Set the webpage title
st.title('Upload and Display TSV Files')

# Upload the first TSV file
st.sidebar.header("Upload the first TSV file")
uploaded_file_1 = st.sidebar.file_uploader("Choose the first TSV file", type=["tsv"])

# Upload the second TSV file
st.sidebar.header("Upload the second TSV file")
uploaded_file_2 = st.sidebar.file_uploader("Choose the second TSV file", type=["tsv"])

if uploaded_file_1 and uploaded_file_2:
    # Read the TSV files
    df1 = load_tsv(uploaded_file_1)
    df2 = load_tsv(uploaded_file_2)
    
    # Ensure the tables have the same columns
    if set(df1.columns) == {"Query", "Fidelity", "PUrl", "ImageUrl"} and set(df2.columns) == {"Query", "Fidelity", "PUrl", "ImageUrl"}:
        # Display the tables
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Left Table")
            st.dataframe(df1)
        with col2:
            st.subheader("Right Table")
            st.dataframe(df2)
    else:
        st.error("The uploaded files must contain the columns 'Query', 'Fidelity', 'PUrl', and 'ImageUrl'!")
else:
    st.warning("Please upload two TSV files.")
