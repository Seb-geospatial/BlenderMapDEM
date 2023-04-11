# Attempt to import packages, raise error if not being run by Blender
try:
    import bpy
except:
    raise ModuleNotFoundError('This function must be run by Blender, it cannot run in a normal python environment')

import re
import os

# Generate 3D elevation map using Blender's bpy package
def renderDEM(dem_dir: str, output_dir: str, exaggeration: float = 0.5, shadow_softness: int = 90, sun_angle: int = 45, resolution_scale: int = 50, samples: int = 5):
    """
    Uses Blender in order to render a hillshade map using DEM image as input

    Parameters:
        dem_dir (string): The path to the input DEM image including file extension
        output_dir (string): The path to the output rendered image file including file extension
        exaggeration (float): Level of topographic exaggeration to be applied to 3D plane based on input DEM
        shadow_softness (int): Softness of shadows with values ranging from 0-180
        sun_angle (int): Vertical angle of sun's rays that lights the map
        resolution_scale (int): Scale of the rendered image resolution in relation to the input DEM resolution in percentage
        samples (int): Amount of samples to be used in the final render determining its quality
    """
    
        ### --- Catch a variety of user-input errors --- ###
    
    # Check for invalid input parameter datatypes
    if type(dem_dir) != str:
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
    if pattern.search(dem_dir) or pattern.search(output_dir):
        raise ValueError('Input or output directory contains invalid characters.')
    
    # Check for invalid input directory or filetype errors
    if not os.path.exists(dem_dir):
        raise FileNotFoundError(f'Input file path "{dem_dir}" does not exist.')
    if not dem_dir.endswith(('.png', '.jpg', '.jpeg', '.bmp','.tif','.tiff')):
        raise ValueError(f'Input file "{dem_dir}"" is not a valid image file.')
    
    # Check for invalid output directory or filetype errors
    output_dir_path = os.path.dirname(output_dir)
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError(f'Output file directory "{output_dir}" does not exist, please create it.')
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
    
    # If the plane exists, delete it
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