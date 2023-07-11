import pyautogui
import time
import winsound
import random
import pyscreeze
import multiprocessing as mp

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05  # Wait a small amount of time after each click

COL_1_LEFT = 1060
COL_1_RIGHT = 1220
COL_2_LEFT = 1430
COL_2_RIGHT = 1560
COL_3_LEFT = 1790
COL_3_RIGHT = 1910
COL_4_LEFT = 2160
COL_4_RIGHT = 2280

# card_files = ["cards\\A_R.png",
#               "cards\\A_B.png",
#               "cards\\2_R.png",
#               "cards\\2_B.png",
#               "cards\\3_R.png",
#               "cards\\3_B.png",
#               "cards\\4_R.png",
#               "cards\\4_B.png",
#               "cards\\5_R.png",
#               "cards\\5_B.png",
#               "cards\\6_R.png",
#               "cards\\6_B.png",
#               "cards\\7_R.png",
#               "cards\\7_B.png",
#               "cards\\8_R.png",
#               "cards\\8_B.png",
#               "cards\\9_R.png",
#               "cards\\9_B.png",
#               "cards\\10_R.png",
#               "cards\\10_B.png",
#               "cards\\J_R.png",
#               "cards\\J_B.png",
#               "cards\\Q_R.png",
#               "cards\\Q_B.png",
#               "cards\\K_R.png",
#               "cards\\K_B.png",]


# card_order_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

card_order = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
              '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}

# card_order_reversed = {value: key for key, value in card_order.items()}

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


def find_cards(name, screenshot):

    # TODO: Optimize by cropping the screenshot

    red = pyscreeze.locateAll(needleImage=f"cards\\{name}_R.png", haystackImage=screenshot, confidence=0.91)
    black = pyscreeze.locateAll(needleImage=f"cards\\{name}_B.png", haystackImage=screenshot, confidence=0.91)

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

    return cards


def get_stack_value(stack):
    """Returns the value of the given stack."""

    total_value = 0

    for card in stack:
        total_value += card_value[card[0]]

    return total_value


def get_playable_cards(cards, stack):

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

    # Then check to see if adding that card to the stack would push it over 31

    bottom_cards = [col for col in [col1, col2, col3, col4] if col]

    playable_cards = []

    for card in bottom_cards:
        if not get_stack_value(stack+[card]) > 31:
            playable_cards.append(card)

    return playable_cards


def score(stack):
    """Find the total score value of the given stack of cards.

    - The first card played to the stack is a jack (+2)
    - Stack total is exactly 15 (+2)
    - Stack total is exactly 31 (+2)
    - Set of 2, 3, or 4 of the same card (+2/+6/+12)
    - Run of 3 to 7 cards in any order (+3 to +7)

    """

    if len(stack) == 0:
        return 0

    score = 0  # Total score generated by this stack

    stack_total = 0  # Total value of the cards

    # Scoring from the first card being a jack
    if stack[0][0] == 'J':
        score += 2

    # The length of sets is stored as a list so that changes in card type can be properly handled
    set_counts = [1]

    # Lists of consecutive cards for scoring runs
    # With how it's currently done, the final runs list will have a blank list within it. It is not intended, but harmless
    runs = [[]]

    # Look through the stack of cards in the order they were placed
    for i in range(len(stack)):

        current_card = stack[i][0]
        current_value = card_value[current_card]

        stack_total += current_value

        # Stack total is exactly 15 or 31 (+2)
        if stack_total == 15 or stack_total == 31:
            score += 2
        elif stack_total > 31:
            break

        # Calculations to determine sets
        if i > 0:

            previous_card = stack[i - 1][0]

            if previous_card == current_card:
                set_counts[-1] += 1
            else:
                set_counts.append(1)

        # Says if the card is not contiguous with the current run
        disjointed = True

        # Says if the current card is already in the run
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


# def greedy(cards, stack):
#     """Attempt the move that gets the most immediate score."""
#     # basic greedy implementation:
#     # create a function that evaluates the increase in score after a particular move
#     # then, choose the playable card that increases score the most

#     # TODO: keep track of which cards are currently in the stack
#     # score() call below should append the playable card to the current stack
#     # keep track of the next stack button

#     playable = get_playable_cards(cards)

#     best_choice = None
#     best_score = 0
#     best_args = None

#     # Find which of the playable cards, if any, will increase score
#     for card in playable:
#         score_but_not_the_function = score(stack+[card])

#         if score_but_not_the_function > best_score:
#             best_choice = card
#             best_score = score_but_not_the_function
#             best_args = stack+[card]

#     # None of the available choices will increase the score, so pick randomly.
#     if best_score == 0:
#         if None in playable:
#             raise NotImplementedError
#         else:
#             choice = random.choice(playable)
#             print(f"Picking a random card: {choice}")
#             return choice
#     else:
#         print(f"Found a best choice: {best_choice}")
#         print(f"... with best args: {best_args}")
#         return best_choice


def play_card(cards, stack, card):
    """Calculate the effect of a specific card on the list of all cards and the current stack."""

    # Calculate the score of the stack before the play is made
    initial_score = score(stack)

    # Find the value of the new stack
    total_value = get_stack_value(stack)

    if total_value > 31:  # The stack would exceed a value of 31, and thus this is not a valid play
        return cards, stack, -10000
    else:

        # Add the played card to the stack
        stack.append(card)

        # Remove the played card from the list of cards on the board
        cards.remove(card)

        # Calculate the increase in score due to this move
        score_delta = score(stack) - initial_score

        return cards, stack, score_delta

# # TODO code somewhere in search that resets stack if no cards are playable due to increase in score


def search(cards, stack, depth):
    """Search through all possible options to a certain depth, then pick the immediate move that will
    eventually result in the highest score."""

    # breakpoint()

    if depth == 0:
        return score(stack), None

    playable_cards = get_playable_cards(cards, stack)

    if len(playable_cards) == 0:
        stack = []
        playable_cards = get_playable_cards(cards, stack)

    best_score = -1
    best_card = None

    for card in playable_cards:
        new_cards, new_stack, score_delta = play_card(cards.copy(), stack.copy(), card)
        if len(new_cards) > 0:
            new_score, __ = search(new_cards, new_stack, depth - 1)
            if new_score > best_score:
                best_score = new_score
                best_card = card

    # return best_score, best_card

    if not best_card:
        return 0, random.choice(playable_cards)
    else:
        return best_score, best_card


# if __name__ == '__main__':

#     # time.sleep(1)

#     stack = [('2', 0),('2', 0),]

#     cards = get_current_cards()

#     res = search(cards, stack, 4)

#     print(res)

# if __name__ == '__main__':
#     stack = [('J', 0), ('2', 0), ('3', 0), ('A', 0), ('5', 0), ('4', 0)]
#     print(score(stack))

# if __name__ == '__main__':
#     time.sleep(1)

#     winsound.Beep(200, 100)
#     cards = get_current_cards()
#     winsound.Beep(500, 100)

#     card_count = len(cards)
#     print(card_count)


if __name__ == '__main__':

    stack = []

    i = 1
    while i <= 52:

        winsound.Beep(150, 100)
        next_button = pyautogui.locateCenterOnScreen("cards\\next_stack.png", confidence=0.95)

        if next_button:
            pyautogui.moveTo(next_button)
            pyautogui.mouseDown()
            pyautogui.mouseUp()
            stack = []

        cards = get_current_cards()
        winsound.Beep(600, 100)

        __, card_to_play = search(cards, stack, 3)
        stack.append(card_to_play)

        pyautogui.moveTo(x=card_to_play[1].left, y=card_to_play[1].top)
        pyautogui.mouseDown()
        pyautogui.mouseUp()

        breakpoint()

        i += 1
