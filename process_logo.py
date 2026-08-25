from PIL import Image
import os
import glob

# Paths
source_logo = r'C:\Users\eyar1\.gemini\antigravity\brain\59e16a99-230d-451b-a518-67e4287a48f4\lendwell_complex_1787578179062.jpg'
dest_dir = r'C:\Users\eyar1\ECOM\antigravity works\Project_Loan\static\logos'
dest_logo = os.path.join(dest_dir, 'lendwell_logo.jpg')
favicon_path = r'C:\Users\eyar1\ECOM\antigravity works\Project_Loan\static\favicon.ico'

# Delete old logos
for f in glob.glob(os.path.join(dest_dir, '*.jpg')):
    try:
        os.remove(f)
    except:
        pass

# Copy main logo
img = Image.open(source_logo)
img.save(dest_logo)

# Create favicon (crop the top square part with the shield/arrow)
width, height = img.size
# Assuming the image is 1024x1024 and the symbol is in the top center
# Let's crop a square from (100, 100) to (924, 924) or similar to avoid text
left = width * 0.15
top = height * 0.15
right = width * 0.85
bottom = height * 0.65 # avoiding text at the bottom

cropped = img.crop((left, top, right, bottom))
# Make it square by adding padding or just cropping a square to begin with
size = min(cropped.size)
center_x = cropped.size[0] // 2
center_y = cropped.size[1] // 2
half = size // 2

square = cropped.crop((center_x - half, center_y - half, center_x + half, center_y + half))

# Resize and save as ICO
icon_sizes = [(32,32), (64,64)]
square.save(favicon_path, format='ICO', sizes=icon_sizes)

print('Logo and favicon created successfully.')
