# GIMP Background Removal Plugin

A GIMP 3.0 plugin that uses AI to automatically remove backgrounds from images using the `rembg` library.

![GIMP Version](https://img.shields.io/badge/GIMP-3.0+-blue)
![Python Version](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-GPL%20v3-red)

## Features

- **AI-Powered Background Removal**: Uses state-of-the-art machine learning models via the `rembg` library
- **Non-Destructive Editing**: Creates a new layer with the background removed, preserving your original image
- **Easy Integration**: Seamlessly integrates into GIMP's menu system
- **Automatic Processing**: No manual selection or complex steps required
- **Undo Support**: Full undo/redo support with proper GIMP integration

## Screenshots

*Before and after example would go here*

## Requirements

### Software Requirements
- GIMP 3.0 or newer
- Python 3.8 or newer
- Internet connection (for downloading AI models on first use)

### Python Dependencies
- `rembg` - AI background removal library
- `pillow` (PIL) - Image processing
- `numpy` - Numerical computing
- `onnxruntime` - AI model inference engine

## Installation

### 1. Install Python Dependencies

#### On Ubuntu/Debian/Kali Linux:
```bash
# Install system packages
sudo apt update
sudo apt install python3-pil python3-numpy

# Install AI libraries (using --break-system-packages if needed)
pip3 install rembg onnxruntime --break-system-packages
```

#### On Other Linux Distributions:
```bash
pip3 install rembg pillow numpy onnxruntime
```

#### On Windows:
```cmd
pip install rembg pillow numpy onnxruntime
```

#### On macOS:
```bash
pip3 install rembg pillow numpy onnxruntime
```

### 2. Install the Plugin

1. Download `rmbg.py` from this repository
2. Copy it to your GIMP plugins directory:
   - **Linux**: `~/.config/GIMP/3.0/plug-ins/`
   - **Windows**: `%APPDATA%\GIMP\3.0\plug-ins\`
   - **macOS**: `~/Library/Application Support/GIMP/3.0/plug-ins/`
3. Make the file executable (Linux/macOS only):
   ```bash
   chmod +x ~/.config/GIMP/3.0/plug-ins/rmbg.py
   ```
4. Restart GIMP

## Usage

1. Open an image in GIMP
2. Select the layer you want to process
3. Go to **Filters → Generic → Remove Background**
4. Wait for the AI processing to complete (may take 10-30 seconds depending on image size)
5. A new layer named "Background Removed" will be created with the transparent background

### First-Time Usage
On first use, the plugin will download the AI model (approximately 100-200MB). This is a one-time download that will be cached for future use.

## Troubleshooting

### "Missing dependencies" error
Make sure all Python packages are installed for the correct Python environment. You can check which Python GIMP is using:

1. In GIMP, go to **Filters → Python-Fu → Console**
2. Run: `import sys; print(sys.executable)`
3. Install packages for that specific Python installation

### "No module named 'onnxruntime'" error
```bash
pip3 install onnxruntime --break-system-packages
```

### Plugin doesn't appear in menu
- Ensure the file is in the correct plugins directory
- Make sure the file is executable (Linux/macOS)
- Restart GIMP completely
- Check GIMP's error console for any Python errors

### Processing is slow
- First-time usage requires downloading the AI model
- Large images take longer to process
- Consider resizing very large images before processing

## Technical Details

### AI Models
This plugin uses the `rembg` library, which provides several pre-trained models:
- **u2net** (default): General purpose background removal
- **u2netp**: Lighter version of u2net
- **silueta**: Good for objects and people
- **isnet-general-use**: Newer, more accurate model

The default model works well for most use cases, including people, objects, and animals.

### Image Processing
- Supports RGB and RGBA images
- Maintains original image resolution
- Preserves image quality during processing
- Creates proper alpha channel for transparency

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork this repository
2. Install GIMP 3.0 development version
3. Install Python dependencies
4. Make changes to `rmbg.py`
5. Test in GIMP
6. Submit pull request

## Known Issues

- Very large images (>4K) may cause memory issues
- First-time model download requires internet connection
- Processing time varies significantly based on image complexity and hardware

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [rembg](https://github.com/danielgatis/rembg) - The amazing AI background removal library
- [GIMP](https://www.gimp.org/) - The GNU Image Manipulation Program
- [U²-Net](https://github.com/xuebinqin/U-2-Net) - The neural network architecture used by rembg

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Search existing [Issues](https://github.com/yourusername/gimp-background-removal/issues)
3. Create a new issue with:
   - Your GIMP version
   - Your Python version
   - Your operating system
   - Complete error message
   - Steps to reproduce

---

⭐ If this plugin helped you, please consider giving it a star on GitHub!
