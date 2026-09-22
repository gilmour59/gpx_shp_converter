# Windows Distribution

The app can be distributed to end users without requiring them to install Python.

## Recommended format

Build the application once on a Windows computer using PyInstaller. Distribute the entire generated folder:

```
dist\GPX_SHP_Converter\
```

The folder contains the executable and all required Python/runtime libraries.

End users can launch:

```
GPX_SHP_Converter.exe
```

or use the included convenience launcher:

```
Run_GPX_SHP_Converter.bat
```

## Build steps

On the Windows build computer:

1. Install Python once for the developer/build machine.
2. Clone this repository.
3. Double-click `build_windows.bat`.
4. Wait for the build to finish.
5. Copy the entire `dist\GPX_SHP_Converter` folder to the end-user computer.
6. Optionally copy `Run_GPX_SHP_Converter.bat` into that same folder.

The end-user computer does **not** need Python installed.

## Why one-folder instead of one-file?

GeoPandas, GDAL/Pyogrio, PROJ, and Streamlit include native libraries and data files. PyInstaller's one-folder mode is more reliable and easier to troubleshoot than forcing everything into a single executable.

## Notes

- Build Windows releases on Windows.
- Test the packaged app on a clean Windows machine before deployment.
- Windows Defender or SmartScreen may warn about unsigned internal executables. Code-signing can be added later if the tool is distributed widely.
