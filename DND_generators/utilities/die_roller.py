import random

def roll_die(die, _max=False):

    quantity, requested_die = die.split('d')

    roll = 0

    if quantity == "":
        quantity = 1
    else:
        quantity = int(quantity)

    requested_die = int(requested_die)

    for _ in range(quantity):
        if not _max:
            roll += random.randint(a=1, b=requested_die)
        else:
            roll += requested_die

    return roll
