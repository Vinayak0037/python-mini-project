import streamlit as st
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Food Redistribution Network",
    page_icon="🌱",
    layout="wide"
)

# --- INITIALIZE DEMO DATA ---
if "donations" not in st.session_state:
    st.session_state.donations = [
        {
            "id": 1,
            "item": "Veg Biryani & Gravy",
            "qty": 50,
            "donor": "Grand Hotel",
            "pickup_address": "123 Main St, Downtown",
            "drop_address": "Hope Shelter, 45 Park Rd",
            "shelter_type": "Orphanage",
            "people_count": 45,
            "drop_time": "08:30 PM",
            "status": "Available"
        },
        {
            "id": 2,
            "item": "Fresh Bread & Pastries",
            "qty": 30,
            "donor": "City Bakery",
            "pickup_address": "88 Bakery Lane, West End",
            "drop_address": "Sunshine Old Age Home, 12 Lakeview",
            "shelter_type": "Old Age Home",
            "people_count": 28,
            "drop_time": "09:15 PM",
            "status": "Claimed"
        }
    ]

# --- APP HEADER ---
st.title("🌱 Food Surplus Redistribution Network")
st.caption("Connecting food donors directly with shelters, orphanages, and old age homes.")
st.divider()

# --- TABS ---
donor_tab, shelter_tab, logistics_tab, analytics_tab = st.tabs([
    "🏪 Donor Portal", 
    "🏠 Shelter Requirements", 
    "🚚 Delivery Chain Tracker",
    "📊 Impact Dashboard"
])

# ==========================================
# 1. DONOR PORTAL
# ==========================================
with donor_tab:
    st.subheader("Log Surplus Food for Pickup")
    
    col1, col2 = st.columns(2)
    with col1:
        donor_name = st.text_input("Donor / Business Name", "Spice Garden Bistro")
        food_item = st.text_input("Food Item Details", "Mixed Meal Boxes")
        pickup_address = st.text_area("Pickup Address", "72 Commercial Street, Sector 4")
        
    with col2:
        quantity = st.number_input("Portions / Meals Available", min_value=1, value=30)
        target_shelter_type = st.selectbox("Preferred Recipient Type", ["Any", "Orphanage", "Old Age Home", "Community Kitchen", "Shelter"])
        estimated_drop = st.time_input("Expected Pickup/Drop Time", datetime.time(20, 0))

    if st.button("🚀 Submit Food Donation", type="primary"):
        new_entry = {
            "id": len(st.session_state.donations) + 1,
            "item": food_item,
            "qty": quantity,
            "donor": donor_name,
            "pickup_address": pickup_address,
            "drop_address": "Pending Claim",
            "shelter_type": target_shelter_type,
            "people_count": 0,
            "drop_time": estimated_drop.strftime("%I:%M %p"),
            "status": "Available"
        }
        st.session_state.donations.append(new_entry)
        st.success("Donation logged! Shelters can now view and claim this delivery.")

# ==========================================
# 2. SHELTER PORTAL & CAPACITY
# ==========================================
with shelter_tab:
    st.subheader("Available Donations for Shelters & Homes")
    
    for item in st.session_state.donations:
        with st.container():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"### 🍱 {item['item']}")
                st.write(f"🏢 **Donor:** {item['donor']} | 📍 **Pickup Location:** {item['pickup_address']}")
                st.write(f"📦 **Quantity:** {item['qty']} meals | 🕒 **Estimated Drop Time:** {item['drop_time']}")
                
                if item["status"] == "Claimed":
                    st.write(f"🎯 **Destination:** {item['drop_address']} (Capacity: {item['people_count']} residents)")
            
            with c2:
                if item["status"] == "Available":
                    st.write("**Claim details:**")
                    shelter_name = st.text_input("Your Shelter Name", key=f"s_name_{item['id']}")
                    residents = st.number_input("Current Residents Count", min_value=1, value=25, key=f"res_{item['id']}")
                    drop_loc = st.text_input("Drop-off Address", key=f"drop_{item['id']}")
                    
                    if st.button("Claim Food", key=f"btn_{item['id']}"):
                        item["status"] = "Claimed"
                        item["drop_address"] = f"{shelter_name} ({drop_loc})"
                        item["people_count"] = residents
                        st.success("Successfully claimed!")
                        st.rerun()
                else:
                    st.info("🔒 Claimed")
            st.divider()

# ==========================================
# 3. DELIVERY CHAIN TRACKER
# ==========================================
with logistics_tab:
    st.subheader("🚚 Active Route & Delivery Chain")
    
    for item in st.session_state.donations:
        if item["status"] == "Claimed":
            st.markdown(f"**Route #{item['id']}:** `{item['donor']}` ➔ `{item['drop_address']}`")
            st.write(f"• **Meals Transported:** {item['qty']} portions for {item['people_count']} residents")
            st.write(f"• **Scheduled Arrival:** {item['drop_time']}")
            st.info("Status: Delivery in progress / En Route")
            st.divider()

# ==========================================
# 4. IMPACT DASHBOARD
# ==========================================
with analytics_tab:
    st.subheader("📊 Community Impact")
    tot_meals = sum(d["qty"] for d in st.session_state.donations)
    tot_people = sum(d["people_count"] for d in st.session_state.donations if d["status"] == "Claimed")
    
    m1, m2 = st.columns(2)
    m1.metric("Total Meals Allocated", tot_meals)
    m2.metric("People Fed in Shelters/Homes", tot_people)