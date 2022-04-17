def reduce_g(num) -> str:
    if num == 0:
        return "0         "

    g_str = f"{num:<10.10G}"

    if "." not in g_str:
        if len(g_str.strip()) > 8:
            g_str = f"{num:<10.10E}"
        else:
            g_str = (g_str.strip() + '.            ')[:10]

    if 'E' in g_str:
        txt_split = g_str.split('E')
        return 'E'.join([txt_split[0][:9 - len(txt_split[1])], txt_split[1]])
    else:
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
                 smooth_before_splind=False):

        self._smooth_inviscid_contour = smooth_inviscid_contour
        self._include_bl = include_bl
        self._bl_use_characteristics = bl_use_characteristics
        self._use_spline = use_spline
        self._smooth_before_splind = smooth_before_splind

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
            [8.67, 6.0, 0, 5.0, 0, -1 * 3, 0, 0],
            [-1])

        self._card4 = ConturCard(
            ["MT", "NT", "IX", "IN", "IQ", "MD", "ND", "NF", "MP", "MQ", "JB", "JX", "JC", "IT", "LR", "NX"],
            [41, 21, 0, 10, 0, 41, 49, -61, 0, 0, 1, 0, 10, 0, -21, 13],
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
            [1000, 46, 172, 2, 0, 0, 0, 0],
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

        if self._include_bl and self._bl_use_characteristics and self._smooth_inviscid_contour:
            card6 = self._cardB
        elif (self._card4["JB"] > 0 and self._card4["LV"] <= 0 and not self._smooth_inviscid_contour) or \
                self._smooth_before_splind:
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

    def print_to_input(self):
        with open('input.txt', 'w') as out_file:
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
    from os import replace, getcwd, mkdir
    from os.path import exists
    import subprocess
    import time

    max_time = .5
    for dmach in [4, 4.5, 5, 5.3, 5.5, 5.7, 6.0, 6.2, 6.5]:
        outdir = f'search_stream{dmach * 10:.0f}'
        if not exists(outdir):
            mkdir(outdir)

        for etad in [60]:
            for fmach in [0]:
                for bmach in [0]:
                    new_name = f'{outdir}/DM{dmach * 10:.0f}_FM_{fmach * 10:.0f}_BM_{bmach * 10:.0f}_ETAD{etad:.0f}.txt'

                    if fmach > dmach or bmach > dmach:
                        continue

                    print(f"{dmach} {etad} {fmach} {bmach}")

                    c = ConturSettings()

                    c["ITLE"] = f"Mach {dmach}"
                    c["JD"] = 0

                    c["SFOA"] = 0
                    c["XBL"] = 1000

                    c["ETAD"] = etad
                    c["RC"] = 6.0
                    c["FMACH"] = fmach
                    c["BMACH"] = bmach
                    c["CMC"] = dmach
                    c["SF"] = 0.26 / 2
                    c["PP"] = 60.0
                    c["XC"] = 0

                    c["MT"] = 61
                    c["NT"] = 41
                    c["IX"] = 0
                    c["IN"] = 10
                    c["IQ"] = 0
                    c["MD"] = 61
                    c["ND"] = 69
                    c["NF"] = -61
                    c["MP"] = 0
                    c["MQ"] = 0
                    c["JB"] = 1
                    c["JX"] = 0
                    c["JC"] = 1
                    c["IT"] = 0
                    c["LR"] = -45
                    c["NX"] = 18

                    c["NOUP"] = 50
                    c["NPCT"] = 85
                    c["NODO"] = 50

                    c["PPQ"] = 70
                    c["TO"] = 1000
                    c["TWT"] = 540
                    c["TWAT"] = 540
                    c["QFUN"] = .38
                    c["ALPH"] = 0
                    c["IHT"] = 0
                    c["IR"] = 0
                    c["ID"] = 1
                    c["LV"] = 5

                    # c["ETAD"] = 60
                    # c["QM"] = 1
                    # c["XJ"] = 1

                    c["XST"] = 1000
                    c["XLOW"] = 50
                    c["XEND"] = 80
                    c["XINC"] = .1
                    c["BJ"] = 0
                    c["XMID"] = 0
                    c["XINC2"] = 0
                    c["CN"] = 0

                    c.print_to_input()
                    time.sleep(0.05)
                    p = subprocess.Popen([r'.\contur.exe'], cwd=getcwd(), stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)

                    t = time.time()
                    while True:
                        result = p.poll()
                        if result is not None:
                            replace('output.txt', new_name)
                            break
                        elif time.time() - t > max_time:
                            p.kill()
                            print(' Killed')
                            time.sleep(.5)
                            break
                        time.sleep(.05)
