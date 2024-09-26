import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
import time
import urllib.parse

# Set page configuration (only once)
st.set_page_config(page_title="QuickPark", page_icon="🅿️", layout="wide")

# Inject custom CSS for a softer baby blue background, black text, and improved styling for input fields
st.markdown(
    """
    <style>
    /* Set the background color to a softer baby blue */
    .stApp {
        background-color: #87CEEB;  /* Softer baby blue color */
        color: black;
    }
    
    /* Make input fields and dropdowns white with black text */
    input, .stNumberInput input, .stTextInput, .stSlider, select, textarea {
        # background-color: white;
        color: black;
        # border: 1px solid #E0F7FA; /* Softens the edges */
    }
    
    /* Style sliders */
    .stSlider > div > div {
        background-color: white;
    }
    
    /* Style the placeholder (example address) in light gray */
    input::placeholder {
        color: lightgray;
    }

     /* Style sliders to match the app's background */
    .stSlider > div > div {
        background-color: #87CEEB; /* Match the app's background */
    }
    
    
    /* Style for the dropdown (for the type of parking) */
    .stSelectbox select {
        background-color: white
        color: black
        border: 1px solid #E0F7FA /* Soft edges */
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# Lägg till några styling och beskrivning
st.markdown("<h2 style='text-align: center;'>QuickPark</h2>", unsafe_allow_html=True)

def get_parking_data(app_id, latitude, longitude, radius, format, type_of_parking):
    API_URL = f'https://data.goteborg.se/ParkingService/v2.3/{type_of_parking}/{app_id}?latitude={latitude}&longitude={longitude}&radius={radius}&format={format}'
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

def get_coordinates(address, retries=3):
    encoded_address = urllib.parse.quote(address)
    geocode_api_url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"

    headers = {
        'User-Agent': 'quick-park'
    }

    for attempt in range(retries):
        time.sleep(1)
        response = requests.get(geocode_api_url, headers=headers)
        
        if response.status_code == 200:
            results = response.json()
            if results:
                lat = float(results[0]["lat"])
                lng = float(results[0]["lon"])
                return lat, lng
            else:
                st.error("Ingen adress hittades. Vänligen kontrollera och försök igen.")
                return None, None
        else:
            st.warning(f"Försök {attempt + 1} misslyckades. Försöker igen...")
            time.sleep(1)  # Wait 1 second before retrying

    st.error("Fel vid anrop till geokodningstjänsten.")
    return None, None


# API ID och initiala positioner
api_id = '07e7edee-b61e-4252-920d-74e9d4b3091e'
latitude = '57.7'
longitude = '11.97'
radius = '1000'
format = 'JSON'

# Typer av parkering
types_of_parking = {
    'Street parkings': 'PublicTimeParkings',
    'Parking garages': 'PrivateTollParkings',
    'Residential parkings': 'ResidentialParkings',
    'Motorcycle parking': 'MCParkings',
    'Truck parking': 'TruckParkings',
    'Handicap parking': 'HandicapParkings',
}

# Välj typ av parkering
selected_parking_type = st.selectbox("Choose type of parking:", list(types_of_parking.keys()))

# Tid för parkering (i timmar)
parking_duration = st.number_input("Duration of parking (in hours):", min_value=0, value=5)

# Radius (distans till parkering i meter)
radius = st.slider("Maximum distance to location (in meters):", 10, 10000, 1000)

# Pris på parkering
max_price = st.number_input("Maximum price for parking (in kronor):", min_value=0, value=50)

# Användare skriver in en adress
address = st.text_input("Enter the address you want to park in:", placeholder="Street and number, f.ex. Storgatan 1, Göteborg")

# Om adressen har angetts, hämta koordinater
if address:
    latitude, longitude = get_coordinates(address)

# Hämta parkeringdata baserat på valt filter
if latitude and longitude:
    parking_data = get_parking_data(api_id, latitude, longitude, radius, format, types_of_parking[selected_parking_type])
else:
    parking_data = None

# Skapa Folium-karta centrerad på Göteborg
gothenburg_map = folium.Map(location=[latitude, longitude], zoom_start=13)

cost = '10 kronor'

# Lägg till parkeringsplatser på kartan
if parking_data:
    filtered_data = []
    for entry in parking_data:
        if (entry.get("Price", 0) <= max_price):
            filtered_data.append(entry)
            folium.Marker(
                location=[entry["Lat"], entry["Long"]],
                # popup=entry["Name"],
                popup=f"{entry["Name"]} 20 kr/h",
                icon=folium.Icon(icon="fa-parking", prefix="fa", color="blue")
            ).add_to(gothenburg_map)

# Visa kartan med Streamlit
folium_static(gothenburg_map, 360, 400)

# Visa information om antal tillgängliga parkeringsplatser
if parking_data:
    st.write(f"Total existent parking spots: {len(parking_data)}")
    st.write(f"Parking spots matching desired criteria: {len(filtered_data)}")
else:
    st.write("No parking spots available. Check your address and filtering criteria.")

