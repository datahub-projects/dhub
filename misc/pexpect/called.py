import random
n=random.randint(0,7)
print ("what is %s * 2? " % n, end='')
x=input("type answer:\n")
if int(x)==n*2:
    print ("Correct")
else:
    print ("Soory -- you have been voted off the island")
