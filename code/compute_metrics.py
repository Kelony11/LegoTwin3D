import os
import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

def load_matching_pairs(gt_dir, pred_dir):
    pairs = []
    for filename in sorted(os.listdir(pred_dir)):
        if not filename.lower().endswith(".png"):
            continue

        gt_path = os.path.join(gt_dir, filename)
        pred_path = os.path.join(pred_dir, filename)

        if os.path.exists(gt_path):
            pairs.append((gt_path, pred_path, filename))
    return pairs

def compute_folder_metrics(gt_dir, pred_dir):
    pairs = load_matching_pairs(gt_dir, pred_dir)

    if not pairs:
        print(f"No matching PNG pairs found between {gt_dir} and {pred_dir}")
        return 
    
    psnr_vals = []
    ssim_vals = []

    for gt_path, pred_path, filename in pairs:
        gt = cv2.imread(gt_path, cv2.IMREAD_COLOR)
        pred = cv2.imread(pred_path, cv2.IMREAD_COLOR)

        if gt is None or pred is None:
            print(f"Skipping unreadable file: { filename }")
            continue
        
        if gt.shape != pred.shape:
            pred = cv2.resize(pred, (gt.shape[1], gt.shape[0]))

        gt_rgb = cv2.cvtColor(gt, cv2.COLOR_BGR2RGB)
        pred_rgb = cv2.cvtColor(pred, cv2.COLOR_BGR2RGB)

        psnr = peak_signal_noise_ratio(gt_rgb, pred_rgb, data_range=255)
        ssim = structural_similarity(gt_rgb, pred_rgb, channel_axis=2, data_range=255)

        psnr_vals.append(psnr)
        ssim_vals.append(ssim)

    if not psnr_vals:
        print("No valid image pairs processed.")
        return
    
    print(f"Compared {len(psnr_vals)} image pairs")
    print(f"Average PSNR: {np.mean(psnr_vals):.4f} dB")
    print(f"Average SSIM: {np.mean(ssim_vals):.4f}")

if __name__ == "__main__":
    gt_dir = "step1_rgbd_data"
    print("=== Study 1: RGB-D Scan vs Ground Truth ===")
    compute_folder_metrics(gt_dir, "step3_rgbd_scan")
    print()
    print("=== Study 1: High-Precision Scan vs Ground Truth ===")
    compute_folder_metrics(gt_dir, "step4_high_precision_3d_scan")

    # STUDY 2 METRICS 
    print()
    print("=== Study 2: 5 Views vs Ground Truth ===")
    compute_folder_metrics(gt_dir, "study2_5views")

    print()
    print("=== Study 2: 10 Views vs Ground Truth ===")
    compute_folder_metrics(gt_dir, "study2_10views")

    print()
    print("=== Study 2: 20 Views vs Ground Truth ===")
    compute_folder_metrics(gt_dir, "study2_20views")

    # STUDY 3 METRICS   
    print()
    print("=== Study 3: Sparse (voxel=0.02) vs Ground Truth ===")
    compute_folder_metrics(gt_dir, "study3_sparse")

    print()
    print("=== Study 3: Medium (voxel=0.01) vs Ground Truth ===")
    compute_folder_metrics(gt_dir, "study3_medium")

    print()
    print("=== Study 3: Dense (voxel=0.005) vs Ground Truth ===")
    compute_folder_metrics(gt_dir, "study3_dense")

    # STUDY 4 METRICS
    print()
    print("=== Study 4: Noisy Reconstruction (noise=0.01) vs Ground Truth ===")
    compute_folder_metrics(gt_dir, "study4_noise_001")