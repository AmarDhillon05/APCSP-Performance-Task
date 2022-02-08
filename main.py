#Imports
import pygame
'''
Authors: Lenard Lindstrom, René Dudfield, Pete Shinners, Nicholas Dudfield, Thomas Kluyver, and others
https://github.com/pygame/,  https://www.pygame.org/
'''
import numpy as np
'''
Authors: Travis Oliphant, Ivan Idris, Wes McKinney, Robert Johansson, Pearu Peterson, Marten Henric van Kerkwijik
https://github.com/numpy/numpy, https://www.numpy.org
'''

#Declaring some variables
W, H = 750, 750
CAPTION = 'Bow 3'
FPS = 60
ROTVEL = 5
SPAWN_RATE = 2.5 #seconds per enemy
rot, frame, score, en_rot, BOW_X, BOW_Y, arrow_count = np.zeros(7)
gamestate = 'start'

#Images and game objects
bg = pygame.image.load('grass.png')
bow = pygame.image.load('bow.png')
arrow = pygame.image.load("arrow.png")
arrows = [] #{'rotation', 'x', 'y'}
enemies = [] #Same dict format

#Spawning and movement functions
def spawn_arrow(ang, startx, starty):
	arr_x, arr_y = startx, starty
	arrows.append({
		'rot' : ang, 
		'x' : arr_x,
		'y' : arr_y,
		'image_path' : 'arrow.png'
	})

def move_objects(lst, vel = 5):
	for idx, o in enumerate(lst):
		ang_radians = np.pi * o['rot'] / 180
		x_delta, y_delta = np.sin(ang_radians) * vel, np.cos(ang_radians) * vel
		o['x'] = o['x'] - x_delta
		o['y'] = o['y'] - y_delta
	return lst

def render_objects(objects, WIN):
	to_remove = []
	for obj in objects:
		rot, x, y = obj['rot'], obj['x'], obj['y']
		#Handling out-of-bounds
		if x < 750 and x > 0 and y < 750 and y > 0:
			root = pygame.image.load(obj['image_path'])
			transformed = pygame.transform.rotate(root, rot)
			WIN.blit(transformed, (x, y))
		else:
			if obj in arrows:
				arrows.pop(arrows.index(obj))
			elif obj in enemies:
				enemies.pop(enemies.index(obj))

def spawn_enemy(ang, startx, starty):
	sk_dict = {
		'rot' : ang, 
		'x' : startx, 
		'y' : starty,
		'image_path' : 'enemy.png'
	}
	enemies.append(sk_dict)

#Game loop
pygame.init()
win = pygame.display.set_mode((W, H))
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()
running = True

while running:
	clock.tick(FPS) 
	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			running = False

		#Player controls for rotating and shooting
		else:
			keys = pygame.key.get_pressed()
			if keys[pygame.K_a]:
				rot += ROTVEL
			elif keys[pygame.K_d]:
				rot -= ROTVEL
			elif keys[pygame.K_SPACE] and e.type == pygame.KEYDOWN:
				spawn_arrow(rot, BOW_X, BOW_Y)
				arrow_count += 1

	#When starting
	if gamestate == 'start':
		win.blit(bg, (0, 0))
		font = pygame.font.Font('main_font.ttf', 36)
		win.blit(font.render('Press ENTER to play', True, (255, 255, 255)), (200, 300))
		if keys[pygame.K_RETURN]:
			gamestate = 'play'

	#Handling death and restarting
	elif gamestate == 'dead':
		win.blit(bg, (0, 0))
		font = pygame.font.Font('main_font.ttf', 36)
		win.blit(font.render(f'Score: {int(score)}', True, (255, 255, 255)), (200, 300))
		win.blit(font.render(f'Accuracy: {int(100 * score / arrow_count)}', True, (255, 255, 255)), (200, 350))
		win.blit(font.render('Press ENTER to replay', True, (255, 255, 255)), (200, 400))
		if keys[pygame.K_RETURN]:
			gamestate = 'play'
			arrows, enemies = [], []
			rot, frame, en_rot, score, BOW_X, BOW_Y, arrow_count = np.zeros(7)
			SPAWN_RATE = 2.5

	#The actual game
	elif gamestate == 'play':
		#Enemy spawning
		frame += 1
		if frame >= FPS * SPAWN_RATE:
			x, y = np.random.randint(1, 750), np.random.randint(1, 750)
			x_delta, y_delta = np.abs(x - BOW_X), np.abs(y - BOW_Y)
			while np.sqrt(x_delta**2 + y_delta**2) < 300:
				x, y = np.random.randint(1, 750), np.random.randint(1, 750)
				x_delta, y_delta = np.abs(x - BOW_X), np.abs(y - BOW_Y)

			#Angles done from North -> West
			theta = 180 * np.arctan(y_delta/x_delta) / np.pi
			if x < BOW_X and y < BOW_Y:
				en_rot = 270 - theta
			elif x < BOW_X and y > BOW_Y:
				en_rot = 270 + theta
			elif x > BOW_X and y < BOW_Y:
				en_rot = 90 + theta
			else:
				en_rot = 90 - theta

			spawn_enemy(180 + en_rot, x, y)
			frame = 0
			SPAWN_RATE -= 0.05

		#Handling collision and death
		for sk_idx, sk in enumerate(enemies):
			for arr_idx, arr in enumerate(arrows):
				if np.sqrt((arr['x'] - sk['x'])**2 + (sk['y']-arr['y'])**2) < 75:
					score += 1
					enemies.pop(sk_idx) 
					arrows.pop(arr_idx)
			if np.sqrt((BOW_X - sk['x'])**2 + (sk['y']-BOW_Y)**2) < 75:
				gamestate = 'dead'

		#Displaying stuff
		win.blit(bg, (0, 0))

		bow_copy = pygame.transform.rotate(bow, rot)
		rot_x, rot_y = bow_copy.get_width() / 2, bow_copy.get_height() / 2 #Based off of last width and height
		BOW_X, BOW_Y = 375 - rot_x, 375 - rot_y
		win.blit(pygame.transform.rotate(bow, rot), (BOW_X, BOW_Y))

		arrows = move_objects(arrows, 10)
		enemies = move_objects(enemies, -1.5)
		render_objects(arrows + enemies, win)
		
		#Arrow counter for how many you've hit and how many you've shot
		font = pygame.font.Font('main_font.ttf', 36)
		if arrow_count > 0:
			win.blit(font.render(f'Score: {int(score)}', True, (255, 255, 255)), (50, 20))
			win.blit(font.render(f'Accuracy: {int(score * 100 / arrow_count)}', True, (255, 255, 255)), (500, 20))

	pygame.display.update();
	