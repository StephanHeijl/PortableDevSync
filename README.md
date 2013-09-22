PortableDevSync
===============
PortableDevSync is a tool for easy to use Dropbox synchronization using Python. Just start the script, allow access to your DropBox, point it to the right directory and it will start to synchronize the folder with your Dropbox account in a dedicated folder at a set interval.

Requirements
------------
PortableDevSync is cross-platform and only requires Python 2.6+ (Standard on Linux) and an internet connection.

Starting PortableDevSync
------------------------
If your system does not have .py files connected to Python by default, use your command line to navigate to the directory with the 

### Command line arguments ###
By default messages, warnings and errors are presented through dialog boxes. With the `-text` argument these dialogs are turned into a text representation and redirected to STDOUT. This will even work for dialogs that require user input.

Message example:

    +------------------------------------------------------------+
    |============== Message - Dropbox authenticated. ============|
    +------------------------------------------------------------+
    | Dropbox access authenticated, connecting to Dropbox...     |
    +------------------------------------------------------------+

Prompt example.

    +------------------------------------------------------------+
    |===================== Prompt - Question ====================|
    +------------------------------------------------------------+
    | What is your mother's maiden name?                         |
    |                                                            |
    | Response: [______________________________________________] |
    +------------------------------------------------------------+
    Response: _

How does PortableDevSync work?
------------------------------
PortableDevSync will run as a background service on your PC. The interface is reached by visiting http://localhost:9000/ with your browser, but it will use another port if required.
