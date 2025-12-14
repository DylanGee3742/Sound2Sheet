from utils import load_file_as_image, save_preprocessed_images, run_audiveris, merge_mxl, mxl_to_midi
import glob
from music21 import converter, key

if __name__ == "__main__":

    # Example: load some preprocessed images (replace with your own loading code)
    images = load_file_as_image({"data": {"file": "./example_data/Solfeggio in C minor, H. 220 - Complete score (Pierre Gouin).pdf"}})

    # 1️⃣ Preprocess & save images
    temp_folder = "./temp_preprocessed"
    save_preprocessed_images(images, temp_folder)

    # 2️⃣ Run Audiveris to generate MusicXML
    output_folder = "./musicxml"
    run_audiveris(temp_folder, output_folder)

    files = glob.glob("./musicxml/*.mxl")
    merge_mxl(files, "./musicxml/full_score.mxl")
    mxl_to_midi(    
        "./musicxml/full_score.mxl",
        "./musicxml/full_score.mid"
    )

    score = converter.parse("./musicxml/full_score.mid")
    ks = score.analyze('key')
    print(f"Detected key: {ks}")
    # for n in score.recurse().notes:
    #     print(n.nameWithOctave, n.pitch.midi)