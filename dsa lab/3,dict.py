#dictionary
student={
    "name":"sri",
    "age" : 20,
    "dept":"cs",
    "mark":99
}
print("student details:",student)
print("name:",student["name"])
print("dept:",student["dept"])
student["city"]="bangalore"
print("after adding city:",student)
student["marks"]=90
print("after updating marks",student)
student.pop("age")
print("after removing age:",student)
print("keys:",student.keys())
print("values:",student.values())
