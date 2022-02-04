import os
import shutil
import time

while True:
    time.sleep(60 * 60)
    os.remove("/home/ubuntu/fast-tmp/example/example.db")
    shutil.copyfile("/home/ubuntu/fast-tmp/example/example.db.bk", "/home/ubuntu/fast-tmp/example/example.db")
