import sys
import random
import itertools
import math
import numpy as np
import cv2 as cv
#import pdb; pdb.set_trace()

MAP_FILE = 'cape_python.png'
RNG = np.random.default_rng(seed=None)
SEARCH_SEQUENCE = {
    1: (1, 1),
    2: (2, 2),
    3: (3, 3),
    4: (1, 2),
    5: (1, 3),
    6: (2, 3)
}


class SearchArea():
    """Search Area info"""

    def __init__(self, area_index,
                 upper_left_coord, height, width,
                 probability, search_effectiveness_probability=0):
        self.area_index = area_index
        self.ul_coord = upper_left_coord
        self.height = height
        self.width = width
        self.initial_probability = probability
        self.probability = probability
        self.search_effectiveness_probability = search_effectiveness_probability
        self.coords_searched = set()
        self.coords_not_searched = set([(x, y) for x in range(upper_left_coord[0], upper_left_coord[0] + height)
                                        for y in range(upper_left_coord[1], upper_left_coord[1] + width)])

    def search(self):
        """Search for sailor within this search area"""
        coords_not_searched_list = list(self.coords_not_searched)
        random.shuffle(coords_not_searched_list)

        new_search_effectiveness = random.uniform(0.2, 0.9)
        num_coords_to_search = int(math.ceil(len(coords_not_searched_list) * new_search_effectiveness))

        for coord in coords_not_searched_list[:num_coords_to_search]:
            self.coords_not_searched.remove(coord)
            self.coords_searched.add(coord)

        self.search_effectiveness_probability = 1 - len(self.coords_not_searched) / (self.height * self.width)


class Search():
    """Bayesian Search & Rescue game with 3 search areas."""

    def __init__(self, name):
        self.name = name
        self.img = cv.imread(MAP_FILE, cv.IMREAD_COLOR)
        if self.img is None:
            print('Could not load map file {}'.format(MAP_FILE),
                  file=sys.stderr)
            sys.exit(1)

        self.num_search_areas = 3
        self.search_areas = [SearchArea(1, (130, 265), 50, 50, 0.2),
                             SearchArea(2, (80, 255), 50, 50, 0.5),
                             SearchArea(3, (105, 205), 50, 50, 0.3)]

        self.sailor_actual = self.sailor_final_location()

    def draw_search_area(self, upper_left_coord, height, width, area_index):
        upper_left_x, upper_left_y = upper_left_coord
        cv.rectangle(self.img, (upper_left_x, upper_left_y),
                     (upper_left_x + height, upper_left_y + width), (0, 0, 0), 1)
        cv.putText(self.img, str(area_index),
                   (upper_left_x + 3, upper_left_y + 15),
                   cv.FONT_HERSHEY_PLAIN, 1, 0)

    def draw_search_areas(self):
        for search_area in self.search_areas:
            self.draw_search_area(search_area.ul_coord, search_area.height, search_area.width, search_area.area_index)

    def draw_map(self, last_known):
        """Display basemap with scale, last known xy location, search areas."""
        # Draw the scale bar.
        cv.line(self.img, (20, 370), (70, 370), (0, 0, 0), 2)
        cv.putText(self.img, '0', (8, 370), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
        cv.putText(self.img, '50 Nautical Miles', (71, 370),
                   cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))

        self.draw_search_areas()

        # Post the last known location of the sailor.
        cv.putText(self.img, '+', (last_known),
                   cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
        cv.putText(self.img, '+ = Last Known Position', (274, 355),
                   cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
        cv.putText(self.img, '* = Actual Position', (275, 370),
                   cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))

        cv.imshow('Search Area', self.img)
        cv.moveWindow('Search Area', 750, 10)
        cv.waitKey(500)

    def sailor_final_location(self):
        """Set the actual x,y location of the missing sailor."""
        # Pick a search area at random.
        area = int(random.triangular(1, self.num_search_areas + 1))

        # Find sailor coordinates with respect to any Search Area sub-array.
        final_x = self.search_areas[area - 1].ul_coord[0] + RNG.integers(0, self.search_areas[area - 1].height)
        final_y = self.search_areas[area - 1].ul_coord[1] + RNG.integers(0, self.search_areas[area - 1].width)

        return (final_x, final_y)

    def conduct_search(self, area_num):
        """Return search results and list of searched coordinates."""
        self.search_areas[area_num - 1].search()
        if self.sailor_actual in self.search_areas[area_num - 1].coords_searched:
            return True

        print(self.search_areas[area_num - 1].coords_not_searched)
        return False

    def revise_target_probs(self):
        """Update area target probabilities based on search effectiveness."""
        denominator = np.array([search_area.initial_probability * (1 - search_area.search_effectiveness_probability)
                                for search_area in self.search_areas]).sum()
        for search_area in self.search_areas:
            search_area.probability = search_area.initial_probability *\
                                      (1 - search_area.search_effectiveness_probability) / denominator


def draw_menu(search_num):
    """Print menu of choices for conducting area searches."""
    print('\nSearch {}'.format(search_num))
    print(
        """
        Choose next areas to search:

        0 - Quit
        1 - Search Area 1 twice
        2 - Search Area 2 twice
        3 - Search Area 3 twice
        4 - Search Areas 1 & 2
        5 - Search Areas 1 & 3
        6 - Search Areas 2 & 3
        7 - Start Over
        """
        )


def main():
    app = Search('Cape_Python')
    app.draw_map(last_known=(160, 290))
    print("-" * 65)
    print("\nInitial Target (P) Probabilities:")
    for search_area in app.search_areas:
        print('P{:d} = {:.3f}'.format(search_area.area_index, search_area.probability))

    search_num = 1
    # Continuously let user conduct searches until quit, sailor found, or restart.
    while True:
        draw_menu(search_num)
        choice = input("Choice: ")
        try:
            choice = int(choice)
        except ValueError:
            print('Please enter an integer.')
            continue

        # Handle all inputs that do not result in a search conducted.
        if choice == 0:
            sys.exit()
        elif choice == 7:
            main()
        elif choice < 0 or choice > 6:
            print("\nSorry, but that isn't a valid choice.", file=sys.stderr)
            continue
        else:
            search_sequence = SEARCH_SEQUENCE[choice]

        results = [app.conduct_search(area) for area in search_sequence]

        app.revise_target_probs()  # Use Bayes' rule to update target probs.

        sailor_found = False
        for i, result in enumerate(results, 1):
            print("\nSearch {} Results {} = {}"
                  .format(search_num, i, "Found" if result is True else "Not Found"))
            if result is True:
                sailor_found = True
                break

        print("\n\nSearch Effectiveness by area")

        for search_area in app.search_areas:
            print("Effectiveness in area {} = {:.3f}"
                  .format(search_area.area_index, search_area.search_effectiveness_probability))

        if not sailor_found:
            print("\nNew Target Probabilities (P) by area")
            for search_area in app.search_areas:
                print("Probability in area {} = {:.3f}"
                      .format(search_area.area_index, search_area.probability))
        else:
            cv.circle(app.img, app.sailor_actual, 3, (255, 0, 0), -1)
            cv.imshow('Search Area', app.img)
            cv.waitKey(5000)
            main()
        search_num += 1


if __name__ == '__main__':
    main()
