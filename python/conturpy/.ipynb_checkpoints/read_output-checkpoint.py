import numpy as np

def read_param(line, find_str, ntype=float):
    numeric_vals = [".", "-", *[str(x) for x in range(10)]]
    
    substr = ''
    idx = line.find(find_str) + len(find_str) - 1
    search = True
    while search and idx < len(line):
        idx += 1
        char = line[idx]
        
        if len(substr) == 0 and char == ' ':
            pass
        elif char in numeric_vals:
            substr += char
        elif char in ['E', 'e'] and idx < len(line) - 1 and \
            (line[idx+1] in numeric_vals or line[idx+1] == '+'):
            substr += char
        elif char == '+' and idx > 0 and line[idx-1] in ['e', 'E']:
            pass
        else:
            search = False
    
    if substr != '':
        return ntype(substr)
    else:
        return None
        
def read_array(in_lines):
    non_numeric_chars = "ABCDFGHIJKLMNOPQRSTUVWXYZabcdfghijklmnopqrstuvwxyz"
    search = True
    idx = 0
    data = []
    
    while search and idx < len(in_lines) - 1:
        idx += 1
        line = in_lines[idx]
        
        if line.strip() == '':
            pass
        elif any([x in non_numeric_chars for x in line]):
            search = False
        else:
            piece = np.fromstring(line, sep=' ')
            
            if data == []:
                data = [piece]
            elif data[0].shape != piece.shape:
                search = False
            else:
                data.append(piece)
    if data:
        return np.vstack(data), idx
    else:
        return None

def _read_until_next_blank(line, idx):
    res = ""
    while idx >= 0 and (line[idx] != ' ' or (line[idx] == ' ' and res == "")):
        char = line[idx]
        res = char + res
        idx -= 1
    return res
    
def get_params(line):
    param_list = []
    for k in range(len(line)-1, -1, -1):
        char = line[k]
        if char == '=' and k > 0:
            find_str = _read_until_next_blank(line, k-1)+'='
            param_list.append((find_str[:-1].strip(), read_param(line, find_str, ntype=float)))
    return param_list
            
                        
def read_table_line(line):
    if len(line.strip()) < 1:
        return None
    
    for num in range(10):
        line = line.replace(f"{num}-", f"{num} -")
    line_sections = [section for section in line.split(' ') if section.strip() != '']
    try:
        table_line = [float(section) for section in line_sections]
    except ValueError:
        return None
    return np.array(table_line)

def identify_tables(lines):
    table_lines = [read_table_line(line) for line in lines]
    table_idx = np.zeros((len(lines), ))
    
    line1 = table_lines[0]
    line2 = table_lines[1]
    
    tables = []
    
    if line1 is not None:
        table_idx[0] == 1
        
        if line2 is not None:
            if len(line1) == len(line2):
                table_idx[1] == 1
                num_tables = 1
            else:
                table_idx[1] == 2
                num_tables = 2
        else:
            num_tables = 1
    elif line2 is not None:
        table_idx[1] == 1
        num_tables = 1
    else:
        num_tables = 0
        
    
    for kdx, line3 in enumerate(table_lines[2:]):
        idx = kdx + 2
        if line2 is not None and line3 is not None:
            if len(line2) == len(line3):
                table_idx[idx] = table_idx[idx-1]
            else:
                num_tables += 1
                table_idx[idx] = num_tables
        elif line1 is not None and line3 is not None:
            if len(line1) == len(line3):
                table_idx[idx] = table_idx[idx-2]
            else:
                pass
        elif line3 is not None:
            num_tables += 1
            table_idx[idx] = num_tables
            
        line1 = line2
        line2 = line3
    
    for table_num in range(1, num_tables+1):
        start_idx = np.argwhere(table_idx == table_num)[0][0]
        header = None
        if start_idx > 1:
            template_line = lines[start_idx]
            changes = np.argwhere(np.diff(np.array([char == ' ' for char in template_line])))
            middle_ends = changes[1::2].flatten() + 1
            text_slices = np.array([[0, *middle_ends], [*middle_ends, len(template_line)]]).T
            header = [lines[start_idx-2][text_slice[0]:text_slice[1]].strip() for text_slice in text_slices]
            table = np.vstack([table_line for idx, table_line in enumerate(table_lines) if table_idx[idx] == table_num and table_line is not None])
        tables.append((header, table))
    return tables, table_idx
    
class ConturTable(object):
    def __init__(self, data, headers=None):
        self.data = data
        
        if headers is not None:
            if len(headers) != len(self.data[0]):
                raise Exception("Data and Header length must match")
            self.headers = self.clean_headers(headers)
            
            for idx, header in enumerate(self.headers):
                setattr(self, header, self.data[:, idx])
    
    def __repr__(self):
        row_min = [max(12, len(header)+2) for header in self.headers]
        header_print = "".join([f"{s:<{row_min[idx]}s}" for idx, s in enumerate(self.headers)])
        
        if self.data.shape[0] < 10:
            data_print = "\n".join(["            " + "".join([f"{cell:<{row_min[idx]}g}" for idx, cell in enumerate(row)]) for row in self.data])
        else:
            data_print = "\n".join(["            " + "".join([f"{cell:<{row_min[idx]}g}" for idx, cell in enumerate(row)]) for row in self.data[:7]])
            data_print += "\n            ...\n"
            data_print += "\n".join(["            " + "".join([f"{cell:<{row_min[idx]}g}" for idx, cell in enumerate(row)]) for row in self.data[-3:]])
        
        return "ConturTable(" + header_print + '\n' + data_print + ")"
    
    def to_numpy(self):
        return self.data
    
    def to_pandas(self):
        import pandas as pd
        return pd.DataFrame(data=self.data, columns=self.headers)
    
    @staticmethod
    def clean_headers(headers):
        clean_headers = []
        allowable_first_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        allowable_next_chars = allowable_first_chars + "0123456789"
        disallowable_ends = ["_"]
        
        special_replace_dict = {"MACH NO.": "Mach"}
        replace_dict = {".": "_", "*": "star_", "/": "_over_", "+": "_plus_"}

        count_unnamed = 0
        
        for header in headers:
            for key in special_replace_dict:
                header = header.replace(key, special_replace_dict[key])
            
            if len(header) > 0:
                clean_header = header[0] if header[0] in allowable_first_chars else "_"
            else:
                clean_header = f"Untitled{count_unnamed}"
                count_unnamed += 1
            
            if len(header) > 1:
                for char in header[1:]:
                    if char in allowable_next_chars:
                        clean_header += char
                    elif char in replace_dict:
                        clean_header += replace_dict[char]
                    else:
                        clean_header += '_'
            
            while clean_header[-1] in disallowable_ends:
                clean_header = clean_header[:-1]
            clean_headers.append(clean_header)

        for idx in range(len(headers)):
            header = headers[idx]
            
            same_msk = np.array([x == header for x in headers])
            if np.sum(same_msk) > 1:
                for kdx in range(len(same_msk)):
                    if same_msk[kdx]:
                        headers[kdx] = ""
            
        for idx in range(len(headers)):
            header = headers[idx]
            if len(header) == 0:
                headers[idx] = f"Untitled{count_unnamed}"
                count_unnamed += 1
        
        return clean_headers

def dispatch_section(section, name):
    parsers = {
            'NOZZLE CONTOUR': parse_nozzle_contour,
            'UPSTREAM CONTOUR': parse_upstream_contour,
            'INTERMEDIATE RIGHT CHARACTERISTIC': parse_intermediate_right_characteristic,
            'INTERMEDIATE LEFT CHARACTERISTIC': parse_intermediate_left_characteristic,
            'BOUNDARY LAYER CALCULATIONS': parse_boundary_layer_calculations,
            'INVISCID CONTOUR': parse_inviscid_contour,
            'THROAT VELOCITY DISTRIBUTION': parse_throat_velocity_distribution,
            'THROAT CHARACTERISTIC': parse_throat_characteristic,
            'COORDINATES AND DERIVATIVES': parse_coordinates_and_derivatives}
    parser_list = [key for key in parsers]

    section_title = section[0].replace(name, '').strip()
    matching_keys = np.array([key in section_title for key in parser_list])
    num_matches = np.sum(matching_keys)
    
    if num_matches == 0:
        raise NotImplementedError
    elif num_matches == 1:
        matching_name = parser_list[np.argwhere(matching_keys)[0][0]]
        return parsers[matching_name](section)
    elif "FROM THROAT CHARACTERISTIC" in section_title and "INVISCID CONTOUR" in section_title:
        return parse_inviscid_contour(section)
    else:
        raise Exception("Multiple matches: parsing ambiguous")

        
class BaseConturOutput(object):
    def __init__(self, raw, parameters=None, tables=None):
        self.raw = raw
        self.parameters = parameters
        self.tables = tables
        self.class_name = "BaseConturOutput"
    
    def __repr__(self):
        return f"{self.class_name}:\n{len(self.raw):15g} lines\n{len(self.parameters):15g} parameter groups\n{len(self.tables):15g} tables"

class ConturOutput(BaseConturOutput):
    def __init__(self, raw, class_name):
        tables, table_idx = identify_tables(raw)
        parameters = []
        
        next_table = 1
        for idx, line in enumerate(raw):
            this_table = table_idx[idx]
            if this_table != 0:
                if idx == 0:
                    parameters.append([(f"Table {this_table:.0f}", )])
                elif idx > 0 and this_table == next_table:
                    parameters.append([(f"Table {this_table:.0f}", )])
                    next_table += 1
            if this_table == 0:
                possible_param = get_params(line)
                if len(possible_param) > 0:
                    parameters.append(possible_param)
                
        
        tables = [ConturTable(data, header) for header, data in tables]
        
        super().__init__(raw, parameters, tables)
        self.class_name = class_name
        
        
class ConturUpstreamContour(BaseConturOutput):
    def __init__(self, raw):
        tables, table_idx = identify_tables(raw)
        parameters = []
        
        next_table = 1
        for idx, line in enumerate(raw):
            this_table = table_idx[idx]
            if this_table != 0:
                if idx == 0:
                    parameters.append([(f"Table {this_table:.0f}", )])
                elif idx > 0 and this_table == next_table:
                    parameters.append([(f"Table {this_table:.0f}", )])
                    next_table += 1
            if this_table == 0:
                possible_param = get_params(line)
                if len(possible_param) > 0:
                    parameters.append(possible_param)
                
        tables = [ConturTable(tables[0][1], ["POINT", *tables[0][0][1:5], "POINT1"])]
        
        super().__init__(raw, parameters, tables)
        self.class_name = "ConturUpstreamContour"

        
class ConturInviscidContour(BaseConturOutput):
    def __init__(self, raw):
        tables, table_idx = identify_tables(raw)
        parameters = []
        
        next_table = 1
        for idx, line in enumerate(raw):
            this_table = table_idx[idx]
            if this_table != 0:
                if idx == 0:
                    parameters.append([(f"Table {this_table:.0f}", )])
                elif idx > 0 and this_table == next_table:
                    parameters.append([(f"Table {this_table:.0f}", )])
                    next_table += 1
            if this_table == 0:
                possible_param = get_params(line)
                if len(possible_param) > 0:
                    parameters.append(possible_param)
        
        if tables[0][1].shape[1] != len(tables[0][0]):
            header = [x.strip() for x in raw[np.argwhere(table_idx == 1)[0][0] - 2].split(' ') if x.strip() != '']
            tables = [ConturTable(tables[0][1], header)]
        else:
            tables = [ConturTable(tables[0][1], tables[0][0])]
        
        super().__init__(raw, parameters, tables)
        self.class_name = "ConturInviscidContour"
        
        
class ConturBoundaryLayerCalculations(BaseConturOutput):
    def __init__(self, raw):
        tables, table_idx = identify_tables(raw)
        parameters = []
        
        next_table = 1
        for idx, line in enumerate(raw):
            this_table = table_idx[idx]
            if this_table != 0:
                if idx == 0:
                    parameters.append([(f"Table {this_table:.0f}", )])
                elif idx > 0 and this_table == next_table:
                    parameters.append([(f"Table {this_table:.0f}", )])
                    next_table += 1
            if this_table == 0:
                possible_param = get_params(line)
                if len(possible_param) > 0:
                    parameters.append(possible_param)
                
        
        data_arr = tables[0][1]
        header_arr = tables[0][0]
        
        extra_headers = [x[0] for x in parameters[-3]]
        table_header = [*header_arr, *extra_headers]
        
        table_dat = np.zeros((data_arr.shape[0], data_arr.shape[1] + len(extra_headers)))
        table_dat[:data_arr.shape[0], :data_arr.shape[1]] = data_arr
        
        table_row_idx = 0
        warning_thrown = False
        for idx, _ in enumerate(raw):
            if table_idx[idx] == 1:
                try:
                    extra_dats = np.array([x[1] for x in self._get_next_param_group(raw, idx)])
                    table_dat[table_row_idx, data_arr.shape[1]:] = extra_dats
                    table_row_idx += 1
                except ValueError:
                    if not warning_thrown:
                        import warnings
                        warnings.warn(f"Boundary Layer: Unable to add unformatted extra CONTUR array output on line {idx}")
                        warning_thrown=True
        
        table = ConturTable(table_dat, table_header)
        
        
        super().__init__(raw, parameters, [table])
        self.class_name = "ConturBoundaryLayerCalculations"
        
    @staticmethod
    def _get_next_param_group(raw, idx):
        search = True
        while search and idx < len(raw) - 1:
            idx += 1
            params = get_params(raw[idx])
            if len(params) > 0:
                search = False
        return params
        
        
def parse_nozzle_contour(section):
    return ConturOutput(section, "ConturNozzleContour")

def parse_upstream_contour(section):
    return ConturUpstreamContour(section)

def parse_intermediate_right_characteristic(section):
    return ConturOutput(section, "ConturIntermediateRightCharacteristic")

def parse_intermediate_left_characteristic(section):
    return ConturOutput(section, "ConturIntermediateLeftCharacteristic")

def parse_boundary_layer_calculations(section):
    if 'STA' in section[5]:
        return ConturOutput(section, "ConturBoundaryLayerCalculations")
    else:
        return ConturBoundaryLayerCalculations(section)

def parse_inviscid_contour(section):
    return ConturInviscidContour(section)

def parse_throat_velocity_distribution(section):
    return ConturOutput(section, "ConturThroatVelocityDistribution")

def parse_throat_characteristic(section):
    return ConturOutput(section, "ConturThroatCharacteristic")

def parse_coordinates_and_derivatives(section):
    return ConturOutput(section, "ConturCoordinatesAndDerivatives")

def post_process(contur_results):
    coords = [x for x in contur_results if x.class_name == "ConturCoordinatesAndDerivatives"] 
    full_coords = [ConturTable(np.vstack([coord.tables[0].data for coord in coords if len(coord.tables) > 0]), coords[0].tables[0].headers)]
    full_text = [coord.raw for coord in coords]
    full_params = [x for coord in coords for x in coord.parameters]
    coord_obj = BaseConturOutput(full_text, full_params, full_coords)
    coord_obj.class_name = "ConturCoordinatesAndDerivatives"
    
    
    consolidated_results = [x for x in contur_results if x.class_name != "ConturCoordinatesAndDerivatives"]
    consolidated_results.append(coord_obj)
    
    return consolidated_results
    
def get_project_title(lines):
    return lines[0][10:20]
    
def get_project_slices(lines, title):
    section_slices = [idx for idx, line in enumerate(lines) if title in line]
    return np.vstack([section_slices, [*section_slices[1:], len(lines)]]).T

class ConturResult(object):
    def __init__(self, filename):
        with open(filename, 'r') as in_file:
            self.raw = in_file.readlines()

        self.title = get_project_title(self.raw)
        section_slices = get_project_slices(self.raw, self.title)
        
        self.sections = []
        for idx, sec in enumerate(section_slices):
            self.sections.append(dispatch_section(self.raw[sec[0]:sec[1]], self.title))
    
        self.sections = post_process(self.sections)
        self.characteristics = [x for x in self.sections if 'Characteristic' in x.class_name]
        self.coordinates = [x for x in self.sections if x.class_name == 'ConturCoordinatesAndDerivatives'][0].tables[0]
        
    def __repr__(self):
        return f"ConturResult:\n{len(self.raw):15g} raw lines\n{len(self.sections):15g} output sections"