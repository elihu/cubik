# Cube Renderer Project

This repository implements a simple 3D cube rendering system in Python, including classes for the cube and its individual cubies, a renderer, utility functions, and a main entry point. It demonstrates basic geometry manipulation and OpenGL rendering concepts.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Repository Structure](#repository-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation
To install the required dependencies, run:
```bash
pip install -r requirements.txt
```

## Usage
Run the main script to launch the renderer:
```bash
python main.py
```
The program will open a window displaying an interactive cube. Use mouse and keyboard controls as described in the code comments.

## Repository Structure
- `cube.py` – Defines the `Cube` class, representing a 3D cube composed of cubies.
- `cubie.py` – Implements the `Cubie` class for individual cubelets.
- `renderer.py` – Contains rendering logic using PyOpenGL and GLFW.
- `utils.py` – Utility functions used across modules.
- `main.py` – Entry point that initializes the renderer and starts the event loop.
- `config.py` – Configuration constants (e.g., window size, colors).
- `requirements.txt` – Python dependencies required to run the project.

## Contributing
Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss your ideas.

## License
This project is licensed under the Apache2.0 License – see the [LICENSE](LICENSE) file for details.
