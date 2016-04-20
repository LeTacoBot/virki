# -*- coding: utf-8 -*-

import libtcodpy as libtcod

DEBUG = False

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 40
VIEW_WIDTH = SCREEN_WIDTH
PANEL_HEIGHT = 7
VIEW_HEIGHT = SCREEN_HEIGHT - PANEL_HEIGHT
PANEL_Y = VIEW_HEIGHT
BAR_WIDTH = 20
MAP_WIDTH = VIEW_WIDTH
MAP_HEIGHT = VIEW_HEIGHT
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 2
INVENTORY_WIDTH = 50
VARIATION_PERCENT = 0.2 # Variation in slightly random stuff. (attacks, healing, etc.) Used in vary() function
LIMIT_FPS = 20 # FPS limit

#FOV
FOV_ALGO = 0 # FOV algorithm
FOV_LIGHT_WALLS = True

#Colours
colour_dark_wall = libtcod.darker_grey
colour_dark_ground = libtcod.darker_grey
colour_light_wall = libtcod.light_grey
colour_light_ground = libtcod.light_grey
colour_background = libtcod.black

#Temporarily hardcoded
GROUND_MATERIAL = 'stone' #stone, dirt, wood, snow, squeaky-wood
TORCH_RADIUS = 10
