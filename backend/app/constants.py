import os

WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Work Directory: {}".format(WORK_DIR))