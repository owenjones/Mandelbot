# Mandelbot
"""
Random Meowing and Such
"""
import sys, random
from threading import Timer

from ..decorators import user

t = None
target = None
noises = ["Meow", "Mrow", "Prrrrr", "Meow", "Meow", "Mrow", "Prrrrr", "Prrrrr", "Prrrrr", "Prrrrr", "Hssss"]
network = None

def initalize(bot) :
	bot.registerCommand("badkitty", (sys.modules[__name__], "stop"))
	bot.registerCommand("kitty", (sys.modules[__name__], "kitty"))
	bot.registerCommand("goodkitty", (sys.modules[__name__], "start"))

@user
def start(obj, m) :
	global network, target
	network = obj
	target = m.flags if m.flags else m.target
	obj.reply(noises[1], m)
	timer()

def kitty(obj, m) :
	global network, target
	if network and target :
		noise(False)

def noise(reset=True) :
	global noises, target, network
	n = random.randint(0, len(noises) - 1)
	n = noises[n]
	network.message(target, n)
	
	if reset :
		timer()
	
def timer() :
	var = 90 + random.randint(0, 240)
	global t
	if t :
		t.cancel()
	t = Timer(var, noise)
	t.start()

@user
def stop(obj, m) :
	obj.reply("Hsssssss", m)
	global t
	t.cancel()
