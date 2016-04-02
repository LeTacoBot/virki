# -*- coding: utf-8 -*-

# VIRKI
# A GAME
# 100% DISTILLED SPAGHETTI CODE

import libtcodpy as libtcod
import math as maths
import textwrap
import unicode_constants as uc
import sounds as snd
import globals as glob
import constant as const
import object as obj

#######################
# CLASSES / FUNCTIONS #
#######################

class Rect:
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
	def centre(self):
		centre_x = (self.x1 + self.x2) / 2
		centre_y = (self.y1 + self.y2) / 2
		return (centre_x, centre_y)
	def intersect(self, other):
		#Returns true if rectangle intersects another 
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
	def __init__(self, x, y, char, name, colour, blocks=False, creature=None, ai=None, item=None):
		self.x = x
		self.y = y
		self.char = char
		self.name = name
		self.colour = colour
		self.blocks = blocks
		self.creature = creature
		if self.creature:
			self.creature.owner = self
		self.ai = ai
		if self.ai:
			self.ai.owner = self
		self.item = item
		if self.item:
			self.item.owner = self
	def move(self, dx, dy):
		if not is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy
	def draw(self):
		if libtcod.map_is_in_fov(fov_map, self.x, self.y):
			libtcod.console_set_default_foreground(view, self.colour)
			libtcod.console_put_char(view, self.x, self.y, self.char, libtcod.BKGND_NONE)
	def clear(self):
		if libtcod.map_is_in_fov(fov_map, self.x, self.y):
			libtcod.console_put_char_ex(view, self.x, self.y, '.', const.colour_light_ground, const.colour_background)
	def move_towards(self, target_x, target_y):
		dx = target_x - self.x
		dy = target_y - self.y
		distance = maths.sqrt(dx ** 2 + dy ** 2)
		#Restrict to grid
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		self.move(dx, dy)
	def distance_to(self, other):
		dx = other.x - self.x
		dy = other.y - self.y
		return maths.sqrt(dx ** 2 + dy ** 2)
	def send_to_back(self):
		glob.objects.remove(self)
		glob.objects.insert(0, self)

class Item:
	def __init__(self, use_function=None, use_argument=None):
		self.use_function = use_function
		self.use_argument = use_argument
	def use(self, use_argument):
		if self.use_function is None:
			message('You can\'t think of anything to do with the  ' + self.owner.name + '.')
		else:
			if self.use_function(self.use_argument) != 'do-not-destroy':
				glob.inventory.remove(self.owner)
	def pick_up(self):
		if len(glob.inventory) >= 26:
			message('Your inventory is full!', libtcod.white)
		else:
			glob.inventory.append(self.owner)
			glob.objects.remove(self.owner)
			message('Picked up a ' + self.owner.name + ".", libtcod.white)

class Tile:
		def __init__(self, blocked, block_sight = None):
			self.blocked = blocked
			if block_sight is None: block_sight = blocked
			self.block_sight = block_sight
			self.explored = False

class Creature:
	def __init__(self, hp, defence, attack, ep=None, on_death=None, inventory=[]):
		self.max_hp = hp
		self.hp = hp
		self.defence = defence
		self.attack = attack
		self.max_ep = ep
		self.ep = ep
		self.on_death = on_death
		self.inventory = inventory
	def take_damage(self, damage):
		if damage > 0:
			self.hp -= damage
			if self.hp <= 0:
				function = self.on_death
				if function is not None:
					function(self.owner)
	def fight(self, target):
		damage = vary(self.attack) - vary(target.creature.defence)
		if damage > 0:
			message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hp!', libtcod.white)
			target.creature.take_damage(damage)
		else:
			message(self.owner.name.capitalize() + ' attacks ' + target.name + ', but it has no effect!', libtcod.white)
	def heal(self, amount):
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp

class BasicMonster:
	def take_turn(self):
		monster = self.owner
		if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
			if monster.distance_to(player) >= 2:
				monster.move_towards(player.x, player.y)
			elif player.creature.hp > 0:
				monster.creature.fight(player)

#Dungeon building functions
def create_room(room):
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			glob.map[x][y].blocked = False
			glob.map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
	for x in range(min(x1, x2), max(x1, x2) + 1):
		glob.map[x][y].blocked = False
		glob.map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
	for y in range(min(y1, y2), max(y1, y2) + 1):
		glob.map[x][y].blocked = False
		glob.map[x][y].block_sight = False

def make_dungeon():
	glob.map = [[Tile(True)for y in range(const.MAP_HEIGHT)] for x in range(const.MAP_WIDTH) ]
	rooms = []
	num_rooms = 0
	for i in range(const.MAX_ROOMS):
		w = libtcod.random_get_int(0, const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE)
		h = libtcod.random_get_int(0, const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE)
		x = libtcod.random_get_int(0, 0, const.MAP_WIDTH - w - 1)
		y = libtcod.random_get_int(0, 0, const.MAP_HEIGHT - h - 1)
		new_room = Rect(x, y, w, h)
		failed = False
		for other_room in rooms:
			if new_room.intersect(other_room):
				failed = True
				break
		if not failed:
			create_room(new_room)
			place_objects(new_room)
			(new_x, new_y) = new_room.centre()
			if const.DEBUG == True:
				room_no = Object(new_x, new_y, chr(65+num_rooms), 'room number', libtcod.white)
				objects.insert(0, room_no)
			if num_rooms == 0:
				#First room only
				player.x = new_x
				player.y = new_y
			else:
				#All other rooms
				(prev_x, prev_y) = rooms[num_rooms-1].centre()
				if libtcod.random_get_int(0, 0, 1) == 1:
					create_h_tunnel(prev_x, new_x, prev_y)
					create_v_tunnel(prev_y, new_y, new_x)
				else:
					create_v_tunnel(prev_y, new_y, prev_x)
					create_h_tunnel(prev_x, new_x, new_y)
			rooms.append(new_room)
			num_rooms += 1

def menu(header, options, width):
	if len(options) > 26:
		raise ValueError('Cannot have a menu with over 26 options.')
	header_height = libtcod.console_get_height_rect(view, 0, 0, width, const.SCREEN_HEIGHT, header)
	height = len(options) + header_height
	window = libtcod.console_new(width, height)
	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
	y = header_height
	letter_index = ord('a')
	for option_text in options:
			text = "(" + chr(letter_index) + ') ' + option_text
			libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
			y += 1
			letter_index += 1
	x = const.SCREEN_WIDTH/2 - width/2
	y = const.SCREEN_HEIGHT/2 - height/2
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
	libtcod.console_flush()
	key = libtcod.console_wait_for_keypress(True)
	index = key.c - ord('a')
	if index >= 0 and index < len(options): return index
	return None

def inventory_menu(header):
	if len(glob.inventory) == 0:
		options = ['Inventory is empty.']
	else:
		options = [item.name for item in glob.inventory]
	index = menu(header, options, const.INVENTORY_WIDTH)
	if index is None or len(glob.inventory) == 0:
		return None
	return glob.inventory[index].item

def is_blocked(x, y):
	if glob.map[x][y].blocked:
		return True
	for object in glob.objects:
			if object.blocks and object.x == x and object.y == y:
				return True
	return False

def heal_player(amount):
	if player.creature.hp == player.creature.max_hp:
		message('You are already at max health.', libtcod.white)
		return 'do-not-destroy'
	message('Your woulds start to heal!', libtcod.light_violet)
	player.creature.heal(vary(amount))

def render_all():
	if glob.fov_recompute:
		glob.fov_recompute = False
		libtcod.map_compute_fov(fov_map, player.x, player.y, const.TORCH_RADIUS, const.FOV_LIGHT_WALLS, const.FOV_ALGO)
		for y in range(const.MAP_HEIGHT):
			for x in range(const.MAP_WIDTH):
				visible = libtcod.map_is_in_fov(fov_map, x, y)
				wall = glob.map[x][y].block_sight
				if not visible:
					#If out of FOV
					if glob.map[x][y].explored:
						if wall:
							libtcod.console_put_char_ex(view, x, y, '#', const.colour_dark_wall, const.colour_background)
						else:
							libtcod.console_put_char_ex(view, x, y, '.', const.colour_dark_ground, const.colour_background)
				else:
					#If visible
					if wall:
						libtcod.console_put_char_ex(view, x, y, '#', const.colour_light_wall, const.colour_background)
					else:
						libtcod.console_put_char_ex(view, x, y, '.', const.colour_light_ground, const.colour_background)
					glob.map[x][y].explored = True
	for object in glob.objects:
		if object != player:
			object.draw()
	player.draw()
	libtcod.console_blit(view, 0, 0, const.SCREEN_WIDTH, const.SCREEN_HEIGHT, 0, 0, 0)
	#Panel
	libtcod.console_set_default_background(panel, const.colour_background)
	libtcod.console_clear(panel)
	#Log
	y = 1
	for (line, colour) in glob.game_msgs:
		libtcod.console_set_default_foreground(panel, colour)
		libtcod.console_print_ex(panel, const.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
		y += 1
	#GUI
	render_bar(1, 1, const.BAR_WIDTH, 'HP', player.creature.hp, player.creature.max_hp, libtcod.dark_red, libtcod.darker_red)
	render_bar(1, 2, const.BAR_WIDTH, 'EP', player.creature.ep, player.creature.max_ep, libtcod.dark_blue, libtcod.darker_blue)
	libtcod.console_set_default_foreground(panel, libtcod.light_gray)
	libtcod.console_print_ex(panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
	#Outlines
	libtcod.console_print_frame(panel, 0, 0, const.SCREEN_WIDTH, const.PANEL_HEIGHT, clear=False, flag=libtcod.BKGND_NONE)
	#Blit that puppy!
	libtcod.console_blit(panel, 0, 0, const.SCREEN_WIDTH, const.PANEL_HEIGHT, 0, 0, const.PANEL_Y)

def render_bar(x, y, total_width, name, value, maximum, bar_colour, back_colour):
	bar_width = int(float(value) / maximum * total_width)
	#Background
	libtcod.console_set_default_background(panel, back_colour)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
	#Bar
	libtcod.console_set_default_background(panel, bar_colour)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

def player_move_or_attack(dx, dy):
	x = player.x + dx
	y = player.y + dy
	target = None
	for object in glob.objects:
		if object.creature and object.x == x and object.y == y:
			target = object
			break
	if target is not None:
		player.creature.fight(target)
	else:
		ground_sound()
		player.move(dx, dy)
		glob.fov_recompute = True

def player_death(player):
	message('You have met an untimely end...', libtcod.red)
	glob.game_state = 'dead'
	player.char = '%'
	player.colour = libtcod.dark_red

def monster_death(monster):
	message('The ' + monster.name + ' dies!', libtcod.white)
	monster.char = '%'
	monster.colour = libtcod.dark_red
	monster.blocks = False
	monster.creature = None
	monster.ai = None
	monster.name = monster.name + ' corpse'
	monster.send_to_back()

def get_names_under_mouse():
	global mouse
	(x, y) = (mouse.cx, mouse.cy)
	names = [obj.name for obj in glob.objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
	names = ", ".join(names)
	return names.capitalize()

def handle_keys():
	global key
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		return 'exit'
	if glob.game_state == 'playing':
		if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
			player_move_or_attack(0, -1)
		elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
			player_move_or_attack(0, 1)
		elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
			player_move_or_attack(-1, 0)
		elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
			player_move_or_attack(1, 0)
		elif key.vk == libtcod.KEY_KP7:
			player_move_or_attack(-1, -1)
		elif key.vk == libtcod.KEY_KP9:
			player_move_or_attack(1, -1)
		elif key.vk == libtcod.KEY_KP1:
			player_move_or_attack(-1, 1)
		elif key.vk == libtcod.KEY_KP3:
			player_move_or_attack(1, 1)
		else:
			#Other keys
			key_char = chr(key.c)
			#Pick up
			if key_char == 'g' or key_char == ',':
				for object in glob.objects:
					if object.x == player.x and object.y == player.y and object.item:
						object.item.pick_up()
						break
			if key_char == 'i':
				chosen_item = inventory_menu('Press a key to use an item, or any other key to exit.\n')
				if chosen_item is not None:
					chosen_item.use(chosen_item.use_argument)
			return 'didnt-take-turn'

def vary(number):
	return int(number + (number * libtcod.random_get_float(0, 0, const.VARIATION_PERCENT)) - (number * libtcod.random_get_float(0, 0, const.VARIATION_PERCENT)))

def place_objects(room):
	num_monsters = libtcod.random_get_int(0, 0, const.MAX_ROOM_MONSTERS)
	for i in range(num_monsters):
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
		if not is_blocked(x, y):
			if libtcod.random_get_int(0, 0, 100) < 80:
				creature_component = Creature(hp=10, defence=0, attack=3, on_death=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'G', 'goblin', libtcod.green, blocks=True, creature=creature_component, ai=ai_component)
			else:
				creature_component = Creature(hp=15, defence=1, attack=4, on_death=monster_death)
				ai_component = BasicMonster()
				monster = Object(x, y, 'O', 'orc', libtcod.darker_green, blocks=True, creature=creature_component, ai=ai_component)
			glob.objects.append(monster)
	num_items = libtcod.random_get_int(0, 0, const.MAX_ROOM_ITEMS)
	for i in range(num_items):
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
		if not is_blocked(x, y):
			item_component = Item(use_function=heal_player, use_argument=5)
			item = Object(x, y, '!', 'health potion', libtcod.pink, item=item_component)
			glob.objects.append(item)
			item.send_to_back()

def ground_sound():
	#A monster of a spaghetti function. Bon appetit!
	sndnum = libtcod.random_get_int(0, 1, 3)
	if sndnum == 1:
		if const.GROUND_MATERIAL == 'stone':
			snd.step_stone_1.play()
		elif const.GROUND_MATERIAL == 'dirt':
			snd.step_dirt_1.play()
		elif const.GROUND_MATERIAL == 'snow':
			snd.step_snow_1.play()
		elif const.GROUND_MATERIAL == 'wood':
			snd.step_wood_1.play()
		elif const.GROUND_MATERIAL == 'squeaky-wood':
			snd.step_squeaky_1.play()
	elif sndnum == 2:
		if const.GROUND_MATERIAL == 'stone':
			snd.step_stone_2.play()
		elif const.GROUND_MATERIAL == 'dirt':
			snd.step_dirt_2.play()
		elif const.GROUND_MATERIAL == 'snow':
			snd.step_snow_2.play()
		elif const.GROUND_MATERIAL == 'wood':
			snd.step_wood_2.play()
		elif const.GROUND_MATERIAL == 'squeaky-wood':
			snd.step_squeaky_wood_2.play()
	elif sndnum == 3:
		if const.GROUND_MATERIAL == 'stone':
			snd.step_stone_3.play()
		elif const.GROUND_MATERIAL == 'dirt':
			snd.step_dirt_3.play()
		elif GROUND_MATERIAL == 'snow':
			snd.step_snow_3.play()
		elif const.GROUND_MATERIAL == 'wood':
			snd.step_wood_3.play()
		elif const.GROUND_MATERIAL == 'squeaky-wood':
			snd.step_squeaky_wood_3.play()

def message(new_msg, colour = libtcod.white):
	#split into multiple lines, if needed
	new_msg_lines = textwrap.wrap(new_msg, const.MSG_WIDTH)
	for line in new_msg_lines:
		#If buffer is full, remove oldest message to make room
		if len(glob.game_msgs) == const.MSG_HEIGHT:
			del glob.game_msgs[0]
		glob.game_msgs.append((line, colour))

########
# INIT #
########

libtcod.console_set_custom_font('gfx/font_vcr.png', libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=32, nb_char_vertic=64)
libtcod.console_init_root(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, 'VIRKI', False)
root = libtcod.console_new(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
view = libtcod.console_new(const.VIEW_WIDTH, const.VIEW_HEIGHT)
panel = libtcod.console_new(const.SCREEN_WIDTH, const.PANEL_HEIGHT)
libtcod.sys_set_fps(const.LIMIT_FPS)

#Map stuff
creature_component = Creature(hp=30, ep=10, defence=2, attack=5, on_death=player_death)
player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, creature=creature_component)
glob.objects.append(player)
make_dungeon()
fov_map = libtcod.map_new(const.MAP_WIDTH, const.MAP_HEIGHT)
for y in range(const.MAP_HEIGHT):
	for x in range(const.MAP_WIDTH):
		libtcod.map_set_properties(fov_map, x, y, not glob.map[x][y].block_sight, not glob.map[x][y].blocked)

#Init stuff

message("WELCOME TO VIRKI! GOOD LUCK, ADVENTURER!", libtcod.green)

snd.music.queue(snd.mus_spooky_ambient)
snd.music.play()

mouse = libtcod.Mouse()
key = libtcod.Key()

#############
# MAIN LOOP #
#############

while not libtcod.console_is_window_closed():
	libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
	render_all()
	libtcod.console_flush()
	for object in glob.objects:
			object.clear()
	glob.player_action = handle_keys()
	if glob.player_action == 'exit':
		break
	if glob.game_state == 'playing' and glob.player_action != 'didnt-take-turn':
		for object in glob.objects:
			if object.ai:
				object.ai.take_turn()
