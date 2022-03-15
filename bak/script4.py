total_secs=int(input("How many seconds? "))
hours=total_secs//3600
secs_remaining=total_secs%3600
minutes=secs_remaining//60
seconds=secs_remaining%60
print("Hours=",hours,", minutes=",minutes,", seconds=",seconds)
