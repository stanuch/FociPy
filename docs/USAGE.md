# FociPy User Guide
This document provides step-by-step instructions on how to set up the environment, prepare your data, and run the FociPy analysis pipeline.

## 1. Installation & Setup
Before running the program, ensure you have Python 3.8+ installed.

Clone the repository: 
```bash 
git clone [https://github.com/stanuch/focipy](https://github.com/yourusername/focipy)
cd focipy
```

Install dependencies: 
```bash
pip install -r requirements.txt
```

## 2. Data Preparation

FociPy requires a specific directory structure to recognize experiment datasets correctly.

**Rule**: Place your raw microscopy images in the data/raw/ folder. Create a subfolder for each experiment.

Directory Structure Example: 
```text
focipy/
└── data/
    └── raw/
        ├── experiment_01_UV/       <-- Your Experiment Name
        │   ├── image_001.tif
        │   ├── image_002.tif
        │   └── ...
        └── experiment_02_Control/  <-- Another Experiment
            ├── img_A.png
            └── ...
```

Note: Supported image formats currently include: .tif, .png, .jpg.

## 3. Running the Analysis

Navigate to the project root directory in your terminal. The program will ask for the Experiment Name. Enter the exact name of the folder you created in data/raw/. The program will now process all images found in data/raw/experiment_01_UV/.

## 4. Results & Output

Once the processing is complete, results are saved automatically to the data/processed/ directory.

Output Structure: 
```text
data/
└── processed/
    └── experiment_01_UV_processed/
        ├── 001_experiment_01_UV.tif    <-- Processed Image / Mask
        ├── 002_experiment_01_UV.tif
        └── results.csv                 <-- (If you have stats)
```

File Naming Convention
Processed files are renamed for consistency: [original_index]_[experiment_name].[extension]

## 5. Troubleshooting

- "Experiment not found" error: Check that the folder name in data/raw/ matches exactly what you typed (case-sensitive).

- Images not processed: Ensure your image extensions are supported by the script.