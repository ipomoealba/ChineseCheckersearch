#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import logging
import time
import sys
sys.setrecursionlimit(10000)

from checkerboard import Checkerboard
log = logging.getLogger(__name__)

log_file_handler = logging.FileHandler('./logs/test.log')
log_file_handler.setLevel(logging.DEBUG)

log.addHandler(log_file_handler)
logging.basicConfig(level=logging.DEBUG, handlers=[
    log_file_handler,
])


def heuristic_cost(x1, y1, x2, y2):
    """How far from the goal to final
    Args:
        x1, y1: next step location
        x2, y2: goal state location
    Returns:
        Double
    """
    return math.sqrt((x1 - x2) ** 2 + ((y1 - y2) / 2 ** math.sqrt(3)) ** 2)


def goal_cost(cost_length, steps=1):
    """Average One step can go how far
    Args:
        cost_length: how far can the step go
        steps: initial is 1, how many chess move in the player round
    Returns:
        Double
    """
    return cost_length / steps

def _target_can_jump(next_step, chess_table):
    try:
        log.debug("--- predict step: " +
                  str([2 * next_step[0] - x, 2 * next_step[1] - y]))
        log.debug("--- predict step value: " + str(chess_table.checkerboard[chess_table.package_location(
            2 * next_step[0] - x, 2 * next_step[1] - y)]))
        return chess_table.checkerboard[chess_table.package_location(next_step[0], next_step[1])] == 1 and \
            chess_table.checkerboard[chess_table.package_location(
                2 * next_step[0] - x, 2 * next_step[1] - y)] == 0
    except KeyError as e:
        log.debug("=== next step %s not exist in space. " % str(next_step))

def frontier(x, y, chess_table, frontier_nodes=None, black_list=[], first_flag=True):
    """The chess has next step
    Args:
        x, y: the chess location
        chess_table: the table current status
        frontier_nodes: the nodes can be frontier_node, it was a list
        black_list: the chess last jump location
    Returns:
        None
        # List of nodes, like [[1,2],[4,6]]

    TODO: get the nodes to frontier
    """
    log.debug("! Initial Step [%d, %d]" % (x, y))
    black_list.append([x, y])
    if frontier_nodes == None:
        frontier_nodes = []
    target_steps = [[x, y + 1], [x - 1, y + 1],
                    [x - 1, y], [x + 1, y], [x, y - 1], [x + 1, y - 1]]
    log.debug("- init target_step: " + str(target_steps))
    tmp_node_queue = []
    for target_step in target_steps[0:8]:
        log.debug("-- target step: " + str(target_step))
        # If step not exist in chess table, it will cause Error.
        try:
            step_value = chess_table.checkerboard[chess_table.package_location(
                target_step[0], target_step[1])]
        except KeyError as e:
            step_value = -1
            log.debug("=== next step %s not exist in space. " %
                      str([target_step[0], target_step[1]]))

        log.debug("-- step value: " + str(step_value))
        if step_value == -1:
            log.debug("--- location %s value: %d cannot go!" %
                      (str(target_step), step_value))
        elif _target_can_jump(target_step, chess_table):
            next_step = [target_step[0] * 2 - x, target_step[1]
                         * 2 - y]
            frontier_nodes.append(next_step)
            frontier(next_step[0], next_step[1], chess_table,
                     frontier_nodes, black_list=black_list, first_flag=False)
        elif first_flag and step_value == 0:
            log.debug("--- final location: " + str(target_step))
            frontier_nodes.append(target_step)


def generate_near_steps(x, y):
    for i in range(-1, 1):
        for j in range(-1, 1):
            log.debug([x + i], [x + j])
# 
#
# def astar(nodes, target):
#     for node in nodes:
#         goal_cost(node[0], node[1])

if __name__ == "__main__":
    checkerboard = Checkerboard(8, 8)
    log.debug("* checkerboard space count: " +
              str(checkerboard.checkerboard.values().count(0)))
    init = checkerboard.init_barrack(4, 0, 4, -8, -4, -4, 1)
    log.debug("* init chess count: " + str(len(init)))
    target_list = checkerboard.init_barrack(-4, 0, -4, 4, 4, 8, 2)
    mid_point = [0, 0]
    last_point = [-4, 8]

    for x, y in target_list:
        mid_point[0] += x
        mid_point[1] += y
    mid_point[0] /= len(target_list)
    mid_point[1] /= len(target_list)
    log.debug("* target mean point: " + str(mid_point))
    frontier_nodes = []

    for i in init:
        frontier(i[0], i[1], checkerboard, frontier_nodes)
    # frontier(4, -8, checkerboard, frontier_nodes)
    log.debug("* frontier nodes: " + str(frontier_nodes))
