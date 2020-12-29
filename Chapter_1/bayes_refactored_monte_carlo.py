"""Tests best practice for choosing where to search for the lost sailor. Uses Monte Carlo simulations."""
import sys
import random
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
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


class SearchArea:
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


class Search:
    """Bayesian Search & Rescue game with 3 search areas."""

    def __init__(self, name=None):
        self.name = name
        self.num_search_areas = 3
        self.search_areas = [SearchArea(1, (130, 265), 50, 50, 0.2),
                             SearchArea(2, (80, 255), 50, 50, 0.5),
                             SearchArea(3, (105, 205), 50, 50, 0.3)]

        self.sailor_actual = self.sailor_final_location()

    def sailor_final_location(self):
        """Set the actual x,y location of the missing sailor."""
        # Pick a search area at random.
        area = int(random.triangular(1, self.num_search_areas + 1))

        # Find sailor coordinates with respect to any Search Area sub-array.
        final_x = self.search_areas[area - 1].ul_coord[0] + RNG.integers(0, self.search_areas[area - 1].height)
        final_y = self.search_areas[area - 1].ul_coord[1] + RNG.integers(0, self.search_areas[area - 1].width)

        return final_x, final_y

    def conduct_search(self, area_num):
        """Return search results and list of searched coordinates."""
        self.search_areas[area_num - 1].search()
        if self.sailor_actual in self.search_areas[area_num - 1].coords_searched:
            return True
        return False

    def revise_target_probs(self):
        """Update area target probabilities based on search effectiveness."""
        denominator = np.array([search_area.initial_probability * (1 - search_area.search_effectiveness_probability)
                                for search_area in self.search_areas]).sum()
        for search_area in self.search_areas:
            search_area.probability = search_area.initial_probability *\
                                      (1 - search_area.search_effectiveness_probability) / denominator


def get_search_area_choices(search_areas, search_method):
    if search_method == 123:        # Search the most probably area twice.
        search_area_max_prob = max(search_areas, key=lambda area: area.probability).area_index
        search_area_choices = (search_area_max_prob, search_area_max_prob)
    elif search_method == 456:      # Split searches among two most probably areas.
        search_area_min_prob = min(search_areas, key=lambda area: area.probability).area_index
        search_area_choices = tuple({1, 2, 3} - {search_area_min_prob})
    else:
        print('Invalid search method. Exiting.', file=sys.stderr)
        sys.exit(1)
    return search_area_choices


def monte_carlo(num_finds, search_method):
    """Simulate finding the sailor num_finds times."""
    results_dict = dict()       # Key is number of searches to find sailor. Value is number of times key is the result.
    for num_find in range(num_finds):
        app = Search()
        sailor_found = False
        search_num = 0

        while not sailor_found:
            search_num += 1
            search_sequence = get_search_area_choices(app.search_areas, search_method)

            results = [app.conduct_search(area) for area in search_sequence]
            if results[0] is True or results[1] is True:
                sailor_found = True

            app.revise_target_probs()       # Use Bayes' rule to update target probabilities.

        if search_num not in results_dict:
            results_dict[search_num] = 1
        else:
            results_dict[search_num] += 1
        del app

    return results_dict


def test_best_search_method():
    results_123 = np.array(list(monte_carlo(10000, 123).items()))
    results_456 = np.array(list(monte_carlo(10000, 456).items()))
    layout = dict(
        xaxis_title="Number of Searches to Find the Sailor",
        yaxis_title="Frequency",
        title="How many Search Attempts to Find the Sailor",
        barmode="group"
    )
    fig = go.Figure(go.Bar(x=results_123[:, 0], y=results_123[:, 1], name="Search one area twice."))
    fig.add_trace(go.Bar(x=results_456[:, 0], y=results_456[:, 1], name="Search two areas once each."))
    fig.update_layout(layout)

    fig.show()


def main():
    test_best_search_method()


if __name__ == '__main__':
    main()
