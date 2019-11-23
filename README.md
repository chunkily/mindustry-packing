# Mindustry Packing

Given an input containing a patch of ores, place 2x2 tiles on top such that each has a path to the outside and we maximize the number of patches covered while minimizing the number of 2x2 tiles.

Paths can only go in the 4 cardinal directions.

This problem is NP-hard, so good luck xD

## Sample input

Note that current algorithm requires an exit tile and that ores be minimum 2 tiles from the edges.

``` text
E.........
..........
....##....
...####...
...####...
..######..
...#####..
.....###..
......##..
..........
..........
```
