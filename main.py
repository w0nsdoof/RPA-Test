import os, logging, unittest
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                    ])

def categorize_files_by_type(folder_path, min_size=None, max_size=None, modified_last=None, skip_extensions=None,pass_extensions=None):
    """
    Categorize files by type/extension (txt/pdf/...) with optional filters and skip list.

    :param folder_path: Path to the directory to scan
    :param min_size: Minimum file size in bytes
    :param max_size: Maximum file size in bytes
    :param modified_last: Maximum modification date as a datetime object
    :param skip_extensions: List of file extensions to skip (['.txt', '.jpg'])
    :param pass_extensions: List of file extension to pass through filter, others would be skipped
    :return: Dictionary with file extensions as keys and lists of file paths as values
    """
    result = {}

    if skip_extensions is None:
        skip_extensions = set()
    else:
        skip_extensions = set(skip_extensions)

    if not os.path.isdir(folder_path): 
        error_message = f"The path '{folder_path}' is not a valid directory or does not exist."
        logging.error(error_message)
        raise ValueError(error_message)
    
    logging.info(f"Starting to scan directory: {folder_path}")

    def scan_dir(current_path):
        logging.debug(f"Scanning directory: {current_path}")
        with os.scandir(current_path) as current_folder:
            for entry in current_folder:
                if entry.is_file():
                    file_size = entry.stat().st_size
                    file_mtime = datetime.fromtimestamp(entry.stat().st_mtime)
                    extension = os.path.splitext(entry.name)[1].lower()
                    path = entry.path

                    if (skip_extensions is not None) and (extension in skip_extensions):
                        logging.debug(f"Skipping file {path} due to extension filter")
                        continue

                    if (pass_extensions is not None) and (extension not in pass_extensions):
                        logging.debug(f"Skipping file {path} due to extension filter")
                        continue
                    
                    if (min_size is not None) and (file_size < min_size):
                        logging.debug(f"Skipping file {path} due to size filter")
                        continue
                    
                    if (max_size is not None) and (file_size > max_size):
                        logging.debug(f"Skipping file {path} due to size filter")
                        continue
                    
                    if (modified_last is not None) and (file_mtime > modified_last):
                        logging.debug(f"Skipping file {path} due to modification date filter")
                        continue

                    logging.debug(f"Found file: {path} with extension: {extension}")

                    if extension in result:
                        result[extension].append(path)
                    else:
                        result[extension] = [path]
                
                elif entry.is_dir():
                    logging.debug(f"Found directory: {entry.path}, scanning recursively")
                    scan_dir(entry.path)  

    scan_dir(folder_path)
    logging.info(f"Finished scanning directory: {folder_path}")
    return result

class TestCategorizingByPath(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_directory'
        os.makedirs(self.test_dir, exist_ok=True)
        self.subfolder = os.path.join(self.test_dir, 'subfolder')
        os.makedirs(self.subfolder, exist_ok=True)

        self.files = [
            os.path.join(self.test_dir, 'file1.txt'),
            os.path.join(self.test_dir, 'file2.pdf'),
            os.path.join(self.test_dir, 'file3'),
            os.path.join(self.test_dir, 'subfolder', 'file4.txt'),
            os.path.join(self.test_dir, 'subfolder', 'file5.txt'),
            os.path.join(self.test_dir, 'subfolder', 'file6.pdf')
        ]

        for file in self.files:
            with open(file, 'w') as f:
                f.write('Sample content' * 10)

        with open(self.files[0], 'w') as f: # file1.txt
            f.write('Small content')  

        with open(self.files[1], 'w') as f: # file2.pdf
            f.write('Large content' * 1000) 

    def tearDown(self):
        for file in self.files:
            if os.path.exists(file):
                os.remove(file)
        
        if os.path.exists(self.subfolder):
            os.rmdir(self.subfolder)
        os.rmdir(self.test_dir)

    def test_empty_directory(self):
        empty_dir = 'empty_directory'
        os.makedirs(empty_dir, exist_ok=True)

        result = categorize_files_by_type(empty_dir)
        expected = {}

        self.assertEqual(result, expected)

        os.rmdir(empty_dir)

    def test_directory_with_files(self):
        result = categorize_files_by_type(self.test_dir)
        expected = {
            '.txt': ['test_directory\\file1.txt', 'test_directory\\subfolder\\file4.txt', 'test_directory\\subfolder\\file5.txt'], 
            '.pdf': ['test_directory\\file2.pdf', 'test_directory\\subfolder\\file6.pdf'], 
            '': ['test_directory\\file3']
        }
        self.assertEqual(result, expected)

    def test_directory_with_no_files(self):
        no_files_dir = 'no_files_directory'
        os.makedirs(no_files_dir, exist_ok=True)
        os.makedirs(os.path.join(no_files_dir, 'subfolder1'), exist_ok=True)
        os.makedirs(os.path.join(no_files_dir, 'subfolder2'), exist_ok=True)

        result = categorize_files_by_type(no_files_dir)
        expected = {}

        self.assertEqual(result, expected)

        os.rmdir(os.path.join(no_files_dir, 'subfolder1'))
        os.rmdir(os.path.join(no_files_dir, 'subfolder2'))
        os.rmdir(no_files_dir)

    def test_invalid_path(self):
        invalid_path = 'invalid_directory'

        with self.assertRaises(ValueError):
            categorize_files_by_type(invalid_path)

    def test_min_size_filter(self, min_size=1000):
        result = categorize_files_by_type(self.test_dir, min_size=min_size)  

        for key in result:
            for item in result[key]:
                file_size = os.path.getsize(item)
                self.assertGreaterEqual(file_size, min_size,f"File {item} should be larger than {min_size} bytes")

    def test_max_size_filter(self, max_size=20):
        result = categorize_files_by_type(self.test_dir, max_size=max_size)  

        for key in result:
            for item in result[key]:
                file_size = os.path.getsize(item)
                self.assertLessEqual(file_size, max_size, f"File {item} should be lighter than {max_size} bytes")

    def test_modified_last_filter(self):
        file_mtime = datetime.now() - timedelta(days=5)  
        os.utime(self.files[0], (file_mtime.timestamp(), file_mtime.timestamp()))

        result = categorize_files_by_type(self.test_dir, modified_last=datetime.now() - timedelta(days=3))
        expected = {
            '.txt': ['test_directory\\file1.txt'],
        }
        self.assertEqual(result, expected)

    def test_skip_extensions(self):
        result = categorize_files_by_type(self.test_dir, skip_extensions=['.pdf', '']) 
        keys = result.keys()

        self.assertNotIn(".pdf", keys, "PDF files should be skipped")
        self.assertNotIn("", keys, "No extension should be skipped")

        self.assertIn(".txt", keys, "Text  files should not be skipped")

    def test_pass_extensions(self):
        result = categorize_files_by_type(self.test_dir, pass_extensions=[".pdf"])
        keys = result.keys()
        
        self.assertIn(".pdf", keys, "PDF files should be skipped but found in result")  
        self.assertEqual(len(keys), 1, "Result dictionary should have only 1 key ['.pdf']")

if __name__ == '__main__':
    path_to_root = "test_data"

    skip_extensions = ['.txt', '.png']
    result = categorize_files_by_type(path_to_root, skip_extensions=skip_extensions)
    for key in result:
        print(f"'{key}': {result[key]}")

# Expected output (format):
# {
#   '.txt': ['/path/to/root/folder/file1.txt', '/path/to/root/folder/subfolder/file2.txt'],
#   '.jpg': ['/path/to/root/folder/image1.jpg', '/path/to/root/folder/subfolder/image2.jpg'],
#   '.pdf': ['/path/to/root/folder/document1.pdf']
# }