.. _examples:

Examples
==========

.. contents::
   :local:
   :depth: 1


Specifying parameters by arguments
----------------------------------

In addition to the input file, all listed parameters can be specified/overridden
via arguments to the function:

.. code-block:: python

    from golfball.sim import Sim

    gb_sim = Sim()
    gb_sim.run()
    print(gb_sim.qoi)

produces:

.. code-block:: text

   {'max_height': 50.08844542014751, 'max_range': 185.2417438617364, 'time_of_flight': 6.28}

so Sim.qoi is a dictionary with the Quantities of Interest (QoI), or outputs
from the sim.

Similarly, you can also see what inputs were used by querying the attribute
"inputs".  Below we do this using the "PrettyPrint" module to make the
dictionary more readable:

.. code-block:: python

    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(gb_sim.inputs)

which produces:

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


All parameters and the initial state (but not the QoIs, those are outputs!)
listed in the output above can specified via an argument list to
:py:func:`golfball.sim.main`.  This is usually done to tweak something quickly
or for automated testing purposes.

*NOTE: Best practice is to edit and use input files so the user has a
re-run-able single source for a run.*


The sim also runs at the command line:

.. code-block:: text

   $ gball --verbose --angle 23.0 --vel_mag 75.0
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
   -- angle    : 23.0
   -- pos_LL   : [0.0, 0.0, 0.0]
   -- vel_mag  : 75.0

   Quantities of Interest (QoI):
   -----------------------------
   -- Distance Travelled:   171.951781 m
   -- Max Height:            25.312299 m
   -- time @ impact:          4.430000 s

or without the verbose output:

.. code-block:: text

   $ gball --angle 23.0 --vel_mag 75.0


Saving full trajectory data
---------------------------

If the user wants to save the detailed output from the ODE solver of the
trajectory, they can do so by specifying the "write_traj" boolean option.  The
user can also specify a filename for the trajectory using the "--traj_filename"
option.

.. code-block:: python

   gb_sim.write_trajectories('ang24_traj.h5')

or equivalently at the command line:

.. code-block:: text

   $ gball --write_traj --traj_filename ang24_traj.h5 --angle 24 --verbose

produces the following output:

.. code-block:: text

   Config Parameters
   ----------------
   -- out_filename   : projectile_outputs.yml
   -- traj_filename  : ang24_traj.h5
   -- write_traj     : True

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
   -- angle    : 24.0
   -- pos_LL   : [0.0, 0.0, 0.0]
   -- vel_mag  : 70.0

   Quantities of Interest (QoI):
   -----------------------------
   -- Distance Travelled:   164.399779 m
   -- Max Height:            24.850240 m
   -- time @ impact:          4.400000 s

This saves the output to an HDF5 file for re-loading using the python utility
provided:

.. code-block:: python

   from golfball.sim import load_gball_h5

   traj_df = load_gball_h5('ang24_traj.h5')

   traj_df

.. code-block:: text

             p_LL_x  p_LL_y    p_LL_z     v_LL_x  v_LL_y     v_LL_z
   time
   0.00    0.000000     0.0  0.000000  63.948182     0.0  28.471565
   0.01    0.637998     0.0  0.283565  63.651957     0.0  28.241804
   0.02    1.273050     0.0  0.564842  63.358889     0.0  28.013898
   0.03    1.905186     0.0  0.843849  63.068926     0.0  27.787817
   0.04    2.534438     0.0  1.120605  62.782016     0.0  27.563529
   ...          ...     ...       ...        ...     ...        ...
   4.36  163.379549     0.0  0.843387  25.577324     0.0 -19.655098
   4.37  163.635142     0.0  0.646483  25.541460     0.0 -19.725570
   4.38  163.890378     0.0  0.448876  25.505572     0.0 -19.795884
   4.39  164.145254     0.0  0.250566  25.469659     0.0 -19.866042
   4.40  164.399771     0.0  0.051556  25.433721     0.0 -19.936041

   [441 rows x 6 columns]

Which when plotted:

.. code-block:: python

   import matplotlib.pyplot as plt

   fig, ax = plt.subplots()

   ax.plot(np.linalg.norm(traj_df[['p_LL_x','p_LL_y']],axis=1),
                          traj_df['p_LL_z'])
   ax.grid(True)
   ax.set_xlabel('distance [m]')
   ax.set_ylabel('height [m]')

   fig.savefig('trajectory.png')

produces:

.. image:: figures/trajectory.png


Any other user loading this h5 file should realize that the data is internally
stored to be loaded by the python pandas package into a DataFrame object.  The
HDF5 file has a '/traj_df' group where that data resides.  The formatting of
that group is dictated by how Pandas likes to save its DataFrames in the default
"fixed" format.


Using golfball with Dakota
--------------------------

This simulation was written to work at the command line with text-editable YAML
input files, which can be used with Dakota via the "fork" interface.  For
example a shell script 'golfball.sh' can use the command line tools installed
with this module:

.. code-block:: text

   #!/bin/sh

   # Projectile Sim Wrapper for dakota

   # See the "Building a black box interface to Simulation Code" (section 10.3) and
   # also the "Advanced Simulation Code Interfaces" (chapter 16) in the Dakota
   # Users' Manual

   # This sript is called as the analysis_driver in dakota.in and is executed per
   # sample run by Dakota when it runs an individual job.
   #
   # It expects two inputs:
   #  $1 is specified parameters_file in dakota.in
   #  $2 is specified results_file in dakota.in


   # --------------
   # PRE-PROCESSING
   # --------------
   # Incorporate the parameters from DAKOTA (parameters.in) into the template
   # (projectile_template.yml) to produce the simulation input
   # (projectile_inputs.yml)

   dprepro $1  projectile_template.yml  projectile_inputs.yml


   # --------
   # ANALYSIS
   # --------
   # Run simulation

   gball -i projectile_inputs.yml -o projectile_outputs.yml


   # ---------------
   # POST-PROCESSING
   # ---------------
   # Process simulation outputs (projectile_outputs.yml) into the format expected
   # by Dakota (results.out)

   yaml2results projectile_outputs.yml $2

to work in conjunction with the following interface block of a dakota.in file:

.. code-block:: text

   interface
       fork
           analysis_drivers = 'golfball.sh'
           parameters_file = 'dakota_params.in'
           results_file    = 'dakota_results.out'
           work_directory directory_tag
           copy_files = 'template_files/*'
           named 'run/sample' file_save directory_save

See the examples in the test/uq_dakota for two examples of how dakota uses this
simulation.
