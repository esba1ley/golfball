"""Pytest regression tests for running the GolfBall Simulation."""
import os
import filecmp
import numpy as np
import pandas as pd
from ruamel.yaml import YAML


from golfball.sim import main, load_gball_h5


def test_runsim_noargs():
    """Run the sim with no arguments.

    Asserts if the results change value from the tested values used.

    Source of values:  Version of code from QMU101 test, Session 4.
        (185.24144949104283, 50.08835940145908, 2.86)

    """
    main(arg_list=['--verbose'])
    assert filecmp.cmp('projectile_inputs.yml',
                       'tests/sim/inputs/projectile_inputs_default.yml')

    yaml = YAML()

    with open('projectile_outputs.yml', 'r', encoding='utf8') as infile:
        outputs = yaml.load(infile)

    with open('tests/sim/outputs/projectile_outputs_default.yml', 'r',
              encoding='utf8') as infile:
        exp_outputs = yaml.load(infile)

    for key, val in exp_outputs.items():
        print(f'key: {key}, val: {val}, outputs[key]: {outputs[key]}')
        np.testing.assert_almost_equal(val, outputs[key], decimal=4)

    os.remove('projectile_outputs.yml')
    os.remove('projectile_inputs.yml')


def test_runsim_0deg():
    """Run the sim with argument of angle=0.0.

    Asserts if the results change value from the tested values used.

    Source of values:  Version of code from QMU101 test, Session 4.
        (103.70609947453183, 5.672934747775829, 1.01)

    """
    print(os.path.abspath(os.getcwd()))
    testargs = ['--in_filename', 'tests/sim/inputs/projectile_inputs_0deg.yml',
                '--verbose']
    main(arg_list=testargs)
    assert filecmp.cmp('projectile_outputs.yml',
                       'tests/sim/outputs/projectile_outputs_0deg.yml')
    os.remove('projectile_outputs.yml')


def test_output_traj():
    """Run the sim with argument of angle=0.0.

    Asserts if the results change value from the tested values used.

    Source of values:  Version of code from QMU101 test, Session 4.
        (103.70609947453183, 5.672934747775829, 1.01)

    """
    testargs = ['--in_filename', 'tests/sim/inputs/projectile_inputs_traj.yml',
                '--verbose']
    main(arg_list=testargs)
    traj_exp = load_gball_h5('tests/sim/outputs/projectile_trajectory.h5')
    traj = load_gball_h5('projectile_trajectory.h5')
    pd.testing.assert_frame_equal(traj, traj_exp, check_exact=False, atol=1e-5)

    os.remove('projectile_outputs.yml')
    os.remove('projectile_trajectory.h5')
