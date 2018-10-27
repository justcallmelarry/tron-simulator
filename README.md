# tron-simulator
Based on the work done by: /u/Azgurath & /u/mpaw975

## The games
The game creates a deck of the following:
* 12 tron pieces
* 8 star effects
* 4 ancient stirrings
* 4 expedition maps
* 4 sylvan scrying
* 5 forest (could be any untapped green source)
* 2 other lands (colorless for all intents and purposes)
* 4 karn

The main to try to emulate these types of games are to make better mulliganing decisions and to see how often you can expect to have tron (with or without karn) on t3.

There are a few experimental settings to see if you should try scrying/maping for the second piece if you only have a tron piece and nothing else to do with your mana.

## Usage
```
$ python tron.py [otp] [number of emulated games]
```
otp makes the emulator run on the play, as it runs on the draw 100 000 times per defult.
