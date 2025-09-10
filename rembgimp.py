#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   GIMP - The GNU Image Manipulation Program
#   Copyright (C) 1995 Spencer Kimball and Peter Mattis
#
#   rmbg.py
#   Background removal plugin using rembg library
#   Copyright (C) 2025
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import tempfile
import os

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl

from gi.repository import GLib

try:
    from rembg import remove
    from PIL import Image
    import numpy as np
    DEPENDENCIES_AVAILABLE = True
    IMPORT_ERROR = None
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    IMPORT_ERROR = str(e)

class RemoveBackgroundPlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        return ["rembgimp"]

    def do_set_i18n(self, name):
        return False

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)

        procedure.set_image_types("RGB*, RGBA*")

        procedure.set_menu_label("Remove Background")
        procedure.add_menu_path('<Image>/Filters/')

        procedure.set_documentation("Remove background using AI",
                                    "Uses the rembg library to automatically remove backgrounds from images using AI models",
                                    name)
        procedure.set_attribution("GIMP Community", "GIMP Community", "2025")

        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):
        # Check if dependencies are available
        if not DEPENDENCIES_AVAILABLE:
            import sys
            error_details = f"""Required dependencies not found: {IMPORT_ERROR}

Python executable: {sys.executable}
Python version: {sys.version}

Please install the required packages:
pip install rembg pillow numpy onnxruntime

Or if using a specific Python version:
pip3 install rembg pillow numpy onnxruntime

For GIMP's Python environment, you may need to use:
{sys.executable} -m pip install rembg pillow numpy onnxruntime"""
            
            Gimp.message(error_details)
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, 
                                             GLib.Error("Missing dependencies"))

        if not drawables:
            Gimp.message("No drawable selected")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR,
                                             GLib.Error("No drawable"))

        drawable = drawables[0]
        
        try:
            # Start undo group
            image.undo_group_start()
            
            # Get the drawable dimensions using the correct GIMP 3.0 API
            width = drawable.get_width()
            height = drawable.get_height()
            
            # Get pixel data from GIMP drawable
            buffer = drawable.get_buffer()
            
            # Create a GeglRectangle for the full drawable
            rect = Gegl.Rectangle.new(0, 0, width, height)
            
            # Get pixel data as RGBA - try different format strings
            try:
                pixel_array = buffer.get(rect, 1.0, "R'G'B'A u8", Gegl.AbyssPolicy.NONE)
            except:
                # Fallback format
                try:
                    pixel_array = buffer.get(rect, 1.0, "RGBA u8", Gegl.AbyssPolicy.NONE)
                except:
                    # Another fallback
                    pixel_array = buffer.get(rect, 1.0, None, Gegl.AbyssPolicy.NONE)
            
            # Convert to numpy array and reshape
            np_array = np.frombuffer(pixel_array, dtype=np.uint8)
            
            # Determine the number of channels
            total_pixels = width * height
            channels = len(np_array) // total_pixels
            
            if channels == 3:
                np_array = np_array.reshape((height, width, 3))
                # Convert RGB to RGBA
                rgba_array = np.zeros((height, width, 4), dtype=np.uint8)
                rgba_array[:, :, :3] = np_array
                rgba_array[:, :, 3] = 255  # Full alpha
                np_array = rgba_array
            elif channels == 4:
                np_array = np_array.reshape((height, width, 4))
            else:
                raise ValueError(f"Unexpected number of channels: {channels}")
            
            # Convert to PIL Image (RGBA)
            pil_image = Image.fromarray(np_array, 'RGBA')
            
            # Remove background
            Gimp.message("Processing... This may take a moment.")
            Gimp.displays_flush()  # Update display
            
            output_image = remove(pil_image)
            
            # Convert back to numpy array
            output_array = np.array(output_image)
            
            # Ensure output is RGBA
            if output_array.shape[2] == 3:
                rgba_output = np.zeros((height, width, 4), dtype=np.uint8)
                rgba_output[:, :, :3] = output_array
                rgba_output[:, :, 3] = 255
                output_array = rgba_output
            
            # Create new layer for the result
            new_layer = Gimp.Layer.new(image, "Background Removed", 
                                      width, height, 
                                      Gimp.ImageType.RGBA_IMAGE, 
                                      100.0, 
                                      Gimp.LayerMode.NORMAL)
            
            # Add the new layer above the current one
            parent = drawable.get_parent()
            position = image.get_item_position(drawable)
            image.insert_layer(new_layer, parent, position)
            
            # Set pixel data on new layer
            new_buffer = new_layer.get_buffer()
            
            # Try different ways to set the buffer data
            try:
                new_buffer.set(rect, "R'G'B'A u8", output_array.tobytes())
            except:
                try:
                    new_buffer.set(rect, "RGBA u8", output_array.tobytes())
                except:
                    # Final fallback
                    new_buffer.set(rect, None, output_array.tobytes())
            
            new_buffer.flush()
            
            # Update the display
            new_layer.update(0, 0, width, height)
            
            # End undo group
            image.undo_group_end()
            
            Gimp.message("Background removal completed successfully!")
            
        except Exception as e:
            # End undo group on error
            image.undo_group_end()
            error_msg = f"Error processing image: {str(e)}"
            Gimp.message(error_msg)
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR,
                                             GLib.Error(error_msg))

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(RemoveBackgroundPlugin.__gtype__, sys.argv)
