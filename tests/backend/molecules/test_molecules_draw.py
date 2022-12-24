import math
import os
import tempfile

from backend.database import Molecule, MoleculeSet, current_app
from backend.SMILES_handler.draw import draw_molecules_from_molset


def test_draw_molset(session):
    """
    :Authors:
        Simon Welker
    """
    molset = MoleculeSet()
    session.add(molset)

    # test possible issues with filename numbering of mol2svg, which left-fills the numbers with
    # zeros so all numbers have the same length
    for num_molecules in [1, 2, 9, 10, 99, 100]:
        patterns = [
            'O=C(Oc1ccccc1)NCCCC',
            'BrC=1c2c(OC(S(=O)(=O)N3C(=O)NC(=O)C3)1)cccc2',
            'S(=O)(=O)(N)c1ccc(NC2=NNC(c3ccc([N+]([O-])=O)cc3)=C2)cc1'
        ] * math.ceil(num_molecules / 3)  # approximately fit num_molecules
        patterns = patterns[:num_molecules]  # cut off leftovers to exactly fit num_molecules
        assert len(patterns) == num_molecules  # self-test

        for i, pattern in enumerate(patterns):
            molecule = Molecule(pattern=pattern, name=str(i), molset=molset)
            session.add(molecule)
        session.commit()

        with tempfile.TemporaryDirectory() as fake_outdir:
            current_app.config['STATIC_MOL2SVG_MOLECULE_SETS_PATH'] = fake_outdir

            draw_molecules_from_molset(molset)

            expected_output_path = os.path.join(fake_outdir, str(molset.id))
            assert os.path.isdir(expected_output_path)
            for molecule in molset.molecules:
                assert os.path.isfile(os.path.join(expected_output_path, f'{molecule.id}.svg'))
