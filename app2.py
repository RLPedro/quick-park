import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

# Set page configuration (only once)
st.set_page_config(page_title="Location Map", page_icon="🌍", layout="wide")

def get_parking_data(app_id, latitude, longitude, radius, format, types_of_parking):
    parking_data = []
    for type_of_parking in types_of_parking:
        API_URL = f'https://data.goteborg.se/ParkingService/v2.3/{type_of_parking}/{app_id}?latitude={latitude}&longitude={longitude}&radius={radius}&format={format}'
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            parking_data.extend(data)
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {type_of_parking}: {e}")
    return parking_data

def get_coordinates(address):
    # Nominatim geocoding API
    geocode_api_url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
    response = requests.get(geocode_api_url)
    if response.status_code == 200:
        results = response.json()
        if results:
            lat = results[0]["lat"]
            lng = results[0]["lon"]
            return lat, lng
        else:
            st.error("Ingen adress hittades. Vänligen kontrollera och försök igen.")
            return None, None
    else:
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
    'Handikapsparkering': 'HandicapParkings',
    'MC-parkering': 'MCParkings',
}

# Välj typer av parkering med kryssrutor
selected_parking_types = []
for parking_type in types_of_parking.keys():
    if st.checkbox(parking_type):
        selected_parking_types.append(types_of_parking[parking_type])


# Användare skriver in en adress
address = st.text_input("Ange adress dit du ska åka:", placeholder="Gata och gatnummer, t.ex. Storgatan 1")

# Om adressen har angetts, hämta koordinater
if address:
    latitude, longitude = get_coordinates(address)

    # Hämta parkeringdata baserat på valt filter
    parking_data = []
    if latitude and longitude and selected_parking_types:
        # parking_data = get_parking_data(api_id, latitude, longitude, radius, format, selected_parking_types)
        for parking_type in selected_parking_types:
            parking_data.append(get_parking_data(api_id, latitude, longitude, radius, format, parking_type))
    else:
        parking_data = None

    # Skapa Folium-karta centrerad på den nya adressen
    gothenburg_map = folium.Map(location=[latitude, longitude], zoom_start=13, control_scale=True)

    # Lägg till parkering platser på kartan
    if parking_data:
        filtered_data = []
        for entry in parking_data:
            filtered_data.append(entry)
            folium.Marker(
                location=[entry["Lat"], entry["Long"]],
                popup=entry["Name"],
                icon=folium.Icon(icon="fa-parking", prefix="fa", color="blue")
            ).add_to(gothenburg_map)

    # Ändra bakgrunden till vit
    folium.TileLayer('CartoDB positron').add_to(gothenburg_map)

    # Visa kartan med Streamlit
    folium_static(gothenburg_map, 300, 400)

# Lägg till några styling och beskrivning
st.markdown("<h2 style='text-align: center;'>Parkeringsplatser i Göteborg</h2>", unsafe_allow_html=True)

# Visa information om antal tillgängliga parkeringsplatser
# if parking_data:
#     st.write(f"Totalt antal parkeringsplatser: {len(parking_data)}")
#     st.write(f"Antal parkeringsplatser som matchar kriterierna: {len(filtered_data)}")
# else:
#     st.write("Inga parkeringsdata tillgängliga. Kontrollera din adress och filterinställningar.")
