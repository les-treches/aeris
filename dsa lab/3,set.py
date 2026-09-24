#set
subjects={"python","java","python","dbms","java"}
print("subjects:",subjects)
subjects.add("cloud computing")
print("after adding:",subjects)
subjects.remove("java")
print("after removing java:",subjects)
subjects2={"python","java","ai"}
print("union:",subjects|subjects2)
print("intersection:",subjects & subjects2)
