import os
import piexif
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point

def coordinate_parse(coord_exif, direction):
        """
        Parse piexif exif format to decimal lat or lon
        """

        deg = float(coord_exif[0][0]/coord_exif[0][1])
        minutes = float(coord_exif[1][0]/coord_exif[1][1])
        seconds = float(coord_exif[2][0]/coord_exif[2][1])

        out = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction in ['W', 'S'] else 1)

        return out

def extract_gps_coordinates(image_path):
    try:
        exif_data = piexif.load(image_path)

        lat_exif = exif_data['GPS'][2]
        lon_exif = exif_data['GPS'][4]

        latitude = coordinate_parse(lat_exif, exif_dict["GPS"][1].decode('UTF-8'))
        longitude = coordinate_parse(lon_exif, exif_dict["GPS"][3].decode('UTF-8'))
        
        return latitude, longitude

    except Exception as e:
        print(f"Error extracting GPS coordinates from {image_path}: {str(e)}")
        return None, None

def plot_gps_coordinates_in_folder(folder_path):
    image_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    latitudes = []
    longitudes = []

    for image_path in image_paths:
        lat, lon = extract_gps_coordinates(image_path)
        if lat and lon:
            latitudes.append(lat)
            longitudes.append(lon)

    if len(latitudes) == 0 or len(longitudes) == 0:
        print("No GPS coordinates found in the images in the folder.")
        return

    # Plot the GPS coordinates on a scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(longitudes, latitudes, color='blue', marker='o', label='GPS Coordinates')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('GPS Coordinates from GoPro Images in Folder')
    plt.legend()
    plt.grid(True)
    plt.show()
    
def create_geojson_from_images(folder_path, output_geojson_path):
    image_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    
    data = []
    
    for image_path in image_paths:
        lat, lon = extract_gps_coordinates(image_path)
        if lat and lon:
#             lat = float(lat[0]) / float(lat[1])
#             lon = float(lon[0]) / float(lon[1])
            data.append({'geometry': Point(lon, lat), 'properties': {'image_path': image_path}})

    if len(data) == 0:
        print("No GPS coordinates found in the images in the folder.")
        return

    gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
    gdf.to_file(output_geojson_path, driver="GeoJSON")

if __name__ == "__map_geotagged_images__":
    folder_path = "D:/DCIM_from_sd_card_1/101GOPRO"  # Path to image folder
    output_geojson_path = f"{folder_path}/path.geojson"  # Replace with the desired output GeoJSON file name
    
    create_geojson_from_images(folder_path, output_geojson_path)
#     plot_gps_coordinates_in_folder(folder_path)
