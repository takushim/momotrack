# momotrack

This is a graphical user interface (GUI) application to help object tracking in 2D/3D images written using Python and the Qt6 library. This application can load 2D/3D microscope images saved in the TIFF or OME-TIFF format, especially those acquired with the [diSPIM light-sheet microscope](http://dispim.org) using [Micro-Manager](https://micro-manager.org/). This application is used in our next paper, whose preprint will be available soon.

**momotrack** was named after [Micro-Manager](https://micro-manager.org/), the famous software for controlling microscope hardware, and also after the tiny friend of our family, **Momo**, who survived the COVID-19 pandemic with our family.

![Momo (hamster)](https://github.com/takushim/momotrack/raw/main/samples/momo.jpg)

Momo (2020-2021, RIP)

## Introduction

**momotrack** is a GUI application available on major operating systems including Windows, MacOSX and Linux. X Window System is necessaary to run on Linux. In this document, the basic usage is described using [FakeTracks.tif](https://samples.fiji.sc/FakeTracks.tif), which is a sample file for TrackMate storing 2D time-lapse images. Object tracking in 3D time-lapse images is also available with this application (sample file will be prepared soon).

## Getting Started
### Installation and usage
This program provides a GUI based on Qt6 and PySide6. Thus, please install the following components beforehand:
* [`Qt6 open-source version`](https://www.qt.io/download-open-source) -- Installation of Qt6 can be **tricky**. See **Notes #2 and #3** below.
* [`Python`](https://www.python.org) -- Version **3.12.x** is recommended, as PySide6 may not fully support **3.13.x** 

After installing these components, please refer to the following guides, using the **momotrack** as the repository name.
* [Installation of the Python toolkits](https://github.com/takushim/momodoc/blob/main/installation.md)
* [Basic usage of Python scripts](https://github.com/takushim/momodoc/blob/main/usage.md)

The required Python packages are:
* `PySide6` -- see **Notes #2 and #3** below.
* `numpy`
* `scipy`
* `tifffile`
* `ome-types`
* `NumpyEncoder`
* `progressbar2` -- make sure to install **progressbar2**, not progressbar

You can install these packages using the following command:
```
pip install PySide6 numpy scipy tifffile ome-types NumpyEncoder progressbar2
```

To clone this repository, run:
```
git clone https://github.com/takushim/momotrack.git
```

**Note #1:** You do not need to install `cupy`, even though some scripts contain codes for GPU computation. GPU acceleration is not used in this application.

**Note #2:** The version of `PySide6` must match the version of Qt6. You can install a specific version of PySide6 using the `pip` command as shown below. `pip` will automatically uninstall the currently installed version and replace it with the specified one. If you are using an older version of Qt6, consider using Python 3.11.x to ensure compatibility.
```
pip install PySide6==6.5.3
```

**Note #3:** Certain versions of the Qt framework (notably 6.6, 6.7, and 6.8) fail to create a `QUiLoader` instance, causing the application to **remain running without displaying the main window**. This is likely a bug, as described in [this Stack Overflow thread](https://stackoverflow.com/questions/77736041/pyside6-quiloader-doesnt-show-window). To avoid this issue, install **the latest 6.9.x version** of Qt6, along with the matching version of PySide6. You can experiment with different versions by creating separate Python virtual environments.

## Open an image

Run the following command in the folder where [FakeTracks.tif](https://samples.fiji.sc/FakeTracks.tif) is saved.
```
mmtrack.py FakeTracks.tif
```

This will open a window with an image as shown below. You can browse the image using cursor keys (`RIGHT/LEFT` keys for the time, `UP/DOWN` keys for the Z-stack).

![Main Window](https://github.com/takushim/momotrack/raw/main/samples/cartoons_mainwindow.jpg)

Tracking records will be saved in a file, `XXX_track.json`, which will be `FakeTracks_track.json` unless otherwise specified. You can load this tracking file during the start-up with an option `-f` as shown below.

```
mmtrack.py -f FakeTracks_track.json FakeTracks.tif
```

 **Note:** Scripts to help this process are prepared in the top folder (`track` for bash and `track.ps1` for PowerShell).


**Note:** When loading a 3D image, the Z and T axes may be swapped with each other. In this case, open the image with Fiji and reassign the axes from `Image -> Hyperstacks -> Re-order hyperstack`.

## Object tracking

Object tracking begins with `Ctrl + click` to place a marker followed by `a sequence of clicks` until the `ESC` key is pressed. By default, the "Move Automatically" option is ON to help your tracking by moving the time frame after each click and by going back to the frame of the first marker after each cycle.

![Legends](https://github.com/takushim/momotrack/raw/main/samples/cartoons_legend.jpg)

During the tracking, a **reticle** appears to help precise marking. Press `SPACE` to add a marker at the center of the reticle. This reticle can be moved using `CTRL + cursor keys`. You can also move to an image at a different time frame or Z-frame using cursor keys.

**Note:** You can add the next marker anywhere - even in the previous frame. This is a disadvantage for giving a high degree of freedom. Be careful.

**Note:** Small spots named "ghosts" appear when you track objects in 3D images. This will help you to find the original spot in the 3D stack.

Markers can be deleted using a **context menu** that appears after a `right click` to the marker. You can also delete a marker by pressing `DELETE` after selecting the marker.

When a marker is selected, you can move the position of marker using `SHIFT + cursor keys`. You can also add the "descendant" of the marker by `clicking the image` or pressing `SPACE`. By combining the **context menu** in the previous paragraph, you can remove the "descendants" of a marker and resume tracking. You can also check which marker is the "ascendant" and the "descendants" of the selected marker.

**Note:** You can add multiple "descendants" for a marker. This can be highly confusing. Use with caution.

## Author

* **[Takushi Miyoshi](https://github.com/takushim)** - Assistant professor, Department of Biomedicine, Southern Illinois University School of Medicine

## License

This application is licensed under the MIT license.
