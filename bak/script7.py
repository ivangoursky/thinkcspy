def collatz(n):
	""" Print Collatz sequence starting from n """
	while n!=1:
		print(n,end=", ")
		if n%2==0:
			n=n//2
		else:
			n=n*3+1
	
	print(n,end=".\n")
	
n=int(input("Please, enter integer n: "))
collatz(n)
