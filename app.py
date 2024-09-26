import streamlit as st
import requests
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static

# Set page configuration
st.set_page_config(page_title="Location Map", page_icon="🌍", layout="wide")

def get_parking_data(app_id, latitude, longitude, radius, format, type_of_parking):
    API_URL = f'https://data.goteborg.se/ParkingService/v2.3/{type_of_parking}/{app_id}?latitude={latitude}&longitude={longitude}&radius={radius}&format={format}'

    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        # st.write(f"{response.json()[5]}")
        # print(len(response.json()))
        # st.write(f"{(response.json())}")
        return response.json()  # Assuming the API returns JSON

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

api_id = '07e7edee-b61e-4252-920d-74e9d4b3091e'
# latitude = '57.684134935303085'
latitude = '57.7'
# longitude = '11.913471010871941'
longitude = '11.97'
radius = '1000'
format = 'JSON'
type_of_parking = 'HandicapParkings'


places_list_longitude = []
places_list_latitude = []
places_list_labels = []
types_of_parking = ["MCParkings", "HandicapParkings", "TruckParkings"]

locations = []
print(len(locations))

for parking in types_of_parking:
    for entry in get_parking_data(api_id, latitude, longitude, radius, format, type_of_parking):
        locations.append(
            {
                "name": entry["Name"],
                "longitude": entry["Long"],
                "latitude": entry["Lat"]
            }
        )


# Render the Plotly map using Streamlit
# st.plotly_chart(fig)

# Add a title to the Streamlit app
# st.markdown("# 🗺️ Scattergeo Locations Map")
# st.markdown("This map shows different locations using latitude and longitude.")

# Fetch the parking data
parking_data = get_parking_data(api_id, latitude, longitude, radius, format, type_of_parking)

# Create a Folium map centered on Gothenburg
gothenburg_map = folium.Map(location=[57.7, 11.97], zoom_start=13)

# Add parking locations to the map
# if parking_data:
#     for entry in parking_data:
#         folium.Marker(
#             location=[entry["Lat"], entry["Long"]],
#             popup=entry["Name"],
#             icon=folium.Icon(icon="fa-parking", prefix="fa", color="blue")
#         ).add_to(gothenburg_map)

for location in locations:
    folium.Marker(
        location=[location["latitude"], location["longitude"]],
        popup=location["name"],
        icon=folium.Icon(icon="fa-parking", prefix="fa", color="blue")
    ).add_to(gothenburg_map)


# Display the map using Streamlit
folium_static(gothenburg_map, 300, 400)

# Add some styling using markdown and CSS
# st.markdown("""
#     <style>
#         .subheader {
#             font-size:24px;
#             color: #4CAF50;
#             text-align: center;
#         }
#         .main {
#             text-align: center;
#             background-color: #ffffff;
#         }
#     </style>
# """, unsafe_allow_html=True)


# UI Elements
# st.markdown('<div class="main"><p class="subheader">Quick Parking</p></div>', unsafe_allow_html=True)
# st.markdown('<p class="subheader">Get Public Data Seamlessly</p>', unsafe_allow_html=True)
# st.markdown('<p class="center">White background?</p>', unsafe_allow_html=True)


# {APPID}: Applikationens GUID som fås från http://data.goteborg.se
# {LATITUDE}: Användarens latitud i decimalform, t.ex. 57.7. Frivilligt
# {LONGITUDE}: Användarens longitud i decimalform, t.ex. 11.9. Frivilligt
# {RADIUS}: Radie i meter inom vilken träffar returneras. Frivilligt
# {FORMAT}: Format på svaret, XML eller JSON. XML som standard om inget anges. Frivilligt
