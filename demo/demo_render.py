# This file will be fed into Blender in order to render our map

# Import renderDEM() module added to Blender's module folder
from renderDEM import *

# Call renderDEM() function to generate rendered map (remember that Blender requires absolute paths)
renderDEM(dem_dir = 'C:/Home/Documents/School/Course Resources/GEOG 464/BlenderMapDEM/demo/data/BarbadosDEM_image.png',
		  output_dir = 'C:/Home/Documents/School/Course Resources/GEOG 464/BlenderMapDEM/demo/data/Barbados_render.png',
		  exaggeration = 1, # Specify topographic exaggeration
		  shadow_softness = 90, # Specify shadow softness of light source
		  sun_angle = 45, # Specify vertical angle of light source
		  resolution_scale = 100, # Specify final resolution scale in relation to input DEM
		  samples = 20 # Specify samples for final render quality
		  )

# End of file