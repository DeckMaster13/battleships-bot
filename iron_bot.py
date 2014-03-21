import json, sys, random, math

state = json.loads(sys.argv[1])

# to get the args
def get_args():
    res_json = sys.argv[1]
    res = json.loads(res_json)
    ships = ["2", "3", "4", "5"]
    smallest_size = int(min(filter(lambda x: x not in destroyed, ships)))
    largest_size = int(max(filter(lambda x: x not in destroyed, ships)))
    return [res["moves"], res["hit"], res["missed"], res["destroyed"], smallest_size, largest_size]

# to get a map (double entry array)
def get_map(missed, hits):
    x = ["blank" for i in range(0,8)]
    map = [list(x) for i in range(0,8)]
    for yx in missed:
        y0 = int(yx[0])
        x0 = int(yx[1])
        map[x0][y0] = "missed"
    for yx in hits:
        y0 = int(yx[0])
        x0 = int(yx[1])
        map[x0][y0] = "hit"
    
    pos = []
    for x in range(0,8):
        for y in range(0,8):
            pos.append(str(y)+str(x))
    return [map,pos]

# to return the positions around a hit (no filter)
def check_around(hit):
    pos = []
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
    return pos

# to return the good place to fire around the hits where we have not already fired
def check_hits(hits, fired_list):
    to_fire = []
    pos = []
    if hits != []:
        for hit in hits:
            pos = check_around(hit)
            for p in pos:
                if p not in fired_list:
                    to_fire.append(p)
    return to_fire

# to return the best places to fire around the hits
def checkfocus_ships(hits, to_fire, smallest_size, largest_size):
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
                        if (math.fabs(y1 - y2) + 2 <= largest_size):
                            to_fire_better[int(math.fabs(y1-y2))].append(str(y0)+str(x0))
            if (y1 == y0):
                for hit2 in [item for item in hits if item != hit1]:
                    y2 = int(hit2[0])
                    x2 = int(hit2[1])
                    if (y2 == y0):
                        if (math.fabs(x1 - x2) + 2 <= largest_size):
                            to_fire_better[int(math.fabs(x1-x2))].append(str(y0)+str(x0))
    return to_fire_better

# to check for a hit, the neighbors recursively and build get_parts() below
def check_next(hit, len, align):
    y = int(hit[0])
    x = int(hit[1])
    if map[x][y] == "hit":
        print hit
        len += 1
        if align == "h" and y < 7:
            y+=1
        elif align == "v" and x < 7:
            x+=1
        else:
            return len
        hit = str(y)+str(x)
        len = check_next(hit, len, align)
    return len

# to get the consecutive hits
def get_parts(map, hits):
    h_ships_parts = {k: [] for k in range(1,9)}
    elem = ["blank" for i in range(0,8)]
    for x in range(0,8):
        y=0
        while y in range(0,7):
            print map[x][y]
            if map[x][y] == "hit":
                status = map[x][y]
                hit = str(y)+str(x)
                print "---"
                len = check_next(hit,0,"h")
                print "---"
                h_ships_parts[len].append(hit)
                y += len
            else:
                y += 1

    v_ships_parts = {k: [] for k in range(1,9)}
    for y in range(0,8):
        x=0
        while x in range(0,7):
            print map[x][y]
            if map[x][y] == "hit":
                status = map[x][y]
                hit = str(y)+str(x)
                print "---"
                len = check_next(hit,0,"v")
                print "---"
                v_ships_parts[len].append(hit)
                x += len
            else:
                x += 1

    return [h_ships_parts, v_ships_parts]

# to check the positions of the sunk ships
def check_sunk(map, parts, destroyed):
    sunk_ships = []
    for i in range(2,6):
        print i
        if i in destroyed:
            print "tut"
            if len(parts[0][i]+parts[1][i]) == 1:
                if len(parts[0][i]) == 1:
                    start_pos = parts[0][i][0]
                    align = "h"
                elif len(parts[1][i]) == 1:
                    start_pos = parts[1][i][0]
                    align = "v"
                else:
                    raise SunkShipError
                x = int(start_pos[1])
                y = int(start_pos[0])
                
                for j in range(0,i):
                    if align == "h":
                        map[x][y+j] = "sunk"
                        sunk_ships.append(str(y+j)+str(x))
                    elif align =="v":
                        map[x+j][y] = "sunk"
                        sunk_ships.append(str(y)+str(x+j))
                    else:
                        raise SunkShipError
    return map, sunk_ships


hits = [ "10", "30", "40", "50", "31","41","51","61","71"]
missed = []
destroyed = [5]
map, pos = get_map(missed, hits)
parts = get_parts(map, hits)
map, sunk_ships = check_sunk(map, parts, destroyed)
print map
print sunk_ships

def init():
    print("{ \"2\" :{\"point\": \"00\",\"orientation\" : \"vertical\"},\"3\" :"
        +"{\"point\": \"22\",\"orientation\" : \"vertical\"},\"4\" :{\"point\": \"42\",\"orientation\" : \"vertical\"},"
        +"\"5\" :{\"point\": \"37\",\"orientation\" : \"horizontal\"}}")

def classic_search():
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

def search():
    pass
def destroy():
    pass

if state["cmd"] == "init":
    init()
else:
    moves, hits, missed, destroyed, smallest_size, largest_size = get_args()
    map, pos = get_map(missed, hits)
    parts = get_parts(map, hits)
    map, sunk_ships = check_sunk(map, parts, destroyed)
    fired_list = list(missed+hits+sunk_ships)
    to_fire_at = check_ships()