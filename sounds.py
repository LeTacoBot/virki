# -*- coding: utf-8 -*-

import pyglet

music = pyglet.media.Player()
music.eos_action = 'loop'

#################
# SOUND EFFECTS #
#################

### Movement ###

#Stone
step_stone_1 = pyglet.resource.media('sfx/sfx_step_stone_1.wav', streaming=False)
step_stone_2 = pyglet.resource.media('sfx/sfx_step_stone_2.wav', streaming=False)
step_stone_3 = pyglet.resource.media('sfx/sfx_step_stone_3.wav', streaming=False)
#Dirt
step_dirt_1 = pyglet.resource.media('sfx/sfx_step_dirt_1.wav', streaming=False)
step_dirt_2 = pyglet.resource.media('sfx/sfx_step_dirt_2.wav', streaming=False)
step_dirt_3 = pyglet.resource.media('sfx/sfx_step_dirt_3.wav', streaming=False)
#Snow
step_snow_1 = pyglet.resource.media('sfx/sfx_step_snow_1.wav', streaming=False)
step_snow_2 = pyglet.resource.media('sfx/sfx_step_snow_2.wav', streaming=False)
step_snow_3 = pyglet.resource.media('sfx/sfx_step_snow_3.wav', streaming=False)
#Wood
step_wood_1 = pyglet.resource.media('sfx/sfx_step_wood_1.wav', streaming=False)
step_wood_2 = pyglet.resource.media('sfx/sfx_step_wood_2.wav', streaming=False)
step_wood_3 = pyglet.resource.media('sfx/sfx_step_wood_3.wav', streaming=False)
#Squeaky Wood
step_squeaky_wood_1 = pyglet.resource.media('sfx/sfx_step_squeaky_wood_1.wav', streaming=False)
step_squeaky_wood_2 = pyglet.resource.media('sfx/sfx_step_squeaky_wood_2.wav', streaming=False)
step_squeaky_wood_3 = pyglet.resource.media('sfx/sfx_step_squeaky_wood_3.wav', streaming=False)

#########
# MUSIC #
#########

mus_spooky_ambient = pyglet.resource.media('sfx/mus_spooky_ambient.ogg')
