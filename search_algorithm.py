#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import logging
import time
import sys
sys.setrecursionlimit(10000)

from checkerboard import Checkerboard
log = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
log_file_handler = logging.FileHandler('./logs/test.log')
log_file_handler.setLevel(logging.DEBUG)

log.addHandler(log_file_handler)
logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        log_file_handler,
                    ], format=FORMAT
                    )


def heuristic_cost(x1, y1, x2, y2):
    """How far from the goal to final
    Args:
        x1, y1: next step location
        x2, y2: goal state location
    Returns:
        Double
    """
    return math.sqrt((x1 - x2) ** 2 + ((y1 - y2) / 2 ** math.sqrt(3)) ** 2)


def goal_cost(x1, y1, x2, y2):
    """Average One step can go how far
    Args:
        x1, y1: initial step location
        x2, y2: next state location
    Returns:
        Double
    """
    return math.sqrt((x1 - x2) ** 2 + ((y1 - y2) / 2 ** math.sqrt(3)) ** 2)


def cost_function_combine(initial_state, frontier_node, final_state):
    return (goal_cost(frontier_node[0],  frontier_node[1], final_state[0], final_state[1]) +
            heuristic_cost(initial_state[0], initial_state[1], frontier_node[0], frontier_node[1]))


def _target_can_jump(start_step, next_step, chess_table):
    try:
        x = start_step[0]
        y = start_step[1]
        log.debug("predict step: " +
                  str([2 * next_step[0] - x, 2 * next_step[1] - y]))
        log.debug("predict step value: " + str(chess_table.checkerboard[chess_table.package_location([
            2 * next_step[0] - x, 2 * next_step[1] - y])]))
        return chess_table.checkerboard[chess_table.package_location([next_step[0], next_step[1]])] == 1 and \
            chess_table.checkerboard[chess_table.package_location([
                2 * next_step[0] - x, 2 * next_step[1] - y])] == 0
    except KeyError as e:
        log.debug("[!] next step %s not exist in space. " % str(next_step))


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
    log.debug("init target_step: " + str(target_steps))
    tmp_node_queue = []
    for target_step in target_steps[0:8]:
        log.debug("target step: " + str(target_step))
        # If step not exist in chess table, it will cause Error.
        try:
            step_value = chess_table.checkerboard[chess_table.package_location(
                target_step)]
        except KeyError as e:
            step_value = -1
            log.debug("next step %s not exist in space. " %
                      str([target_step[0], target_step[1]]))

        log.debug("step value: " + str(step_value))
        if step_value == -1:
            log.debug("location %s value: %d cannot go!" %
                      (str(target_step), step_value))
        elif _target_can_jump([x, y], target_step, chess_table):
            next_step = [target_step[0] * 2 - x, target_step[1]
                         * 2 - y]
            frontier_nodes.append(next_step)
            frontier(next_step[0], next_step[1], chess_table,
                     frontier_nodes, black_list=black_list, first_flag=False)
        elif first_flag and step_value == 0:
            log.debug("final location: " + str(target_step))
            frontier_nodes.append(target_step)


def generate_near_steps(x, y):
    for i in range(-1, 1):
        for j in range(-1, 1):
            log.debug([x + i], [x + j])


def choose_next_node(initial_states, nodes_list, target):
    distance_dict = {}
    result_node = {}
    for initial_state, nodes in zip(initial_states, nodes_list):
        for node in nodes:
            log.debug("initial_state: %s / goal_state: %s " %
                      (str(initial_state), str(node)))
            distance = cost_function_combine(initial_state, node, target)
            log.debug("distance: %f " % distance)
            distance_dict["|".join(map(str, initial_state)) +
                          "||" + "|".join(map(str, node))] = [node, distance]

    tmp_distance = -100
    for k, d in distance_dict.items():
        if d[1] > tmp_distance:
            result_node = d[0]
    return k, d, result_node


def check_final_status(checkerboard, target, flag):
    final_status = True
    for i in target:
        if checkerboard[checkerboard.package_location(i)] = flag:
            pass
        else:
            final_status = False
            break
    return final_status


if __name__ == "__main__":
    FLAG = 1
    FINAL_FLAG = 2
    checkerboard = Checkerboard(8, 8)
    log.debug("* checkerboard space count: " +
              str(checkerboard.checkerboard.values().count(0)))
    init = checkerboard.init_barrack(4, 0, 4, -8, -4, -4, FLAG)
    log.debug("* init chess count: " + str(len(init)))
    target_list = checkerboard.init_barrack(-4, 0, -4, 4, 4, 8, FINAL_FLAG)
    # mid_point = [0, 0]
    # last_point = [-4, 8]
    target = [-4, 8]
    # for x, y in target_list:
    # mid_point[0] += x
    # mid_point[1] += y
    # mid_point[0] /= len(target_list)
    # mid_point[1] /= len(target_list)
    # log.debug("* target mean point: " + str(mid_point))
    frontier_nodes_list = []

    for i in init:
        frontier_nodes = []
        frontier(i[0], i[1], checkerboard, frontier_nodes)
        frontier_nodes_list.append(frontier_nodes)

        # for fn in frontier_nodes:
        # print(i, fn, [-4, 8])
        # astar(initial_state=i, nodes=frontier_nodes, target=[-4, 8])
    print(choose_next_node(init, frontier_nodes_list, target))

    log.debug("* initial state: " + str(init))
    log.debug("* frontier nodes: " + str(frontier_nodes_list))
