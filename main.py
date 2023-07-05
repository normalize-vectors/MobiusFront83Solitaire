import pyautogui
import time
import winsound
import random
import pyscreeze
import multiprocessing as mp

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

COL_1_LEFT = 1080
COL_1_RIGHT = 1180
COL_2_LEFT = 1440
COL_2_RIGHT = 1550
COL_3_LEFT = 1800
COL_3_RIGHT = 1900
COL_4_LEFT = 2170
COL_4_RIGHT = 2270

card_files = ["cards\\A_R.png",
              "cards\\A_B.png",
              "cards\\2_R.png",
              "cards\\2_B.png",
              "cards\\3_R.png",
              "cards\\3_B.png",
              "cards\\4_R.png",
              "cards\\4_B.png",
              "cards\\5_R.png",
              "cards\\5_B.png",
              "cards\\6_R.png",
              "cards\\6_B.png",
              "cards\\7_R.png",
              "cards\\7_B.png",
              "cards\\8_R.png",
              "cards\\8_B.png",
              "cards\\9_R.png",
              "cards\\9_B.png",
              "cards\\10_R.png",
              "cards\\10_B.png",
              "cards\\J_R.png",
              "cards\\J_B.png",
              "cards\\Q_R.png",
              "cards\\Q_B.png",
              "cards\\K_R.png",
              "cards\\K_B.png",]


card_order_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

card_order = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
              '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}

card_order_reversed = {value: key for key, value in card_order.items()}

card_value = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
              '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}


def gt(A, B):
    """Greater than comparison for cards.

    A > B"""

    if card_order[A] > card_order[B]:
        return True
    else:
        return False


def lt(A, B):
    """Less than comparison for cards.

    A > B"""

    if card_order[A] < card_order[B]:
        return True
    else:
        return False


def in_col_1(pos):

    if COL_1_LEFT < pos.left < COL_1_RIGHT:
        return True
    else:
        return False


def in_col_2(pos):

    if COL_2_LEFT < pos.left < COL_2_RIGHT:
        return True
    else:
        return False


def in_col_3(pos):

    if COL_3_LEFT < pos.left < COL_3_RIGHT:
        return True
    else:
        return False


def in_col_4(pos):

    if COL_4_LEFT < pos.left < COL_4_RIGHT:
        return True
    else:
        return False


def in_col_any(pos):

    if in_col_1(pos) or in_col_2(pos) or in_col_3(pos) or in_col_4(pos):
        return True
    else:
        return False


def is_overlapping(box1, box2):

    left1, top1, width1, height1 = box1
    left2, top2, width2, height2 = box2

    right1 = left1 + width1
    right2 = left2 + width2
    bottom1 = top1 + height1
    bottom2 = top2 + height2

    # Check for overlap
    if left1 < right2 and right1 > left2 and top1 < bottom2 and bottom1 > top2:
        return True
    else:
        return False


def remove_overlapping(boxes):

    non_overlapping_boxes = []

    for i in range(len(boxes)):
        box = boxes[i]
        overlap = False

        for j in range(i + 1, len(boxes)):
            other_box = boxes[j]

            if is_overlapping(box[1], other_box[1]):
                overlap = True
                break

        if not overlap:
            non_overlapping_boxes.append(box)

    return non_overlapping_boxes


# def clean_card_list(name, red, black):

#     # Convert from n, the index in card_files to the

#     # name = card_order_reversed[n//2]

#     combined_cards = [(name, pos) for pos in red if in_col_any(pos)] + [(name, pos) for pos in black if in_col_any(pos)]

#     return remove_overlapping(combined_cards)


def find_cards(name, screenshot):

    # TODO: Optimize by cropping the screenshot

    red = pyscreeze.locateAll(needleImage=f"cards\\{name}_R.png", haystackImage=screenshot, confidence=0.93)
    black = pyscreeze.locateAll(needleImage=f"cards\\{name}_B.png", haystackImage=screenshot, confidence=0.93)

    # Reorganize the cards as well as process the generators created by pyscreeze.locateAll (time intensive)
    combined = [(name, pos) for pos in red if in_col_any(pos)] + [(name, pos) for pos in black if in_col_any(pos)]

    return remove_overlapping(combined)


def get_current_cards():

    screenshot = pyscreeze.screenshot()

    with mp.Pool(processes=13) as pool:

        args = (('A', screenshot),
                ('2', screenshot),
                ('3', screenshot),
                ('4', screenshot),
                ('5', screenshot),
                ('6', screenshot),
                ('7', screenshot),
                ('8', screenshot),
                ('9', screenshot),
                ('10', screenshot),
                ('J', screenshot),
                ('Q', screenshot),
                ('K', screenshot))

        list_of_lists = pool.starmap(find_cards, args)

        cards = [item for sublist in list_of_lists for item in sublist]

        # screenshot = pyscreeze.screenshot()

        # # Return a list of generators for each combination of card value and card color
        # # Every other index the color switches
        # # Every two indices the type switches
        # # So all_cards[0] and all_cards[1] are both generators of aces, but of different colors
        # # The time intensive searching does not happen until the generator objects are actually iterated across
        # all_cards = [pyscreeze.locateAll(needleImage=file, haystackImage=screenshot,
        #                                  confidence=0.93) for file in card_files]

        # with mp.Pool(processes=13) as pool:
        #     # Take the list of generators, and send the generators to workers
        #     # So that the time intensive part is parallelized :)

        #     args = (('A', all_cards[0], all_cards[1]),
        #             ('2', all_cards[2], all_cards[3]),
        #             ('3', all_cards[4], all_cards[5]),
        #             ('4', all_cards[6], all_cards[7]),
        #             ('5', all_cards[8], all_cards[9]),
        #             ('6', all_cards[10], all_cards[11]),
        #             ('7', all_cards[12], all_cards[13]),
        #             ('8', all_cards[14], all_cards[15]),
        #             ('9', all_cards[16], all_cards[17]),
        #             ('10', all_cards[18], all_cards[19]),
        #             ('J', all_cards[20], all_cards[21]),
        #             ('Q', all_cards[22], all_cards[23]),
        #             ('K', all_cards[24], all_cards[25]))

        #     cards = pool.starmap(clean_card_list, args)

        # A = clean_card_list(0, 1)
        # two = clean_card_list(2, 3)
        # three = clean_card_list(4, 5)
        # four = clean_card_list(6, 7)
        # five = clean_card_list(8, 9)
        # six = clean_card_list(10, 11)
        # seven = clean_card_list(12, 13)
        # eight = clean_card_list(14, 15)
        # nine = clean_card_list(16, 17)
        # ten = clean_card_list(18, 19)
        # J = clean_card_list(20, 21)
        # Q = clean_card_list(22, 23)
        # K = clean_card_list(24, 25)

        # def fix(short_name, var_name):
        #     return list(zip([f'{short_name}']*len(var_name), var_name))

        # cards = fix('A', A) + fix('2', two) + fix('3', three) + fix('4', four) + fix('5', five) + fix('6', six) + \
        #     fix('7', seven) + fix('8', eight) + fix('9', nine) + fix('10', ten) + fix('J', J) + fix('Q', Q) + fix('K', K)

    return cards


def get_playable_cards(cards):

    # Find the lowest y value card in each column

    col1, col2, col3, col4, = None, None, None, None

    for number, box in cards:

        if in_col_1(box):

            if not col1:
                col1 = (number, box)
            elif box.top > col1[1].top:
                col1 = (number, box)

        elif in_col_2(box):

            if not col2:
                col2 = (number, box)
            elif box.top > col2[1].top:
                col2 = (number, box)

        elif in_col_3(box):

            if not col3:
                col3 = (number, box)
            elif box.top > col3[1].top:
                col3 = (number, box)

        elif in_col_4(box):

            if not col4:
                col4 = (number, box)
            elif box.top > col4[1].top:
                col4 = (number, box)

        else:
            raise 'Big Ouchie'

    return [col1, col2, col3, col4]


def score(cards):
    """Find the total score value of the given stack of cards.

    - The first card played to the stack is a jack (+2)
    - Stack total is exactly 15 (+2)
    - Stack total is exactly 31 (+2)
    - Set of 2, 3, or 4 of the same card (+2/+6/+12)
    - Run of 3 to 7 cards in any order (+3 to +7)

    """

    # if len(cards) == 0:
    #     return 0

    score = 0  # Total score generated by this stack

    stack_total = 0  # Total value of the cards

    # Scoring from the first card being a jack
    if cards[0][0] == 'J':
        score += 2

    # The length of sets is stored as a list so that changes in card type can be properly handled
    set_counts = [1]

    # Lists of consecutive cards for scoring runs
    # With how it's currently done, the final runs list will have a blank list within it. It is not intended, but harmless
    runs = [[]]

    # Look through the stack of cards in the order they were placed
    for i in range(len(cards)):

        current_card = cards[i][0]
        current_value = card_value[current_card]

        stack_total += current_value

        # Stack total is exactly 15 or 31 (+2)
        if stack_total == 15 or stack_total == 31:
            score += 2
        elif stack_total > 31:
            break

        # Calculations to determine sets
        if i > 0:

            previous_card = cards[i - 1][0]

            if previous_card == current_card:
                set_counts[-1] += 1
            else:
                set_counts.append(1)

        # The card is not contiguous with the current run
        disjointed = True

        # The current card is already in the run
        duplicate = False

        for card in runs[-1]:
            if (current_value == card_value[card] + 1) or (current_value == card_value[card] - 1):
                disjointed = False
                break

        if current_card in runs[-1]:
            duplicate = True

        # The current card is unique and within the correct range
        if not disjointed and not duplicate:
            runs[-1].append(current_card)

        # The current run has ended and a new run is started
        elif disjointed or duplicate:
            runs.append([current_card])

    # Scoring from a set
    for count in set_counts:
        if count == 2:
            score += 2
        elif count == 3:
            score += 6
        elif count >= 4:
            score += 12

    # Score from a run
    for run in runs:
        length = len(run)
        if length >= 3:
            score += length

    return score

# def random_card(cards):

#     playable = get_playable_cards(cards)

#     # For now, chose a card at random
#     i = random.randint(0, 3)

#     return playable[i]


def greedy(cards, stack):
    """Attempt the move that gets the most immediate score."""
    # basic greedy implementation:
    # create a function that evaluates the increase in score after a particular move
    # then, choose the playable card that increases score the most

    # TODO: keep track of which cards are currently in the stack
    # score() call below should append the playable card to the current stack
    # keep track of the next stack button

    playable = get_playable_cards(cards)

    best_choice = None
    best_score = 0

    # Find which of the playable cards, if any, will increase score
    for card in playable:
        score_but_not_the_function = score(stack+[card])

        if score_but_not_the_function > best_score:
            best_choice = card
            best_score = score_but_not_the_function

    # None of the available choices will increase the score, so pick randomly.
    if best_score == 0:
        if None in playable:
            raise NotImplementedError
        else:
            return random.choice(playable)
    else:
        return best_choice


# if __name__ == '__main__':
#     stack = [('A', 0), ('2', 0), ('3', 0), ('2', 0), ('J', 0), ('3', 0)]
#     print(score(stack))

if __name__ == '__main__':
    time.sleep(1)

    winsound.Beep(200, 100)
    cards = get_current_cards()
    winsound.Beep(500, 100)

    card_count = len(cards)
    print(card_count)


# if __name__ == '__main__':
#     time.sleep(2)

#     stack = []

#     i = 1
#     while i <= 52:
#         winsound.Beep(200, 100)

#         next_button = pyautogui.locateCenterOnScreen("cards\\next_stack.png", confidence=0.95)

#         if next_button:
#             pyautogui.moveTo(next_button)
#             pyautogui.mouseDown()
#             pyautogui.mouseUp()
#             stack = []

#         cards = get_current_cards()
#         winsound.Beep(500, 100)

#         # card_count = len(cards)

#         card_to_play = greedy(cards, stack)
#         stack.append(card_to_play)

#         pyautogui.moveTo(x=card_to_play[1].left, y=card_to_play[1].top)
#         pyautogui.mouseDown()
#         pyautogui.mouseUp()

#         i += 1
