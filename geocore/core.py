import ee
import json
import time
import datetime

import geocore.visuals as vis

def initialize():
    try:
        ee.Initialize()

    except ee.EEException:
        ee.Authenticate()
        ee.Initialize()

def createGeometry(shapedata: str) -> ee.Geometry:
    shape = json.loads(shapedata)

    coordinates = shape['features'][0]['geometry']['coordinates'][0]
    geometry = ee.Geometry.Polygon(coordinates)

    return geometry

def getDatePair():
    today = datetime.datetime.utcnow()
    past = today - datetime.timedelta(days=7)

    today = today.isoformat().split("T")[0]
    past = past.isoformat().split("T")[0]

    return past, today

def generateImage(geometry: ee.Geometry) -> ee.Image:
    dates = getDatePair()

    S2 = ee.ImageCollection("COPERNICUS/S2_SR").filterBounds(geometry).filterDate(dates[0], dates[1])
    image = S2.first()

    return image

def generateNDVI(image: ee.Image, geometry: ee.Geometry) -> ee.Image:
    values = {"NIR": image.select('B8'), "RED": image.select('B4')}
    image = image.expression("(NIR-RED)/(NIR+RED)", values).rename('NDVI')

    focalized = ee.Image(image).clip(geometry).toFloat().multiply(10).toInt().toFloat().focal_median(kernelType="square", radius=5)
    focalized = focalized.visualize(**vis.NDVIFOCAL)

    return focalized

def exportImage(image: ee.Image, geometry: ee.Geometry, name: str) -> ee.batch.Task:
    exportconfig = {
        "bucket": "terrascope-bucket",
        "scale": 1,
        "crs": "EPSG:4326",
        "maxPixels": 100000000,
        "fileFormat": "GeoTIFF",
        "skipEmptyTiles": True,
        "image": image,
        "description": f"export-{name}"[0:100],
        "fileNamePrefix": name,
        "region": geometry
    }

    task = ee.batch.Export.image.toCloudStorage(**exportconfig)
    return task

def startExport(task: ee.batch.Task) -> bool:
    task.start()

    while task.status()['state'] in ["READY", "RUNNING", "UNSUBMITTED"]: 
        time.sleep(5)
        continue

    return False if task.status['state'] != "COMPLETED" else True
