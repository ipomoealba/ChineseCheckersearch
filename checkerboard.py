#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Checkerboard(object):
    """
    -1: null place
    0: exist place
    """
    def __init__(self, x_num, y_num):
        self.x_num = x_num
        self.y_num = y_num
        self.checkerboard = dict((self.package_location(x, y), -1) for x in range(-self.x_num + 1, self.x_num)
                                 for y in range(-self.y_num + 1, self.y_num))
        self.create_space()

    def get_checkerboard(self):
        return self.checkerboard
    
    def package_location(self, x, y):
        """Because of list not hashable in dict, so we use str to deal the problem
        Args:
            location x y
        Returns:
            str
        """
        return str(x) + "|" + str(y)

    def unpackage_location(self, xy):
        return [int(i) for i in xy.split("|")]

    def chess_table_can_go(self, location):
        place = self.checkerboard[self.package_location(location[0], location[1])]
        if place == 0:
            return True
        else:
            return False

    def init_barrack(self, x1, x2, x3, y1, y2, y3, status=1):
        """Get chess initial locations
        Args:
            Triangle Vertex [x1, y1] [x2, y2] [x3, y3] locations
        Returns:
            location list
        """
        map_list = [[x1, x2, x3], [y1, y2, y3]]
        all_c = [x + y for x, y in zip(map_list[0], map_list[1])]
        recursive_layer = range(min(all_c), max(all_c) + 1)
        result = []
        for k in recursive_layer:
            for x in range(min(map_list[0]), max(map_list[0]) + 1):
                for y in range(min(map_list[1]), max(map_list[1]) + 1):
                    if x + y == k:
                        self.checkerboard[self.package_location(x, y)] = status
                        result.append([x, y])
        return result

    def create_space(self):
        self.init_barrack(-4, -4, 8, 8, -4, -4, 0)
        self.init_barrack(-8, 4, 4, 4, -8, 4, 0)

    def getChessLocations(self):
        """Get chess location is not empty
        Args:
            None
        Returns:
            Locations List not equal zero
        """
        results = {}
        for location, status in self.checkerboard.items():
            if status != 0:
                results[location] = status
        return results

    def print_checkerboard_graph(self):
        pass


if __name__ == '__main__':
    checkerboard = Checkerboard(8, 8)
    checkerboard.init_barrack(4, 0, 4, -8, 4, -4, status=2)
    print(checkerboard.getChessLocations())
    print(len(checkerboard.getChessLocations()))
    # print("get checkerboard array: " + checkerboard.get_checkerboard())
    # print("get checkerboard length: " + len(checkerboard.get_checkerboard()))
