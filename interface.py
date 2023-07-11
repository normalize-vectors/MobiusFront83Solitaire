import pyscreeze
import multiprocessing as mp
import time
# import main

from PIL import ImageEnhance
from PIL import ImageFont
from PIL import ImageDraw


COL_1_LEFT = 1085
COL_1_RIGHT = 1200
COL_2_LEFT = 1450
COL_2_RIGHT = 1570
COL_3_LEFT = 1820
COL_3_RIGHT = 1920
COL_4_LEFT = 2185
COL_4_RIGHT = 2290
BOTTOM = 1000


class Card():

    order = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
             '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}

    value = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
             '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}

    def __init__(self, name, box=None):

        self.name = name
        self.value = Card.value[name]
        self.order = Card.order[name]

        if box:
            self.box = box
            self.x, self.y = pyscreeze.center(self.box)
            self.column = which_column(self.box)
        else:
            self.box = None
            self.x = None
            self.y = None
            self.column = None

    def __gt__(self, other):

        if Card.order[self.name] > Card.order[other.name]:
            return True
        else:
            return False

    def __ge__(self, other):

        if Card.order[self.name] >= Card.order[other.name]:
            return True
        else:
            return False

    def __lt__(self, other):

        if Card.order[self.name] < Card.order[other.name]:
            return True
        else:
            return False

    def __le__(self, other):

        if Card.order[self.name] <= Card.order[other.name]:
            return True
        else:
            return False

    def __eq__(self, other):

        if Card.order[self.name] == Card.order[other.name]:
            return True
        else:
            return False

    def __ne__(self, other):

        if Card.order[self.name] != Card.order[other.name]:
            return True
        else:
            return False

    def __repr__(self):
        return f"{self.name} in column {self.column}"


def in_col_1(pos):

    if COL_1_LEFT < pos.left < COL_1_RIGHT:
        if pos.top < BOTTOM:
            return True
    return False


def in_col_2(pos):

    if COL_2_LEFT < pos.left < COL_2_RIGHT:
        if pos.top < BOTTOM:
            return True
    return False


def in_col_3(pos):

    if COL_3_LEFT < pos.left < COL_3_RIGHT:
        if pos.top < BOTTOM:
            return True
    return False


def in_col_4(pos):

    if COL_4_LEFT < pos.left < COL_4_RIGHT:
        if pos.top < BOTTOM:
            return True
    return False


def which_column(box):

    if in_col_1(box):
        return 1
    elif in_col_2(box):
        return 2
    elif in_col_3(box):
        return 3
    elif in_col_4(box):
        return 4

    return None


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


def remove_overlapping(cards):

    non_overlapping_boxes = []

    for i in range(len(cards)):
        card = cards[i]
        overlap = False

        for j in range(i + 1, len(cards)):
            other_card = cards[j]

            if is_overlapping(card.box, other_card.box):
                overlap = True
                break

        if not overlap:
            non_overlapping_boxes.append(card)

    return non_overlapping_boxes


def find_cards_greyscale(name, screenshot):
    """Find all cards of a given face."""

    # Creates generators
    greyscale = pyscreeze.locateAll(
        needleImage=f"cards\\{name}.png",
        haystackImage=screenshot,
        confidence=0.75,
        grayscale=True)

    # Process the generators (time intensive)
    combined = [Card(name, box) for box in greyscale]

    return combined


def preprocess_image(image):
    """Convert the image to greyscale."""

    # Convert image to grayscale
    image = image.convert("L")

    # Increase brightness and contrast
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(0.92)

    # Maximize contrast
    image = image.point(lambda x: 0 if x < 128 else 255, "L")

    image.save('processed.png')

    return image


def get_all_cards_greyscale():
    """Takes a screenshot to get the postion of all cards on the screen. Returns a list of Card objects."""

    screenshot = preprocess_image(pyscreeze.screenshot())

    with mp.Pool(processes=13) as pool:

        # The order of this tuple seems to affect which way overlapping cards are resolved
        # Q is a very false-positive prone character, so it is done first so that other characters may overwrite it
        args = (('Q', screenshot),
                ('9', screenshot),
                ('A', screenshot),
                ('2', screenshot),
                ('3', screenshot),
                ('4', screenshot),
                ('5', screenshot),
                ('6', screenshot),
                ('7', screenshot),
                ('8', screenshot),
                ('10', screenshot),
                ('J', screenshot),
                ('K', screenshot))

        list_of_lists = pool.starmap(find_cards_greyscale, args)

        cards = [item for sublist in list_of_lists for item in sublist]

        cards = [card for card in remove_overlapping(cards) if card.column]

    font = ImageFont.truetype("arial.ttf", 60)
    draw = ImageDraw.Draw(screenshot)

    for card in cards:

        draw.text((card.x+30, card.y-40), card.name, 155, font=font)

    screenshot.save('processed_labelled.png')

    return cards


if __name__ == "__main__":

    ti = time.time()

    cards = get_all_cards_greyscale()

    tf = time.time()

    print(f"Found {len(cards)} cards")

    print(f"Took {round(tf-ti,3)} seconds")

    card_count = {}

    for card in cards:

        name = card.name

        key = f"{name}"

        card_count[key] = card_count.get(key, 0) + 1
