# progsynth_assignments
Assignments for a Program Synthesis course.

# Assignment 1
Bottom-up search and breadth-first search for solving the following problems:
* Problem 1
  * CFG: {if-then-else, less than, 1, 2, x, y}
  * Goal: {x, y, out} -> [{5, 10, 5}, {10, 5, 5}, {4, 3, 3}]
* Problem 2
  * CFG: {plus, times, if-then-else, less than, not, and, 10, x, y}
  * Goal: {x, y, out} -> [{5, 10, 5}, {10, 5, 5}, {4, 3, 4}, {3, 4, 4}]
* Problem 3
  * CFG: {plus, times, if-then-else, less than, not, and, -1, 5, x, y}
  * Goal: {x, y, out} -> [{10, 7, 17}, {4, 7, -7}, {10, 3, 13}, {1, -7, -6}, {1, 8, -8}]

# Assignment 2
Re-implementing the Probe algorithm from [this paper](https://dl.acm.org/doi/10.1145/3428295).

# Assignment 3
Synthesizing strategies for the board game [Can't Stop](https://en.wikipedia.org/wiki/Can%27t_Stop_(board_game)) based on the [Rule of 28](https://www.solitairelaboratory.com/cantstop.html).
