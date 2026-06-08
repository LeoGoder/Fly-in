*This project has been created as part of the 42 curriculum by lgoderne.*

# FLY-IN: Drones are interesting

## Description
Fly-In is a drone routing simulation and visualization project that models the movement of multiple drones through a network of hubs. Its goal is to efficiently find optimal, collision-free paths for all drones from a starting hub to an ending hub, considering varying connection capacities and hub restrictions. The project features an interactive 3D graphical interface to visualize the computed paths in real-time.

## Instructions
The project uses `uv` as the package manager and requires Python 3.13 or newer. 

**Installation:**
To install the necessary dependencies (such as `raylib`), simply run:
```bash
make install
```

**Execution:**
To start the application, use:
```bash
make run
```

Other available commands:
- `make debug`: Run the application with `pdb` for debugging.
- `make lint` / `make lint-strict`: Run `flake8` and `mypy` for code quality checks.
- `make clean`: Clean cache and virtual environment files.

## Resources
- [Raylib Python (Pyray) Documentation](https://electronstudio.github.io/raylib-python-cffi/)
- [Raylib Website with the example and cheatsheet](https://www.raylib.com/)
- [Bellman-Ford Algorithm Overview](https://www.youtube.com/watch?v=BCkk_RvuFdw)
- [Bellman-Ford Video of a mathematician](https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm)

**AI Usage Statement:**
AI tools (such as Gemini) were used during this project to assist with debugging edge cases in the time-space Bellman-Ford implementation, generating some of the repetitive 3D rendering boilerplate for the GUI, and constructing the skybox shader (`shader_sky.fs`).

## Algorithm Choices and Implementation Strategy
To solve the multi-agent pathfinding problem, the project implements a modified, time-space expanded **Bellman-Ford algorithm**.

- **Time-Space Routing**: Instead of standard edge costs, the algorithm tracks reservations across time and space. Both hubs and connections have capacity constraints that are reserved by drones at specific "turns". 
- **Sequential Pathfinding**: Drones are routed one by one. The algorithm calculates the shortest path for a drone while checking a global dictionary of time-space reservations (`reservation` and `connection_reservation`). If a hub or connection is full at a given time, the algorithm incorporates waiting turns until space becomes available.
- **Zone Constraints**: Different hubs have specific zones (e.g., `normal`, `blocked`, `restricted`, `priority`), which influence the traversal cost. For instance, `blocked` zones carry infinite cost, making them impassable.
- **Priority Breaking**: The algorithm resolves pathfinding ties using a priority metric, favoring hubs designated with the `priority` zone.

## Visual Representation Features
The visual representation is built using `pyray` (Raylib), providing an immersive 3D environment that greatly enhances the user experience:

- **3D Hubs and Drones**: Hubs are represented by textured, rotating 3D planet models (`.gltf`), where colors correspond to their operational zone/type. Drones are modeled as 3D spaceships traveling between hubs.
- **Real-Time Animation**: Users can use the keyboard (Left/Right Arrows) to scrub through the turns or press Enter to auto-play the simulation. The drones smoothly interpolate their positions between hubs.
- **Dynamic Camera & Skybox**: A free-moving 3D camera allows users to explore the network from any angle. The background features a dynamic skybox powered by a custom fragment shader (`shader_sky.fs`).
- **Informative On-Screen Display (OSD)**: Users can toggle an informational overlay (by pressing 'I') that displays detailed hub data (capacity, type), drone IDs, current simulation turn, and total active drones. An integrated file tree also enables quick loading of different map files.
