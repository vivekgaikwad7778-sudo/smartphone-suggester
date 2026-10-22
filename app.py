import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Smartphone Suggester 2026",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern look
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e9ecef;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .badge {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)


# Load dataset safely with fallback dummy data structure if missing
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("smartphones.csv")
    except FileNotFoundError:
        # Sample dataset structure for demonstration/fallback
        data = {
            "model": [
                "Redmi Note 15 Pro", "OnePlus Nord CE 5", "Realme GT Neo 7", 
                "Samsung Galaxy A56", "iPhone 16", "OnePlus 13", 
                "Samsung Galaxy S25", "iPhone 17 Pro", "Google Pixel 10 Pro"
            ],
            "brand": [
                "Xiaomi", "OnePlus", "Realme", "Samsung", 
                "Apple", "OnePlus", "Samsung", "Apple", "Google"
            ],
            "price": [22000, 28000, 32000, 38000, 79900, 69999, 82999, 134900, 109999],
            "ram": [8, 8, 12, 8, 8, 16, 12, 12, 16],
            "storage": [128, 256, 256, 256, 128, 512, 256, 256, 512],
            "os": ["Android", "Android", "Android", "Android", "iOS", "Android", "Android", "iOS", "Android"]
        }
        df = pd.DataFrame(data)
    return df


df = load_data()

# Header Section
st.title("📱 Smartphone Suggester (2026 Edition)")
st.caption("Find and compare the best smartphones tailored to your specs, budget, and brand preferences.")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Options")

# 1. Budget Slider
max_price_in_data = int(df['price'].max()) if 'price' in df.columns else 170000
min_price_in_data = int(df['price'].min()) if 'price' in df.columns else 15000

budget = st.sidebar.slider(
    "Maximum Budget (₹)",
    min_value=min_price_in_data,
    max_value=max_price_in_data,
    value=min(60000, max_price_in_data),
    step=2500,
    format="₹%d"
)

# 2. Hardware Specs
col_sb1, col_sb2 = st.sidebar.columns(2)
with col_sb1:
    min_ram = st.selectbox("Min RAM", [4, 6, 8, 12, 16], index=2, format_func=lambda x: f"{x} GB")
with col_sb2:
    min_storage = st.selectbox("Min Storage", [64, 128, 256, 512, 1024], index=1, format_func=lambda x: f"{x} GB")

# 3. Brand Filter (if brand column exists)
if 'brand' in df.columns:
    all_brands = sorted(df['brand'].dropna().unique().tolist())
    selected_brands = st.sidebar.multiselect("Preferred Brands", options=all_brands, default=all_brands)
else:
    selected_brands = None

# 4. OS Filter (if os column exists)
if 'os' in df.columns:
    all_os = sorted(df['os'].dropna().unique().tolist())
    selected_os = st.sidebar.multiselect("Operating System", options=all_os, default=all_os)
else:
    selected_os = None

# 5. Sorting
sort_option = st.sidebar.selectbox(
    "Sort Results By",
    ["Price: Low to High", "Price: High to Low", "RAM: High to Low", "Storage: High to Low"]
)

# --- FILTER LOGIC ---
filtered_df = df[
    (df['price'] <= budget) & 
    (df['ram'] >= min_ram) & 
    (df['storage'] >= min_storage)
]

if selected_brands and 'brand' in df.columns:
    filtered_df = filtered_df[filtered_df['brand'].isin(selected_brands)]

if selected_os and 'os' in df.columns:
    filtered_df = filtered_df[filtered_df['os'].isin(selected_os)]

# Apply Sorting
if sort_option == "Price: Low to High":
    filtered_df = filtered_df.sort_values(by='price', ascending=True)
elif sort_option == "Price: High to Low":
    filtered_df = filtered_df.sort_values(by='price', ascending=False)
elif sort_option == "RAM: High to Low":
    filtered_df = filtered_df.sort_values(by='ram', ascending=False)
elif sort_option == "Storage: High to Low":
    filtered_df = filtered_df.sort_values(by='storage', ascending=False)


# --- MAIN CONTENT AREA ---

# Top Search Bar
search_query = st.text_input("🔎 Quick Search Model Name:", placeholder="e.g. Galaxy S25, iPhone...")
if search_query and 'model' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['model'].str.contains(search_query, case=False, na=False)]

st.divider()

# Dashboard Metrics
if not filtered_df.empty:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Matching Phones", len(filtered_df))
    m2.metric("Lowest Price", f"₹{filtered_df['price'].min():,}")
    m3.metric("Avg Price", f"₹{int(filtered_df['price'].mean()):,}")
    top_brand = filtered_df['brand'].mode()[0] if 'brand' in filtered_df.columns and not filtered_df['brand'].empty else "N/A"
    m4.metric("Top Available Brand", top_brand)
    
    st.divider()

    # View Mode Toggle (Card View vs Data Table)
    view_type = st.radio("Display Style:", ["📱 Card View", "📊 Detailed Table"], horizontal=True)

    if view_type == "📱 Card View":
        # Card Layout
        for _, row in filtered_df.iterrows():
            model_name = row.get('model', 'Smartphone')
            price_formatted = f"₹{row['price']:,}"
            ram_val = row.get('ram', 'N/A')
            storage_val = row.get('storage', 'N/A')
            brand_val = row.get('brand', '')
            os_val = row.get('os', '')

            with st.expander(f"**{model_name}** — **{price_formatted}**"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**Brand:** {brand_val} | **OS:** {os_val}")
                    st.markdown(f"""
                    <span class="badge">💾 {ram_val} GB RAM</span>
                    <span class="badge">📦 {storage_val} GB Storage</span>
                    <span class="badge">💰 {price_formatted}</span>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.metric(label="Price", value=price_formatted)

    else:
        # Table Layout
        display_df = filtered_df.copy()
        display_df['price'] = display_df['price'].apply(lambda x: f"₹{x:,}")
        st.dataframe(
            display_df, 
            use_container_width=True,
            hide_index=True
        )

    # Export CSV Option
    st.markdown("---")
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_data,
        file_name="smartphone_recommendations_2026.csv",
        mime="text/csv"
    )

else:
    st.warning("⚠️ No smartphones found matching your current filter criteria.")
    st.info("Try increasing your budget, relaxing RAM/Storage options, or selecting more brands from the sidebar.")