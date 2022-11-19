# Maya Workflow Tools

A collection of workflow related tools for Maya.

## Installation

- Download the [latest release](https://github.com/bohdon/maya-workflowtools/releases/latest)
- Unzip and copy the contents to:
    - Windows: `~/Documents/maya/modules/`
    - Mac: `~/Library/Preferences/Autodesk/maya/modules/`
    - Linux: `~/maya/modules/`

> Note that you may need to create the `modules` folder if it does not exist.
    
Once installed, the result should look like this:
```
.../modules/workflowtools/
.../modules/workflowtools.mod
```

## Setup & Usage

- View the READMEs for each tool for more info, setup, and usage.
    - [Quick Menus](/src/workflowtools/scripts/quickmenus/README.md)
    - [Resetter](/src/workflowtools/scripts/resetter/README.md)
    - [RMB Menu Hook](/src/workflowtools/scripts/rmbmenuhook/README.md)

## Known Issues

PyMel contains a bug that prevents using some commands in Python 3 due to old-style dynamic imports. This will cause issues when trying to run some functionality in the workflowtools. [This pull request](https://github.com/LumaPictures/pymel/pull/445) fixes issues, and is a fix you can make to the installed version of PyMel.
