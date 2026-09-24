purchase = float(input("Enter purchase amount: "))
premium = input("Are you a premium member? (True/False): ")
premium = premium == "True"  # Convert string to boolean

result = purchase >= 1000 or premium
print("Eligible (Purchase >= 1000 OR Premium Member):", result)
