"""
Terrascope GeoCore Library
"""
import ee
import os
import cv2
import json

def convert_GeoTIFF_TO_JPEG(geotiffpath: str, jpegpath: str):
    if not geotiffpath.endswith(".tif"):
        raise ValueError("Invalid path to GeoTIFF file. Must end with '.tif' extension.")

    if not jpegpath.endswith(".jpg"):
        raise ValueError("Invalid path to JPG file. Must end with '.jpg' extension.")

    if not os.path.isfile(geotiffpath):
        raise FileNotFoundError("Invalid path to GeoTIFF file. Does not exist!")

    geotiff = cv2.imread(geotiffpath)
    cv2.imwrite(jpegpath, geotiff, [int(cv2.IMWRITE_JPEG_QUALITY), 200])
    return

def generate_geometry(geojson: str) -> ee.Geometry:
    """ """
    geodata = json.loads(geojson)
    coordinates = geodata['features'][0]['geometry']['coordinates'][0]
    geometry = ee.Geometry.Polygon(coordinates)
    return geometry

def generate_image_identifier(image: ee.Image) -> str:
    """"""
    return f"COPERNICUS/S2_SR/{image.id().getInfo()}"