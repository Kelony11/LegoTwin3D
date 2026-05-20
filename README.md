# LegoTwin3D 🧩

**LegoTwin3D** is a Blender and Open3D project that generates RGB-D views of a Lego model, reconstructs point clouds from multiple camera views, and evaluates reconstruction quality under different viewpoint, density, and camera noise settings.

## Features
- Generate RGB and depth images from Blender
- Reconstruct point clouds from multi-view RGB-D data
- Render reconstructed point clouds back into image space
- Compare reconstructions against ground truth using PSNR and SSIM
- Study viewpoint coverage with 5, 10, and 20 views
- Study point cloud density with sparse, medium, and dense voxel settings
- Study reconstruction sensitivity to camera pose noise

## Tech Stack 🧱
- Python
- Blender
- Open3D
- NumPy
- OpenCV
- scikit-image

## Project Structure
- `blender/` Blender scene file
- `code/` reconstruction, rendering, viewing, and metrics scripts
- `output/` point cloud outputs and reference scan
- `generated/` rendered/generated image folders

## Scripts
- `generate_rgbd.py` generate RGB and depth images
- `rgbd-pc.py` reconstruct point clouds from RGB-D views
- `view_ply.py` inspect point cloud outputs
- `lego_ply_render.py` render `.ply` point clouds in Blender
- `compute_metrics.py` compute PSNR and SSIM

## Run
```bash
python code/rgbd-pc.py --views 20 --output output/reconstructed.ply
python code/view_ply.py output/reconstructed.ply
python code/compute_metrics.py
```


### NOTES
This project focuses on digital twin reconstruction, point cloud evaluation, and controlled experiments on viewpoint coverage, voxel density, and camera noise.

## AUTHOR 
`Kelvin Ihezue`