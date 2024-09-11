# Function: _categorize_files_by_type_

Is a utility function that scans a given directory and its subdirectories, categorizing files based on their file extensions. It supports multiple optional parameters for filtering files and also goes with a simple logging system, unit testing.

## Functionality Overview:

- **Input**:
  - **folder_path (str, required)**: The path to the root folder
  - min_size (int, optional): Filters files by a minimum file size, in bytes
  - max_size (int, optional): Filters files by a maximum file size, in bytes
  - modified_last (datetime, optional): Filters files by their last modification date
  - skip_extensions (list, optional): A list of file extensions to skip
  - pass_extensions(list, optional): A list of file extension to pass
- **Output**: returns a dictionary where:
  - Keys: File extensions (e.g., .txt, .pdf, .jpg).
  - Values: Lists of full paths to the files with those extensions.

## How to run

The test data was provided in a .zip file from HR

### Run with test data

```bash
    py main.py
```

### Run unit test

```bash
    py -m unittest main.py
```
