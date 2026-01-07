import cv2
import os

def provide_folder_name():
    folder_name = input("Enter the folder name: ")
    return folder_name

def load_image(image_name, folder_name):
    image = cv2.imread(f"./data/test/{folder_name}/{image_name}")
    return image

def main():
    folder_name = provide_folder_name()
    for image_name in os.listdir(f"./data/test/{folder_name}"):
        image = load_image(image_name, folder_name)
        cv2.imshow(image_name, image)   
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()