import math

import mytest


def eratosphen_primes(maxn):
    """ Find primes up to maxn using Eratosphenes sieve"""
    isprime=[True]*(maxn+1)
    isprime[0]=False
    isprime[1]=False

    for i in range(int(math.sqrt(maxn))+1):
        if isprime[i]:
            j=i*2
            while j<=maxn:
                isprime[j]=False
                j+=i

    res=[]
    for (i,t) in enumerate(isprime):
        if t:
            res.append(i)

    return res

def isprime(n):
    """ Test if n is prime by trying possible dividers up to sqrt(n) """
    if n<2:
        return False

    maxdiv=int(math.sqrt(n))
    i=2
    while i<=maxdiv:
        if n%i==0:
            return False
        i+=1

    return True

def straightforward_primes(maxn):
    """ Find primes up to maxn using straightforward approach """
    res=[]
    for i in range(maxn+1):
        if isprime(i):
            res.append(i)

    return res


mytest.test(eratosphen_primes(10)==straightforward_primes(10))
mytest.test(eratosphen_primes(1000)==straightforward_primes(1000))
mytest.test(eratosphen_primes(100000)==straightforward_primes(100000))

maxn=int(input("Please, enter maximal N to search for prime numbers: "))
print("Calculating using Eratosphen method...")
print(eratosphen_primes(maxn))

#print("Calculating using straightforward method...")
#print(straightforward_primes(maxn))