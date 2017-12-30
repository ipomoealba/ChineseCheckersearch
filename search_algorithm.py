#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import logging
import sys

from checkerboard import Checkerboard

sys.setrecursionlimit(10000)

log = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
log_file_handler = logging.FileHandler('./logs/test.log')
log_stream_handler = logging.StreamHandler(stream=None)
log_file_handler.setLevel(logging.INFO)

log.addHandler(log_file_handler)
logging.basicConfig(
    handlers=[
        log_file_handler,
        log_stream_handler,
    ], format=FORMAT)


def _target_can_jump(start_step, next_step, chess_table):
    try:
        x = start_step[0]
        y = start_step[1]
        log.debug("predict step: " +
                  str([2 * next_step[0] - x, 2 * next_step[1] - y]))
        log.debug("predict step value: " +
                  str(chess_table.checkerboard[chess_table.package_location(
                      [2 * next_step[0] - x, 2 * next_step[1] - y])]))
        return chess_table.checkerboard[chess_table.package_location([next_step[0], next_step[1]])] == 1 and \
            chess_table.checkerboard[chess_table.package_location([
                2 * next_step[0] - x, 2 * next_step[1] - y])] == 0
    except KeyError as e:
        pass
        # log.debug("[!] next step %s not exist in space. " % str(next_step))


def heuristic_cost(x1, y1, x2, y2):
    """How far from the goal to final
    Args:
        x1, y1: next step location
        x2, y2: goal state location
    Returns:
        Double
    """
    return math.sqrt((x1 - x2)**2 + ((y1 - y2) / 2**math.sqrt(3))**2)
    # return abs(x1 - x2) + abs(y1 - y2)


def goal_cost(x1, y1, x2, y2):
    """Average One step can go how far
    Args:
        x1, y1: initial step location
        x2, y2: next state location
    Returns:
        Double
    """
    return math.sqrt((x1 - x2)**2 + ((y1 - y2) / 2**math.sqrt(3))**2)


#
# def heuristic_cost(x1, y1, x2, y2):
#     return abs(x1 - x2) + abs(y1 - y2)
#
#
# def goal_cost(x1, y1, x2, y2):
#     pass


def cost_function_combine(initial_state,
                          frontier_node,
                          final_state,
                          h_weight=1,
                          g_weight=1):
    return (goal_cost(frontier_node[0], frontier_node[1], final_state[0],
                      final_state[1]) * g_weight +
            heuristic_cost(initial_state[0], initial_state[1],
                           frontier_node[0], frontier_node[1]) * g_weight)
    # / math.sqrt((initial_state[0] - initial_state[1])**2  + (frontier_node[0] - frontier_node[1])**2)


def frontier(x,
             y,
             chess_table,
             frontier_nodes=None,
             black_list=[],
             first_flag=True):
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
    log.debug("! Frontier Initial Step [%d, %d]" % (x, y))
    black_list.append([x, y])
    if frontier_nodes == None:
        frontier_nodes = []
    target_steps = [[x, y + 1], [x - 1, y + 1], [x - 1, y], [x + 1, y],
                    [x, y - 1], [x + 1, y - 1]]
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
            log.debug("next step %s not exist in space. " % str(
                [target_step[0], target_step[1]]))

        log.debug("step value: " + str(step_value))
        if step_value == -1:

            log.debug("location %s value: %d cannot go!" % (str(target_step),
                                                            step_value))
            pass
        elif _target_can_jump([x, y], target_step,
                              chess_table) and [x, y] not in black_list:
            next_step = [target_step[0] * 2 - x, target_step[1] * 2 - y]
            frontier_nodes.append(next_step)
            frontier(
                next_step[0],
                next_step[1],
                chess_table,
                frontier_nodes,
                black_list=black_list,
                first_flag=False)
        elif first_flag and step_value == 0:
            log.debug("final location: " + str(target_step))
            frontier_nodes.append(target_step)


def generate_near_steps(x, y):
    for i in range(-1, 1):
        for j in range(-1, 1):
            log.debug([x + i], [x + j])


def choose_next_node_reward_jump(initial_states, nodes_list, target):
    distance_dict = {}
    result_node = []
    result_value = -1
    result_initial_state = []
    for initial_state, nodes in zip(initial_states, nodes_list):
        for node in nodes:
            log.debug("initial_state: %s / goal_state: %s " %
                      (str(initial_state), str(node)))
            distance = cost_function_combine(initial_state, node, target, 1,
                                             100)
            log.debug("distance: %f " % distance)
            distance_dict["|".join(map(str, initial_state)) + "||" +
                          "|".join(map(str, node))] = [node, distance]

    tmp_distance = -1000
    for k, d in distance_dict.items():
        if d[1] > tmp_distance:
            tmp_distance = d[1]
            result_node = d[0]
            result_value = d[1]
            result_initial_state = k
    return result_initial_state, result_node, result_value


def node_is_jump(initial, node):
    if node not in [[initial[0] + 1, initial[1]], [initial[0], initial[1] + 1],
                    [initial[0] - 1, initial[1]], [initial[0],
                                                   initial[1] - 1]]:
        return True
    else:
        return False


def choose_next_node(initial_states, nodes_list, target):
    distance_dict = {}
    result_node = []
    result_value = -1
    result_initial_state = []
    for initial_state, nodes in zip(initial_states, nodes_list):
        for node in nodes:
            log.debug("initial_state: %s / goal_state: %s " %
                      (str(initial_state), str(node)))
            h_distance = cost_function_combine(initial_state, node, target)
            log.debug("distance: %f " % h_distance)
            j_distance = goal_cost(initial_state[0], initial_state[1], node[0],
                                   node[1])
            distance_dict["|".join(map(str, initial_state)) + "||" + "|".join(
                map(str, node))] = [node, h_distance, j_distance]

    tmp_distance = 1000
    tmp_g_distance = -100
    for k, d in distance_dict.items():
        if d[1] < tmp_distance:
            # if is_jump()
            tmp_distance = d[1]
            result_node = d[0]
            tmp_g_distance = d[2]
            result_value = d[1]
            result_initial_state = k
        elif d[1] == tmp_distance and d[2] > tmp_g_distance:
            tmp_distance = d[1]
            result_node = d[0]
            tmp_g_distance = d[2]
            result_value = d[1]
            result_initial_state = k
    return result_initial_state, result_node, result_value


def check_final_status(checkerboard, target, flag):
    final_status = True
    for i in target[:]:
        if checkerboard.checkerboard[checkerboard.package_location(i)] == flag:
            pass
        else:
            final_status = False
            break
    return final_status


def change_target(current_target, target_list, chess_table):
    if chess_table.checkerboard[chess_table.package_location(
            current_target)] != 0:
        x, y = current_target
        candidate_targets = [[x - 1, y + 1], [x, y + 1], [x + 1, y],
                             [x + 1, y - 1], [x, y - 1], [x - 1, y]]
        # print("try", chess_table.checkerboard[chess_table.package_location([-5, 9])])
        # print(chess_table.checkerboard)
        for ct in candidate_targets[:]:
            try:
                if chess_table.checkerboard[chess_table.package_location(
                        ct)] != 0:
                    candidate_targets.remove(ct)
                elif ct not in target_list:
                    candidate_targets.remove(ct)
            except KeyError:
                candidate_targets.remove(ct)

        heuristic_costs = [
            heuristic_cost(ct[0], ct[1], current_target[0], current_target[1])
            for ct in candidate_targets
        ]
        return (candidate_targets[heuristic_costs.index(max(heuristic_costs))])


def write2file(data, filename):
    with open(filename, a) as f:
        f.write(str(data))


def easy_solution(FLAG,
                  FINAL_FLAG,
                  choose_next_node=choose_next_node,
                  board_size=[8, 8],
                  init_barrak=[4, 0, 4, -8, -4, -4],
                  targets=[-4, 0, -4, 4, 4, 8],
                  target=[-4, 8],
                  obstacles=[]):
    # black_list = [[-4, -4, -1, 8, 4, 5], [-8, -5, -5, 4, 1, 5], [-4, -4, -1, -1,-4,-4], ]
    checkerboard = Checkerboard(*board_size)
    init_barrak.append(FLAG)
    init = checkerboard.init_barrack(*init_barrak)
    targets.append(0)
    target_list = checkerboard.init_barrack(*targets)
    error_place = checkerboard.init_barrack(-4, -4, -1, -1, -4, -4, -1)
    log.debug("* checkerboard space count: " +
              str(checkerboard.checkerboard.values()))
    log.debug("* checkerboard: " + str(checkerboard.checkerboard))
    log.debug("* init chess count: " + str(len(init)))
    k = 0
    step_counter = 0
    for obstacle in obstacles:
        checkerboard.checkerboard[checkerboard.package_location(obstacle)] = 100
    while not check_final_status(
            checkerboard=checkerboard, target=target_list, flag=FINAL_FLAG):
        k += 1
        frontier_nodes_dict = {}
        frontier_nodes_list = []
        for i in init:
            frontier_nodes = []
            frontier(i[0], i[1], checkerboard, frontier_nodes)
            # frontier_nodes_dict["|".join(i)] = frontier_nodes
            frontier_nodes_list.append(frontier_nodes)
        the_step_result = choose_next_node(init, frontier_nodes_list, target)
        next_step = the_step_result[1]
        step_counter += 1
        # print(next_step)
        print("(" + the_step_result[0].replace("||", ");(").replace("|", ",")+")")
        result_initial_state = the_step_result[0].split("||")[0].split("|")
        checkerboard.chess_go(result_initial_state, next_step, FLAG)

        if next_step == target:
            checkerboard.checkerboard[checkerboard.package_location(
                target)] = FINAL_FLAG
            target_list.remove(target)
            if len(target_list) > 0:
                target = change_target(target, target_list, checkerboard)
            else:
                break
        log.debug("* initial state: " + str(init))
        log.debug("* frontier nodes: " + str(frontier_nodes_list))
        log.debug("* checkerboard status: %s" +
                  str(checkerboard.getChessLocationByFlag(FLAG)))
        log.debug("* next step: " + str(next_step))
        init = checkerboard.getChessLocationByFlag(FLAG)
    log.debug("final state: " + str(checkerboard.checkerboard))
    print("all steps: %d" % step_counter)


def layer_search(FLAG, FINAL_FLAG, max_layer=1):
    checkerboard = Checkerboard(8, 8)
    init = checkerboard.init_barrack(4, 0, 4, -8, -4, -4, FLAG)
    target_list = checkerboard.init_barrack(-4, 0, -4, 4, 4, 8, 0)
    target = [-4, 8]
    log.debug("* checkerboard space count: " +
              str(checkerboard.checkerboard.values()))
    log.debug("* checkerboard: " + str(checkerboard.checkerboard))
    log.debug("* init chess count: " + str(len(init)))
    print(checkerboard.checkerboard)
    k = 0
    step_counter = 0
    while not check_final_status(
            checkerboard=checkerboard, target=target_list, flag=FINAL_FLAG):
        k += 1
        steps_list = []
        frontiers = []
        layer = 0
        while layer < max_layer:
            layer += 1
            frontier_nodes_list = []

            for i in init:
                frontier_nodes = []
                frontier(i[0], i[1], checkerboard, frontier_nodes)
                frontier_nodes
                frontier_nodes_list.append(
                    [str(i) + "||" + str(n) for n in frontier_nodes])
                print(frontier_nodes_list)
            step_counter += 1
            # result_initial_state = the_step_result[0].split("||")[0].split("|")
            # checkerboard.chess_go(result_initial_state, next_step, FLAG)
            #
            # if next_step == target:
            #     checkerboard.checkerboard[checkerboard.package_location(
            #         target)] = FINAL_FLAG
            #     target_list.remove(target)
            #     if len(target_list) > 0:
            #         target = change_target(target, target_list, checkerboard)
            #     else:
            #         break
            #     print("target change: " + str(target))
            log.debug("* initial state: " + str(init))
            log.debug("* frontier nodes: " + str(frontier_nodes_list))
            log.debug("* checkerboard status: %s" +
                      str(checkerboard.getChessLocationByFlag(FLAG)))
            # log.debug("* next step: " + str(next_step))
    log.debug("final state: " + str(checkerboard.checkerboard))
    print("all steps: %d" % step_counter)


if __name__ == "__main__":
    # tmp_chessboard = Checkerboard(8,8)
    # GOOD_SEARCH_PLACE = tmp_chessboard.init_barrack(-4, -4, 8, 8, -4, -4, 0) + tmp_chessboard.init_barrack(-8, 4, 4, 4, -8, 4, 0)
    # tmp_set = set(GOOD_SEARCH_PLACE)
    # GOOD_SEARCH_PLACE.remove(list(tmp_set))
    # print(GOOD_SEARCH_PLACE)
    FLAG = 1
    FINAL_FLAG = 2
    RESULT_FILE = "results.txt"
    #Q1
    print("Question1: ")
    print("=======================================")

    easy_solution(FLAG=FLAG, FINAL_FLAG=FINAL_FLAG)

    print("Question1 end")
    print("=======================================\n")


    # Q2
    print("Question2: ")
    print("=======================================")

    easy_solution(
        FLAG=FLAG,
        FINAL_FLAG=FINAL_FLAG,
        choose_next_node=choose_next_node,
        board_size=[8, 8],
        init_barrak=[4, 0, 4, -8, -4, -4],
        targets=[-4, -8, -4, 0, 4, 4],
        target=[-8, 4])

    print("Question2 end")
    print("=======================================\n")
    # Q3
    print("Question3: ")
    print("=======================================")

    obstacles = []
    with open("obstacle.txt", "r") as f:
        for i in f.readlines():
            obstacles.append(map(int,i.replace("\n","")[1:-1].split(",")))
    print("obstacles: " + str(obstacles))
    easy_solution(FLAG=FLAG, FINAL_FLAG=FINAL_FLAG,
                  board_size=[8, 8],
                  init_barrak=[4, 0, 4, -8, -4, -4],
                  targets=[-4, 0, -4, 4, 4, 8],
                  target=[-4, 8],
                  obstacles=obstacles)
