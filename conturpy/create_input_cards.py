import os


def reduce_g(num):
    g_str = f"{num:<.10G}"

    if '.' not in g_str:
        g_str += '.'

    while len(g_str) > 10:
        if 'E' in g_str:
            sp_str = g_str.split('E')
            g_str = sp_str[0][:-1] + 'E' + sp_str[1]
        else:
            g_str = g_str[:-1]

    while len(g_str) < 10:
        g_str += ' '

    return g_str


class ConturCard(object):
    def __init__(self, labels=None, values=None, widths=None, aligns=None):
        self.card_labels = [] if labels is None else labels
        self.card_values = [] if values is None else values
        self.card_widths = [] if widths is None else widths
        self.card_aligns = [] if aligns is None else aligns

    def print(self) -> str:
        aligns = self.card_aligns
        widths = self.card_widths

        if len(self.card_aligns) == 0:
            aligns = ["<" for _ in range(len(self.card_labels))]
        elif len(self.card_aligns) == 1:
            aligns = [self.card_aligns[0] for _ in range(len(self.card_labels))]

        if len(self.card_widths) == 1:
            widths = [self.card_widths[0] for _ in range(len(self.card_labels))]

        return "".join([f"{val:{aligns[idx]}{widths[idx]}}" if widths[idx] != -1 else reduce_g(val)
                        for idx, val in enumerate(self.card_values)])

    def to_dict(self):
        return dict(zip(self.card_labels, self.card_values))

    def __repr__(self):
        return self.to_dict()

    def __str__(self):
        return "".join([f"{label}: {value}\n" for label, value in zip(self.card_labels, self.card_values)])

    def __getitem__(self, label: str):
        if label in self.card_labels:
            return self.card_values[self.card_labels.index(label)]
        else:
            raise AttributeError(f"Card label {label} not found")

    def __setitem__(self, label, value):
        if label in self.card_labels:
            self.card_values[self.card_labels.index(label)] = value
        else:
            raise AttributeError(f"Card label {label} not found")


class ConturCard1(ConturCard):
    def print(self) -> str:
        return f" {self.card_values[0]:^10.10s}  {self.card_values[1]:<2d}"


class ConturSettings(object):
    def __init__(self, smooth_inviscid_contour=True, include_bl=True, bl_use_characteristics=True, use_spline=True,
                 smooth_before_spline=False):

        self._smooth_inviscid_contour = smooth_inviscid_contour
        self._include_bl = include_bl
        self._bl_use_characteristics = bl_use_characteristics
        self._use_spline = use_spline
        self._smooth_before_spline = smooth_before_spline

        self._card1 = ConturCard1(
            ["ITLE", "JD"],
            ["Title", 0],
            ["10.10s", "2d"],
            ["^", "<"])

        self._card2 = ConturCard(
            ["GAM", "AR", "ZO", "RO", "VISC", "VISM", "SFOA", "XBL"],
            [1.40, 1716.563, 1.0, 0.896, 2.26968E-8, 198.72, 0, 1000],
            [-1])

        self._card3 = ConturCard(
            ["ETAD", "RC", "FMACH", "BMACH", "CMC", "SF", "PP", "XC"],
            [60, 6.0, 0, 0, 0, -1 * 3, 0, 0],
            [-1])

        self._card4 = ConturCard(
            ["MT", "NT", "IX", "IN", "IQ", "MD", "ND", "NF", "MP", "MQ", "JB", "JX", "JC", "IT", "LR", "NX"],
            [61, 41, 0, 10, 0, 61, 69, -61, 0, 0, 1, 0, 1, 0, -25, 13],
            ["5d"]
        )

        self._cardA = ConturCard(
            ["NOUP", "NPCT", "NODO"],
            [50, 85, 50],
            ["5d"])

        self._cardB = ConturCard(
            ["PPQ", "TO", "TWT", "TWAT", "QFUN", "ALPH", "IHT", "IR", "ID", "LV"],
            [90, 1030, 540, 540, 0, 0, 0, 0, 1, 5],
            [-1, -1, -1, -1, -1, -1, "5d", "5d", "5d", "5d"])

        self._cardC = ConturCard(
            ["ETAD", "QM", "XJ"],
            [60, 0, 0],
            [-1]
        )

        self._cardD = ConturCard(
            ["XST", "XLOW", "XEND", "XINC", "BJ", "XMID", "XINC2", "CN"],
            [1000, 0, 50, 2, 0, 0, 0, 0],
            [-1])

        self._card_deck = [self._card1, self._card2, self._card3, self._card4, self._cardA, self._cardB,
                           self._cardC, self._cardD]
        self._str_fields = [card.card_labels for card in self._card_deck]

    def get_deck(self) -> str:
        card5 = None
        card6 = None
        card7 = None

        if self._smooth_inviscid_contour:
            card5 = self._cardA
        elif self._include_bl and self._bl_use_characteristics and not self._smooth_inviscid_contour:
            card5 = self._cardB
        elif self._card4["JX"] > 0 and not self._smooth_inviscid_contour:
            card5 = self._cardC
        elif self._card4["JX"] <= 0 and self._card4["JB"] <= 0 and not self._smooth_inviscid_contour:
            card5 = self._cardD

        # noinspection PyChainedComparisons
        if self._include_bl and self._bl_use_characteristics and self._smooth_inviscid_contour:
            card6 = self._cardB
        elif (self._card4["JB"] > 0 and self._card4["LV"] <= 0 and not self._smooth_inviscid_contour) or \
                self._smooth_before_spline:
            card6 = self._cardD

        if self._include_bl and not self._bl_use_characteristics and self._smooth_inviscid_contour:
            card7 = self._cardB
        elif self._smooth_inviscid_contour and self._include_bl and self._use_spline:
            card7 = self._cardD

        return "".join([
            self._card1.print() + "\n",
            self._card2.print() + "\n",
            self._card3.print() + "\n",
            self._card4.print() + "\n",
            card5.print() + "\n" if card5 is not None else "",
            card6.print() + "\n" if card6 is not None else "",
            card7.print() + "\n" if card7 is not None else "",
        ])

    def print_to_input(self, file_name=None, output_directory=None):
        file_name = 'input.txt' if file_name is None else file_name
        file_path = file_name if output_directory is None else os.path.join(output_directory, file_name)
        with open(file_path, 'w') as out_file:
            out_file.write(self.get_deck())

    def __getitem__(self, label: str):
        is_present = [label in row for row in self._str_fields]

        if not any(is_present):
            raise AttributeError(f"Card label {label} not found")

        return self._card_deck[is_present.index(True)][label]

    def __setitem__(self, label: str, value):
        is_present = [label in row for row in self._str_fields]

        if not any(is_present):
            raise AttributeError(f"Card label {label} not found")

        self._card_deck[is_present.index(True)][label] = value


if __name__ == "__main__":
    throat_radius = 0.26 / 2

    for design_mach in [4, 4.5, 5, 5.3, 5.5, 5.7, 6.0, 6.2, 6.5]:
        c = ConturSettings()

        c["ITLE"] = f"Mach {design_mach}"

        c["ETAD"] = 60
        c["RC"] = 6.0
        c["CMC"] = design_mach
        c["SF"] = throat_radius

        c["PPQ"] = 70
        c["TO"] = 1000
        c["TWT"] = 540
        c["TWAT"] = 540

        c["XLOW"] = 0
        c["XEND"] = 100
        c["XINC"] = .1

        c.print_to_input(file_name=f'm{design_mach:.1f}.txt')
