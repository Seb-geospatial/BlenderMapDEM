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
- [Usage](#usage)
    - [Render from python script using terminal](#terminal)
    - [Render from python script using GUI](#GUI)
    - [Usage tips](#tips)
- [Acknowledgements](#acknowledgements)

## 🧐 About <a name = "about"></a>
This is a python module of functions for creating 3D hillshade maps using Blender. It enables users with minimal Blender knowledge to fetch, clean, and visualize DEM data in the form of beautifully rendered hillshade maps.


This module is ultimately centered around its `renderDEM()` function which interfaces with Blender in order to generate a 3D rendered hillshade map using an input DEM image file.

## 🏁 Getting Started <a name = "getting_started"></a>

### 🔧 Requirements <a name = "requirements"></a>
- This module requires an installation of **Blender**, a free and open-source 3D modelling software, in order to utilize its 3D visualization capabilities. At the time of writing this module is working as of Blender 3.4 (latest version) and can be downloaded [here](https://www.blender.org/download/)

### ⛏️ Installation <a name = "installation"></a>

## 🗺️ Usage <a name = "usage"></a>

### 🖥️ Render Map from Python Script Using Terminal <a name = "terminal"></a>
- Steps to render map using terminal:
    - If Blender is not added to your PATH, in your terminal navigate to your Blender installation directory that contains your Blender.exe file. On Windows this defaults to: `C:\Program Files\Blender Foundation\Blender 3.4` as of Blender 3.4.
    - If Blender is added to your PATH, you should be able to run Blender from anywhere in your terminal. You can be sure it is added to your PATH if running "Blender" in your terminal from any directory opens a Blender instance. (see LINK for adding Blender to PATH).
    - To run a python script which contains the renderDEM() function, input `./Blender.exe --background --python path/to/script.py` into your terminal (working on Git Bash, executing applications from the terminal may differ slightly between terminal clients).
    - This will render a DEM image to the absolute directory specified in your renderDEM() function WITHOUT opening Blender's GUI.
    - For more information on starting Blender from the command line see [here](https://docs.Blender.org/manual/en/dev/advanced/command_line/launch/index.html).

### 🖥️ Render Map from Python Script Using GUI <a name = "GUI"></a>
- While rendering from the terminal is quicker and more resource efficient, it may be simpler if you are not that familiar with the command line to render using Blender's GUI.


- **NOTE:** the renderDEM() function is intended to work on a **new** Blender project file that features the default cube, camera, and light. If you already have Blender open and have made any changes to your project, go to `File>New>General` to create a new project.


- Steps to render map using GUI:
    1. When Blender starts, create a new project default by clicking the "General" template. Then, navigate to the "Scripting" workspace located at the far right along the top bar.
    ![alt text](https://docs.Blender.org/manual/en/latest/_images/interface_window-system_workspaces_screen.png "Blender workspace")
    2. You should see a new workspace featuring a text editor and Blender's own python console. Along the top bar of the text editor click "Open Text" (folder icon).
    3. Navigate to your python script (which imports bpy, this module, and calls the `renderDEM()` function) and open it.
    4. Click the "Run Script" (play button icon) and the script should produce a rendered image according to the parameters specified in the renderDEM() function.
    5. If you wish to make changes and run the script again, you must open a new project and repeat the previous steps. This is because the script is built around a new default project that is present each time the script is run from the terminal. (This is why it is recommended to render using the terminal (see above).

### 💡 Usage Tips <a name = "tips"></a>
It is recommended to start with **very** conservative quality settings (renderDEM() arguments of `resolution_scale` and `samples`) so that you are able to quickly perform many test renders while you fine-tune the stylistic arguments before your final high-quality render (see HERE for context on appropriate argument values). 
This is because different input maps may have better readability with certain scale exaggerations, colors, shadows, etc. and rendering a high-quality map every time to tweak these parameters would require an unnecessary amount of time and resources.

## 🙌 Acknowledgements <a name = "acknowledgements"></a>
- This documentation was created with reference from the following template created by [@kylelobo](https://github.com/kylelobo), accessible [here](https://github.com/kylelobo/The-Documentation-Compendium/blob/master/en/README_TEMPLATES/Standard.md)