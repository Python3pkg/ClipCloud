#ClipCloud

ClipCloud is a program for quickly sharing files. Currently it consists of a command line program written in program that can upload files to Dropbox.
A GUI is planned, as well as the ability to upload elsewhere, such as a personal server via SSH.
It has only been tested on Windows, and the ability to take screenshots is only supported on Windos because that part is written in C#.

##Arguments:
- `help`: display the help file.
- `file </path/to/file>`: upload the specified file
- `screenshot`: take a screenshot and upload it.
- If no arguments are specified, the enitre primary screen is used.
- `history [number_of_items]`: show a history of the files you've uploaded previously. defaults to the last 10 records.
- `record <operation> <id>`: Do something with a previously uploaded file.
    id specifies which file to upload
    operation can be either `reupload`, `open_remote` or `open_local`

##Options
- `-s` `--share`: Specify what to do with the link to the upload file. Current options are sharing to Facebook, Twitter, Email or setting the clipboard. Defaults to `clipboard`

##Todo:
- Package as a .exe for distribution to users without python
- Cross platform support - starting with screenshots
- Add custom dimensions to screenshots
- Add text snippet sharing - to Gist?
