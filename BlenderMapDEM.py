# Import required packages
from PIL import Image
import requests
import os
import re

# Fetch DEM .GeoTIFF image of user specified extent
def fetchDEM(north_bound: float, south_bound: float, east_bound: float, west_bound: float, API_Key: str, output_dir: str, dataset: str = 'SRTMGL1'):
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

# Generate 3D elevation map using Blender
def renderDEM(dem_dir: str, output_dir: str, exaggeration: float = 0.5, shadow_softness: float = 90, sun_angle: float = 45, resolution_scale: int = 50, samples: int = 5):
    
        ### --- Catch a variety of user-input errors --- ###
    
    # Check for invalid characters in input and output directories
    pattern = re.compile(r'[^a-zA-Z0-9_\-\\/.\s:]')
    if pattern.search(dem_dir) or pattern.search(output_dir):
        raise ValueError('Input or output directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(dem_dir):
        raise ValueError(f'Input file path "{dem_dir}" does not exist.')
    if not dem_dir.endswith(('.png', '.jpg', '.jpeg', '.bmp','.tif','.tiff')):
        raise ValueError(f'Input file "{dem_dir}"" is not a valid image file.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise ValueError(f'Output file path "{output_dir}" does not exist, please create it.')
    if not output_dir.endswith(('.png', '.jpg', '.jpeg', '.bmp','.tif','.tiff')):
        raise ValueError(f'Output file "{output_dir}" is not a valid image file.')  
    
    # Import DEM image
    DEM = bpy.data.images.load(dem_dir)
    
    # Set variables to hold resolution of DEM image
    width, height = DEM.size
    
        ### --- Render Settings --- ###
    
    # Set render engine to "Cycles" and select "Experimental" feature set
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
    
    # Set render output resolution to the same as DEM image
    bpy.data.scenes['Scene'].render.resolution_x = width
    bpy.data.scenes['Scene'].render.resolution_y = height
    
    # Specify render quality
    bpy.data.scenes['Scene'].render.resolution_percentage = resolution_scale
    bpy.data.scenes['Scene'].cycles.samples = samples
    
        ### --- Plane Settings --- ###

    # Get the cube and plane objects if they exists
    cube = bpy.data.objects.get('Cube')
    plane = bpy.data.objects.get('Plane')
    
    # If the cube exists, delete it
    if cube != None:
        bpy.data.objects['Cube'].select_set(True)
        bpy.ops.object.delete() 
    
    # If the cube exists, delete it
    if plane != None:
        bpy.data.objects['Plane'].select_set(True)
        bpy.ops.object.delete() 

    # Add plane to scene
    bpy.ops.mesh.primitive_plane_add()
    plane = bpy.data.objects['Plane']

    # Scale plane to aspect ratio of image
    plane.scale[0] = width/1000
    plane.scale[1] = height/1000

    # Check if the subsurf modifier is already applied to the plane
    subsurf_modifier = plane.modifiers.get('Subdivision')
    if subsurf_modifier == None:
        # Add subdivision surface modifier to plane if it doesn't exist
        subsurf_modifier = plane.modifiers.new(name='Subdivision', type='SUBSURF')
        subsurf_modifier.subdivision_type = 'SIMPLE'
        bpy.context.object.cycles.use_adaptive_subdivision = True

        ### --- Camera Settings --- ###
    
    camera = bpy.data.objects["Camera"]
    
    # Set camera location to origin
    camera.location[0] = 0
    camera.location[1] = 0
    camera.location[2] = 3
    
    # Set camera rotation to point down
    camera.rotation_euler[0] = 0
    camera.rotation_euler[1] = 0
    camera.rotation_euler[2] = 0
    
    # Set camera to orthographic
    bpy.data.cameras['Camera'].type = 'ORTHO'
    
    # Set orthographic scale to be twice the largest dimension of our plane (so plane fills view)
    if width/1000 > height/1000:
        orthographic_scale = 2*(width/1000)
    elif height/1000 > width/1000:
        orthographic_scale = 2*(height/1000)
    elif height/1000 == width/1000:
        orthographic_scale = 2*(height/1000)
    
    bpy.data.cameras['Camera'].ortho_scale = orthographic_scale
    
        ### --- Light Settings --- ###
    
    light = bpy.data.objects['Light']
    
    # Make sure shadow_strength falls in acceptable range
    if shadow_softness > 180:
        shadow_softness = 180
    elif shadow_softness < 0:
        shadow_softness = 0
    
    # Select light and change its type to "Sun"
    bpy.data.lights['Light'].type = 'SUN'
    
    # Change strength and hardness of light
    bpy.data.lights['Light'].energy = 5
    bpy.data.lights['Light'].angle = shadow_softness/57.295
    
    # Change direction of the light
    light.rotation_euler[0] = 0
    light.rotation_euler[1] = sun_angle/57.295
    light.rotation_euler[2] = 2.35619
    
        ### --- Shader Settings --- ###

    mat = bpy.data.materials['Material']
    
    # Add new material to plane
    bpy.data.objects['Plane'].active_material = mat
    bpy.context.object.active_material.cycles.displacement_method = 'DISPLACEMENT'
    
    # Set material color and change "Roughness" to 1 and "Specular" to 0 (makes material matte)
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.6, 0.6, 0.6, 1)
    mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1
    mat.node_tree.nodes['Principled BSDF'].inputs['Specular'].default_value = 0
    
    # Add image texture node if it doesnt exist and specify its extension, interpolation, and colorspace modes
    if 'Image Texture' not in mat.node_tree.nodes:
        imageTexture = mat.node_tree.nodes.new('ShaderNodeTexImage')
    else:
        imageTexture = mat.node_tree.nodes['Image Texture']

    imageTexture.image = DEM
    imageTexture.extension = 'EXTEND'
    imageTexture.interpolation = 'Smart'
    imageTexture.image.colorspace_settings.name = 'Linear'
    
    # Add displacement node if it doesnt exist and specify the elevation exaggeration of heightmap
    if 'Displacement' not in mat.node_tree.nodes:
        displacement = mat.node_tree.nodes.new('ShaderNodeDisplacement')
    else:
        displacement = mat.node_tree.nodes['Displacement']
        
    displacement.inputs['Scale'].default_value = exaggeration
    
    # Add color ramp node if it doesnt exist
    if 'ColorRamp' not in mat.node_tree.nodes:
        colorRamp = mat.node_tree.nodes.new('ShaderNodeValToRGB')
    else:
        colorRamp = mat.node_tree.nodes['ColorRamp']
    
    # Link everything together
    mat.node_tree.links.new(imageTexture.outputs['Color'], displacement.inputs['Height'])
    mat.node_tree.links.new(displacement.outputs['Displacement'], mat.node_tree.nodes['Material Output'].inputs['Displacement'])
       
        ### --- Render Image --- ###
    
    # Check output file type and set accordingly
    if output_dir.endswith(('.tif','.tiff')):
        file_type = 'TIFF'
    elif output_dir.endswith(('.jpg', '.jpeg')):
        file_type = 'JPEG'
    elif output_dir.endswith(('.bmp')):
        file_type = 'BMP'
    else:
        file_type = 'PNG'
    
    # Set the output file path and format
    bpy.context.scene.render.filepath = output_dir
    bpy.context.scene.render.image_settings.file_format = file_type
    
    # Render the image
    bpy.ops.render.render(write_still=True)

# Simplify DEM image to a lower resolution
def simplifyDEM(dem_dir: str, output_dir: str, reduction_factor: int = 2):
    
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