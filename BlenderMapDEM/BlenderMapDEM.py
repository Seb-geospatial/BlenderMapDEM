# Import required packages
from PIL import Image
import requests
import os
import re

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
    
    # Check for invalid characters in output directory
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(output_dir):
        raise ValueError('Input or output directory contains invalid characters.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise ValueError(f'Output file path "{output_dir}" does not exist, please create it.')
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
        url = 'https://portal.opentopography.org/API/globaldem?demtype='+dataset+'&south='+str(south_bound)+'&north='+str(north_bound)+'&west='+str(west_bound)+'&east='+str(east_bound)+'&outputFormat=GTiff&API_Key='+API_Key
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
    
    # Check for invalid characters in input and output directories
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(dem_dir) or pattern.search(output_dir):
        raise ValueError('Input or output directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(dem_dir):
        raise ValueError(f'Input file path "{dem_dir}" does not exist.')
    if not dem_dir.endswith(('.png','.bmp','.tif','.tiff')):
        raise ValueError(f'Input file "{dem_dir}"" is not a valid image file.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise ValueError(f'Output file path "{output_dir}" does not exist, please create it.')
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

# Convert .GeoTIFF to image file
def geotiffToImage(dem_dir: str, output_dir: str):
    """
    Converts a GeoTIFF file (such as one gotten from OpenTopography) to a viewable image file.

    Parameters:
        dem_dir (string): The path to the input DEM GeoTIFF file including file extension
        output_dir (string): The path to the output image file including file extension
    """
    
    # Check for invalid characters in input and output directories
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(dem_dir) or pattern.search(output_dir):
        raise ValueError('Input or output directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(dem_dir):
        raise ValueError(f'Input file path "{dem_dir}" does not exist.')
    if not dem_dir.endswith(('.tif','.tiff')):
        raise ValueError(f'Input file "{dem_dir}"" is not a valid .geotiff DEM file.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise ValueError(f'Output file path "{output_dir}" does not exist, please create it.')
    if not output_dir.endswith(('.png','.bmp','.tif','.tiff')):
        raise ValueError(f'Output file "{output_dir}" is not a valid image file.')  

    # Open .geotiff file using rasterio
    DEM = rasterio.open(dem_dir)
    
    # Read the data from DEM into numpy array
    data = DEM.read()

    # Get the metadata from DEM to be used in creating new output file
    meta = DEM.meta.copy()

    # Specify the output format for image and edit metadata
    if output_dir.endswith('.png'):
        file_type = 'PNG'
    else:
        file_type = 'JPEG'
    
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
