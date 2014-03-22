import json, sys, random, math

def print_map(map):
    print "---"
    for line in map:
        print line
    print "---"

# to get the args
def get_args():
    res_json = sys.argv[1]
    res = json.loads(res_json)
    ships = ["2", "3", "4", "5"]
    destroyed = res["destroyed"]
    smallest_size = int(min(filter(lambda x: x not in destroyed, ships)))
    largest_size = int(max(filter(lambda x: x not in destroyed, ships)))
    return [res["moves"], res["hit"], res["missed"], destroyed, smallest_size, largest_size]

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
def check_next(map, hit, len, align):
    y = int(hit[0])
    x = int(hit[1])
    if map[x][y] == "hit":
        len += 1
        if align == "h" and y < 7:
            y+=1
        elif align == "v" and x < 7:
            x+=1
        else:
            return len
        hit = str(y)+str(x)
        len = check_next(map,hit, len, align)
    return len

# to get the consecutive hits
def get_parts(map, hits):
    h_ships_parts = {k: [] for k in range(1,9)}
    elem = ["blank" for i in range(0,8)]
    for x in range(0,8):
        y=0
        while y in range(0,7):
            if map[x][y] == "hit":
                status = map[x][y]
                hit = str(y)+str(x)
                len = check_next(map,hit,0,"h")
                h_ships_parts[len].append(hit)
                y += len
            else:
                y += 1

    v_ships_parts = {k: [] for k in range(1,9)}
    for y in range(0,8):
        x=0
        while x in range(0,7):
            if map[x][y] == "hit":
                status = map[x][y]
                hit = str(y)+str(x)
                len = check_next(map,hit,0,"v")
                v_ships_parts[len].append(hit)
                x += len
            else:
                x += 1

    return [h_ships_parts, v_ships_parts]

def get_parts2(parts):
    parts2 = [{k:[] for k in range(1,9)},{k: [] for k in range(1,9)}]
    for key in parts[0].keys():
        while parts[0][key] != []:
            pos = parts[0][key].pop()
            pos_list = [pos]
            for i in range(1,key):
                x = int(pos[1])
                y = int(pos[0])
                pos_list.append(str(y+i)+str(x))
            parts2[0][key].append(pos_list)
    for key in parts[1].keys():
        while parts[1][key] != []:
            pos = parts[1][key].pop()
            pos_list = [pos]
            for i in range(1,key):
                x = int(pos[1])
                y = int(pos[0])
                pos_list.append(str(y)+str(x+i))
            parts2[1][key].append(pos_list)
    return parts2
# to check the positions of the sunk ships
def check_sunk(map, parts, destroyed):
    sunk_ships = []
    for i in range(2,6):
        if i in destroyed:
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


# hits = [ "10", "30", "40", "50", "31","41","51","61","71"]
# missed = []
# destroyed = [5]
# largest_size = 4
# map, pos = get_map(missed, hits)
# parts = get_parts(map, hits)
# map, sunk_ships = check_sunk(map, parts, destroyed)
# print_map(map)
# print sunk_ships
# fired_list = missed+hits+sunk_ships

def init():
    print("{ \"2\" :{\"point\": \"00\",\"orientation\" : \"vertical\"},\"3\" :"
        +"{\"point\": \"22\",\"orientation\" : \"vertical\"},\"4\" :{\"point\": \"42\",\"orientation\" : \"vertical\"},"
        +"\"5\" :{\"point\": \"37\",\"orientation\" : \"horizontal\"}}")

def classic_search():
    pass

def check_fit(map, pos, ship_size, align):
    x0, y0 = pos
    if align == "vertical":
        for x in range(x0, x0+ship_size):
            if x > 7:
                return False
            if (map[x][y0] in ["sunk", "hit"]):
                return False
    elif align == "horizontal":
        for y in range(y0, y0+ship_size):
            if y > 7:
                return False
            if (map[x0][y] in ["sunk", "hit"]):
                return False
    else:
        raise AlignError
    return True

def make_pmap(map, remaining_ships, parts, parts2, largest_size, fired_list):
    x = [0 for i in range(0,8)]
    pmap = [list(x) for i in range(0,8)]
    for i in range(0,8):
        for j in range(0,8):
            for ship_size in remaining_ships:
                if check_fit(map, [i,j], ship_size, "vertical"):
                    for x in range(i, i+ship_size):
                        pmap[x][j] += 1
                if check_fit(map, [i,j], ship_size, "horizontal"):
                    for y in range(j, j+ship_size):
                        pmap[i][y] += 1

    around_hits1 = check_hits(parts[0][1], fired_list)
    around_hits1.append(check_hits(parts[1][1], fired_list))

    around_hits2_v = check_hits(parts[0][2], fired_list)
    around_hits2_h = check_hits(parts[1][2], fired_list)

    if around_hits1 != [[]]:
        for pos in around_hits1:
            x1 = int(pos[1])
            y1 = int(pos[0])
            pmap[x1][y1] += 50

    for key in parts2[0].keys():
        if key < largest_size:
            #horizontal
            for pos_list in parts2[0][key]:
                around_hits3 = check_hits(pos_list, fired_list)
                for pos in around_hits3:
                    x3 = int(pos[0])
                    y3 = int(pos[1])
                    pmap[x3][y3] += 50
            # vertical
            for pos_list in parts2[1][key]:
                around_hits3 = check_hits(pos_list, fired_list)
                for pos in around_hits3:
                    x3 = int(pos[0])
                    y3 = int(pos[1])
                    pmap[x3][y3] += 50

    return pmap

def chose_move(pmap):
    max = 0
    x0 = 0
    y0 = 0
    for x in range(0,8):
        for y in range(0,8):
            if pmap[x][y] > max:
                max = pmap[x][y]
                x0 = x
                y0 = y
    return str(y0)+str(x0)

# ships = range(2,6)
# print ships
# remaining_ships = filter(lambda x: x not in destroyed, ships)
# hits = filter(lambda x: x not in sunk_ships, hits)
# print hits
# print remaining_ships

#print_map(pmap)
#print parts
# parts2 = get_parts2(parts)
# pmap = make_pmap(map, remaining_ships, parts, parts2, largest_size, fired_list)
# print parts2[0]
# print parts2[1]
# print_map(pmap)

def search():
    pass
def destroy():
    pass

def run():
    state = json.loads(sys.argv[1])
    
    if state["cmd"] == "init":
        init()
    else:
        moves, hits, missed, destroyed, smallest_size, largest_size = get_args()
        map, pos = get_map(missed, hits)
        parts = get_parts(map, hits)
        parts2 = get_parts2(parts)
        map, sunk_ships = check_sunk(map, parts, destroyed)
        fired_list = list(missed+hits)
        hits = filter(lambda x: x not in sunk_ships, hits)
        ships = range(2,6)
        remaining_ships = filter(lambda x: x not in destroyed, ships)
        pmap = make_pmap(map, remaining_ships, parts, parts2, largest_size, fired_list)
        move = chose_move(pmap)
        print "{ \"move\" : \""+move+"\" }"

run()