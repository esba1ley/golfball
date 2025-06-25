"""golfball is a Simple 2D Golf Ball Trajectory Simulation in Python."""

from .__version__ import __version__
from .sim import main, Sim, load_gball_h5

__all__ = ['__version__', 'main', 'Sim', 'load_gball_h5']