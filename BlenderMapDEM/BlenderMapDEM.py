# Import Packages
from PIL import Image
import requests
import os
import re
import subprocess
import fiona
import matplotlib.pyplot as plt
import numpy as np

import rasterio
from rasterio.plot import show, show_hist
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask

# Fetch DEM .GeoTIFF image of user specified extent
def fetchDEM(north_bound: float, south_bound: float, east_bound: float, west_bound: float, API_Key: str, output_dir: str, dataset: str = 'SRTMGL1'):
    """
    Uses the OpenTopography API in order to fetch a .GeoTIFF raster image containing DEM of chosen extent
    
    Parameters:
        north_bound (float): Latitude coordinate of the northern bound of chosen DEM extent
        south_bound (float): Latitude coordinate of the southern bound of chosen DEM extent
        east_bound (float): Longitude coordinate of the eastern bound of chosen DEM extent
        west_bound (float): Longitude coordinate of the western bound of chosen DEM extent
        API_Key (string): OpenTopography API key that is needed to fetch data
        output_dir (string): The path to the output image file including file extension
    """

    # Declare possible DEM datasets
    possible_datasets = ['SRTMGL3',
                         'SRTMGL1',
                         'SRTMGL1_E',
                         'AW3D30',
                         'AW3D30_E',
                         'SRTM15Plus',
                         'NASADEM',
                         'COP30',
                         'COP90',
                         'EU_DTM',
                         'GEDI_L3']
    
        ### --- Catch a variety of user-input errors --- ###
    
    # Check for invalid input parameter datatypes
    if type(north_bound) != float:
        raise TypeError('north_bound is not of type float, please input a float.')
    elif type(south_bound) != float:
        raise TypeError('south_bound is not of type float, please input a float.')
    elif type(east_bound) != float:
        raise TypeError('east_bound is not of type float, please input a float.')
    elif type(west_bound) != float:
        raise TypeError('west_bound is not of type float, please input a float.')
    elif type(API_Key) != str:
        raise TypeError('API_Key is not of type string, please input a string.')
    elif type(output_dir) != str:
        raise TypeError('output_dir is not of type string, please input a string.')
    elif type(dataset) != str:
        raise TypeError('dataset is not of type string, please input a string.')
    
    # Check for invalid characters in output directory
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(output_dir):
        raise ValueError('Output directory contains invalid characters.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError(f'Output file path "{output_dir}" does not exist, please create it.')
    if not output_dir.endswith(('.tif','.tiff')):
        raise ValueError(f'Invalid output filetype "{output_dir}", make sure output_dir argument ends with ".tif"')
    
    # Raise error if dataset specified by user is not one of the available DEM datasets offered by OpenTopography
    if dataset not in possible_datasets:
        raise ValueError(f'Invalid dataset: "{dataset}" not present in available datasets offered by OpenTopography, see documentation for a list of available datasets')
    
    # Raise errors if invalid bounds were given by user
    if (north_bound > 90 or south_bound > 90) or (north_bound < -90 or south_bound < -90):
        raise ValueError('The values for north/south bounds must fall between -90 and 90')
    elif (north_bound < south_bound):
        raise ValueError('The north bound must be greater than the south bound')
    elif (east_bound > 180 or west_bound > 180) or (east_bound < -180 or west_bound < -180):
        raise ValueError('The values for east/west bounds must fall between -180 and 180')
    elif (east_bound < west_bound):
        raise ValueError('The east bound must be greater than the west bound')
    
        ### --- Download DEM data from OpenTopography --- ###
    
    try:
        # Query the OpenTopography API to download .GeoTiff of DEM according to user parameters
        url = 'https://portal.opentopography.org/API/globaldem?demtype='+dataset+'&south='+str(south_bound)+'&north='+str(north_bound)+'&west='+str(west_bound)+'&east='+str(east_bound)+'&outputFormat=GTiff&API_Key='+API_Key+'&nullFill=true'
        response = requests.get(url)
        
        # Raise an exception if the response is not 200 (OK)
        response.raise_for_status()
        
        # Raise error if no data exists for chosen bounding box in dataset
        if "No Data" in response.text:
            raise Exception("Request was OK, however there is no data for specified extent")
        
        # Download DEM image into output directory specified by user
        open(output_dir, 'wb').write(response.content)

        ### --- Raise server response errors --- ###
        
    # Depending on server response, raise a variety of errors as outlined in the API informing user about possible issues in their query
    except requests.exceptions.HTTPError as error:
        if response.status_code == 400:
            raise Exception('Bad Request (Error Code 400): Verify boundaries provided create a valid bounding box and do not exceed the area limitations of the dataset')
        elif response.status_code == 401:
            raise Exception('Unauthorized (Error Code 401): API key provided is invalid')
        elif response.status_code == 500:
            raise Exception('Internal Server Error (Error Code 500): OpenTopography database is currently down')
        else:
            raise error

# Create 2D plot of DEM .geotiff file
def plotDEM (geotiff_dir: str, histogram: bool = True, colormap: str = 'Greys_r', plot_title: str = 'DEM Map'):
    """
    Plots the DEM .geotiff file using rasterio and matplotlib
    
    Parameters:
        geotiff_dir (str): The path to the input DEM GeoTIFF file including file extension
        histogram (bool): If True, will plot a historgram of elevation values alongside base plot
        colormap (str): Define matplotlib cmap to use for plotting
        plot_title (str): Title for plot
    """
    
        ### --- Catch a variety of user-input errors --- ###
    
    # Check for invalid input parameter datatypes
    if type(geotiff_dir) != str:
        raise TypeError('geotiff_dir is not of type string, please input a string.')
    elif type(histogram) != bool:
        raise TypeError('histogram is not of type boolean, please input a boolean.')
    elif type(colormap) != str:
        raise TypeError('colormap is not of type string, please input a string.')
    elif type(plot_title) != str:
        raise TypeError('plot_title is not of type string, please input a string.')
    
    # Check for invalid characters in input directory
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(geotiff_dir):
        raise ValueError('Input directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(geotiff_dir):
        raise FileNotFoundError(f'Input file path "{geotiff_dir}" does not exist.')
    if not geotiff_dir.endswith(('.tif','.tiff')):
        raise ValueError(f'Input file "{geotiff_dir}"" is not a valid .geotiff file.')
    
        ### --- Create plot of .geotiff DEM --- ###
        
    # Read in DEM from geotiff_dir
    DEM = rasterio.open(geotiff_dir)
    
    # Create plot
    fig, ax = plt.subplots()
    
    # Set colorbar
    color_data = ax.imshow(DEM.read()[0], cmap = colormap)
    bar = fig.colorbar(color_data, ax=ax)
    bar.set_label('Pixel Value')

    # Set axis labels
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Show plot of DEM data
    rasterio.plot.show(DEM,
                       ax=ax,
                       title = plot_title,
                       cmap = colormap)

        ### --- Plot histogram of elevation values --- ###
    
    if histogram == True:
        # Get the elevation values from the DEM .geotiff file
        elevation_values = DEM.read(1).flatten()

        # Plot a histogram of elevation values
        fig, ax = plt.subplots()
        ax.hist(elevation_values, bins=50)
        ax.set_xlabel("Elevation Pixel Value")
        ax.set_ylabel("Frequency of Pixels")
        ax.set_title("Histogram of Elevation Values")

        # Show both plots
        plt.show(block=True)

# Describe DEM map
def describeDEM(geotiff_dir: str) -> dict:
    """
    Returns a dictionary including important geospatial information about an input .geotiff DEM

    Parameters:
        geotiff_dir (str): Input directory of .geotiff DEM file
    """
    
        ### --- Catch a variety of user-input errors --- ###
        
    # Check for invalid input parameter datatypes
    if type(geotiff_dir) != str:
        raise TypeError('geotiff_dir is not of type string, please input a string.')
        
    # Check for invalid characters in input directory
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(geotiff_dir):
        raise ValueError('Input directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(geotiff_dir):
        raise FileNotFoundError(f'Input file path "{geotiff_dir}" does not exist.')
    if not geotiff_dir.endswith(('.tif','.tiff')):
        raise ValueError(f'Input file "{geotiff_dir}"" is not a valid .geotiff file.')
    
        ### --- Open .geotiff file using rasterio --- ###
        
    # Open .geotiff file using rasterio
    DEM = rasterio.open(geotiff_dir)
    
    # Read the data from DEM into numpy array
    data = DEM.read()
    
        ### --- Add information to dictionary --- ###
        
    # Declare dictionary to hold DEM information
    information = {}
    
    # Get min and max elevation pixel values
    minimum_elevation = data.min()
    information['min_elevation'] = minimum_elevation
    
    maximum_elevation = data.max()
    information['max_elevation'] = maximum_elevation
    
    # Get width and height
    width, height =  DEM.shape
    information['width'], information['height'] = width,height
    
    # Get number of bands
    bands = DEM.count
    information['bands'] = bands
    
    # Get coordinates for corners of DEM
    
    # Get CRS
    crs = DEM.crs
    information['crs'] = crs
    
    return information

# Reprojects an input .GeotTiff file to a target EPSG crs code
def reprojectDEM(geotiff_dir: str, epsg_num: str, output_dir: str):
    """
    Reprojects an input .geotiff file to a specified EPSG crs code and outputs a new reprojected .geotiff
    
    Parameters:
        geotiff_dir (str): The path to the input DEM GeoTIFF file including file extension
        epsg_num (str): The specific EPSG code with which to reproject the input .geotiff to; int is also accepted
        output_dir (str): The path to the output clipped image file including file extension
    """

        ### --- Catch a variety of user-input errors --- ###
        
    # Check for invalid input parameter datatypes
    if type(geotiff_dir) != str:
        raise TypeError('geotiff_dir is not of type string, please input a string.')
    elif type(epsg_num) != str and type(epsg_num) != int:
        raise TypeError('epsg_num is not of type string or integer, please input a string or integer.')
    elif type(output_dir) != str:
        raise TypeError('output_dir is not of type string, please input a string.')
   
    # Check for invalid characters in input and output directories
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(geotiff_dir):
        raise ValueError('Input directory contains invalid characters.')
    elif pattern.search(output_dir):
        raise ValueError('Output directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(geotiff_dir):
        raise FileNotFoundError(f'Input file path "{geotiff_dir}" does not exist.')
    if not geotiff_dir.endswith(('.tif','.tiff')):
        raise ValueError(f'Input file "{geotiff_dir}"" is not a valid .geotiff DEM file.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError(f'Output file path "{output_dir}" does not exist, please create it.')
    if not output_dir.endswith(('.tif','.tiff')):
        raise ValueError(f'Invalid output filetype "{output_dir}", make sure output_dir argument ends with ".tif"') 
       
        ### --- Open .geotiff image and prepare crs data --- ###
    
    # Open the input DEM file and read metadata
    geotiff = rasterio.open(geotiff_dir)
    geotiff_crs = geotiff.crs
    
    # Define the target CRS
    output_crs = f"EPSG:{epsg_num}"
    
    # Try to calculate the transform and dimensions for the target CRS and raise error if EPSG is invalid
    try: 
        transform, width, height = calculate_default_transform(
            geotiff_crs,
            output_crs,
            geotiff.width,
            geotiff.height,
            *geotiff.bounds
        )
    except:
        raise ValueError(f'Input EPSG code "{epsg_num}" is not a valid EPSG crs code.')
    
    # Define the output metadata
    output_profile = geotiff.profile.copy()
    output_profile.update({'crs': output_crs,
                           'transform': transform,
                           'width': width,
                           'height': height})
    
        ### --- Reproject .geotiff and save as new file --- ###
    
    # Reproject the DEM to the target CRS and save to the output directory
    with rasterio.open(output_dir, 'w', **output_profile) as output:
        for i in range(1, output.count+1):
            reproject(
                source=rasterio.band(geotiff, i),
                destination=rasterio.band(output, i),
                src_transform=geotiff.transform,
                src_crs=geotiff_crs,
                dst_transform=transform,
                dst_crs=output_crs,
                resampling=Resampling.bilinear)
    
    # Close input and output files
    geotiff.close()
    output.close()

# Clips an input .geotiff file according to a geometry file 
def clipDEM(geotiff_dir: str, geometry_dir: str, output_dir: str, crop: bool = True):
    """
    Clips an input .geotiff file according to a geometry file and outputs a new clipped .geotiff
    
    Parameters:
        geotiff_dir (str): The path to the input DEM GeoTIFF file including file extension
        geometry_dir (str): The path to the geometry file with which to clip .geotiff by
        output_dir (str): The path to the output clipped image file including file extension
        crop (bool): Choose if to crop the image to clipped extent (True), or leave original extent creating an "island" effect (False)
    """
    
        ### --- Catch a variety of user-input errors --- ###
    
    # Check for invalid input parameter datatypes
    if type(geotiff_dir) != str:
        raise TypeError('geotiff_dir is not of type string, please input a string.')
    elif type(geometry_dir) != str:
        raise TypeError('geometry_dir is not of type string, please input a string.')
    elif type(output_dir) != str:
        raise TypeError('output_dir is not of type string, please input a string.')
    elif type(crop) != bool:
        raise TypeError('crop is not of type bool, please input an bool.')
    
    # Check for invalid characters in input, output, and geometry directories
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(geotiff_dir):
        raise ValueError('Input directory contains invalid characters.')
    elif pattern.search(output_dir):
        raise ValueError('Output directory contains invalid characters.')
    elif pattern.search(geometry_dir):
        raise ValueError('Geometry directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(geotiff_dir):
        raise FileNotFoundError(f'Input file path "{geotiff_dir}" does not exist.')
    if not geotiff_dir.endswith(('.tif','.tiff')):
        raise ValueError(f'Input file "{geotiff_dir}"" is not a valid .geotiff file.')
    
    # Check for invalid geometry directory or filetype errors
    if not os.path.exists(geometry_dir):
        raise FileNotFoundError(f'Geometry file path "{geometry_dir}" does not exist.')
    if not geometry_dir.endswith(('.shp','.json','.geojson')):
        raise ValueError(f'Geometry file "{geometry_dir}"" is not a valid geometry file format. Supported formats include ".shp", ",json", ".geojson".')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError(f'Output file path "{output_dir}" does not exist, please create it.')
    if not output_dir.endswith(('.tif','.tiff')):
        raise ValueError(f'Invalid output filetype "{output_dir}", make sure output_dir argument ends with ".tif"')  
    
        ### --- Open .geotiff and geometry data --- ###
    
    # Open file containing geometry data
    geometry = fiona.open(geometry_dir)
    shapes = [feature["geometry"] for feature in geometry]
    
    # Open input .geotiff file
    geotiff = rasterio.open(geotiff_dir)
    
        ### --- Prepare mask parameters --- ###
        
    # Specify output mask parameters
    output_image, output_transform = rasterio.mask.mask(geotiff, shapes, crop=crop)
    
    # Set values below 0 to 0 to avoid overflow errors when using geotifftoImage() on the output
    output_image = np.clip(output_image, 0, None)
    
    # Get metadata from input and apply it to output
    output_meta = geotiff.meta
    
        ### --- Clip .geotiff according to mask and save output file --- ###
        
    # Update metadata of output image with masked data
    output_meta.update({"driver": "GTiff",
                        "height": output_image.shape[1],
                        "width": output_image.shape[2],
                        "transform": output_transform,
                        "nodata": 0})
    
    # Create output file
    with rasterio.open(output_dir, "w", **output_meta) as output:
        output.write(output_image)
    
    # Close input and output files
    geotiff.close()
    output.close()

# Convert .GeoTIFF to image file
def geotiffToImage(geotiff_dir: str, output_dir: str):
    """
    Converts a GeoTIFF file (such as one gotten from OpenTopography) to a viewable image file.

    Parameters:
        geotiff_dir (str): The path to the input DEM GeoTIFF file including file extension
        output_dir (str): The path to the output image file including file extension
    """
    
        ### --- Catch a variety of user-input errors --- ###
        
    # Check for invalid input parameter datatypes
    if type(geotiff_dir) != str:
        raise TypeError('geotiff_dir is not of type string, please input a string.')
    elif type(output_dir) != str:
        raise TypeError('output_dir is not of type string, please input a string.')
   
    # Check for invalid characters in input and output directories
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(geotiff_dir):
        raise ValueError('Input directory contains invalid characters.')
    elif pattern.search(output_dir):
        raise ValueError('Output directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(geotiff_dir):
        raise FileNotFoundError(f'Input file path "{geotiff_dir}" does not exist.')
    if not geotiff_dir.endswith(('.tif','.tiff')):
        raise ValueError(f'Input file "{geotiff_dir}"" is not a valid .geotiff file.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError(f'Output file path "{output_dir}" does not exist, please create it.')
    if not output_dir.endswith(('.png','.bmp','.tif','.tiff')):
        raise ValueError(f'Output file "{output_dir}" is not a valid image file.')  

        ### --- Open .geotiff image using rasterio --- ###
        
    # Open .geotiff file using rasterio
    DEM = rasterio.open(geotiff_dir)
    
    # Read the data from DEM into numpy array
    data = DEM.read()

    # Get the metadata from DEM to be used in creating new output file
    meta = DEM.meta.copy()

    # Specify the output format for image and edit metadata
    if output_dir.endswith('.png'):
        file_type = 'PNG'
    else:
        file_type = 'JPEG'
    
        ### --- Convert .geotiff to image and save --- ###
    
    meta.update(dtype = 'uint8', driver = file_type)

    # Scale the data to 0-255 range to comply with 8-bit output format
    scale_factor = 255 / (data.max() - data.min())
    scaled_data = (data - data.min()) * scale_factor
    
    # Make GDAL not create an annoying .aux file with output
    os.environ['GDAL_PAM_ENABLED'] = 'NO'
    
    # Create output file
    output = rasterio.open(output_dir, 'w', **meta)
    
    # Write DEM data to the output file
    output.write(scaled_data.astype('uint8'))

    # Close input and output files
    DEM.close()
    output.close()

# Simplify DEM image to a lower resolution
def simplifyDEM(dem_dir: str, output_dir: str, reduction_factor: int = 2):
    """
    Downsamples DEM image to lower resolution

    Parameters:
        dem_dir (string): The path to the input DEM image file including file extension
        output_dir (string): The path to the output image file including file extension
        reduction_factor (int): Number by which to divide resolution by
    """

        ### --- Catch a variety of user-input errors --- ###
    
    # Check for invalid input parameter datatypes
    if type(dem_dir) != str:
        raise TypeError('geotiff_dir is not of type string, please input a string.')
    elif type(output_dir) != str:
        raise TypeError('output_dir is not of type string, please input a string.')
    elif type(reduction_factor) != int:
        raise TypeError('reduction_factor is not of type integer, please input an integer.')
    
    # Check for invalid characters in input and output directories
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(dem_dir):
        raise ValueError('Input directory contains invalid characters.')
    elif pattern.search(output_dir):
        raise ValueError('Output directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(dem_dir):
        raise FileNotFoundError(f'Input file path "{dem_dir}" does not exist.')
    if not dem_dir.endswith(('.png','.bmp','.tif','.tiff')):
        raise ValueError(f'Input file "{dem_dir}"" is not a valid image file.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError(f'Output file path "{output_dir}" does not exist, please create it.')
    if not output_dir.endswith(('.png','.bmp','.tif','.tiff')):
        raise ValueError(f'Output file "{output_dir}" is not a valid image file.')  
    
    # Check for invalid reduction_factor that would result in the same or larger image
    if reduction_factor < 2:
        raise ValueError(f'reduction_factor "{reduction_factor}" must be greater than or equal to 2 to reduce resolution.')
    
        ### --- Reduce image resolution and save --- ###
    
    # Open image
    img = Image.open(dem_dir)
    
    # Calculate the new size of the image by dividing image by the reduction_fator
    new_width = img.width // reduction_factor
    new_height = img.height // reduction_factor
    new_size = (new_width, new_height)
    
    # Downsample image while retaining as much quality as possible 
    simplified_img = img.resize(new_size, resample=Image.BICUBIC)

    # Save the downscaled image to a new file
    simplified_img.save(output_dir)

def renderDEM(blender_dir: str, dem_dir: str, output_dir: str, exaggeration: float = 0.5, shadow_softness: int = 90, sun_angle: int = 45, resolution_scale: int = 50, samples: int = 5):
    """
    Uses Blender to generate a 3D rendered hillshade map using an input DEM image file

    Parameters:
        blender_dir (str): Directory of blender.exe found in Blender's installation folder
        dem_dir (string): The path to the input DEM image including file extension
        output_dir (string): The path to the output rendered image file including file extension
        exaggeration (float): Level of topographic exaggeration to be applied to 3D plane based on input DEM
        shadow_softness (int): Softness of shadows with values ranging from 0-180
        sun_angle (int): Vertical angle of sun's rays that lights the map
        resolution_scale (int): Scale of the rendered image resolution in relation to the input DEM resolution in percentage
        samples (int): Amount of samples to be used in the final render determining its quality
    """

        ### --- Check for a variety of user-input errors --- ###

    # Check for invalid input parameter datatypes
    if type(blender_dir) != str:
        raise TypeError('blender_dir is not of type string, please input a string.')
    elif type(dem_dir) != str:
        raise TypeError('dem_dir is not of type string, please input a string.')
    elif type(output_dir) != str:
        raise TypeError('output_dir is not of type string, please input a string.')
    elif type(exaggeration) != float:
        raise TypeError('exaggeration is not of type float, please input a float.')
    elif type(shadow_softness) != int:
        raise TypeError('shadow_softness is not of type integer, please input an integer.')
    elif type(sun_angle) != int:
        raise TypeError('sun_angle is not of type integer, please input an integer.')
    elif type(resolution_scale) != int:
        raise TypeError('resolution_scale is not of type integer, please input an integer.')
    elif type(samples) != int:
        raise TypeError('samples is not of type integer, please input an integer.')

    # Check for invalid characters in input and output directories
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(dem_dir) or pattern.search(output_dir) or pattern.search(blender_dir):
        raise ValueError('Input or output or blender directory contains invalid characters.')
    
    # Check for invalid Blender directory
    if not os.path.exists(blender_dir):
        raise FileNotFoundError(f'Path to Blender executable "{blender_dir}" does not exist.')

    # Check for invalid input directory or filetype errors
    if not os.path.exists(dem_dir):
        raise FileNotFoundError(f'Input file path "{dem_dir}" does not exist.')
    if not dem_dir.endswith(('.png', '.jpg', '.jpeg', '.bmp','.tif','.tiff')):
        raise ValueError(f'Input file "{dem_dir}"" is not a valid image file.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError(f'Output file path "{output_dir}" does not exist, please create it.')
    if not output_dir.endswith(('.png', '.jpg', '.jpeg', '.bmp','.tif','.tiff')):
        raise ValueError(f'Output file "{output_dir}" is not a valid image file.')

        ### --- Use subprocess to start Blender and run renderDEM() function --- ###

    subprocess.run(f"{blender_dir} --background --python-expr \"from renderDEM import *; renderDEM(dem_dir = '{dem_dir}', output_dir = '{output_dir}', exaggeration = {exaggeration}, shadow_softness = {shadow_softness}, sun_angle = {sun_angle}, resolution_scale = {resolution_scale}, samples = {samples})\"")

# Converts a rendered hillshade image to a .geotiff image with geospatial metadata
def georeferenceDEM(render_dir: str, geotiff_dir: str, output_dir: str):
    """
    Converts an image (such as a hillshade rendered in Blender) to a .geotiff containing geospatial information gotten from an input .geotiff
    
    Parameters:
        render_dir (str): Directory of the rendered hillshade image to be converted into .geotiff
        geotiff_dir (str): Directory of the .geotiff containing the geospatial metadata to apply to the render
        output_dir (str):  Directory of the saved .geotiff image containing the render with applied geospatial metadata
    """
    
    # Open rendered hillshade image
    render = rasterio.open(render_dir)
    render_data = render.read()
    render_meta = render.meta

    # Open .geotiff image of same extent
    geotiff = rasterio.open(geotiff_dir)

    # Update metadata of rendered image with metadata from .geotiff
    render_meta.update({
            'driver': 'GTiff',
            'dtype': render_data.dtype,
            'transform': geotiff.transform,
            'crs': geotiff.crs
        })
    
    output = rasterio.open(output_dir, 'w', **render_meta)
    output.write(render_data)
    
    render.close()
    geotiff.close()
    output.close()