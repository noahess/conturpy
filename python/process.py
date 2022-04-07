import glob
import numpy as np


def read_file(fn):
    with open(fn, 'r') as in_file:
        read_text = in_file.read()
    return read_text


def check_bad(in_str):
    bad_vals = ['NaN', 'THEORETICAL']
    return any([val in in_str for val in bad_vals])


def valid_line(x):
    if len(x) == 0:
        return False
    if 'Mach' in x:
        return False
    if 'IN' in x:
        return False
    return True


def get_shape(split_text, start_idx):
    dat_arr = [x.strip() for x in split_text[start_idx:] if valid_line(x.strip())]
    return np.vstack([np.fromstring(dat_piece, sep=' ') for dat_piece in dat_arr])


def get_all_shapes(in_files):
    shape_arr = []
    lens = []
    file_arr = []

    for file in in_files:
        split_text = read_file(file).split('\n')

        start_idx = 0
        the_length = 0
        for line_idx, line in enumerate(split_text):
            if 'COORDINATES AND DERIVATIVES' in line:
                start_idx = line_idx
                the_length = float(split_text[start_idx].split('LENGTH=')[1])
                break

        if start_idx != 0:
            shape_arr.append(get_shape(split_text, start_idx))
            lens.append(the_length)
            file_arr.append(file)

    return shape_arr, lens, file_arr


def run(dmach):
    fs = glob.glob(f'search_stream{dmach * 10:.0f}/*.txt')

    good_files = []
    for f in fs:
        in_text = read_file(f)
        if not any([check_bad(x) for x in in_text.split('\n')[-5:]]):
            good_files.append(f)

    shapes, lengths, files = get_all_shapes(good_files)

    unique_arr = []
    for idx in range(len(shapes)):
        arr = shapes[idx]
        noz_length = lengths[idx]

        if len(unique_arr) == 0:
            unique_arr.append(idx)
            continue

        this_unique = True
        for uarr_idx in unique_arr:
            uarr = shapes[uarr_idx]
            if abs(uarr[0, 0] - arr[0, 0]) > .05:
                continue
            start_point = max(uarr[0, 0], arr[0, 0])
            cx = np.linspace(start_point, start_point + noz_length, 15)

            i_u_arr = np.interp(cx, uarr[:, 0], uarr[:, 1])
            i_arr = np.interp(cx, arr[:, 0], arr[:, 1])

            if np.abs(i_u_arr - i_arr).sum() < .1 * 15:
                this_unique = False

        if this_unique and arr[0, 1] > .8 * .25:
            unique_arr.append(idx)

    for u_idx in unique_arr:
        original_f_name = files[u_idx]
        shape = shapes[u_idx]
        length = lengths[u_idx]

        mn = int(files[0].split('DM')[1].split('_')[0])

        output_file = f'complete_stream/M{mn}_{u_idx}.txt'
        # noinspection PyTypeChecker
        np.savetxt(output_file, shape, delimiter=',', header=f'Source File: {original_f_name}\n{length}')


if __name__ == '__main__':
    for dmach in [4, 4.5, 5, 5.3, 5.5, 5.7, 6.0, 6.2, 6.5]:
        run(dmach)
