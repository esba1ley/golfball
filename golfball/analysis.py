from matplotlib import pyplot as plt


def plot_traj(data, ax=None, **kwargs):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
    else:
        fig = ax.figure
    ax.plot(data['p_LL_x'], data['p_LL_y'], data['p_LL_z'], **kwargs)
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_zlabel('z (m)')
    ax.set_title('Golf ball trajectory')

    return fig, ax

if __name__ == '__main__':
    from golfball import main
    from golfball import load_gball_h5

    main(arg_list=['--verbose','--in_filename','projectile_inputs.yml'])
    data = load_gball_h5('projectile_trajectory.h5')

    fig, ax = plot_traj(data)
    fig.savefig('projectile_trajectory_xz.pdf')

    plt.show()