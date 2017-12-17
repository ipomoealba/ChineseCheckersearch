#!/usr/bin/env python
# -*- coding: utf-8 -*-


class checker_node(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set_next_node(self, next_node):
        self.next_node = next_node
