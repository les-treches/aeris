import os
print("------------list-------------")
students=["anu","bala","cathy","david"]
print("original list:",students)
print("first student: ",students[0])
students.append("esha")
print("after adding:",students)
students.remove("bala")
print("after removing:",students)
students[1]="cathy updated"
print("after updating: ",students)
students.sort()
print("sorted lists: ",students)
