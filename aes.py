from copy import copy, deepcopy

""" function desc is input format and expected output format """
""" [["07", "00", "A3", "C3"], ["C9", "90", "87", "D6"],["9E", "13", "22", "83"],["43", "CD", "78", "C0"]] """
""" [["07", "00", "A3", "C3"], ["C9", "90", "87", "D6"],["9E", "13", "22", "83"],["43", "CD", "78", "C0"]] """

s_box = [
    ["63","7C","77","7B","F2","6B","6F","C5","30","01","67","2B","FE","D7","AB","76"],
    ["CA","82","C9","7D","FA","59","47","F0","AD","D4","A2","AF","9C","A4","72","C0"],
    ["B7","FD","93","26","36","3F","F7","CC","34","A5","E5","F1","71","D8","31","15"],
    ["04","C7","23","C3","18","96","05","9A","07","12","80","E2","EB","27","B2","75"],
    ["09","83","2C","1A","1B","6E","5A","A0","52","3B","D6","B3","29","E3","2F","84"],
    ["53","D1","00","ED","20","FC","B1","5B","6A","CB","BE","39","4A","4C","58","CF"],
    ["D0","EF","AA","FB","43","4D","33","85","45","F9","02","7F","50","3C","9F","A8"],
    ["51","A3","40","8F","92","9D","38","F5","BC","B6","DA","21","10","FF","F3","D2"],
    ["CD","0C","13","EC","5F","97","44","17","C4","A7","7E","3D","64","5D","19","73"],
    ["60","81","4F","DC","22","2A","90","88","46","EE","B8","14","DE","5E","0B","DB"],
    ["E0","32","3A","0A","49","06","24","5C","C2","D3","AC","62","91","95","E4","79"],
    ["E7","CB","37","6D","8D","D5","4E","A9","6C","56","F4","EA","65","7A","AE","08"],
    ["BA","78","25","2E","1C","A6","B4","C6","E8","DD","74","1F","4B","BD","8B","8A"],
    ["70","3E","B5","66","48","03","F6","0E","61","35","57","B9","86","C1","1D","9E"],
    ["E1","F8","98","11","69","D9","8E","94","9B","1E","87","E9","CE","55","28","DF"],
    ["8C","A1","89","0D","BF","E6","42","68","41","99","2D","0F","B0","54","BB","16"]
]

round_constant = [
    ["01","00","00","00"],
    ["02","00","00","00"],
    ["04","00","00","00"],
    ["08","00","00","00"],
    ["10","00","00","00"],
    ["20","00","00","00"],
    ["40","00","00","00"],
    ["80","00","00","00"],
    ["1B","00","00","00"],
    ["36","00","00","00"]
]

mix_constant = [
    ["02","03","01","01"],
    ["01","02","03","01"],
    ["01","01","02","03"],
    ["03","01","01","02"]
]


def encrypt(text, key):
    # get keys
    keys = all_10_keys(key)

    current_text = deepcopy(text)
    for i in range(10):
        current_text = text_operation(current_text, keys[i], i)
        print(current_text)


def text_operation(text, key, round):
    state_text = make_state(text)
    state_key = make_state(key)

    keys = all_10_keys(key)
    
    # xor together
    new_state = xor(state_text, state_key)

    # s-box
    new_state = substitute(new_state)

    # round
    new_state = [
        circular_byte_shift(new_state[0], 0),
        circular_byte_shift(new_state[1], 1),
        circular_byte_shift(new_state[2], 2),
        circular_byte_shift(new_state[3], 3),
    ]

    # mix
    new_state = mix(new_state, factor=mix_constant)

    # xor with round_key
    rot_key = make_state(keys[1])
    new_state = xor(new_state, rot_key)

    return new_state


def all_10_keys(key):
    """ [["07", "00", "A3", "C3"],["C9", "90", "87", "D6"],["9E", "13", "22", "83"],["43", "CD", "78", "C0"]] """
    keys = []
    current_key = deepcopy(key)
    keys.append(current_key)
    # print(f"Key 0: {current_key}")
    for k in range(10):
        current_key = next_key(current_key, k)
        keys.append(current_key)
        # print(f"Key {k+1}: {current_key}")

    return keys


def next_key(key, round_no):
    """ [["07", "00", "A3", "C3"],["C9", "90", "87", "D6"],["9E", "13", "22", "83"],["43", "CD", "78", "C0"]] """
    new_key = deepcopy(key)

    # w0
    new_key[0] = key_edge(key, round_no)
    # w1
    new_key[1] = xor([ new_key[0] ], [ key[1] ])[0]
    # w2
    new_key[2] = xor([ new_key[1] ], [ key[2] ])[0]
    # w3
    new_key[3] = xor([ new_key[2] ], [ key[3] ])[0]

    return new_key


def key_edge(key, round_no):
    """ returns w4 w1 w2 w3 """
    """ [["07", "00", "A3", "C3"],["C9", "90", "87", "D6"],["9E", "13", "22", "83"],["43", "CD", "78", "C0"]] """
    """ returns ["07", "00", "A3", "C3"] """
    w_last = key[-1]

    # circular byte left shift of w[last]
    w_last = circular_byte_shift(w_last, 1)

    # byte substitution on w[last]
    w_last = substitute([w_last])[0]

    # adding round constant on w[last]
    w_last = add_round_constant(w_last, round_no)

    # upper xor operation
    w_start = xor([ w_last ], [ key[0] ])[0]

    return w_start


def make_state(one):
    """ [["07", "00", "A3", "C3"],["C9", "90", "87", "D6"],["9E", "13", "22", "83"],["43", "CD", "78", "C0"]] """
    state = deepcopy(one)
    for i in range(len(one)):
        for j in range(len(one[0])):
            state[i][j] = one[j][i]

    return state


def mix(one, factor):
    """ [["07","00","A3","C3"],["C9","90","87","D6"],["9E","13","22","83"],["43","CD","78","C0"]] """
    """ [["01","02","03","02"],["01","02","02","02"],["01","01","02","02"],["01","03","02","01"]] """
    solution = [["00","00","00","00"],["00","00","00","00"],["00","00","00","00"],["00","00","00","00"]]

    # rotate one to row-the-col
    state = make_state(one)

    # word by word
    for i in range(len(state)):
        for j in range(len(state[0])):
            solution[i][j] = word_multiply(state[j], factor=factor[i])

    return solution


def word_multiply(one, factor):
    """ ['B7','5A','9D','85'] """
    """ ["02","03","01","01"] """
    """ returns "00" """
    sol = "00"

    for i in range(len(one)):
        temp = mix_multiply(one[i], factor=factor[i])
        sol = xor([[ sol ]], [[ temp ]])[0][0]

    return sol


def mix_multiply(one, factor):
    """ "A1", "02" """
    # hex to binary
    bin_one = str("{0:08b}".format(int(one, 16)))
    if(factor == "01"):
        return one

    elif(factor == "02"):
        drop = bin_one[0]
        solution = f"{bin_one[1:len(bin_one)]}0"
        if(drop == "1"):
            # xor 1B
            solution = binary_xor(solution, "00011011")

        return str("{0:02x}".format(int(solution, 2)))

    elif(factor == "03"):
        # x02
        drop = bin_one[0]
        solution = f"{bin_one[1:len(bin_one)]}0"
        if(drop == "1"):
            # xor 1B
            solution = binary_xor(solution, "00011011")
        # +bin_one
        solution = binary_xor(bin_one, solution)
        return str("{0:02x}".format(int(solution, 2)))
    
    else:
        return ""


def binary_xor(one, two):
    """ 00000000 """
    solution = ""
    for i in range(len(one)):
        if one[i] == two[i]:
            solution+= "0"
        else:
            solution+= "1"

    return solution


def add_round_constant(word, round_no):
    """ ['B7', '5A', '9D', '85'] """
    return xor([round_constant[round_no]], [word])[0]


def circular_byte_shift(word, rounds):
    """ ['B7', '5A', '9D', '85'] """
    solution = word.copy()
    for r in range(rounds):
        pin = 0
        temp = solution[pin]
        while(pin<len(solution)-1):
            solution[pin] = solution[pin+1]
            pin+= 1
        solution[pin] = temp
    
    return solution


def substitute(state):
    """ [['B7', '5A', '9D', '85']] """
    solution = deepcopy(state)
    for i in range(len(state)):
        for j in range(len(state[0])):
            d1 = state[i][j][0]
            d2 = state[i][j][1]
            row = int(d1, 16)
            col = int(d2, 16)
            solution[i][j] = s_box[row][col]

    return solution


def xor(one, two):
    """ [['B7', '5A', '9D', '85']] """
    solution = deepcopy(one)
    for i in range(len(one)):
        for j in range(len(one[0])):
            # binary strings
            d1 = one[i][j]
            d2 = two[i][j]
            bin_one = str("{0:08b}".format(int(d1, 16)))
            bin_two = str("{0:08b}".format(int(d2, 16)))

            # get xor binary
            bin_sol = binary_xor(bin_one, bin_two)

            # convert sol bin>hex
            hex_sol = str("{0:02x}".format(int(bin_sol, 2)))

            solution[i][j] = hex_sol

    return solution



# key = [
#     ["2B","7E","15","16"],
#     ["28","AE","D2","A6"],
#     ["AB","F7","15","88"],
#     ["09","CF","4F","3C"],
# ]
# all_10_keys(key)

# one = [["63","EB","9F","A0"],["2F","93","92","C0"],["AF","C7","AB","30"],["A2","20","CB","2B"]]
# two = [["02","03","01","01"],["01","02","03","01"],["01","01","02","03"],["03","01","01","02"]]
# print(mix(one, factor=two))


key = [["54","68","61","74"],["73","20","6D","79"],["20","4B","75","6E"],["67","20","46","75"]]
text = [["54","77","6F","20"],["4F","6E","65","20"],["4E","69","6E","65"],["20","54","77","6F"]]

print(text_operation(text, key))