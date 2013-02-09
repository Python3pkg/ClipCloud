# ClipCloud

ClipCloud is a program for quickly sharing files. Currently it consists of a command line program written in Python that can upload files to Dropbox.

## How do I get it?
`[sudo] pip install clipcloud`

or

```
git clone git://github.com/lavelle/ClipCloud.git
cd ClipCloud
[sudo] python setup.py install
```

## How do I use it?

### Arguments:
- `up </path/to/file/or/folder> [second file, third file...]`: Upload the specified files and folders.
- `snap [-m mode]`: Take a screenshot and upload it. Mode can be `draw` or `screen`. Defaults to `screen`.
- `history [-l number_of_records] [-t sort_by] [-b start] [-d direction]`: Show a history of the files you've uploaded previously. Defaults to the last 10 records.
- `revisit <operation> <id>`: Do something with a previously uploaded file. `id` specifies which file to upload. `operation` can be either `upload`, `remote` or `local`.
- `text [-e extension]`: Share the contents of your clipboard. Currently uploads to Dropbox, support for Github Gists planned. Extenstion defaults to `txt`.

### Options:
- `-s` `--share`: Specify what to do with the link to the uploaded file. Current options are sharing to Facebook, Twitter, Email, setting the clipboard or writing to stdout so you can pipe the url to other programs. Defaults to `clipboard`.
- `-h` `--help`: Display the help message

## What does it need?
- Python 2.6
- Argparse if using Python version < 2.7
- The Python Dropbox API and all its dependencies

## Changelog

### 0.1
- Inital release
