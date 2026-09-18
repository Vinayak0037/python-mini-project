import streamlit as st

# Page Configuration
st.set_page_config(page_title="Food Redistribution", page_icon="🌱")

# Main Title
st.title("🌱 Food Surplus Distribution Network")
st.write("Connecting restaurants with local shelters to prevent food waste.")

# Session State Initialization
if "donations" not in st.session_state:
    st.session_state.donations = [
        {"item": "Veg Biryani", "qty": 25, "hours": 2},
        {"item": "Sandwiches", "qty": 15, "hours": 4}
    ]

# Navigation Tabs
donor_tab, shelter_tab = st.tabs(["🏪 Donor Portal", "🏠 Shelter Portal"])

# 1. DONOR TAB
with donor_tab:
    st.header("Log Leftover Food")
    food_item = st.text_input("Food Item Name", "Paneer Gravy")
    quantity = st.number_input("Number of Portions", min_value=1, value=10)
    hours = st.slider("Hours since cooked", min_value=1, max_value=12, value=2)

    if hours >= 5:
        st.error("⚠️ High Priority: This food will expire soon!")
    else:
        st.success("✅ Food is fresh and safe for pickup.")

    if st.button("Submit Donation"):
        st.session_state.donations.append({"item": food_item, "qty": quantity, "hours": hours})
        st.success(f"Successfully logged {quantity} portions of {food_item}!")

# 2. SHELTER TAB
with shelter_tab:
    st.header("Available Food Near You")
    for index, entry in enumerate(st.session_state.donations):
        st.subheader(f"🍱 {entry['item']}")
        st.write(f"**Quantity:** {entry['qty']} meals | **Cooked:** {entry['hours']} hours ago")
        if st.button(f"Claim Item #{index + 1}"):
            st.info(f"You claimed {entry['item']}!")