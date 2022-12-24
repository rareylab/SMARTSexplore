"""
Functions for drawing SMARTS and SMARTS-SMARTS relationships in the SMARTSViewer visual language
paradigm, see [Schomburg2010]_. Uses the ``SMARTScompareViewer`` NAOMI tool for this purpose.
"""

import functools
import os
from typing import Iterable
from pathlib import Path

from ..database import DirectedEdge, SMARTS
from bin.commands.util import run_process


def draw_one_smarts(smarts: SMARTS, viewer_path: str, output_path: str):
    """
    Draws one SMARTS as an SVG file to the output path, using SMARTScompareViewer.

    Output filename will be {smarts.id}.svg.

    :param smarts: The :class:`SMARTS` object to draw.
    :param viewer_path: The path to the SMARTScompareViewer binary.
    :param output_path: The output path to write the SVG file to.
    """
    Path(output_path).mkdir(parents=True, exist_ok=True)

    cmd = [
        viewer_path,
        *("-p 0 0 0 0 0 0 0 1 -d 300 300".split()),
        '-o', os.path.join(output_path, f'{smarts.id}.svg'),
        '-s', smarts.pattern
    ]
    return run_process(cmd)


def draw_one_smarts_subset_relation(directed_edge: DirectedEdge,
                                    viewer_path: str,
                                    output_path: str):
    """
    Draws one DirectedEdge, i.e., a subset relationship from directed_edge.from_smarts to
    directed_edge.to_smarts, as an SVG file to the output path, using SMARTScompareViewer.

    Output filename will be {directed_edge.id}.svg.

    :param directed_edge: The :class:`DirectedEdge` object to draw.
    :param viewer_path: The path to the SMARTScompareViewer binary.
    :param output_path: The output path to write the SVG file to.
    """
    Path(output_path).mkdir(parents=True, exist_ok=True)
    cmd = [
        viewer_path,
        *("-p 0 0 0 0 0 0 0 1 -d 300 300".split()),
        '-o', os.path.join(output_path, f'{directed_edge.id}.svg'),
        '-s', directed_edge.from_smarts.pattern, directed_edge.to_smarts.pattern,
        '-m3'
    ]
    return run_process(cmd)


def draw_multiple_smarts(smarts: Iterable[SMARTS], viewer_path: str, output_path: str):
    """
    Draws multiple SMARTS by parallelizing :func:`draw_one_smarts` via
    :func:`tqdm.contrib.concurrent.process_map`.

    :param smarts: An iterable of SMARTS objects to draw.
    :param viewer_path: The path to a SMARTScompareViewer binary.
    :param output_path: The output path to store the rendered SMARTS SVGs in.
    """
    from tqdm.contrib.concurrent import process_map
    return process_map(
        functools.partial(draw_one_smarts, viewer_path=viewer_path, output_path=output_path),
        smarts,
        chunksize=1,
    )


def draw_multiple_smarts_subset_relations(directed_edges: Iterable[DirectedEdge],
                                          viewer_path: str,
                                          output_path: str):
    """
    Draws multiple SMARTS subset relations by parallelizing
    :func:`draw_one_smarts_subset_relation` via :func:`tqdm.contrib.concurrent.process_map`.

    :param directed_edges: An iterable of DirectedEdge objects to draw.
    :param viewer_path: The path to a SMARTScompareViewer binary.
    :param output_path: The output path to store the rendered subset relation SVGs in.
    """
    from tqdm.contrib.concurrent import process_map
    return process_map(
        functools.partial(draw_one_smarts_subset_relation,
                          viewer_path=viewer_path, output_path=output_path),
        directed_edges,
        chunksize=1
    )
