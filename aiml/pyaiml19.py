age = int(input("Enter age: "))
marks = float(input("Enter marks: "))
attendance = int(input("Enter attendance: "))

result1 = age >= 18 and marks >= 40
result2 = marks >= 80 or attendance >= 90

print("Age >= 18 AND Marks >= 40:", result1)
print("Marks >= 80 OR Attendance >= 90:", result2)
