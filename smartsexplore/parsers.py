"""
Parsing code for file formats and program outputs
"""

valid_modes = ('Similarity', 'SubsetOfFirst', 'Identical', 'SubsetOfSecond')

def _fail():
    assert False


def parse_smartscompare(iterable):
    """
    Parses an iterable of lines of SMARTScompare output, and yields:

    * once: the SMARTScompare mode, as a string (Similarity/SubsetOfFirst/Identical/SubsetOfSecond)
    * for each pair: a 5-tuple of (line no., left name, right name, MCS similarity, SP similarity)
    """
    for i, line in enumerate(iterable):
        if i < 2:
            continue

        if i == 2:
            _, _, mode = line.rpartition(' ')
            mode = mode.strip().replace("'", "")
            if mode not in valid_modes:
                raise ValueError(f'Unknown/unimplemented mode: {mode}. Must be '
                                 f'one of [{", ".join(valid_modes)}].')
            yield mode
            continue

        # Split on ^ to separate into pieces (lpattern`ltag)^(sim`rpattern`rtag)
        left, right = line.split('|')
        # Split (lpattern`ltag) into pattern and tag
        _lpattern, ltag = left.split('`')
        # Split (sim`rpattern`rtag) into similarities, pattern, and tag
        similarities, _rpattern, rtag = right.split('`')

        # Remove whitespace & parentheses around the label
        ltag, rtag = ltag.strip()[1:-1], rtag.strip()[1:-1]
        lname_, rname_ = ltag.split(maxsplit=1), rtag.split(maxsplit=1)

        lname = lname_[0] if len(lname_) == 1 else (lname_[1] if len(lname_) == 2 else _fail())
        rname = rname_[0] if len(rname_) == 1 else (rname_[1] if len(rname_) == 2 else _fail())

        # Split the similarity string (a,b) on comma, while ignoring (a,b,[...])
        # Currently the ignored part could only be "sub", which does not give us
        # any additional information since we know the mode
        mcssim_, spsim_, *_ = similarities.split(',')
        mcssim_, spsim_ = mcssim_.strip().replace("(", ""), spsim_.strip().replace(")", "")
        # Cut off the ( and ), parse each piece as a float
        mcssim, spsim = float(mcssim_), float(spsim_)

        yield (i+1, lname, rname, mcssim, spsim)


def parse_moleculematch(iterable):
    """
    Parses an iterable of lines of output of molecules matched with SMARTS, and yields:

    * for each pair: a 2-tuple of (smartsID, moleculeID)
    """
    for line in iterable:
        linelist=line.split("\t")
        yield int(linelist[0].strip()),\
              int(linelist[1].strip())
