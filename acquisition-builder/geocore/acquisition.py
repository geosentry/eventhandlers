"""
Terrascope GeoCore Package
"""
import ee
import datetime

def filter_coverage(collection: ee.ImageCollection, geometry: ee.Geometry) -> ee. ImageCollection:
    """
    A function that returns an Earth Engine ImageCollection that has been filtered such that every 
    Image in a given ImageCollection has full coverage for a given Earth Engine Geometry.

    This coverage filter is performed by assigning a coverage value to each image 
    which is value between 0-100 that represents the percentage of geometry coverage 
    in that image. The collection is then filtered based on this value.
    """
    # Assign a coverage value to each Image in the ImageCollection
    collection = collection.map(lambda image: image.set({
        "coverage": ee.Number.expression("100-(((expected-actual)/expected)*100)", {
            "expected": geometry.area(5), 
            "actual": image.clip(geometry).geometry().area(5)
        })
    }))

    # Filter the collection to only have Images with 100% coverage
    collection = collection.filter(ee.Filter.eq("coverage", 100))
    # Return the filtered collection
    return collection

def generate_latest_date(geometry: ee.Geometry) -> datetime.dateime:
    """
    A function that returns a datetime object that represents date of the latest 
    available Sentinel-2 L2A acquisition for the given Earth Engine Geometry.
    """
    from geocore import temporal

    # Generate daterange spanning a week prior to the current date
    today = datetime.datetime.utcnow()
    weekrange = temporal.generate_daterange(date=today, days=7)

    # Define an ImageCollection for Sentinel-2 MSI L2A
    collection = ee.ImageCollection("COPERNICUS/S2_SR")
    # Filter the ImageCollection for the given geometry and the weekrange
    collection = collection.filterBounds(geometry).filterDate(*weekrange)

    # Generate a datelist for the filtered collection
    datelist = temporal.generate_datelist(collection)
    # Return the latest date from the datelist
    return datelist[-1]

def generate_latest_image(date: datetime.datetime, geometry: ee.Geometry) -> ee.Image:
    """
    A function that returns an Earth Engine Image that represents the latest available
    Sentinel-2 L2A acquisition by for the given Earth Engine Geometry by accepting an 
    expected acquisiton date value and creating a buffer around that date.

    The buffered date range is used to filter Images which are then tested for geometry
    coverage to ensure that the Image fully cover the given Geometry.
    """
    from geocore import temporal

    # Generate a daterange spanning a 1 day before and after the given date
    daybuffer = temporal.generate_datebuffer(date=date, buffer=1)

    # Define an ImageCollection for Sentinel-2 MSI L2A
    collection = ee.ImageCollection("COPERNICUS/S2_SR")
    # Filter the ImageCollection for the given geometry and the daybuffer
    collection = collection.filterBounds(geometry).filterDate(*daybuffer)

    # Filter the ImageCollection based on geometry coverage
    filtered_collection = filter_coverage(collection, geometry)
    # Return the first Image from the filtered ImageCollection
    return filtered_collection.first()
