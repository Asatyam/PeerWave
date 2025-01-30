import hashlib
import os


def generate_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def get_file_metadata(file_path: str) -> dict:
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        checksum = generate_checksum(file_path)
        return {"file_name": file_name, "file_size": file_size, "checksum": checksum}
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file '{file_path}' does not exist")


def verify_checksum(file_path, expected_checksum):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as file:
            while chunk := file.read(4096):
                sha256_hash.update(chunk)

        actual_checksum = sha256_hash.hexdigest()
        return actual_checksum == expected_checksum

    except Exception as e:
        print(f"Error calculating checksum for {file_path}: {e}")
        return False


def get_files_to_send(dir_name):

    files_dir = os.getcwd() + "/" + dir_name
    files = [
        f for f in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir, f))
    ]
    return files
