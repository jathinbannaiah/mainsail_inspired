import os
import cairosvg

# Directory containing SVG files
directory = '/home/j2002/Desktop/sigma images'

# Iterate through files in the directory
for filename in os.listdir(directory):
        # Check if the file is an SVG file
        print("in")
        svg_file = os.path.join(directory, filename)
        png_file = os.path.join(directory,filename + ".png")

        # Convert SVG to PNG
        cairosvg.svg2png(url=svg_file, write_to=png_file)

        print(f"Converted {svg_file} to {png_file}")
