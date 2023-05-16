# Hexhams-Reckoning
An RPG Platformer game

Hexham’s Reckoning is an RPG platformer game where the player moves around 10 maps collecting coins and fighting enemies. The game is built using the python module “Pygame” as a framework and using additional modules to put the game together. 

The game was built over a span of 2-3 months using various sources for inspiration and development.

The main goal of the game is to reach the end of the game by progressing through maps, collecting coins and fighting/avoiding enemies. The player has 3 lives, and he/she can lose those lives through various circumstances such as colliding with enemies and falling into lava. The player also has access to fireball projectiles, which can be shot at enemies to eliminate them. Each level has an exit point through which one can progress to the next level. There are 10 levels. Once the player beats all levels, a victory screen is displayed with victory music. Conversely, if the player runs out of lives, a game over screen displays. However, if the player collects 10 coins, they receive a life as reward and get their score reset to 0.

The enemies boast a rudimentary AI which automatically starts path tracing towards the player once they enter within a certain victinity of an enemy.

There are also various obstacles present such as trees and lava which the player or enemies cannot pass through.

Throughout the duration of the game a soundtrack (not original) plays to set a tone to the game.

The game also comes with a level editor which is used to edit the various levels of the games. This level editor was mostly made using other sources for reference. It uses the python module pickle to easily change the data of level files. It has an easy-to-use GUI to edit levels with ease.

The level editor is stored inside the assets folder, which holds all the game files necessary to the game such as sprite and tile images, soundtracks, fonts etc.

Finally the game also uses a python file named “paths” to facilitate easy usage of the many path names of the game files. This file utilises the module “Paths” to easily fetch path names when called by the main file or level editor.!

[Screen Shot 2023-05-16 at 7 43 34 PM](https://github.com/deas28/Hexhams-Reckoning/assets/66839991/4c67602a-0b3d-40dc-a9d7-502a38226ad7)
[Screen Shot 2023-05-16 at 7 43 53 PM](https://github.com/deas28/Hexhams-Reckoning/assets/66839991/9e343061-5e58-429f-abb2-183ff38d3c57)
