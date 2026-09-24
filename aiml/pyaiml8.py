c = float(input("Enter temperature in Celsius: "))
f = (c * 9 / 5) + 32

print("Temperature in Fahrenheit:", f)
p = float(input("Enter Principal: "))
r = float(input("Enter Rate: "))
t = float(input("Enter Time: "))

si = (p * r * t) / 100
amount = p + si

print("Simple Interest:", si)
print("Total Amount:", amount)
