import cv2
import os

RAW_PATH = "./data/test_raw/"
PROCESSED_PATH = "./data/test_processed/"

def load_image(image_name, folder_name):
    return cv2.imread(f"{RAW_PATH}{folder_name}/{image_name}")

def save_image(image, image_name, folder_name):
    output_folder = f"{PROCESSED_PATH}{folder_name}"
    os.makedirs(output_folder, exist_ok=True)

    image_new_name = image_name.split(".")[0] + "_processed." + image_name.split(".")[1]
    cv2.imwrite(f"{output_folder}/{image_new_name}", image)
    print(f"Image saved as {image_new_name}")

def main():
    experiment_name = str(input("Enter the experiment folder name: "))
    if not os.path.exists(f"{RAW_PATH}{experiment_name}"):
        print(f"Folder {experiment_name} does not exist.")
        return

    for image_name in os.listdir(f"{RAW_PATH}{experiment_name}"):
        if not os.path.isfile(f"{RAW_PATH}{experiment_name}/{image_name}"):
            continue
        image = load_image(image_name, experiment_name)
        save_image(image, image_name, experiment_name)
    
if __name__ == "__main__":
    main()