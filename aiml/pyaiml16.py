age = int(input("Enter age: "))
attendance = int(input("Enter attendance percentage: "))

result = age >= 18 and attendance >= 75
print("Eligible (Age >= 18 AND Attendance >= 75):", result)
