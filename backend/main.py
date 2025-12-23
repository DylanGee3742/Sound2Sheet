from utils import load_file_as_image, save_preprocessed_images, run_audiveris, merge_mxl, mxl_to_midi
import glob
from music21 import converter, key
import os, shutil

if __name__ == "__main__":

    # Example: load some preprocessed images (replace with your own loading code)
    folder_path = "./example_data"
    folder_list = os.listdir(folder_path)
    for image in folder_list:
        images = load_file_as_image({"data": {"file": f"./example_data/{image}"}})

        image = image.replace(".pdf", "")
        # 1️⃣ Preprocess & save images
        temp_folder = "./temp_preprocessed"
        save_preprocessed_images(images, temp_folder)

        # 2️⃣ Run Audiveris to generate MusicXML
        output_folder = "./musicxml"
        run_audiveris(temp_folder, output_folder)

        files = glob.glob("./musicxml/*.mxl")
        merge_mxl(files, f"./musicxml/{image}_full_score.mxl")
        mxl_to_midi(    
            f"./musicxml/{image}_full_score.mxl",
            f"./full_scores/{image}_full_score.mid"
        )

        musicxml_folder = './musicxml'

        for filename in os.listdir(musicxml_folder):
            file_path = os.path.join(musicxml_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        temp_preprocessed_folder = './temp_preprocessed'

        for filename in os.listdir(temp_preprocessed_folder):
            file_path = os.path.join(temp_preprocessed_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # score = converter.parse(f"./full_scores/{image}_full_score.mid")
        # ks = score.analyze('key')
        # print(f"Detected key: {ks}")
        # for n in score.recurse().notes:
        #     print(n.nameWithOctave, n.pitch.midi)