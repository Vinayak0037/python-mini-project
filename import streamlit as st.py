import streamlit as st
import datetime
import pandas as pd
from supabase import create_client, Client
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Food Redistribution Network", page_icon="🌱", layout="wide")

# Connect to Supabase using Streamlit Secrets
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# Free geocoder to turn text addresses into map coordinates
@st.cache_data(show_spinner=False)
def get_coordinates(address):
    try:
        geolocator = Nominatim(user_agent="food_redistribution_app")
        location = geolocator.geocode(address, timeout=5)
        if location:
            return location.latitude, location.longitude
    except Exception:
        pass
    return None, None

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
        pickup_address = st.text_area("Pickup Address (Include City for Map Pin)", "FC Road, Pune, Maharashtra")
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
                drop_loc = st.text_input("Drop-off Address (Include City)", "Kothrud, Pune", key=f"d_{item['id']}")
                if st.button("Claim Food", key=f"b_{item['id']}"):
                    supabase.table("donations").update({
                        "status": "Claimed",
                        "drop_address": f"{shelter_name} - {drop_loc}",
                        "people_count": residents
                    }).eq("id", item["id"]).execute()
                    st.success("Claimed!")
                    st.rerun()
            else:
                st.info("🔒 Claimed")
        st.divider()

# 3. DELIVERY CHAIN TRACKER (WITH LIVE MAP)
with logistics_tab:
    st.subheader("🚚 Active Route & Live Delivery Map")
    claimed = [d for d in donations if d["status"] == "Claimed"]

    map_points = []
    for item in donations:
        p_lat, p_lon = get_coordinates(item["pickup_address"])
        if p_lat and p_lon:
            map_points.append({"lat": p_lat, "lon": p_lon, "type": "Pickup", "name": item["donor"]})
        if item["status"] == "Claimed":
            clean_drop = item["drop_address"].split(" - ")[-1]
            d_lat, d_lon = get_coordinates(clean_drop)
            if d_lat and d_lon:
                map_points.append({"lat": d_lat, "lon": d_lon, "type": "Drop-off", "name": item["drop_address"]})

    if map_points:
        st.map(pd.DataFrame(map_points), zoom=11)
        st.caption("Showing live pins for active restaurant pickups and shelter drop-offs.")
    else:
        st.info("Add recognizable street/city addresses (e.g., 'FC Road, Pune') to see live pins on the map.")

    st.divider()
    if not claimed:
        st.info("No active deliveries right now. Claim a donation in the Shelter tab to see routes!")
    for item in claimed:
        st.markdown(f"**Route #{item['id']}:** `{item['donor']}` ({item['pickup_address']}) ➔ `{item['drop_address']}`")
        st.write(f"• **Meals:** {item['qty']} portions for {item['people_count']} residents | **ETA:** {item['drop_time']}")
        st.divider()

# 4. IMPACT DASHBOARD (WITH CHARTS & CSV EXPORT)
with analytics_tab:
    st.subheader("📊 Live Community & Sustainability Impact")
    if not donations:
        st.info("No donation data available yet to generate analytics.")
    else:
        df = pd.DataFrame(donations)
        tot_meals = int(df["qty"].sum())
        tot_people = int(df[df["status"] == "Claimed"]["people_count"].sum())
        food_saved_kg = round(tot_meals * 0.45, 1)  # ~450g per meal rescued
        co2_prevented_kg = round(food_saved_kg * 2.5, 1)  # ~2.5 kg CO2e saved per kg food waste

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Meals Logged", tot_meals)
        m2.metric("People Fed in Shelters", tot_people)
        m3.metric("Food Waste Diverted", f"{food_saved_kg} kg")
        m4.metric("CO₂ Emissions Saved", f"{co2_prevented_kg} kg")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🏢 Meals Contributed by Donor")
            donor_chart = df.groupby("donor")["qty"].sum()
            st.bar_chart(donor_chart, color="#2e7d32")
        with c2:
            st.markdown("#### 📦 Donation Status Breakdown")
            status_chart = df.groupby("status")["qty"].sum()
            st.bar_chart(status_chart, color="#ef6c00")

        st.divider()
        st.markdown("#### 📄 Full Audit Log & CSR Export")
        display_cols = ["id", "donor", "item", "qty", "status", "pickup_address", "drop_address", "people_count", "drop_time"]
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

        csv_data = df[available_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Impact Report (CSV)",
            data=csv_data,
            file_name="food_redistribution_impact_report.csv",
            mime="text/csv",
            type="primary"
        )
