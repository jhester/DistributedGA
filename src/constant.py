class constant_class:
	#client codes
	observercode = 1
	clientcode = 0

	#client stuff
	maxHealth = 50

	#I don't think this is used
	#please check, and delete if not used
	mapwidth = 40 
	mapheight = 40

    #a way to convert from direction to position
    #0-up  1-right 2-down 3-left 4-no move
	directionconvert = [(0,-1), (1,0), (0,1), (-1,0), (0,0)]

	#packet codes
	packet_heartbeat = 0
	packet_spawn = 1
	packet_main = 2
	packet_err = 8 #this must not be a direction!!

	#game state
	game_wait = 0
	game_main = 1
	game_spawn = 2

	#gamemaster
	game_speed = 0.8
