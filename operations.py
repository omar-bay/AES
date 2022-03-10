from copy import copy, deepcopy
from constants import *

""" function desc is input format and expected output format """


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

