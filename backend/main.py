from utils import load_file_as_image, ocr_images, preprocessing, save_preprocessed_images, run_audiveris

# if __name__ == "__main__":
#     test_file = "example.pdf"  # or "example.png", "example.jpg"

#     # 1. Load file as images
#     images = load_file_as_image({"data": {"file": "./Solfeggio in C minor, H. 220 - Complete score (Pierre Gouin).pdf"}})

#     print(f"Loaded {len(images)} images from {"./Solfeggio in C minor, H. 220 - Complete score (Pierre Gouin).pdf"}")

#     # 2. Run OCR on all images
#     preprocessed_images = preprocessing(images)

#     # 3. Output result
#     print("---------- OCR Result ----------")
#     print(extracted_text)
#     print("--------------------------------")

#     # 4. Optional: save preprocessed images to check results visually
#     for i, img in enumerate(images):
#         preprocessed = preprocessing(img)
#         preprocessed.save(f"preprocessed_page_{i+1}.png")
#         print(f"Saved preprocessed_page_{i+1}.png")

if __name__ == "__main__":

    # Example: load some preprocessed images (replace with your own loading code)
    images = load_file_as_image({"data": {"file": "./example_data/Solfeggio in C minor, H. 220 - Complete score (Pierre Gouin).pdf"}})

    # 1️⃣ Preprocess & save images
    temp_folder = "./temp_preprocessed"
    save_preprocessed_images(images, temp_folder)

    # 2️⃣ Run Audiveris to generate MusicXML
    output_folder = "./musicxml"
    run_audiveris(temp_folder, output_folder)