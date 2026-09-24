import os
import pickle
import time

file_path = r"C:\Users\sridh\Downloads\aq_models_both_scopes.pkl"

print("STEP 1: Checking file...")

size = os.path.getsize(file_path)

print("File size:", size / (1024 * 1024), "MB")

print("STEP 2: Opening file...")

start = time.time()

with open(file_path, "rb") as f:
    print("STEP 3: File opened!")
    data = pickle.load(f)

print("STEP 4: File loaded!")
print("Loading time:", time.time() - start, "seconds")
print("Type:", type(data))
