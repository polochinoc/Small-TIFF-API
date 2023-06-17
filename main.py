import json

import numpy
import rasterio
import uvicorn
from PIL import Image, ImageEnhance, ImagePalette
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse

from doc import init_doc, Palette

thumbnail_path = "img/thumbnail.png"
ndvi_path = "img/ndvi.png"

app = FastAPI()


@app.post("/attributes",
          summary="Retrieves information from a GeoTIFF image using Rasterio",
          tags=["Information Retrieval"])
async def retrieve_attributes_from_tiff(file: UploadFile) -> str:
    """
    Retrieves information from a GeoTiff image using Rasterio:
    - Size: (width, height)
    - Bands number
    - Coordinate Reference System
    - Georeferenced Bounding Box

    Returns a JSON string containing the latter.
    """
    dataset = rasterio.open(file.file)
    if dataset is None:
        return json.dumps({})

    coordinate_ref_sys = "unspecified"
    if dataset.crs and dataset.crs.data and "init" in dataset.crs.data:
        coordinate_ref_sys = dataset.crs.data["init"]

    return json.dumps({
        "img_size": (dataset.width, dataset.height),
        "bands_nbr": dataset.count,
        "coordinate_ref_sys": coordinate_ref_sys,
        "georef_bounding_box": dataset.bounds
    })


@app.post("/thumbnail",
          summary="Computes a RGB thumbnail as PNG from a GeoTIFF image",
          tags=["Image Processing"])
async def convert_tiff_to_png(file: UploadFile, width: int = None, height: int = None) -> FileResponse:
    """
    Computes an RGB thumbnail as PNG from a GeoTIFF image.

    Resolution can be changed through optional 'width' and 'height' parameters (note that it will preserve the image
    dimension).

    Returns the latter and save it as well in the img folder.
    """
    dataset = rasterio.open(file.file)
    if dataset is None or dataset.count == 0:
        return FileResponse(thumbnail_path)

    img_list = []
    for idx in range(dataset.count):
        uint8_array = (dataset.read(idx + 1) // 2 ** 8).astype(numpy.uint8)
        img_list.append(Image.fromarray(uint8_array, "L"))

    if width is None:
        width = img_list[0].width
    if height is None:
        height = img_list[0].height

    img = img_list[0]
    for idx, sub_img in enumerate(img_list[1:]):
        img = Image.blend(img, sub_img, 0.5)

    img.thumbnail((width, height))
    img = ImageEnhance.Contrast(img).enhance(10.0)

    rgb_img = Image.new("RGB", img.size)
    rgb_img.paste(img)
    rgb_img.save(thumbnail_path, "PNG")

    return FileResponse(thumbnail_path)


@app.post("/ndvi",
          summary="Computes a colored PNG using NDVI algorithm from a GeoTIFF image",
          tags=["Image Processing"])
async def compute_ndvi_as_png(file: UploadFile, palette: Palette = None) -> FileResponse:
    """
    Computes a colored PNG using NDVI algorithm from a GeoTIFF image.

    Palette can be changed through optional 'palette' parameter from a predefined list.

    Returns the latter and save it as well in the img folder.
    """
    dataset = rasterio.open(file.file)
    if dataset is None or dataset.count == 0:
        return FileResponse(ndvi_path)

    red = numpy.zeros(dataset.read(1).shape, dtype=float)
    for idx in range(4):
        red += (dataset.read(idx + 1) / float(2 ** 16)).astype(float)

    nir = numpy.zeros(dataset.read(1).shape, dtype=float)
    for idx in range(4, 10):
        nir += (dataset.read(idx + 1) / float(2 ** 16)).astype(float)

    ndvi = (nir - red) / (nir + red)
    ndvi += numpy.ones(ndvi.shape, dtype=float)
    ndvi *= 2 ** (8 - 1)

    img = Image.fromarray(ndvi.astype(numpy.uint8), "L")
    if palette and palette in Palette:
        if palette == Palette.sepia:
            img.putpalette(ImagePalette.sepia())
        elif palette == Palette.wedge:
            img.putpalette(ImagePalette.wedge())
        elif palette == Palette.random:
            img.putpalette(ImagePalette.random())
        elif palette == Palette.negative:
            img.putpalette(ImagePalette.negative())
    else:
        palette = []  # This is a funky home-made palette, hope it outlines vegetation from urban areas, bodies of
        # water and bare lands
        for idx in range(0, 2 ** 8):
            palette.append(min(255, 255 - int(idx * idx / 255.0) + 75))
            palette.append(max(0, idx - int(idx * (255.0 - idx) / (255.0 + idx)) - 50))
            palette.append(0)
        img.putpalette(palette)

    img.save(ndvi_path, "PNG")

    return FileResponse(ndvi_path)


if __name__ == "__main__":
    init_doc(app)
    uvicorn.run(app, log_level="info")
