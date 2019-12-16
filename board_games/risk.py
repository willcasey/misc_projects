import random
import csv

a_dice_roll = []
d_dice_roll = []
dice_roll_array = []
defender_casualties = []
attacker_casualties = []
attacker_army_count_list = []
defender_army_count_list = []
iterations_count_list = [0]
attacker_wins_list = []
defender_wins_list = []
defender_casualties_list = []
attacker_casualties_list = []
count_rolls_list = []
master_list = []


count_rolls = 0
max_attacker_dice = 0
max_defender_dice = 0
defender_wins = 0
attacker_wins = 0

simulation_count = 100000
print("This will simulate " + str(simulation_count) +  "times.")


def dice_rolls(attacker_army_count, defender_army_count):
    a_dice_roll = []
    d_dice_roll = []
    if attacker_army_count > 3:
        max_attacker_dice = 3
    elif attacker_army_count == 3:
        max_attacker_dice = 2
    elif attacker_army_count == 2:
        max_attacker_dice = 1

    if defender_army_count >= 2:
        max_defender_dice = 2
    elif defender_army_count == 1:
        max_defender_dice = 1

        
    for i in range(0,max(max_attacker_dice, max_defender_dice)):
        if i < max_attacker_dice:
            a_dice_roll.append(random.randint(1,6))
        if i < max_defender_dice:
            d_dice_roll.append(random.randint(1,6))
    
    
    a_dice_roll = sorted(a_dice_roll, reverse =True)
    d_dice_roll = sorted(d_dice_roll, reverse =True)
    return a_dice_roll, d_dice_roll, min(max_attacker_dice, max_defender_dice) 




def compare_rolls(a, d, a_count, d_count, min_dice_count):
    defender_army_count = d_count
    attacker_army_count = a_count
    for i in range(0, min_dice_count):
        if a[i] > d[i]:
            defender_army_count = defender_army_count - 1
        else:
            attacker_army_count = attacker_army_count - 1
                  
        
    return attacker_army_count, defender_army_count




for j in range(2, 31): #attacker loop
    for k in range(1, 31): #defender loop
        attacker_army_count = j
        defender_army_count = k
        starting_attacker_army_count = attacker_army_count
        starting_defender_army_count = defender_army_count
        attacker_army_count_list.append(j)
        defender_army_count_list.append(k)
        iterations_count_list.append(max(iterations_count_list)+1)
        for i in range(1, simulation_count + 1):
            #print "i, j, k: ", i, j, k
            attacker_army_count = starting_attacker_army_count
            defender_army_count = starting_defender_army_count
            while attacker_army_count > 1 and defender_army_count >0:
                dice_roll_array = dice_rolls(attacker_army_count, defender_army_count) #setting the result of the dice_rolls function to equal a list
                resulting_army_counts = compare_rolls(dice_roll_array[0], dice_roll_array[1],attacker_army_count, defender_army_count, dice_roll_array[2]);
                #print "Armies Left: ", resulting_army_counts    
                attacker_army_count = resulting_army_counts[0]
                defender_army_count = resulting_army_counts[1]
                count_rolls = count_rolls  +1
            
                if attacker_army_count == 1:
                    defender_wins = defender_wins + 1
                    defender_casualties.append(starting_defender_army_count - defender_army_count)
                elif defender_army_count == 0:
                    attacker_wins = attacker_wins + 1
                    attacker_casualties.append(starting_attacker_army_count - attacker_army_count)
        attacker_wins_list.append(attacker_wins)
        defender_wins_list.append(defender_wins)
        defender_casualties_list.append(sum(defender_casualties)) 
        attacker_casualties_list.append(sum(attacker_casualties)) 
        count_rolls_list.append(count_rolls)
        count_rolls = 0 
        defender_wins = 0
        attacker_wins = 0
        defender_casualties = []
        attacker_casualties = []


iterations_count_list.remove(iterations_count_list[0]) 
master_list = [iterations_count_list, attacker_army_count_list, defender_army_count_list, attacker_wins_list, defender_wins_list, attacker_casualties_list, defender_casualties_list, count_rolls_list]      



out = open('Risk simulation results.csv', 'w')
for row in master_list:
    for column in row:
        out.write('%d;' % column)
    out.write('\n')
out.close()

print("Done")



