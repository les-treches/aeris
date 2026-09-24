#file writing
file_name="student1.txt"
try:
    file=open(file_name,"w")
    file.write("student name: anu\n")
    file.write("department: computer science\n")
    file.write("mark:90\n")
    file.close()
    print("data successfully written to",file_name)
except Exception as e:
    print("error while writing file:",e)
    
