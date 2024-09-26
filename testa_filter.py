import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

# Set page configuration
st.set_page_config(page_title="Location Map", page_icon="🌍", layout="wide")

def get_parking_data(app_id, latitude, longitude, radius, format, type_of_parking):
    API_URL = f'https://data.goteborg.se/ParkingService/v2.3/{type_of_parking}/{app_id}?latitude={latitude}&longitude={longitude}&radius={radius}&format={format}'
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

# API ID och positioner
api_id = '07e7edee-b61e-4252-920d-74e9d4b3091e'
latitude = '57.7'
longitude = '11.97'
radius = '1000'
format = 'JSON'

# Typer av parkering
types_of_parking = {
    'Handikapsparkering': 'HandicapParkings',
    'MC-parkering': 'MCParkings',
}

# Välj typ av parkering
selected_parking_type = st.multiselect("Välj typ av parkering:", list(types_of_parking.keys()))

# Tid för parkering (i timmar)
parking_duration = st.number_input("Ange hur länge du ska parkera (i timmar):", min_value=0, value=5)

# Distans till parkering (i meter)
# max_distance = st.number_input("Max distans till parkering (i meter):", min_value=0, value=1000)
radius = st.slider("slide",10,10000, 5000)

# Pris på parkering
max_price = st.number_input("Maxpris för parkering (i kronor):", min_value=0, value=20)

# Hämta parkeringdata baserat på valt filter
parking_data = get_parking_data(api_id, latitude, longitude, radius, format, types_of_parking[selected_parking_type])

# Skapa Folium-karta centrerad på Göteborg
gothenburg_map = folium.Map(location=[57.7, 11.97], zoom_start=13)

# Lägg till parkeringsplatser på kartan
if parking_data:
    filtered_data = []
    for entry in parking_data:
        # Filtrera baserat på användarens angivna kriterier (exempel)
        if (entry.get("Price", 0) <= max_price):
            filtered_data.append(entry)
            folium.Marker(
                location=[entry["Lat"], entry["Long"]],
                popup=entry["Name"],
                icon=folium.Icon(icon="fa-parking", prefix="fa", color="blue")
            ).add_to(gothenburg_map)

# Visa kartan med Streamlit
folium_static(gothenburg_map, 300, 400)

# Lägg till några styling och beskrivning
st.markdown("<h2 style='text-align: center;'>Parkeringsplatser i Göteborg</h2>", unsafe_allow_html=True)

# Visa information om antal tillgängliga parkeringsplatser
if parking_data:
    st.write(f"Totalt antal parkeringsplatser: {len(parking_data)}")
    st.write(f"Antal parkeringsplatser som matchar kriterierna: {len(filtered_data)}")
