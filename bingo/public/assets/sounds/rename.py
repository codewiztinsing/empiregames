import os
import re

def rename_files():
    """
    Rename files from format A(66).mp3 to 66.mp3
    """
    # Get current directory
    current_dir = os.getcwd()
    
    # Pattern to match files like A(66).mp3
    pattern = r'^A\((\d+)\)\.mp3$'
    
    # Get all files in current directory
    for filename in os.listdir(current_dir):
        match = re.match(pattern, filename)
        
        if match:
            # Extract the number from parentheses
            number = match.group(1)
            
            # Create new filename
            new_filename = f"{number}.mp3"
            
            # Get full paths
            old_path = os.path.join(current_dir, filename)
            new_path = os.path.join(current_dir, new_filename)
            
            try:
                # Rename the file
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")
                
            except OSError as e:
                print(f"Error renaming {filename}: {e}")

if __name__ == "__main__":
    rename_files()
