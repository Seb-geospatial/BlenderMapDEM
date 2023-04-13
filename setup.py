from setuptools import setup, find_packages

setup(
    name='BlenderMapDEM',
    version='1.0.5',
    description='A python module of functions for creating 3D elevation maps using Blender. Enables users with minimal Blender knowledge to fetch, clean, and visualize DEM data.',
    packages=find_packages(),
    install_requires=[
        'Pillow',
        'requests',
        'rasterio',
        'matplotlib',
        'fiona',
        'numpy'
    ]
)