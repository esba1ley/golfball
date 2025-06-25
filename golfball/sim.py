"""3D Golf Ball demo simulation with varying Drag Crisis and Magus Effect."""
import sys
import os
import argparse
from ruamel.yaml import YAML
import numpy as np

import pandas as pd
from scipy.integrate import odeint

from .stdAtm76 import getStandardDensity
from .stdAtm76 import getStandardTemperature, getGeopotential, getReynoldsNumber

DEFAULT_INPUT_FILE = 'projectile_inputs.yml'
# NOTE: make sure all tests referring to this file import this variable

DEFAULT_OUTPUT_FILE = 'projectile_outputs.yml'

DEFAULT_INPUTS_YAML = f"""\
# Golfball Sim Inputs
config:
  out_filename: {DEFAULT_OUTPUT_FILE}
  traj_filename: 'projectile_trajectory.h5'
  write_traj: false
time: 
  t_init: 0.0
  t_stop: 20.0
  dt: 0.01
state:
  angle: 38.0
  azimuth: 0.0
  vel_mag: 70.0
  pos_LL: [0.0, 0.0, 0.0]
  w_LL_B_LL: [0.0, 0.0, 0.0]
params:
  m: 0.0459
  D: 0.04222
  eD: 0.0125
  S: 0.000005  
  g_LL: [0.0, 0.0, -9.81]
  rho_scale: 1.0
  wind: [0.0, 0.0, 0.0]
"""


def main(arg_list=None):
    """Read in the inputs, run the sim, write out the outputs.

    Parameters
    ----------
    arg_list : list of str, optional
        List of individual commandline arguments to invoke main with. If
        omitted, the actual commandline arguments will be used.

    """
    if arg_list is None:
        arg_list = sys.argv[1:]
    args = get_args(arg_list)

    sim = Sim(args)
    sim.run()
    sim.write_outputs()


def get_args(arg_list=None):
    """Make CLI argument parser and parse arguments."""
    parser = _make_parser()
    return parser.parse_args(arg_list)


def _make_parser():
    """Define command line interface (CLI) argument parser."""
    parser = argparse.ArgumentParser()

    parser.add_argument("--verbose", "-v", action='store_true',
                        help="print inputs and outputs to STDOUT")

    parser.add_argument(
        "--in_filename", '-i',
        metavar="IN_FILENAME",
        nargs="?",
        default=None,
        help=f"filename of YAML w/ inputs (default: {DEFAULT_INPUT_FILE})",
    )

    parser.add_argument('--t_init', default=None, type=float,
                        help="initial sim time. default: specified by input"
                        " file)")
    parser.add_argument('--t_stop', default=None, type=float,
                        help="simulation max time.  default: specified by input"
                        " file")
    parser.add_argument('--dt', default=None, type=float,
                        help="simulation time step.  default: specified by"
                        " input file")
    parser.add_argument('--pos_LL', default=None, type=float, nargs=3,
                        help="initial position vector in Local Level frame."
                        "  default: specified by input file")
    parser.add_argument('--w_LL_B_LL', default=None, type=float, nargs=3,
                        help="initial angular velocity vector in Local Level"
                        " frame.  default: specified by input file")    
    parser.add_argument('--vel_mag', default=None, type=float,
                        help="initial velocity magnitude.  default: specified"
                        " by input file")
    parser.add_argument('--angle', default=None, type=float,
                        help="launch angle above horizontal.  default:"
                        " specified by input file")
    parser.add_argument('--azimuth', default=None, type=float,
                        help="launch angle about z axis.  default:"
                        " specified by input file")      
    parser.add_argument('--m', '-m', default=None, type=float,
                        help="golf ball mass.  default: specified by input"
                        " file")
    parser.add_argument('--D', '-D', default=None, type=float,
                        help="golf ball diameter.  default: specified by input"
                        " file")
    parser.add_argument('--eD', default=None, type=float,
                        help="dimple size ratio.  default: specified by input"
                        " file")
    parser.add_argument('--S', default=None, type=float,
                        help="Magnus Effect parameter.  default: specified by input file")
    parser.add_argument('--g_LL', default=None, type=float,
                        help="gravity vector in Local Level frame.  default:"
                        " specified by input file")
    parser.add_argument('--rho_scale', default=None, type=float,
                        help="density scale multiplier.  default: specified by"
                        " input file")
    parser.add_argument('--wind', default=None, type=float, nargs=3,
                        help="constant wind vector in Local Level.  default:"
                        " specified by input file")
    parser.add_argument("--out_filename", '-o', metavar="OUT_FILENAME",
                        nargs="?", default=None, help="name of YAML output file"
                        " for QoI.  default: specified by input file")
    parser.add_argument('--write_traj', action='store_true',
                        help="flag to write trajectory file.  default: False")
    parser.add_argument('--traj_filename', default=None,
                        help="trajectory output filename.  default: specified"
                        " by input file")
    return parser


CD_TABLE_FILE = os.path.join(os.path.dirname(__file__), 'cd_table.h5')
CD_TABLE = pd.read_hdf(CD_TABLE_FILE, '/cd_table')


def calc_drag_coeff(height, vel_mag, l_ref, rho, dimple_size):
    """Calcualte the Coefficient of Drag (Cd).

    Calculate Cd as a function of height, velocity magnitude,
    reference length, and density.  Note:  this assumes a
    Temperature profile from the US Standard ATM, and uses CD
    """
    temp = getStandardTemperature(getGeopotential(height, units='m'))
    reynolds_no = getReynoldsNumber(vel_mag, rho, l_ref, temp)

    drag_coeff = np.interp(reynolds_no, CD_TABLE.index.values,
                           CD_TABLE.loc[:, dimple_size].values)
    return drag_coeff, reynolds_no


class Sim():
    """The primary simulation object."""

    def __init__(self, args=None):
        self.inputs = None
        self.yaml = YAML()
        self.traj = None
        self.qoi = {}

        # Use an argparser if no args are passed in
        if args is None:
            self.args = get_args()
        else:
            self.args = args

        # if we're asking for the default input file and it doesn't exist,
        # create it.
        if self.args.in_filename is None:
            if not os.path.isfile(DEFAULT_INPUT_FILE):
                self.write_default_inputs()
            self.inputs = self.read_inputs(DEFAULT_INPUT_FILE)
        else:
            # if we specified an input file, load it
            self.inputs = self.read_inputs(self.args.in_filename)

        input_groups = self.inputs.keys()

        # pylint: disable=E1136
        # NOTE (esb): self.inputs is a dictionary with keys, read from a YAML
        #             file E1136 from pylint is not correct.
        for input_group in input_groups:
            for argname in self.inputs[input_group].keys():
                val = getattr(self.args, argname)
                if argname != 'write_traj':
                    if val is not None:
                        self.inputs[input_group][argname] = val
                else:
                    if val is True:
                        self.inputs[input_group][argname] = val
        # pylint: enable=E1136

    def write_default_inputs(self):
        """Write default parameters to the default input file."""

        default_input = self.yaml.load(DEFAULT_INPUTS_YAML)

        with open(DEFAULT_INPUT_FILE, 'w', encoding='utf8') as f_def_inp:
            self.yaml.dump(default_input, f_def_inp)

    def read_inputs(self, filename):
        """Read inputs YAML file.

        Parameters
        ----------
        filename : type
            Input YAML file.

        Raises
        ------
        FileNotFoundError :
            Raised if the specified file is not present.

        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(f'{filename}')

        with open(filename, 'r', encoding="utf8") as inputfile:
            inputs = self.yaml.load(inputfile)

        return inputs

    def write_qoi(self):
        """Write Quantities of Interest to YAML.

        Parameters
        ----------
        qoi : dict
            Quantities of Interest to write out.
        filename : str
            name of YAML output file for QoI

        """
        with open(self.inputs['config']['out_filename'], 'w',
                  encoding="utf8") as fh_in:
            self.yaml.dump(self.qoi, fh_in)

    def write_trajectories(self, filename):
        """Save full trajectory to traj_df.h5 HDF5 file.

        Parameters
        ----------
        filename : str
            Name of the output file for the trajectory HDF5.

        """
        self.traj.to_hdf(filename, '/traj_df')

    def write_outputs(self):
        """Write quantities of interest to YAML, and optional traj to HDF5."""
        # Save QoI to YAML file
        self.write_qoi()

        if self.inputs['config']['write_traj']:
            self.write_trajectories(self.inputs['config']['traj_filename'])

    def run(self):
        """Run the simulation."""
        def print_inputs(gname):
            print(f'{gname} Parameters')
            print('----------------')
            names = sorted(list(self.inputs[gname].keys()))
            max_width = max([len(name) for name in names])
            output_str = ''
            for name in names:
                output_str += (f'-- {name.ljust(max_width + 2)}: '
                               f'{self.inputs[gname][name]}\n')
            print(output_str)

        #  Print the input parameters
        if self.args.verbose:
            for input_group in self.inputs.keys():
                print_inputs(input_group)

        # pylint: disable=C0103,W0613
        # NOTE (esb): "t" argument dictated by ODE solver, despite note being
        #             used (W0613)
        # TODO: (esb) consider using better, longer variable names. (C0103)

        def x_dot(x, _, params):
            """Differential equations for ODE solver.

            x is a vector consisting of [p_x, p_y, p_z, v_x, v_y, v_z, theta_x, theta_y, theta_z, w_x, w_y, w_z]
            """
            mass = params['m']
            g = np.array(params['g_LL'])
            A = (params['D'] / 2.0)**2 * np.pi
            eD = params['eD']
            S = params['S']

            wind_rel_vel = x[3:6] - np.array(params['wind'])
            wind_vel_mag = np.linalg.norm(wind_rel_vel)
            vel_mag = np.linalg.norm(x[3:6])
            fpa = np.arctan2(x[5], np.linalg.norm(x[3:5]))
            rho = getStandardDensity(x[2], units='m') * params['rho_scale']
            l_ref = np.sqrt(4 * A / np.pi)
            Cd, Re = calc_drag_coeff(x[2], wind_vel_mag, l_ref, rho, eD)

            q_dyn = 0.5 * rho * wind_vel_mag**2
            drag_vec = -q_dyn * Cd * A * wind_rel_vel / wind_vel_mag
            magnus_vec = S * np.cross(x[9:12], wind_rel_vel)
            accel_vec = (drag_vec + magnus_vec) / mass + g 

            derivs = [x[3],  # map \dot{x} to itself
                      x[4],  # map \dot{y} to itself
                      x[5],  # map \dot{z} to itself
                      accel_vec[0],
                      accel_vec[1],
                      accel_vec[2],
                      x[9],
                      x[10],
                      x[11],
                      0.0,  # no angular acceleration modeled
                      0.0,  # no angular acceleration modeled
                      0.0]  # no angular acceleration modeled
            return derivs
        # pylint: enable=C0103,W0613

        # Initial Condition
        ang = self.inputs['state']['angle'] * np.pi / 180.
        az = self.inputs['state']['azimuth'] * np.pi / 180.
        vel_mag = self.inputs['state']['vel_mag']
        x0 = np.array(
            self.inputs["state"]["pos_LL"]
            + [np.cos(ang) * np.cos(az) * vel_mag, 
               np.cos(ang) * np.sin(az) * vel_mag,
               np.sin(ang) * vel_mag]
            + [0.0, 0.0, 0.0]
            + self.inputs["state"]["w_LL_B_LL"]
        )
        # print(f'x0: {x0}')

        # time vector
        dt = self.inputs['time']['dt']
        t_init = self.inputs['time']['t_init']
        t_stop = self.inputs['time']['t_stop']
        time = np.arange(t_init, t_stop, dt)

        # integrate the ODE
        traj = odeint(x_dot, x0, time, args=(self.inputs['params'],))

        # Trim to only be for heights above initial height
        mask_above_init_height = traj[:, 2] >= traj[0, 2]
        traj = traj[mask_above_init_height]
        time = time[mask_above_init_height]

        # Store Quantities of Interest
        rel_pos = traj[:, 0:3] - traj[0, 0:3]
        ground_dist = np.linalg.norm(traj[:, 0:2], axis=1)
        height = rel_pos[:, 2]
        max_height = height.max()
        t_at_max_h = time[height.argmax()]
        range_mag = np.linalg.norm(rel_pos, axis=1)
        max_range = range_mag.max()
        i_max_range = range_mag.argmax()
        h_at_max_range = height[i_max_range]
        t_at_max_range = time[i_max_range]
        time_of_flight = time[-1]

        self.qoi['max_height'] = float(max_height)
        # self.qoi['t_at_max_height'] = float(t_at_max_h)
        self.qoi['max_range'] = float(max_range)
        # self.qoi['t_at_max_range'] = float(t_at_max_range)
        # self.qoi['h_at_max_range'] = float(h_at_max_range)
        self.qoi['time_of_flight'] = float(time_of_flight)

        if self.args.verbose:
            print('Quantities of Interest (QoI):')
            print('-----------------------------')
            print(f"-- Distance Travelled: {self.qoi['max_range']:12.6f} m")
            print(f"-- Max Height:         {self.qoi['max_height']:12.6f} m")
            # print('-- time @ max height:  %12.6f s' %
            #       float(t_at_max_h))
            print(f'-- time @ impact:      {float(time_of_flight):12.6f} s')

        self.traj = pd.DataFrame(traj)
        self.traj.columns = ['p_LL_x', 'p_LL_y', 'p_LL_z',
                             'v_LL_x', 'v_LL_y', 'v_LL_z',
                             'theta_x', 'theta_y', 'theta_z',
                             'w_x', 'w_y', 'w_z']
        self.traj.index = time
        self.traj.index.name = 'time'


def load_gball_h5(h5_file=None):
    """Load the saved Pandas DataFrame from the specified HDF5 file."""
    return pd.read_hdf(h5_file, '/traj_df')


if __name__ == "__main__":
    main()
