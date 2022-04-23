import numpy as np
import os
import matplotlib.pyplot as plt
from .plot_results import gen_bl_thickness_plot, gen_bl_temperature_plot, gen_noz_characteristics, \
    gen_throat_characteristics, gen_contours, gen_flow_angles, gen_flow_angles_throat


def save_table(table, directory, base_name, section_num, table_num=None):
    header = ",".join(table.headers)
    table_name_section = "" if table_num is None else f"_{table_num}"
    filename = f"{base_name}_{section_num}" + table_name_section + ".csv"
    np.savetxt(os.path.join(directory, filename), table.to_numpy(), delimiter=',', header=header)


def save_group(subsection, base_name, directory):
    for idx, individual in enumerate(subsection):
        if len(individual.tables) > 1:
            for table_num, table in enumerate(individual.tables):
                save_table(table, directory, base_name, idx, table_num)
        elif len(individual.tables) == 1:
            save_table(individual.tables[0], directory, base_name, idx)


def save_all(r, directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

    names = ['IntermediateLeftCharacteristic',
             'BoundaryLayerCalculations',
             'NozzleContour',
             'InviscidContour',
             'IntermediateRightCharacteristic',
             'UpstreamContour',
             'ThroatVelocityDistribution',
             'ThroatCharacteristic',
             'CoordinatesAndDerivatives']
    for name in names:
        subsection = [x for x in r.sections if x.class_name.replace('Contur', '') == name]
        save_group(subsection, name, directory)

    plot_functions = [gen_bl_thickness_plot, gen_bl_temperature_plot, gen_noz_characteristics,
                      gen_throat_characteristics, gen_contours, gen_flow_angles, gen_flow_angles_throat]
    plot_fun_names = ["Boundary_Layer_Thickness.png", "Boundary_Layer_Temperature.png", "Nozzle_Characteristics.png",
                      "Throat_Characteristics.png", "Contours.png", "Flow_Angles.png", "Flow_Angles_At_Throat.png"]

    for plot_fun, plot_name in zip(plot_functions, plot_fun_names):
        f, ax = plot_fun(r)
        f.savefig(os.path.join(directory, plot_name))
        plt.close()
