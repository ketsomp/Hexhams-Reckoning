from os import path
# path.join(path.dirname(path.abspath(__file__)), 'assets')
Paths = {}
Paths['Prefix'] = path.join(path.dirname(path.abspath(__file__)), 'assets')
Paths['Icon'] = 'mario.png'
Paths['SpriteRImage'] = path.join('mario_walking','mario6.png')
Paths['SpriteLImage'] = 'firemario_L.png'
Paths['Enemy1Image'] = 'goomba.png'
Paths['Music1'] = 'medieval_ost.mp3'
Paths['Projectile'] = 'fireball.png'
Paths['ProjectileSoundEffect'] = 'fireball.mp3'
Paths['ShootingSoundEffect'] = 'fireball.mp3'
Paths['GameOverSoundEffect'] = 'oof.mp3'
Paths['GameCompleteSoundEffect'] = 'game_complete_sound_effect.mp3'
Paths['Lava'] = 'lava.png'
Paths['DeadPlayer'] = 'ghost.png'
Paths['RestartButton'] = 'restart_btn.png'
Paths['StartButton'] = 'start_btn.png'
Paths['SaveButton'] = 'save_btn.png'
Paths['LoadButton'] = 'load_btn.png'
Paths['ExitButton'] = 'exit_btn.png'
Paths['Exit'] = 'dirt.png'
Paths['Coin'] = 'coin.png'
Paths['CoinSFX'] = 'coin.wav'
Paths['Background'] = 'bg.png'
Paths['Grass'] = 'grass.png'
Paths['Tree'] = 'tree.png'
Paths['MuteButton']='mute_btn.png'

for k, v in Paths.items():
    if k != 'Prefix':
        Paths[k] = path.join(Paths['Prefix'], v)
