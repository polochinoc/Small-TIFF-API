# Small-TIFF-API
Small API built with FastAPI to retrieve and do some operations on TIFF images.

## Requirements
Python 3+ and the following libraries:
- FastAPI (fastapi)
- Python-Multipart (python-multipart)
- Uvicorn (uvicorn)
- Rasterio (rasterio)
- aiofiles (aiofiles)
- PIL (Pillow)
- NumPy (numpy)

## How-to
1. Pull the project
2. Execute the main.py
3. Open the [Swagger Doc](http://127.0.0.1:8000/docs)!
4. Have fun with the routes! (click on "Try it out" button to be able to use them)

## Areas for improvement

### Form-related
- Store dependencies in a **requirements.txt** file
- Separate routes in specific file
- Enhance documentation
  - Path and body parameters
  - Schemas
  - ...

### Substance-related
- Find an already-made better palette for **NDVI**
- Specify resolution through a *quality* parameter
- Make the **NDVI** calculation independent of the satellite providing the data