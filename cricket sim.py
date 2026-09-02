import os
import random
import json
from time import sleep
from prettytable import PrettyTable
from math import log
innings = 0
team1_total_runs = 0
team2_total_runs = 0
scores = []
teams = []
team1XI = []
team2XI = []

p_wicket = 0.017 #averages test cricket probabilites
p_1 = 0.2
p_2 = 0.05
p_3 = 0.005
p_4 = 0.04
p_6 = 0.001
p_wide = 0.001
p_n = 0.002
p_lb = 0.006
p_b = 0.0035

team_name1 = ""
team_name2 = ""

with open("the_players.json","r") as f:
    players = json.load(f)

#allows the user to select team 1 and 2 from the teams in the json
teams = list({player["country"] for player in players})
teams.sort()
while True:
    os.system("cls")
    print("Choose Team 1 by typing the name of a team below.")
    for team in teams:
        print(team)
    selection = input("").strip()
    if selection in teams:
        team_name1 = selection
        break
    else:
        print("Team is not in the dataset. Please select one of the teams listed above.")
        sleep(1)
teams.remove(team_name1)
while True:
    os.system("cls")
    print("Choose Team 2 by typing the name of a team below.")
    for team in teams:
        print(team)
    selection = input("").strip()
    if selection in teams:
        team_name2 = selection
        break
    else:
        print("Team is not in the dataset. Please select one of the teams listed above.")
        input("")
os.system("cls")

def wicket_prob(live_batter, players, live_bowler, player, p_wicket): #adjusts wicket probabilites
    for player in players:
        if player["name"] == live_batter:
            average_batter, strike_rate = adjusted_average(player)
        if player["name"] == live_bowler:
            bowler_strike_rate, bowler_econ = adjusted_bowling_average(player)
    p_wicket = (60 / ((average_batter * 100) / strike_rate)) * (60 / bowler_strike_rate) * 0.0165
    return p_wicket

def boundary_prob(live_batter, players, live_bowler, player, p_4, p_6): #adjust the probability of 4s and 6s based on the strike rate of the batter and the economy of the bowlers
    for player in players:
        if player["name"] == live_batter:
            average_batter, strike_rate = adjusted_average(player)
        if player["name"] == live_bowler:
            bowler_strike_rate, bowler_econ = adjusted_bowling_average(player)
    multiplier = (bowler_econ / 6) * (strike_rate / 100) * 4
    p_4 = 0.04 * (multiplier**1.2)
    p_6 = 0.001 * (multiplier**1.5)
    return p_4, p_6

def adjusted_average(player):
    innings = player.get("innings") or 0
    not_outs = player.get("not_outs") or 0 
    total_fc_dismissals = max(0, (player.get("fc_innings") or 0) - (player.get("fc_not_outs") or 0))
    total_fc_runs = player.get("fc_runs") or 0
    total_fc_balls = player.get("fc_balls") or 0
    if innings > 0:
        test_dismissals = max(1, innings - not_outs)
        test_runs = player.get("runs") or 0
        test_balls = max(1, player.get("balls") or 1)
        test_avg = test_runs / test_dismissals
        test_sr = (test_runs / test_balls) * 100
        non_test_dismissals = max(1, total_fc_dismissals - (innings - not_outs))
        non_test_runs = max(0, total_fc_runs - test_runs)
        non_test_balls = max(1, total_fc_balls - (player.get("balls") or 0))
    else:
        test_avg = 0.0
        test_sr = 0.0
        non_test_dismissals = max(1, total_fc_dismissals)
        non_test_runs = max(0, total_fc_runs)
        non_test_balls = max(1, total_fc_balls)
    fc_avg = (non_test_runs / non_test_dismissals) * 0.85
    fc_sr = ((non_test_runs / non_test_balls) * 100) * 0.92
    if innings >= 40:
        w = 1.0
    elif innings >= 10:
        w = log((innings / 2.5), 16)
    elif innings >= 1:
        w = innings / 20
    else:
        return fc_avg, fc_sr
    average_batter = (w * test_avg) + ((1.0 - w) * fc_avg)
    strike_rate = (w * test_sr) + ((1.0 - w) * fc_sr)
    return average_batter, strike_rate

def adjusted_bowling_average(player):
    wickets = player.get("wickets") or 0
    runs = player.get("bowler_runs") or 0
    balls = player.get("balls_bowled") or 0
    total_fc_wickets = player.get("fc_wickets") or 0
    total_fc_runs = player.get("fc_bowler_runs") or 0
    total_fc_balls = player.get("fc_balls_bowled") or 0
    fc_wickets = total_fc_wickets - wickets
    fc_runs = max(0, total_fc_runs - runs)
    fc_balls = max(1, total_fc_balls - balls)
    if fc_wickets > 0:
        fc_sr = (fc_balls / fc_wickets) * 1.12
    else:
        fc_sr = 200.0
    fc_eco = (fc_runs / (fc_balls / 6.0)) * 1.08
    if balls == 0:
        return fc_sr, fc_eco
    test_sr = (balls / wickets) if wickets > 0 else fc_sr
    test_eco = (runs / (balls / 6.0)) if balls > 0 else fc_eco
    if balls >= 3000:
        w = 1.0
    elif balls >= 750:
        w = log((balls / 187.5), 16)
    elif balls >= 1:
        w = balls / 1500
    else:
        return fc_sr, fc_eco
    bowler_strike_rate = (w * test_sr) + ((1.0 - w) * fc_sr)
    bowler_econ = (w * test_eco) + ((1.0 - w) * fc_eco)
    return bowler_strike_rate, bowler_econ

def ball_result(p_wicket,p_1,p_2,p_3,p_4,p_6,p_wide,p_n,p_lb,p_b): #defines the result of the ball with the given probabilities
        rng = random.random()
        if rng <= p_wicket:
            return "w"
        elif rng <= p_wicket + p_1:
            return "1"
        elif rng <= p_wicket + p_1 + p_2:
            return "2"
        elif rng <= p_wicket + p_1 + p_2 + p_3:
            return "3"
        elif rng <= p_wicket + p_1 + p_2 + p_3 + p_4:
            return "4"
        elif rng <= p_wicket + p_1 + p_2 + p_3 + p_4 + p_6:
            return "6"
        elif rng <= p_wicket + p_1 + p_2 + p_3 + p_4 + p_6 + p_wide:
            return "wide"
        elif rng <= p_wicket + p_1 + p_2 + p_3 + p_4 + p_6 + p_wide + p_n:
            return "n"
        elif rng <= p_wicket + p_1 + p_2 + p_3 + p_4 + p_6 + p_wide + p_n + p_lb:
            rng2 = random.random()
            if rng2 <= 0.8:
                return "lb1"
            elif rng2 <= 0.92:
                return "lb2"
            elif rng2 <= 0.93:
                return "lb3"
            else:
                return "lb4"
        elif rng <= p_wicket + p_1 + p_2 + p_3 + p_4 + p_6 + p_wide + p_n + p_lb + p_b:
                rng2 = random.random()
                if rng2 <= 0.8:
                    return "b1"
                elif rng2 <= 0.92:
                    return "b2"
                elif rng2 <= 0.93:
                    return "b3"
                else:
                    return "b4"
        else:
            return "0"

def change_batter(live_batter, batter1, batter2): #switches the live batter
    if live_batter == batter1:
        return(batter2)
    else:
        return(batter1)

#chooses the type of the wicket depending on the type of bowler.
def wicket_type(players, live_bowler, team1XI, team2XI, innings):
    for player in players:
        if player["name"] == live_bowler:
            bowling_type = player["bowling_type"]
    if innings == 0 or innings == 2:
        for player in team2XI:
            if player["role"] == "WICKET_KEEPER":
                wk = player.get("name")
    else:
        for player in team1XI:
            if player["role"] == "WICKET_KEEPER":
                wk = player.get("name")
    rng = random.random()
    if bowling_type == "PACE":
        if rng <= 0.31:
            catcher = wk
            return f"c {catcher}  b {live_bowler}"
        elif rng <= 0.62:
            if innings == 0 or innings == 2:
                while True:
                    catcher = team2XI[random.randint(0,10)]["name"]
                    if catcher != wk:
                        break
            else:
                while True:
                    catcher = team1XI[random.randint(0,10)]["name"]
                    if catcher != wk:
                        break
            return f"c {catcher}  b {live_bowler}"
        elif rng <= 0.8:
            return f"b {live_bowler}"
        elif rng <= 0.96:
            return f"lbw  b {live_bowler}"
        elif rng <= 0.98:
            return "run-out"
        else:
            return f"st {wk}  b {live_bowler}"
    elif bowling_type == "SPIN":
        if rng <= 0.2:
            catcher = wk
            return f"c {catcher}  b {live_bowler}"
        elif rng <= 0.5:
            if innings == 0 or innings == 2:
                while True:
                    catcher = team2XI[random.randint(0,10)]["name"]
                    if catcher != wk:
                        break
            else:
                while True:
                    catcher = team1XI[random.randint(0,10)]["name"]
                    if catcher != wk:
                        break
            return f"c {catcher}  b {live_bowler}"
        elif rng <= 0.71:
            return f"b {live_bowler}"
        elif rng <= 0.90:
            return f"lbw  b {live_bowler}"
        elif rng <= 0.95:
            return "run-out"
        else:
            return f"st {wk}  b {live_bowler}"

#loads in the teams from the players.json file
def load_teams(players, team_name1, team_name2):
    for player in players:
        if player["country"] == team_name1:
            team1_player_data.append(player)
        elif player["country"] == team_name2:
            team2_player_data.append(player)
    return team1_player_data, team2_player_data

#adds the rows for displaying a teams data. allows the user to make informed selection choices based on the data
def squad_add_row(squad, table, sort):
    if sort == "role":  
        squad = sorted(squad, key = lambda x: x.get("role"))
    if sort == "batting":
        def sort_key(player):
            average, strike_rate = adjusted_average(player)
            return -average
        squad = sorted(squad, key = sort_key)
    if sort == "bowling":
        def sort_key_bowling(player):
            bowling_strike_rate, economy = adjusted_bowling_average(player)
            if isinstance(bowling_strike_rate, (int, float)) and isinstance(economy, (int, float)) and bowling_strike_rate > 0 and economy > 0:
                bowling_average = bowling_strike_rate * economy / 6
                return (0, bowling_average)
            else:
                return (1, float("inf"))
        squad = sorted(squad, key = sort_key_bowling)
    for player in squad:
        id = player.get("id")
        name = player.get("name")
        role = player.get("role")
        bowling_type = player.get("bowling_type", "NONE")
        average, strike_rate = adjusted_average(player)
        bowling_strike_rate, economy = adjusted_bowling_average(player)
        if bowling_strike_rate > 0 and economy > 0:
            bowling_average = round((economy * bowling_strike_rate) / 6.0, 2)
            bowling_strike_rate = round(bowling_strike_rate, 2)
            economy = round(economy, 2)
        else:
            bowling_average = "None"
            bowling_strike_rate = "None"
            economy = "None"
        average = round(average, 2)
        strike_rate = round(strike_rate, 2)
        table.add_row([id, name, role, average, strike_rate, bowling_average, economy, bowling_strike_rate, bowling_type])
    return table


sort = "role"
while True:
    team1_player_data = []
    team2_player_data = []
    load_teams(players, team_name1, team_name2)
    i = 0
    #displays the team and allows the user to choose the starting 11
    while i < 11:
        os.system("cls")
        print(f"Choose the players from {team_name1}:")
        print(f'''The squad is currently sorted by {sort}. 
To change the sort to batting average, type "batting". 
To change the sort to bowling average, type "bowling".
To change the sort to player role, type "role".
''')
        table = PrettyTable()
        table.field_names = ["PLayer ID", "Name", "Role", "Batting Average", "Batting Strike Rate", "Bowling Average", "Economy", "Bowling Strike Rate", "Bowling Type"]
        squad = team1_player_data
        squad_add_row(squad, table, sort)
        print(table)
        while True:
            found = False
            digit = False
            player_id = input(f"Type the ID of the player you want to bat at #{i + 1}: ")
            if player_id.isdigit():
                player_id = int(player_id)
                digit = True
            for player in team1_player_data:
                if player_id == player.get("id"):
                    team1_player_data.remove(player)
                    player["batting_order"] = i + 1
                    team1XI.append(player)
                    found = True
                    print(f"{player.get('name')} is added to {team_name1}'s starting XI at #{i + 1}")
                    input("Press enter to continue.")
                    break
            if found:
                i += 1
                break
            if digit == False:
                if player_id.lower().strip() == "role":
                    sort = "role"
                    print("Squad will be sorted by role.")
                    break
                elif player_id.lower().strip() == "batting":
                    sort = "batting"
                    print("Squad will be sorted by batting average.")
                    break
                elif player_id.lower().strip() == "bowling":
                    sort = "bowling"
                    print("Squad will be sorted by bowling average.")
                    break
            print("ID not found. Please Check id and try again.")
    is_wk = False
    number_of_bowlers = 0
    #ensures the team features a wicket keeper and at least 2 bowlers
    for player in team1XI:
        if player.get("role") == "WICKET_KEEPER":
            is_wk = True
        if player.get("role") == "BOWLER" or player.get("role") == "ALL_ROUNDER":
            number_of_bowlers += 1
    if not is_wk:
        print("Please redo the starting 11 with a Wicket Keeper selected.")
        input("")
    elif number_of_bowlers < 2:
        print("Please redo the starting 11 with at least 2 bowlers selected.")
        input("")
    else:
        break

os.system("cls")
wicket_keepers = []
table = PrettyTable()
table.field_names = ["Player ID", "Name"]
for player in team1XI:
    if player.get("role") == "WICKET_KEEPER":
        id = player.get("id")
        name = player.get("name")
        table.add_row([id, name])
        wicket_keepers.append(player)
print(table)
while True:
    found = False
    player_id = input(f"Type the ID of the player you want to be the wicket keeper: ")
    if player_id.isdigit():
        player_id = int(player_id)
    for player in wicket_keepers:
        if player_id == player.get("id"):
            wk = player
            found = True
            print(f"{player.get('name')} is {team_name1}'s wicket keeper.")
            input("Press enter to continue.")
            break
    if found:
        for player in wicket_keepers:
            if player != wk:
                player["role"] = "BATTER"
        break
    else:
        print("ID not found. Please Check id and try again.")

sort = "role"
while True:
    team2_player_data = []
    load_teams(players, team_name1, team_name2)
    i = 0
    #displays the team and allows the user to choose the starting 11
    while i < 11:
        os.system("cls")
        print(f"Choose the players from {team_name2}:")
        print(f'''The squad is currently sorted by {sort}. 
To change the sort to batting average, type "batting". 
To change the sort to bowling average, type "bowling".
To change the sort to player role, type "role".
''')
        table = PrettyTable()
        table.field_names = ["PLayer ID", "Name", "Role", "Batting Average", "Batting Strike Rate", "Bowling Average", "Economy", "Bowling Strike Rate", "Bowling Type"]
        squad = team2_player_data
        squad_add_row(squad, table, sort)
        print(table)
        while True:
            found = False
            digit = False
            player_id = input(f"Type the ID of the player you want to bat at #{i + 1}: ")
            if player_id.isdigit():
                player_id = int(player_id)
                digit = True
            for player in team2_player_data:
                if player_id == player.get("id"):
                    team2_player_data.remove(player)
                    player["batting_order"] = i + 1
                    team2XI.append(player)
                    found = True
                    print(f"{player.get('name')} is added to {team_name2}'s starting XI at #{i + 1}")
                    input("Press enter to continue.")
                    break
            if found:
                i += 1
                break
            if digit == False:
                if player_id.lower().strip() == "role":
                    sort = "role"
                    print("Squad will be sorted by role.")
                    break
                elif player_id.lower().strip() == "batting":
                    sort = "batting"
                    print("Squad will be sorted by batting average.")
                    break
                elif player_id.lower().strip() == "bowling":
                    sort = "bowling"
                    print("Squad will be sorted by bowling average.")
                    break
            print("ID not found. Please Check id and try again.")
    is_wk = False
    number_of_bowlers = 0
    #ensures the team features a wicket keeper and at least 2 bowlers
    for player in team2XI:
        if player.get("role") == "WICKET_KEEPER":
            is_wk = True
        if player.get("role") == "BOWLER" or player.get("role") == "ALL_ROUNDER":
            number_of_bowlers += 1
    if not is_wk:
        print("Please redo the starting 11 with a Wicket Keeper selected.")
        input("")
    elif number_of_bowlers < 2:
        print("Please redo the starting 11 with at least 2 bowlers selected.")
        input("")
    else:
        break

os.system("cls")
wicket_keepers = []
table = PrettyTable()
table.field_names = ["Player ID", "Name"]
for player in team2XI:
    if player.get("role") == "WICKET_KEEPER":
        id = player.get("id")
        name = player.get("name")
        table.add_row([id, name])
        wicket_keepers.append(player)
print(table)
while True:
    found = False
    player_id = input(f"Type the ID of the player you want to be the wicket keeper: ")
    if player_id.isdigit():
        player_id = int(player_id)
    for player in wicket_keepers:
        if player_id == player.get("id"):
            wk = player
            found = True
            print(f"{player.get('name')} is {team_name2}'s wicket keeper.")
            input("Press enter to continue.")
            break
    if found:
        for player in wicket_keepers:
            if player != wk:
                player["role"] = "BATTER"
        break
    else:
        print("ID not found. Please Check id and try again.")

#defines the teams with just the names of each player
team1 = [player["name"] for player in team1XI]
team2 = [player["name"] for player in team2XI]

#displays the team sheets in their batting order
os.system("cls")
print(f"{team_name1}:")
for i in range(len(team1)):
    print(team1[i])
print(f'''
{team_name2}:''')
for i in range(len(team2)):
    print(team2[i])

#main innings loop. repeats every innings
while innings < 4:
    input("press enter to continue")
    runs = 0
    wickets = 0
    balls = 0
    extras = 0
    #sets up the batting order and the bowlers from the team sheets
    if innings == 0 or innings == 2:
        batting_order = team1
        batter_runs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        batter_balls = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #defines opening batters
        outs = ["not out"] * 11
        batter1 = batting_order[0]
        batter2 = batting_order[1]
        live_batter = batter1
        bowlers = []
        for player in team2XI:
            if player["role"] == "ALL_ROUNDER" or player["role"] == "BOWLER":
                bowlers.append(player["name"])
        bowler_wickets = [0] * len(bowlers)
        bowler_runs = [0] * len(bowlers)
        bowler_balls = [0] * len(bowlers)
        live_bowler = bowlers[random.randint(0,len(bowlers)-1)]
        prev_bowler = live_bowler
    else:
        batting_order = team2
        batter_runs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        batter_balls = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #defines opening batters
        outs = ["not out"] * 11
        batter1 = batting_order[0]
        batter2 = batting_order[1]
        live_batter = batter1
        bowlers = []
        for player in team1XI:
            if player["role"] == "ALL_ROUNDER" or player["role"] == "BOWLER":
                bowlers.append(player["name"])
        bowler_wickets = [0] * len(bowlers)
        bowler_runs = [0] * len(bowlers)
        bowler_balls = [0] * len(bowlers)
        live_bowler = bowlers[random.randint(0,len(bowlers)-1)]
        prev_bowler = live_bowler

    while wickets < 10:
        os.system("cls")
        if innings == 3:
            if scores[0] + scores[2] < scores[1] + runs:
                break
        p_wicket = wicket_prob(live_batter, players, live_bowler, player, p_wicket)
        p_4, p_6 = boundary_prob(live_batter, players, live_bowler, player, p_4, p_6)
        result = ball_result(p_wicket,p_1,p_2,p_3,p_4,p_6,p_wide,p_n,p_lb,p_b)
        try: #takes the result of the ball and adjust the scores accordingly
            runs += int(result)
            if int(result) == 1:
                print("1 run")
            else:
                print(f"{result[-1]} runs")
            balls += 1
            batter_runs[batting_order.index(live_batter)] += int(result)
            batter_balls[batting_order.index(live_batter)] += 1
            bowler_balls[bowlers.index(live_bowler)] += 1
            bowler_runs[bowlers.index(live_bowler)] += int(result)
            if int(result) % 2 == 1:
                live_batter = change_batter(live_batter, batter1, batter2)
        except:
            if result == "w":
                print("WICKET")
                wicket_result = wicket_type(players, live_bowler, team1XI, team2XI, innings)
                if wicket_result != "run-out":
                    bowler_wickets[bowlers.index(live_bowler)] += 1
                wickets += 1
                balls += 1
                batter_balls[batting_order.index(live_batter)] += 1
                bowler_balls[bowlers.index(live_bowler)] += 1
                outs[batting_order.index(live_batter)] = ""
                print(f"{live_batter} is out {batter_runs[batting_order.index(live_batter)]}({batter_balls[batting_order.index(live_batter)]}) {wicket_result}")
                if wickets != 10:
                    if live_batter == batter1:
                        batter1 = batting_order[wickets + 1]
                        live_batter = batter1
                    else:
                        batter2 = batting_order[wickets + 1]    
                        live_batter = batter2
            elif result == "n":
                print("No Ball")
                runs += 2
                extras += 2
                batter_balls[batting_order.index(live_batter)] += 1
            elif result == "wide":
                print("Wide Ball")
                runs += 1
                extras += 1
            elif result[:2] == "lb":
                if result[-1] == "1":
                    print("1 leg bye")
                else:
                    print(f"{result[-1]} leg byes")
                runs += int(result[-1])
                balls += 1
                extras += int(result[-1])
                batter_balls[batting_order.index(live_batter)] += 1
                bowler_balls[bowlers.index(live_bowler)] += 1
                bowler_runs[bowlers.index(live_bowler)] += int(result[-1])
                if int(result[-1]) % 2 == 1:
                    live_batter = change_batter(live_batter, batter1, batter2)
            elif result[:1] == "b":
                if result[-1] == "1":
                    print("1 bye")
                else:
                    print(f"{result[-1]} byes")
                runs += int(result[-1])
                balls += 1
                extras += int(result[-1])
                batter_balls[batting_order.index(live_batter)] += 1
                bowler_balls[bowlers.index(live_bowler)] += 1
                bowler_runs[bowlers.index(live_bowler)] += int(result[-1])
                if int(result[-1]) % 2 == 1:
                    live_batter = change_batter(live_batter, batter1, batter2)
        if balls % 6 == 0:
            live_batter = change_batter(live_batter, batter1, batter2) #changes batter at the end of the over
            while prev_bowler == live_bowler:
                live_bowler = bowlers[random.randint(0,len(bowlers)-1)]
            prev_bowler = live_bowler
        print(f"{runs}/{wickets}")
        print(f"{int((balls - (balls % 6)) / 6)}.{balls % 6}") #calculates overs and balls
        print(f"{batter1} {batter_runs[batting_order.index(batter1)]}({batter_balls[batting_order.index(batter1)]})")
        print(f"{batter2} {batter_runs[batting_order.index(batter2)]}({batter_balls[batting_order.index(batter2)]})")
        print(f"{live_bowler} {bowler_runs[bowlers.index(live_bowler)]}/{bowler_wickets[bowlers.index(live_bowler)]} {int((bowler_balls[bowlers.index(live_bowler)] - (bowler_balls[bowlers.index(live_bowler)] % 6)) / 6)}.{bowler_balls[bowlers.index(live_bowler)] % 6}")
        if result == "w":
            input("")

    os.system("cls")
    print(f"{runs}/{wickets}")
    print(f"{int((balls - (balls % 6)) / 6)}.{balls % 6}")
    print("")
    for i in range(len(batting_order)):
        if batter_balls[i] != 0:
            print(f"{batting_order[i]} {batter_runs[i]}({batter_balls[i]}) {outs[i]}")
    print(f"extras {extras}")
    print("")
    for i in range(len(bowlers)):
        if bowler_balls[i] != 0:
            print(f"{bowlers[i]} {bowler_runs[i]}/{bowler_wickets[i]} {int((bowler_balls[i] - (bowler_balls[i] % 6)) / 6)}.{bowler_balls[i] % 6} {round(bowler_runs[i] * 6 / bowler_balls[i], 2)}")
    print("")
    if innings == 0 or innings == 2:
        team1_total_runs += runs
    else:
        team2_total_runs += runs 
    scores.append(runs)
    if innings == 0:
        if team1_total_runs == 0:
            print("Scores Tied.")
        else:
            print(f"{team_name2} trails by {team1_total_runs}.")
    elif innings == 1:
        if team1_total_runs > team2_total_runs:
            print(f"{team_name1} leads by {team1_total_runs - team2_total_runs}.")
        elif team1_total_runs < team2_total_runs:
            print(f"{team_name1} trails by {team2_total_runs - team1_total_runs}.")
        else:
            print("Scores Tied.")
    elif innings == 2:
        if team1_total_runs > team2_total_runs:
            print(f"{team_name2} neads {team1_total_runs - team2_total_runs + 1} runs to win.")
        elif team1_total_runs < team2_total_runs:
            break
        else:
            print(f"{team_name2} neads 1 run to win.")        
    innings += 1
print("")
if team1_total_runs > team2_total_runs:
    print(f"{team_name1} win by {team1_total_runs - team2_total_runs} runs.")
elif team1_total_runs < team2_total_runs and innings == 4:
    print(f"{team_name2} win by {10 - wickets} wickets.")
elif team1_total_runs < team2_total_runs:
    print(f"{team_name2} win by an innings and {team2_total_runs - team1_total_runs} runs.")
else:
    print("Match Tied.")
