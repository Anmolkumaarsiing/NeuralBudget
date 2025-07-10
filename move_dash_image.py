
import os
import shutil

src = "D:/NeuralBudget/apps/core/templates/core/image.png"
dest = "D:/NeuralBudget/apps/core/static/core/img/image_from_pages.png"

try:
    shutil.move(src, dest)
    print(f"Moved {src} to {dest}")
except FileNotFoundError:
    print(f"Error: File not found - {src}")
except Exception as e:
    print(f"Error moving {src} to {dest}: {e}")
