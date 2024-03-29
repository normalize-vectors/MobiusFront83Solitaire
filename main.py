import interface
import time
import pyautogui

INF = 10000


def score_single(stack):
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
    if stack[0].name == 'J':
        score += 2

    # The length of sets is stored as a list so that changes in card type can be properly handled
    set_counts = [1]

    # Lists of consecutive cards for scoring runs
    # With how it's currently done, the final runs list will have a blank list within it. It is not intended, but harmless
    runs = [[]]

    # Look through the stack of cards in the order they were placed
    for i in range(len(stack)):

        current_card = stack[i]

        stack_total += current_card.value

        # Stack total is exactly 15 or 31 (+2)
        if stack_total == 15 or stack_total == 31:
            score += 2
        elif stack_total > 31:
            break

        # Calculations to determine sets
        if i > 0:

            previous_card = stack[i - 1]

            if previous_card.name == current_card.name:
                set_counts[-1] += 1
            else:
                set_counts.append(1)

        # Says if the card is not contiguous with the current run
        disjointed = True

        # Says if the current card is already in the run
        duplicate = False

        for card in runs[-1]:
            if (current_card.order == card.order + 1) or (current_card.order == card.order - 1):
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


def score_multiple(stacks):
    """"Calculate the score for a list of cards representing all cards that have been played in all stacks."""

    stack = []

    total_score = 0

    sub_total = 0

    # Attempt to split the list of cards into stacks, then sum the score of each stack
    for card in stacks:

        if sub_total + card.value > 31:
            total_score += score_single(stack)
            sub_total = 0
            stack = []

        sub_total += card.value
        stack.append(card)

    total_score += score_single(stack)

    return total_score


def partial_stack(stacks):
    """Split a list of all cards that have been played into the one remaining active stack.

    Also returns the value of that stack."""

    stack = []
    sub_total = 0

    # Attempt to split the list of cards into stacks, then sum the score of each stack
    for card in stacks:

        if sub_total + card.value > 31:
            sub_total = 0
            stack = []

        sub_total += card.value
        stack.append(card)

    return stack, sub_total


def simulate_move(all_cards, played_cards, card_to_play):
    """Update the lists of cards to reflect a card being played."""

    new_cards = [card for card in all_cards if card is not card_to_play]

    new_played = played_cards.copy()
    new_played.append(card_to_play)

    return new_cards, new_played


def get_playable_cards(cards, stacks):
    """Returns a list of cards that can be played. Only returns cards that would not push the stack over a value of 31."""

    # Find the lowest y value card in each column

    col1, col2, col3, col4, = None, None, None, None

    def lowest(card, col, num):

        if card.column == num:
            if not col:

                return card
            elif card.y > col.y:
                return card
            else:
                return col

    for card in cards:

        match card.column:

            case 1:
                col1 = lowest(card, col1, 1)
            case 2:
                col2 = lowest(card, col2, 2)
            case 3:
                col3 = lowest(card, col3, 3)
            case 4:
                col4 = lowest(card, col4, 4)

    bottom_cards = [col for col in [col1, col2, col3, col4] if col]

    stack, value = partial_stack(stacks)

    # Exclude cards that would push the stack over a value of 31
    playable_cards = []
    for card in bottom_cards:

        if value + card.value <= 31:
            playable_cards.append(card)

    # breakpoint()

    # If all cards make the stack too big, return all bottom cards (start a new stack)
    if len(playable_cards) == 0:
        return bottom_cards

    else:
        return playable_cards


def search(depth, all_cards, played_cards, playable_card):
    """Returns the final score of the best possible path that could result from playing the given card."""

    # breakpoint()

    # Return the total score accumulated when the end of a path has been reached
    if depth == 0:
        return score_multiple(played_cards), []

    best_score = -INF
    best_path = []

    new_all, new_played = simulate_move(all_cards, played_cards, playable_card)

    new_playable_cards = get_playable_cards(new_all, new_played)

    # Stop the search if we have run out of cards
    if len(new_all) == 0:
        return score_multiple(played_cards), []

    for card in new_playable_cards:

        # The list of cards that have been played for the next depth
        this_played = new_played

        # Score that results from this child node
        result, path = search(depth=depth-1, all_cards=new_all, played_cards=this_played, playable_card=card)

        if result > best_score:
            best_score = result
            best_path = [card] + path

    return best_score, best_path


def find_move(all_cards, played_cards):
    """Find and return the best card to play."""

    playable_cards = get_playable_cards(all_cards, played_cards)

    best_card = None
    best_score = -2*INF
    best_path = None

    for card in playable_cards:

        score, path = search(depth=6, all_cards=all_cards, played_cards=played_cards, playable_card=card)

        if score > best_score:
            best_card = card
            best_score = score
            best_path = [card] + path

    if best_score == -INF:
        print("Unable to find a scoring path.")
    # else:
    #     print(f"Found a path worth {best_score}")

    return best_card, best_path


if __name__ == '__main__':

    played_cards = []

    time.sleep(1)

    # Read the screen and find all card locations
    all_cards = interface.get_all_cards_greyscale()

    # Ready the cursor
    pyautogui.moveTo(x=100, y=100)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

    for i in range(52):

        if len(all_cards) < 1:
            break

        card, path = find_move(all_cards, played_cards)

        all_cards, played_cards = simulate_move(all_cards, played_cards, card)

        print(f"Attempting to play card: {card}")

        pyautogui.moveTo(x=card.x, y=card.y)
        pyautogui.mouseDown()
        pyautogui.mouseUp()

        time.sleep(0.07)

        next_button = pyautogui.locateCenterOnScreen(
            "cards\\next_stack.png",
            confidence=0.95,
            region=(635, 430, 350, 1000))

        if next_button:
            pyautogui.moveTo(next_button)
            pyautogui.mouseDown()
            pyautogui.mouseUp()
            time.sleep(0.07)

    print("All cards played.")
