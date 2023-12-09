This folder contains layouts of Rooms and Corridors (current/latest version).

The idea behind them is, during a master map generation:
1. a Corridor does not attach to another Corridor
2. a Room does not attach to another Room,
which results in Rooms leading to Corridors, and Corridors to Rooms.

At this stage, they don't work with other template types, which means if you want to use Rooms + Corridors, you might want to consider specifying `/mini_ada/Minigrid/minigrid/templates/templates_4` as the only path to your layouts. It will still work if you do not, but it will lead to more time needed to generate a master map. This is due to the algorithm randomly choosing a layout among the directories you have provided, in order to add it to the master map at each step of the generational process, until the stopping criterion is met.

The previous version lives in `/mini_ada/Minigrid/minigrid/templates/templates_3`.