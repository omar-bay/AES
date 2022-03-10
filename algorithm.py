from operations import *
from copy import deepcopy

def encrypt(text, key):
    # get keys
    keys = all_10_keys(key)
    print("Keys:")
    for i in range(len(keys)):
        print(f"Key {i}: {keys[i]}")

    current_text = deepcopy(text)

    # add round key
    current_text = xor(current_text, keys[0])
    current_text = make_state(current_text)

    print("\n\nTexts:")
    for i in range(10):
        current_text = text_operation(current_text, keys, i)
        print(f"Round {i+1}: {current_text}")


def text_operation(text, keys, round):
    # state_text = make_state(text)
    state_text = deepcopy(text)

    # s-box
    new_state = substitute(state_text)

    # round
    new_state = [
        circular_byte_shift(new_state[0], 0),
        circular_byte_shift(new_state[1], 1),
        circular_byte_shift(new_state[2], 2),
        circular_byte_shift(new_state[3], 3),
    ]

    # mix
    if round != 9:
        new_state = mix(new_state, factor=mix_constant)

    # xor with round_key
    rot_key = make_state(keys[round+1])
    new_state = xor(new_state, rot_key)

    return new_state
