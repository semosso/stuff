# virtual good vibes jar
import random
import datetime

log = "../../Google Drive/virtualjar2019.txt"
today_date = datetime.date.today().strftime(f"%B %d, %Y")

print("You should be grateful for / mindful of all the good things happening around you that you might miss or forget. So what happened today?")
memory = input("> ")

# lns 12, 14 and 17 seem so ugly as they are right now, but I tried to change and couldn't get it to work... so it is what it is for now
with open(log, "a+") as f:
    f.write(f"{today_date}: {memory}\n")
with open(log, "r") as f:
    lines = f.readlines()
random.shuffle(lines)
with open(log, "w") as f:
        f.writelines(lines)

print("Do you need a good memento?")
answer = input("> ")

if answer == "y":
    whatevs = open(log).readline()
    print(whatevs)
else: exit(0)