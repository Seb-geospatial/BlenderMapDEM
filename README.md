<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/6wj0hh6.jpg" alt="Project logo"></a>
</p>

<h3 align="center">Blender DEM Visualization Toolkit</h3>

---
 
## 📝 Table of Contents
- [About](#about)
- [Getting Started](#getting_started)
    - [Requirements](#requirements)
    - [Installation](#installation)
- [Functions in this Module](#functions)
    - [renderDEM](#render)
- [Blender Usage](#usage)
    - [Render from python script using terminal](#terminal)
    - [Render from python script using GUI](#gui)
    - [Usage tips](#tips)
- [Acknowledgements](#acknowledgements)

## 🧐 About <a name = "about"></a>
This is a python module of functions for creating 3D hillshade maps using Blender. It enables users with minimal Blender knowledge to fetch, clean, and visualize DEM data in the form of beautifully rendered hillshade maps.


This module is ultimately centered around its `renderDEM()` function which interfaces with Blender in order to generate a 3D rendered hillshade map using an input DEM image file.

### What is DEM Data?
A digital elevation model (DEM) is a 3D representation of a terrain's surface, created by using digital data to model the elevation of the ground. Essentially, it's a map that shows the height and shape of the land, including features like mountains, valleys, and rivers. DEMs are often created using remote sensing technologies like LiDAR or radar, which bounce signals off the Earth's surface to create a highly accurate elevation model.


A DEM image is simply a visual representation of a digital elevation model (DEM), created by rendering the elevation data in a way that is easy to understand and interpret. Typically, within a DEM image each pixel carries its elevation data as values closer to white are higher and values closer to black are lower. These images can be fed into blender to visualize this information in 3D space, creating high quality "hillshade" maps for use in cartography.

## 🏁 Getting Started <a name = "getting_started"></a>
This module requires an installation of **Blender**, a free and open-source 3D modelling software, in order to utilize its 3D visualization capabilities. At the time of writing, this module is working as of Blender 3.4 (latest version) and can be downloaded [here](https://www.blender.org/download/)

### 🔧 Requirements <a name = "requirements"></a>
- Blender
- Python packages:

### ⛏️ Installation <a name = "installation"></a>

## Functions in this Module <a name = "functions"></a>
Below you will find documentation surrounding the functions featured in this module, their parameters, and usage examples.

### renderDEM() <a name = "render"></a>
```Python
renderDEM(dem_dir, output_dir, exaggeration = 0.5, resolution_scale = 50, samples = 5)
```

Uses Blender to generate a 3D rendered hillshade map using an input DEM image file

Parameters:
- `dem_dir: str`
    - Absolute directory of the input DEM image.
    - **Requires string.**
- `output_dir: str`
    - Absolute directory path of the outputted rendered image.
    - **Requires string.**
- `exaggeration: float`
    - Level of topographic exaggeration to be applied to 3D plane based on input DEM. Higher values will result in "spiky" terrain and darker crevices between landforms.
    - **Requires float and defaults to 0.5.**
- `resolution_scale: int`
    - Scale of the rendered image resolution in relation to the input DEM resolution in the form of percentage. An input DEM with resolution 2000x2000 and a `resolution_scale = 100` will result in a rendered image with resolution 2000x2000, whereas `resolution_scale = 50` will result in a final render of 1000x1000.
    - It is recommended to keep this value around or below 50 while performing test renders to improve speed before raising it to 100 for the final render at full resolution. Has a great affect on render speed and resource load on computer.
    - **Requires integer and defaults to 50.**
- `samples: int`
    - Amount of samples to be used in the final render. Samples can be understood as how many "passes" Blender takes over the image during the rendering process, refining the image more and more each sample/pass, making it more clear and less noisy. Has an **extremely large** affect on render speed and resource load on computer.
    - It is recommended to keep this value very low (from 1-10) while performing test renders or depending on the strength of your computer before your final render where you can then raise it to anywhere from 20-500 for crisp image quality.
    - **Requires integer and defaults to 5.**


Usage example:
```Python
# Notice my very conservative resolution_scale and samples values,
# do not underestimate the length of time it takes to render image
# with a high sample and resolution_scale value

renderDEM(dem_dir = 'C:/Users/sebas/OneDrive/Desktop/Test Blender Map/DEM.png', output_dir = 'C:/Users/sebas/OneDrive/Desktop/render.png', exaggeration = 0.5, resolution_scale = 25, samples = 2)
```

## 🗺️ Blender Usage <a name = "usage"></a>
**IMPORTANT:** The following methods will render a map based on your python script using Blender's own python installation and interpreter. This means it does not have any packages installed other than its own default bpy package (and some others). There are likely ways around this that install outside packages into Blender however it is beyond the scope of this project. For this reason it is important that the script you feed into Blender to render your 3D map **ONLY contains your function call of renderDEM()** and your chosen argument parameters like this...


Example script.py:
```Python
# Script to render a 3D hillshade map in Blender
import BlenderMapDEM

renderDEM(dem_dir = 'path/to/dem.tif', output_dir = 'path/to/outputRender.png', exaggeration = 0.5, resolution_scale = 100, samples = 50)

# End of script
```

### 🖥️ Render Map from Python Script Using Terminal <a name = "terminal"></a>
- Steps to render map using terminal:
    - If Blender is not added to your PATH, in your terminal navigate to your Blender installation directory that contains your Blender.exe file. On Windows this defaults to: `C:\Program Files\Blender Foundation\Blender 3.4` as of Blender 3.4.
    - If Blender is added to your PATH, you should be able to run Blender from anywhere in your terminal. You can be sure it is added to your PATH if running "Blender" in your terminal from any directory opens a Blender instance. (see LINK for adding Blender to PATH).
    - To run a python script which contains the renderDEM() function, input `./Blender.exe --background --python path/to/script.py` into your terminal (working on Git Bash, executing applications from the terminal may differ slightly between terminal clients).
    - This will render a DEM image to the absolute directory specified in your renderDEM() function WITHOUT opening Blender's GUI.
    - For more information on starting Blender from the command line see [here](https://docs.Blender.org/manual/en/dev/advanced/command_line/launch/index.html).

### 🖥️ Render Map from Python Script Using GUI <a name = "gui"></a>
- While rendering from the terminal is quicker and more resource efficient, it may be simpler if you are not that familiar with the command line to render using Blender's GUI.


- **NOTE:** the renderDEM() function is intended to work on a **new** Blender project file that features the default cube, camera, and light. If you already have Blender open and have made any changes to your project, go to `File>New>General` to create a new project.


- Steps to render map using GUI:
    - When Blender starts, create a new project default by clicking the "General" template. Then, navigate to the "Scripting" workspace located at the far right along the top bar.
    ![alt text](https://docs.Blender.org/manual/en/latest/_images/interface_window-system_workspaces_screen.png "Blender workspace")
    - You should see a new workspace featuring a text editor and Blender's own python console. Along the top bar of the text editor click "Open Text" (folder icon).
    - Navigate to your python script (which imports module and calls the `renderDEM()` function) and open it.
    - Click the "Run Script" (play button icon) and the script should produce a rendered image according to the parameters specified in the renderDEM() function.
    - If you wish to make changes and run the script again, you must open a new project and repeat the previous steps. This is because the script is built around a new default project that is present each time the script is run from the terminal. (This is why it is recommended to render using the terminal (see above).

### 💡 Usage Tips <a name = "tips"></a>
It is recommended to start with **very** conservative quality settings (renderDEM() arguments of `resolution_scale` and `samples`) so that you are able to quickly perform many test renders while you fine-tune the stylistic arguments before your final high-quality render (see HERE for context on appropriate argument values). 
This is because different input maps may have better readability with certain scale exaggerations, colors, shadows, etc. and rendering a high-quality map every time to tweak these parameters would require an unnecessary amount of time and resources.

## 🙌 Acknowledgements <a name = "acknowledgements"></a>
- This documentation was created with reference from the following template created by [@kylelobo](https://github.com/kylelobo), accessible [here](https://github.com/kylelobo/The-Documentation-Compendium/blob/master/en/README_TEMPLATES/Standard.md)