# The Melee Engine

This is an archived project that used to be private. It is only here as a curiosity and inspiration for others. But also as a warning.
I spent a lot of time building this engine and in the end it did not let me produce the game I wanted to produce. Making an engine is hard. Using one that already exists is easier.
My wisdom to you is, don't make a game engine, if what you want to make is a game. Unless you're Notch.

## What is in this repo

An engine and a game example fused together. I'd be glad for PRs that pry them apart.

The engine itself is based on OpenGL bindings as provided by pyglet. It is not a very fast engine, but it works and got some nice quirks.

## Features
 - wavefont obj files
 - There is support for animations but only through lambda functions (no GPU support yet, but could be easy to implement)
 - Basic physics (CPU) No physx support yet.
 - Raytracing supported (CPU)
 - Triangle intersection (CPU)
 - Basic Menu system
 - Hand controllers
 - Game server / client for network games (still buggy)
 

## Codebase features
 - Strategy pattern (almost) everywhere
 - Observer pattern down to the lowest level
 - SOLID with few exceptions
 - Very few if statements
 - Lighting fast test suite
 - Zen of Python has been followed
 
## Codebase smells
 - GUI lacks proper tests
 - Network lacks proper tests
 - Rendering order is a bit of a hack
