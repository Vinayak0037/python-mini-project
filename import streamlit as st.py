import streamlit as st
import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Food Redistribution Network", page_icon="🌱", layout="wide")

# Connect to Supabase using Streamlit Secrets
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# Fetch live donations from database
def get_donations():
    response = supabase.table("donations").select("*").order("id", desc=True).execute()
    return response.data

st.title("🌱 Food Surplus Redistribution Network")
st.caption("Connecting food donors directly with shelters, orphanages, and old age homes.")
st.divider()

donor_tab, shelter_tab, logistics_tab, analytics_tab = st.tabs([
    "🏪 Donor Portal",
    "🏠 Shelter Requirements",
    "🚚 Delivery Chain Tracker",
    "📊 Impact Dashboard"
])

# 1. DONOR PORTAL
with donor_tab:
    st.subheader("Log Surplus Food for Pickup")
    col1, col2 = st.columns(2)
    with col1:
        donor_name = st.text_input("Donor / Business Name", "Spice Garden Bistro")
        food_item = st.text_input("Food Item Details", "Mixed Meal Boxes")
        pickup_address = st.text_area("Pickup Address", "72 Commercial Street, Sector 4")
    with col2:
        quantity = st.number_input("Portions / Meals Available", min_value=1, value=30)
        estimated_drop = st.time_input("Expected Pickup/Drop Time", datetime.time(20, 0))

    if st.button("🚀 Submit Food Donation", type="primary"):
        supabase.table("donations").insert({
            "item": food_item,
            "qty": quantity,
            "donor": donor_name,
            "pickup_address": pickup_address,
            "drop_address": "Pending Claim",
            "people_count": 0,
            "drop_time": estimated_drop.strftime("%I:%M %p"),
            "status": "Available"
        }).execute()
        st.success("Saved permanently to database! Shelters can now claim this.")
        st.rerun()

# Load live data
donations = get_donations()

# 2. SHELTER PORTAL
with shelter_tab:
    st.subheader("Available Donations for Shelters & Homes")
    if not donations:
        st.info("No donations logged yet. Add one in the Donor Portal!")
    for item in donations:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"### 🍱 {item['item']}")
            st.write(f"🏢 **Donor:** {item['donor']} | 📍 **Pickup:** {item['pickup_address']}")
            st.write(f"📦 **Quantity:** {item['qty']} meals | 🕒 **Drop Time:** {item['drop_time']}")
            if item["status"] == "Claimed":
                st.write(f"🎯 **Destination:** {item['drop_address']} (Capacity: {item['people_count']} residents)")
        with c2:
            if item["status"] == "Available":
                shelter_name = st.text_input("Shelter Name", key=f"s_{item['id']}")
                residents = st.number_input("Residents Count", min_value=1, value=25, key=f"r_{item['id']}")
                drop_loc = st.text_input("Drop-off Address", key=f"d_{item['id']}")
                if st.button("Claim Food", key=f"b_{item['id']}"):
                    supabase.table("donations").update({
                        "status": "Claimed",
                        "drop_address": f"{shelter_name} ({drop_loc})",
                        "people_count": residents
                    }).eq("id", item["id"]).execute()
                    st.success("Claimed!")
                    st.rerun()
            else:
                st.info("🔒 Claimed")
        st.divider()

# 3. DELIVERY CHAIN TRACKER
with logistics_tab:
    st.subheader("🚚 Active Route & Delivery Chain")
    claimed = [d for d in donations if d["status"] == "Claimed"]
    if not claimed:
        st.info("No active deliveries right now.")
    for item in claimed:
        st.markdown(f"**Route #{item['id']}:** `{item['donor']}` ➔ `{item['drop_address']}`")
        st.write(f"• **Meals:** {item['qty']} portions for {item['people_count']} residents | **ETA:** {item['drop_time']}")
        st.divider()

# 4. IMPACT DASHBOARD
with analytics_tab:
    st.subheader("📊 Live Community Impact")
    tot_meals = sum(d["qty"] for d in donations)
    tot_people = sum(d["people_count"] for d in donations if d["status"] == "Claimed")
    m1, m2 = st.columns(2)
    m1.metric("Total Meals Logged", tot_meals)
    m2.metric("People Fed in Shelters/Homes", tot_people)
