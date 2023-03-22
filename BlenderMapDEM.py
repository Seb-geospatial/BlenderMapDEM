# Import required packages

# Fetch DEM of user specified extent
def fetchDEM(upper_lat, lower_lat, left_lon, right_lon, output_dir, filename = 'DEM.tif'):
    # Create a bounding box for the DEM extent coordinates
    bbox = {'lonLower':left_lon,'latLower':lower_lat,'lonHigher':right_lon,'latHigher':upper_lat}
    
    # Search database for DEM

# Fetch satellite imagery of user specified extent
def fetchImagery(upper_lat,lower_lat,left_lon,right_lon, output_dir, filename = 'imagery.tif'):

# Simplify DEM to a lower resolution
def simplifyDEM(dem):

# Plots 2D DEM visualization 
def plotDEM(dem)

# Generate 3D elevation map using Blender
def renderDEM(dem, displacement_scale, peak_color, valley_color, render_quality = 20, camera = 'topdown'):
