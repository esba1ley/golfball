Golf Ball Simulation
====================

.. inclusion-marker-short-desc-start

`golfball <https://github.com/esba1ley/golfball>`_ is
a Projectile Simulation including the "Drag Crisis" with selectable surface
feature size.  The simulation has its own 1976 Standard Atmosphere model to
explore variation in performance with altitude relative to mean sea level.

.. inclusion-marker-short-desc-end

Documentation
=============

Full documentation is `on the GitHub Pages site for this repository <https://github.com/pages/esba1ley/golfball/_build/html/index.html>`_.

.. inclusion-marker-installation-start

Installation
============

Install Dependencies
--------------------

To install the golfball model, you'll need a python installation with the
PyPA/PyPI *pip* tool installed, as well as the *make* command line tool. If you
don't want *pip* to install golfball's dependencies, use your Python package
manager of choice (e.g. *conda*) to automatically install the following
dependencies:

- ruamel.yaml
- pytables
- numpy
- scipy
- pandas

To install the golfball model for use in your python system, make sure you
have the proper virtualenv or conda env active (if you don't know what those
are, don't sweat it), and do the following:

.. code-block:: bash

  $ git clone https://github.com/esba1ley/golfball

or if you have ssh keys set up with GitHub:

.. code-block:: bash

  $ git clone git@github.com:esba1ley/golfball.git

Then:

.. code-block:: bash
  
  $ cd golfball
  $ make install

Pip will automatically install any dependencies from the list above if you
don't have them in your environment already.

.. inclusion-marker-installation-end
.. inclusion-marker-quickstart-start

Quickstart
==========

Command Line
------------

This package installs two command line tools:

- **gball**: the simulation itself

- **yaml2results**: converts the YAML output of the sim into a
  `Dakota <https://dakota.sandia.gov>`_ results file

You can run **gball** as follows:

.. code-block:: text

  $ gball

and you'll have both the default input file and output file written to the
local directory: projectile_inputs.yml and projectile_outputs.yml,
respectively. All the parameters you can change for the simulation are
specified in the input file, which if you edit that file you can run the sim
again, and it will use the local file named 'projectile_inputs.yml'. If you
copy and or re-name the input file, you can specify a different input file as
follows (where we changed the launch angle to 10.0 degrees):

.. code-block:: text

  $ gball -i projectile_inputs_10deg.yml

The '--verbose' or '-v' option shows the configuration and the results in a
nice formatted way for the user to see what was run and what the results were:

.. code-block:: text

  $ gball -i projectile_inputs_10deg.yml -v
   Config Parameters
   ----------------
   -- out_filename   : projectile_outputs.yml
   -- traj_filename  : projectile_trajectory.h5
   -- write_traj     : False

   Time Parameters
   ----------------
   -- dt      : 0.01
   -- t_init  : 0.0
   -- t_stop  : 20.0

   Input Parameters
   ----------------
   -- D          : 0.04222
   -- eD         : 0.0125
   -- g_LL       : [0.0, 0.0, -9.81]
   -- m          : 0.0459
   -- rho_scale  : 1.0
   -- wind       : [0.0, 0.0, 0.0]

   Initial State
   ----------------
   -- angle    : 10.0
   -- pos_LL   : [0.0, 0.0, 0.0]
   -- vel_mag  : 70.0

   Quantities of Interest (QoI):
   -----------------------------
   -- Distance Travelled:   103.706223 m
   -- Max Height:             5.672940 m
   -- time @ impact:          2.130000 s


If you ever need help with the command line options, just use the '--help' or
'-h' option:

.. code-block:: text

  $ gball --help

   usage: golfball [-h] [--verbose] [--in_filename [IN_FILENAME]] [--t_init T_INIT]
                [--t_stop T_STOP] [--dt DT] [--pos_LL POS_LL POS_LL POS_LL]
                [--vel_mag VEL_MAG] [--angle ANGLE] [--m M] [--D D] [--eD ED] [--g_LL G_LL]
                [--rho_scale RHO_SCALE] [--wind WIND WIND WIND]
                [--out_filename [OUT_FILENAME]] [--write_traj] [--traj_filename TRAJ_FILENAME]

   optional arguments:
     -h, --help            show this help message and exit
     --verbose, -v         print inputs and outputs to STDOUT
     --in_filename [IN_FILENAME], -i [IN_FILENAME]
                           filename of YAML w/ inputs (default: projectile_inputs.yml)
     --t_init T_INIT       initial sim time. default: specified by input file)
     --t_stop T_STOP       simulation max time. default: specified by input file
     --dt DT               simulation time step. default: specified by input file
     --pos_LL POS_LL POS_LL POS_LL
                           initial position vector in Local Level frame. default: specified by
                           input file
     --vel_mag VEL_MAG     initial velocity magnitude. default: specified by input file
     --angle ANGLE         launch angle above horizontal. default: specified by input file
     --m M, -m M           golf ball mass. default: specified by input file
     --D D, -D D           golf ball diameter. default: specified by input file
     --eD ED               dimple size ratio. default: specified by input file
     --g_LL G_LL           gravity vector in Local Level frame. default: specified by input file
     --rho_scale RHO_SCALE
                           density scale multiplier. default: specified by input file
     --wind WIND WIND WIND
                           constant wind vector in Local Level. default: specified by input file
     --out_filename [OUT_FILENAME], -o [OUT_FILENAME]
                           name of YAML output file for QoI. default: specified by input file
     --write_traj          flag to write trajectory file. default: False
     --traj_filename TRAJ_FILENAME
                           trajectory output filename. default: specified by input file

Running in Python
-----------------

In your Python environment of choice, after installation as described above you
can run your first sim very easily via the main function, passing it a list of
arguments you'd have used at the command line:

.. code-block:: python

    from golfball.sim import Sim
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    gb_sim = Sim()
    pp.pprint(gb_sim.inputs)
    gb_sim.run()
    pp.pprint(gb_sim.qoi)


Should output

.. code-block:: text

    { 'config': { 'out_filename': 'projectile_outputs.yml',
                  'traj_filename': 'projectile_trajectory.h5',
                  'write_traj': False},
      'params': { 'D': 0.04222,
                  'eD': 0.0125,
                  'g_LL': [0.0, 0.0, -9.81],
                  'm': 0.0459,
                  'rho_scale': 1.0,
                  'wind': [0.0, 0.0, 0.0]},
      'state': {'angle': 38.0, 'pos_LL': [0.0, 0.0, 0.0], 'vel_mag': 70.0},
      'time': {'dt': 0.01, 't_init': 0.0, 't_stop': 20.0}}

    { 'max_height': 50.08844542014751,
      'max_range': 185.2417438617364,
      'time_of_flight': 6.28}


where the assigned variable output is a dictionary containing the Quantities of
Interest (QoI) with the following keys:

.. code-block:: text

    { 'max_height': 50.08844542014751,
       'max_range': 185.2417438617364,
       'time_of_flight': 6.28}

note that if you don't already have it, this example also writes a default
inputs file 'projectile_inputs.yml' and captures the outputs in the default
outputs file 'projectile_outputs.yml'.  The user can specify these files as
command line arguments passed to main().  If no input file is specified, the
default parameters will be used to create a new 'projectile_inputs.yml' if one
doesn't already exist, or use the existing file of that name if it does.

.. inclusion-marker-quickstart-end

See `documentation <https://github.com/pages/esba1ley/golfball_demo_sim/_build/html/index.html>`_ for more
detailed examples and features.


Project Links
=============

- Documentation: https://github.com/pages/esba1ley/golfball_demo_sim/_build/html/index.html
- Issues: https://github.com/esba1ley/golfball_demo_sim/issues


License
=======

Copyright Caltech/JPL, all rights reserved. See the bundled
`LICENSE <https://github.com/esba1ley/golfball_demo_sim/blob/master/LICENSE>`_ file
for more details.
