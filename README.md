# momotrack

This is a GUI application to help object tracking in 2D/3D images written using Python and the Qt6 library. This application can load 2D/3D microscope images saved in the TIFF or OME-TIFF format, especially those acquired with the [diSPIM light-sheet microscope](http://dispim.org) using [Micro-Manager](https://micro-manager.org/). This application is used in our next paper, whose preprint will be available soon.

**momotrack** was named after [Micro-Manager](https://micro-manager.org/), the famous software for controlling microscope hardware, and also after the tiny friend of our family, **Momo**, who survived the COVID-19 pandemic with our family.

![Momo (hamster)](https://github.com/takushim/momotrack/raw/main/samples/momo.jpg)

Momo (2020-2021, RIP)

## Introduction

**momotrack** is a GUI application available on major operating systems including Windows, MacOSX and Linux. X Window System is necessaary to run on Linux. In this document, the basic usage is described using [FakeTracks.tif](https://samples.fiji.sc/FakeTracks.tif), which is a sample file for TrackMate storing 2D time-lapse images. Object tracking in 3D time-lapse images is also available with this application (sample file will be prepared soon).

## Getting Started

### Requirements

First of all, download and install the following programs.

* [`Python 3.11.1 or later, see Note below`](https://www.python.org)
* [`Qt6 open-source version, see Note below`](https://www.qt.io/download-open-source)
* [`Fiji (recommended)`](https://imagej.net/software/fiji/)
* [`Git (recommended)`](https://git-scm.com/)

Next, install the following packages to your Python environment using pip. You can install these packages directly to the Python system, but it is highly recommended to prepare [a virtual environment](https://docs.python.org/3/library/venv.html) and install packages on it. In this case, make sure to activate the virtual environment before running the program.

* `PySide6`
* `numpy`
* `scipy`
* `tifffile`
* `ome-types`
* `NumpyEncoder`
* `progressbar2` -- make sure to install "progressbar2", not progressbar

All of these libraries can be installed using `pip` by typing:
```
pip install PySide6 numpy scipy tifffile ome-types \
    NumpyEncoder progressbar2
```

**Note:** The latest Qt library (version 6.6 as of Feb 2024) may have trouble opening the main window because it fails to create a QUiLoader instance. This is probably a bug ([see this thread in stackoverflow](https://stackoverflow.com/questions/77736041/pyside6-quiloader-doesnt-show-window)). To avoid this issue, install `Python version 3.11`, `Qt version 6.5.3` and `Pyside6 version 6.5.3` instead of the latest versions. You can try these versions without uninstalling the latest versions if you can prepare a virtual environment for Python.

**Note:** You don't have to install `cupy` although codes for GPU calculation appear in some scripts. GPU calculation is not used in this application.

### Installation

Download the zip file from my [GitHub repository](https://github.com/takushim/momotrack) and place all the files in an appropriate folder, for example, `C:\Users\[username]\momotrack` or `C:\Users\[username]\bin\momotrack`. Add the installed folder to the `PATH` environment variable.

**Note:** If you are using PowerShell, add `.PY` to the PATHEXT environment variable. Otherwise, Python will start in a separate window and finishes soon.

If [git](https://git-scm.com/) is installed, my git repository can be cloned using the following commend:
```
git clone https://github.com/takushim/momotrack.git
```

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
