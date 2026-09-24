import os

print("Python is running!")
print()
print("Current folder:")
print(os.getcwd())
print()
print("Files in this folder:")

for file in os.listdir():
    print(file)
