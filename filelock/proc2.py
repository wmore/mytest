from filelock import FileLock
import time
if __name__ == '__main__':

    with FileLock("123.txt") as f:
        # work with the file as it is now locked
        print("Lock acquired.")
        print open(f.file_name).readlines()
