import open3d as o3d
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="Path to the .ply file")
    args = parser.parse_args()

    ply_path = args.filename
    
    if not os.path.exists(ply_path):
        print(f"Error: File '{ply_path}' not found.")
        sys.exit(1)

    pcd = o3d.io.read_point_cloud(ply_path)
    
    print(f"Point cloud has {len(pcd.points)} points.")
    
    # Visualize
    o3d.visualization.draw_geometries([pcd])

if __name__ == "__main__":
    main()
