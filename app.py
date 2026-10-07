import pandas as pd
import streamlit as st

st.title("📱 Smartphone Suggester (2026 Edition)")
st.write("Find the best budget or flagship smartphone matching your requirements!")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("smartphones.csv")

df = load_data()

# User Inputs via Streamlit Widgets (Expanded range for 2026 models)
budget = st.slider("Maximum Budget (₹)", min_value=15000, max_value=170000, value=60000, step=5000)
min_ram = st.selectbox("Minimum RAM (GB)", [4, 6, 8, 12, 16], index=2)
min_storage = st.selectbox("Minimum Storage (GB)", [64, 128, 256, 512], index=1)

# Filter logic
suggestions = df[
    (df['price'] <= budget) & 
    (df['ram'] >= min_ram) & 
    (df['storage'] >= min_storage)
].sort_values(by='price', ascending=True)

# Display Results
if st.button("Search Smartphones"):
    if suggestions.empty:
        st.warning("No smartphones found matching your criteria. Try adjusting your filters!")
    else:
        st.success(f"Found {len(suggestions)} matching smartphone(s):")
        # Format price column with a Rupee symbol for display
        display_df = suggestions.copy()
        display_df['price'] = display_df['price'].apply(lambda x: f"₹{x:,}")
        st.dataframe(display_df, use_container_width=True)