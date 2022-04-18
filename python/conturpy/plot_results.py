import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


def subtract_bl(bl_x, bl_y, noz_x, noz_y):
    bl_y_interp_f = interp1d(bl_x, bl_y, kind='linear', bounds_error=False)
    bl_y_interp = bl_y_interp_f(noz_x)
    return noz_y - bl_y_interp


def get_noz_plot(ax=None):
    fig = None
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 4), dpi=150, tight_layout=True, facecolor='w')
    ax.set_xlabel('X [Inches]')
    ax.set_ylabel('Y [Inches]')
    ax.set_ylim([0, None])
    ax.grid()

    if fig is None:
        return ax
    else:
        return fig, ax


def line_colormap(x, y, cv, norm, colormap='jet'):
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = mplt.collections.LineCollection(segments, norm=norm, cmap=colormap)
    lc.set_array(cv)
    return lc


def gen_bl_thickness_plot(r):
    f, ax, bl_res, bl_cor, bl_x, noz_x, noz_y = prepare_bl_plot(r)

    bl_delta = bl_res.DELTA
    bl_delta_star = bl_res.DELTAstar__1
    bl_theta = bl_res.THETA_1

    f, ax = get_noz_plot()
    ax.plot(noz_x, noz_y, c='k', label='Wall Contour')
    ax.plot(noz_x, subtract_bl(bl_x, bl_delta, noz_x, noz_y), c='darkorange', label='Delta')
    ax.plot(noz_x, subtract_bl(bl_x, bl_delta_star, noz_x, noz_y), c='dodgerblue', label='Delta Star')
    ax.plot(noz_x, subtract_bl(bl_x, bl_theta, noz_x, noz_y), c='blueviolet', label='Theta')
    ax.legend()
    ax.set_title('Boundary Layer Thickness')
    return f, ax


def prepare_bl_plot(r):
    noz_geom = r.refine_coordinates(21)

    bl_res = [x for x in r.bl_calculations if 'X' in x.tables[0].headers][1].tables[0]
    bl_cor = [x for x in r.bl_calculations if 'STA_IN' in x.tables[0].headers][0].tables[0]

    bl_x = bl_cor.STA_IN
    plot_msk = noz_geom[:, 0] <= r.nozzle_length
    noz_x = noz_geom[plot_msk, 0]
    noz_y = noz_geom[plot_msk, 1]

    f, ax = get_noz_plot()

    return f, ax, bl_res, bl_cor, bl_x, noz_x, noz_y


def gen_bl_temperature_plot(r):
    f, ax, bl_res, bl_cor, bl_x, noz_x, noz_y = prepare_bl_plot(r)

    t_norm = mplt.colors.Normalize(vmin=bl_res.TE.min(), vmax=bl_res.TE.max())
    interp_wall_temp = interp1d(bl_x, bl_res.TW, kind='linear', bounds_error=False)
    interp_surf_temp = interp1d(bl_x, bl_res.TE, kind='linear', bounds_error=False)
    wall_temp_l = line_colormap(noz_x, noz_y, interp_wall_temp(noz_x), t_norm)
    surf_temp_l = line_colormap(noz_x, subtract_bl(bl_x, bl_res.DELTAstar__1, noz_x, noz_y),
                                interp_surf_temp(noz_x), t_norm)

    ax.add_collection(wall_temp_l)
    ax.add_collection(surf_temp_l)

    ax.set_xlim([noz_x.min(), noz_x.max()])
    noz_y_rng = noz_y.ptp()
    ax.set_ylim([0 - .1 * noz_y_rng, noz_y.max() + .2 * noz_y_rng])

    cbar = plt.colorbar(surf_temp_l)
    cbar.set_label('Temperature [Rankine]')
    ax.set_title('Wall and External Temperature')

    return f, ax


# noinspection DuplicatedCode
def gen_noz_characteristics(r):
    f, ax, bl_res, bl_cor, bl_x, noz_x, noz_y = prepare_bl_plot(r)
    d_mach = r.design_mach

    m_norm = mplt.colors.Normalize(vmin=1, vmax=d_mach)

    lc = None
    for char in r.characteristics:
        char_tab = char.tables[0]
        lc = line_colormap(char_tab.X_IN, char_tab.Y_IN, char_tab.Mach, m_norm)
        ax.add_collection(lc)

    ax.plot(noz_x, subtract_bl(bl_x, bl_res.DELTAstar__1, noz_x, noz_y), ls='--', c='k', label='Delta Star')
    ax.plot(noz_x, noz_y, ls='-', c='k', label='Wall')
    ax.set_xlim([noz_x.min(), noz_x.max()])
    noz_y_rng = noz_y.ptp()
    ax.set_ylim([0 - .1 * noz_y_rng, noz_y.max() + .2 * noz_y_rng])
    ax.legend()
    cbar = plt.colorbar(lc)
    cbar.set_label('Mach')

    ax.set_title('Characteristics')

    return f, ax


# noinspection DuplicatedCode
def gen_throat_characteristics(r):
    f, ax = gen_noz_characteristics(r)
    _, _, _, _, _, noz_x, noz_y = prepare_bl_plot(r)

    ax.set_xlim([noz_x.min(), noz_x.min() + 2 * noz_y.min()])
    ax.set_ylim([0, 1.5 * noz_y.min()])
    ax.set_title('Throat Characteristics')

    return f, ax


# noinspection DuplicatedCode
def gen_contours(r):
    f, ax, bl_res, bl_cor, bl_x, noz_x, noz_y = prepare_bl_plot(r)
    d_mach = r.contours[0].tables[0].Mach[0]

    m_norm = mplt.colors.Normalize(vmin=1, vmax=d_mach)

    lc = None
    for contour in r.contours:
        if len(contour.tables) > 0:
            contour_tab = contour.tables[0]
            if "X_IN" in contour_tab.headers:
                y_vals = np.zeros(contour_tab.X_IN.shape)
                if "Y_IN" in contour_tab.headers:
                    y_vals = contour_tab.Y_IN
                lc = line_colormap(contour_tab.X_IN, y_vals, contour_tab.Mach, m_norm)
                ax.add_collection(lc)

    ax.plot(noz_x, subtract_bl(bl_x, bl_res.DELTAstar__1, noz_x, noz_y), ls='--', c='k', label='Delta Star')
    ax.plot(noz_x, noz_y, ls='-', c='k', label='Wall')
    ax.set_xlim([noz_x.min(), noz_x.max()])
    noz_y_rng = noz_y.ptp()
    ax.set_ylim([0 - .1 * noz_y_rng, noz_y.max() + .2 * noz_y_rng])
    ax.legend()
    cbar = plt.colorbar(lc)
    cbar.set_label('Mach')

    ax.set_title('Contours')

    return f, ax


# noinspection DuplicatedCode
def gen_flow_angles(r, width=.0015, scale=80):
    xv = np.hstack([char.tables[0].X_IN for char in r.characteristics])
    yv = np.hstack([char.tables[0].Y_IN for char in r.characteristics])
    mn = np.hstack([char.tables[0].Mach for char in r.characteristics])
    theta_u = np.hstack([char.tables[0].FLOW_ANG__D for char in r.characteristics])
    uv = np.cos(theta_u * np.pi / 180)
    wv = np.sin(theta_u * np.pi / 180)

    f, ax, bl_res, bl_cor, bl_x, noz_x, noz_y = prepare_bl_plot(r)

    qv = ax.quiver(xv, yv, uv, wv, mn, cmap='jet', scale_units='width', width=width, scale=scale)
    ax.plot(noz_x, subtract_bl(bl_x, bl_res.DELTAstar__1, noz_x, noz_y), ls='--', c='k', label='Delta Star')
    ax.plot(noz_x, noz_y, ls='-', c='k', label='Wall')
    ax.set_xlim([noz_x.min(), noz_x.max()])
    noz_y_rng = noz_y.ptp()
    ax.set_ylim([0 - .1 * noz_y_rng, noz_y.max() + .2 * noz_y_rng])

    ax.set_title('Flow Angles')

    ax.legend()
    cbar = plt.colorbar(qv)
    cbar.set_label('Mach')

    return f, ax


# noinspection DuplicatedCode
def gen_flow_angles_throat(r, width=.0025, scale=25):
    f, ax = gen_flow_angles(r, width=width, scale=scale)
    _, _, _, _, _, noz_x, noz_y = prepare_bl_plot(r)

    ax.set_xlim([noz_x.min(), noz_x.min() + 2 * noz_y.min()])
    ax.set_ylim([0, 1.5 * noz_y.min()])
    ax.set_title('Throat Flow Angles')

    return f, ax
