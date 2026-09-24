price1 = float(input("Enter price of product 1: "))
qty1 = int(input("Enter quantity of product 1: "))

price2 = float(input("Enter price of product 2: "))
qty2 = int(input("Enter quantity of product 2: "))

price3 = float(input("Enter price of product 3: "))
qty3 = int(input("Enter quantity of product 3: "))

total1 = price1 * qty1
total2 = price2 * qty2
total3 = price3 * qty3

grand_total = total1 + total2 + total3

print("\nProduct 1 Total:", total1)
print("Product 2 Total:", total2)
print("Product 3 Total:", total3)
print("Grand Total:", grand_total)
