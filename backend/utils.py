import fitz
import magic
from PIL import Image
import io
import cv2
import numpy as np
import pytesseract
import os
import subprocess
import glob
from music21 import converter, stream, pitch, note, chord

def get_file_type(file):
    mime = magic.from_file(file, mime=True)
    
    if mime == "application/pdf":
        return "pdf"

    if mime.startswith("image/"):
        return "image"

    else:
        raise ValueError(f"Unsupported File Type {mime}")


def load_file_as_image(request, dpi=300):
    print(request)
    file = request['data']['file']
    file_type = get_file_type(file)
    images = []

    if file_type == "image":
        img = Image.open(file)
        images.append(img)


    if file_type == 'pdf':
        doc = fitz.open(file)
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        for page in doc:
            pix = page.get_pixmap(matrix=matrix)
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
            images.append(img)
    
    return images

def deskew_gray(gray):
    edges = cv2.Canny(gray, 50, 150)

    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    if lines is None:
        return gray
    
    angles = []
    for rho, theta in lines[:, 0]:
        angle = (theta - np.pi / 2) * 180 / np.pi
        angles.append(angle)

    angle = np.median(angles)

    (h, w) = gray.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    return cv2.warpAffine(
        gray,
        M,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )



def preprocessing(img: Image.Image) -> Image.Image:
    img = np.array(img)

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Deskew
    gray = deskew_gray(gray)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray)

    # Binarise
    """
    For each pixel:
      Look at a 31×31 region
      Compute a Gaussian-weighted mean
      Subtract 11 from that mean
      If pixel > threshold → white (255)
      Else → black (0)
    """
    thresh = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return Image.fromarray(thresh)


def ocr_images(images):
    text = []
    for img in images:
        processed = preprocessing(img)
        text.append(pytesseract.image_to_string(processed))
    return "\n".join(text)


def save_preprocessed_images(images, output_dir: str,):
    os.makedirs(output_dir, exist_ok=True)
    saved_files = []
    for i, img in enumerate(images):
        processed = preprocessing(img)
        path = os.path.join(output_dir, f"page_00{i+1}.png")
        processed.save(path)
        saved_files.append(path)
    return saved_files


def run_audiveris(input_folder: str, output_folder: str, audiveris_bin: str = "./audiveris/bin/Audiveris"):
    """
    Run Audiveris CLI on a folder of proprocessed images.
    """
    os.makedirs(output_folder, exist_ok=True)

    images = sorted(glob.glob(os.path.join(input_folder, "*.png")))

    cmd = [
        audiveris_bin,
        "-batch",
        "-export",
        "-output", output_folder,
        *images
    ]

    subprocess.run(cmd, check=True)
    print(f"Audiveris finished. Musicxml saved to {output_folder}")

def merge_mxl(files, output_path):
    full_score = stream.Score()

    for f in sorted(files):
        score = converter.parse(f)

        for part in score.parts:
            clean_part = part.flatten()
            full_score.append(clean_part)

    full_score.write("musicxml", output_path)
    print(f"Merged MusicXML written to {output_path}")

def mxl_to_midi(xml_path, midi_path):
    """
    Converts a MusicXML file to MIDI, automatically adjusts the octave
    to a reasonable piano range, and plays it via FluidSynth.
    """

    # 1️⃣ Load score
    score = converter.parse(xml_path)

    # 2️⃣ Collect all MIDI pitches
    midi_pitches = []
    for n in score.recurse().notes:
        if isinstance(n, note.Note):
            midi_pitches.append(n.pitch.midi)
        elif isinstance(n, chord.Chord):
            midi_pitches.extend(p.midi for p in n.pitches)

    # 3️⃣ Compute average pitch
    avg_pitch = sum(midi_pitches) / len(midi_pitches)

    # 4️⃣ Decide octave shift (piano range ~ C2=36 to C6=84)
    shift = 0
    if avg_pitch < 36:
        shift = 12  # too low → up an octave
    elif avg_pitch > 72:
        shift = -12  # too high → down an octave

    # 5️⃣ Transpose all notes/chords
    if shift != 0:
        for n in score.recurse().notes:
            if isinstance(n, note.Note):
                n.pitch = n.pitch.transpose(shift)
            elif isinstance(n, chord.Chord):
                n.pitches = [p.transpose(shift) for p in n.pitches]

    # 6️⃣ Write MIDI
    score.write("midi", midi_path)