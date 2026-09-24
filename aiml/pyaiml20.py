# Input
name = input("Enter student name: ")
age = int(input("Enter age: "))
m1 = float(input("Enter marks of subject 1: "))
m2 = float(input("Enter marks of subject 2: "))
m3 = float(input("Enter marks of subject 3: "))
attendance = int(input("Enter attendance percentage: "))
college = input("Enter college name: ")

# Processing
total = m1 + m2 + m3
average = total / 3
percentage = (total / 300) * 100

# Boolean checks
pass_check = percentage >= 40
attendance_check = attendance >= 75
distinction = percentage >= 80 and attendance >= 75
excellent = percentage >= 90 or attendance >= 90

# Output
print("\n========== STUDENT REPORT ==========")
print("Name:", name)
print("Age:", age)
print("College:", college)
print("Marks:", m1, ",", m2, ",", m3)
print("Total Marks:", total)
print("Average:", average)
print("Percentage:", percentage, "%")
print("Attendance:", attendance, "%")
print("\n--- Boolean Results ---")
print("Percentage >= 40:", pass_check)
print("Attendance >= 75:", attendance_check)
print("Percentage >= 80 AND Attendance >= 75:", distinction)
print("Percentage >= 90 OR Attendance >= 90:", excellent)
print("====================================")
