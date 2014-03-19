import json, sys, random, math

state = json.loads(sys.argv[1])
move = "88"

#debug
# f = open("moves.txt", "a")
# f.write("+")
# f.close()

def max_hits():
    pass

def check_around(hits, fired_list):
    to_fire = []
    pos = []
    if hits != []:
        for hit in hits:
            y = int(hit[0])
            x = int(hit[1])
            if (y+1) in range(0,8):
                pos.append(str(y+1)+str(x))
            if (y-1) in range(0,8):
                pos.append(str(y-1)+str(x))
            if (x+1) in range(0,8):
                pos.append(str(y)+str(x+1))
            if (x-1) in range(0,8):
                pos.append(str(y)+str(x-1))
            for p in pos:
                if p not in fired_list:
                    to_fire.append(p)
    return to_fire

def possible_ship(hits, to_fire, smallest_size, largest_size):
    to_fire_better = {k: [] for k in range(1, 5)}
    for pos in to_fire:
        y0 = int(pos[0])
        x0 = int(pos[1])
        for hit1 in hits:
            y1 = int(hit1[0])
            x1 = int(hit1[1])
            if (x1 == x0):
                for hit2 in [item for item in hits if item != hit1]:
                    y2 = int(hit2[0])
                    x2 = int(hit2[1])
                    if (x2 == x0):
                        if (smallest_size <= math.fabs(y1 - y2) + 2 <= largest_size):
                            to_fire_better[int(math.fabs(y1-y2))].append(str(y0)+str(x0))
            if (y1 == y0):
                for hit2 in [item for item in hits if item != hit1]:
                    y2 = int(hit2[0])
                    x2 = int(hit2[1])
                    if (y2 == y0):
                        if (smallest_size <= math.fabs(x1 - x2) + 2 <= largest_size):
                            to_fire_better[int(math.fabs(x1-x2))].append(str(y0)+str(x0))
    return to_fire_better

def get_args():
    res_json = sys.argv[1]
    res = json.loads(res_json)
    destroyed = res["destroyed"]
    ships = ["2", "3", "4", "5"]
    smallest_size = int(min(filter(lambda x: x not in destroyed, ships)))
    largest_size = int(max(filter(lambda x: x not in destroyed, ships)))
    return [res["moves"], res["hit"], res["missed"], smallest_size, largest_size]

def get_dist(yx, smallest_size, fired_list):
    if fired_list == []:
        return []
    x = int(yx[1])
    y = int(yx[0])
    for fired in fired_list:
        x0 = int(fired[1])
        y0 = int(fired[0])
        res_x = math.fabs(x-x0)
        res_y = math.fabs(y-y0)
    return [res_x, res_y]

if state["cmd"] == "init":
  
    print("{ \"2\" :{\"point\": \"00\",\"orientation\" : \"vertical\"},\"3\" :"
        +"{\"point\": \"22\",\"orientation\" : \"vertical\"},\"4\" :{\"point\": \"42\",\"orientation\" : \"vertical\"},"
        +"\"5\" :{\"point\": \"37\",\"orientation\" : \"horizontal\"}}")

else:

    moves, hits, missed, smallest_size, largest_size = get_args()

    fired_list = list(missed+hits)
    to_fire = check_around(hits, fired_list)
    to_fire_better = possible_ship(hits, to_fire, smallest_size, largest_size)

    if to_fire != []:
        ship_found = random.choice([True, True, True, True, True])
    else:
        ship_found = False
    


    if len(moves) in range(0,3): #change if the opponent plays multiple time
        while (1):
            x = random.randint(0,7)
            y = random.randint(0,7)
            move = str(y)+str(x)
            if move not in missed+hits:
                break

    # if there is no ship we are targeting
    elif not ship_found:
        coord = []
        for i in range(0,8):
            for j in range(0,8):
                coord.append(str(i)+str(j))
        should_continue = True

        while (should_continue):
            yx = random.choice(coord)
            coord.remove(yx)

            if yx in missed+hits:
                if coord == []:
                    ship_found = True
                    should_continue = False
                continue
            else:
                fired_list = list(missed+hits)
                res_x, res_y = get_dist(yx, smallest_size, fired_list)
                if res_x < smallest_size:
                    if res_y < smallest_size:
                        should_continue = True
                        continue
                    else:
                        should_continue = False
                        break
                else:
                    should_continue = False
                    continue

        move = yx

    # if we are targeting a ship
    if ship_found and to_fire != []:
        #@todo: check if there are blanks between two hits
            should_continue = True
            for i in range(1, largest_size-2):
                if to_fire_better[i] != []:
                    move = random.choice(to_fire_better[i])
                    should_continue = False
                    break

            if should_continue == True:
                move = random.choice(to_fire)

       

    else: #just a regular random
        coord = []
        for i in range(0,8):
            for j in range(0,8):
                coord.append(str(i)+str(j))
        should_continue = True

        while (should_continue):
            yx = random.choice(coord)
            coord.remove(yx)

            if yx in missed+hits:
                continue
            else:
                move = yx
                break

    if int(move[0]) not in range(0,8): #debug
        print move
        print to_fire
        print to_fire_better
        sys.exit()
    elif int(move[1]) not in range(0,8): #debug
        print move
        print to_fire
        print to_fire_better
        sys.exit()
    order = "{ \"move\" : \""+move+"\" }"
    print order