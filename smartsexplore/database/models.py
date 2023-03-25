"""
Defines all relevant models for SMARTSexplore, as SQLAlchemy ORM models.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer, String, Float, UniqueConstraint


"""The SQLAlchemy declarative_base instance that all SMARTSexplore models derive from"""
Base = declarative_base()


### Molecule models ###

class MoleculeSet(Base):
    """
    A set of :class:`Molecule`, grouped together to be more easily manageable.
    Typically corresponds to a set of molecules that were uploaded together as one molecule file
    by a frontend user.
    """
    __tablename__ = 'molecule_sets'

    """The integer ID (primary key) of the molecule set."""
    id = Column(Integer, primary_key=True)
    """The Molecule instances belonging to this molecule set."""
    molecules = relationship(
        'Molecule', back_populates='molset',
        cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return f"<MoleculeSet ({self.id})>"


class Molecule(Base):
    """
    A molecule consisting of a SMILES pattern and an optional name.
    Belongs to a :class:`MoleculeSet`.
    """
    __tablename__ = 'molecules'

    """The integer ID (primary key) of the molecule."""
    id = Column(Integer, primary_key=True)
    """The SMILES pattern encoding the molecule."""
    pattern = Column(String)
    """The name of the molecule."""
    name = Column(String)
    """The ID of the MoleculeSet this molecule belongs to."""
    molset_id = Column(Integer, ForeignKey('molecule_sets.id'), nullable=False)
    """The MoleculeSet this molecule belongs to."""
    molset = relationship('MoleculeSet', foreign_keys=[molset_id], back_populates='molecules')

    def __repr__(self):
        return f"<Molecule('{self.name}', molset={self.molset_id}, pattern='{self.pattern}')>"

    def __init__(self, molset: MoleculeSet, name: str, pattern: str):
        """
        Creates a new Molecule.
        :param molset: The MoleculeSet this Molecule belongs to.
        :param name: The name of this molecule (can be empty).
        :param pattern: The SMILES pattern of this molecule.
        """
        self.molset = molset
        self.name = name
        self.pattern = pattern


### SMARTS models ###

class SMARTS(Base):
    """
    A single SMARTS consisting of its SMARTS pattern, a name, and the SMARTS library it belongs to.
    """
    __tablename__ = 'smarts'
    __table_args__ = {'extend_existing': True}

    """The integer ID (primary key) of this SMARTS."""
    id = Column(Integer, primary_key=True)
    """The name of this SMARTS."""
    name = Column(String)
    """The SMARTS pattern."""
    pattern = Column(String, nullable=False)
    """The library this SMARTS belongs to (as a string)."""
    library = Column(String, nullable=False, index=True)

    def __repr__(self):
        pattern = self.pattern if len(self.pattern) <= 20 else self.pattern[:20] + '...'
        return f"<SMARTS({self.id}, name='{self.name}', pattern='{pattern}')>"


class UndirectedEdge(Base):
    """
    An undirected edge between two :class:`SMARTS`, describing a **similarity** relationship as
    determined by SMARTScompare, along with an MCS similarity value and an SP similarity value.
    .. note::
      This class is currently unused within the larger context of the SMARTSexplore app, because
      only directed edges are delivered to the frontend and rendered.
    """
    __tablename__ = 'smarts_undirected_edges'
    __table_args__ = (
        UniqueConstraint('low_id', 'high_id', name='_unique_undirected_edge'),
    )

    """The unique ID (primary key) of this undirected edge."""
    id = Column(Integer, primary_key=True)
    """The smaller ID of the connected SMARTS. Used to ensure undirected edge uniqueness."""
    low_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)
    """The larger ID of the connected SMARTS. Used to ensure undirected edge uniqueness."""
    high_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)
    """The connected SMARTS with the smaller ID."""
    low_smarts = relationship(SMARTS, foreign_keys=[low_id])
    """The connected SMARTS with the larger ID."""
    high_smarts = relationship(SMARTS, foreign_keys=[high_id])

    """The maximum common subgraph similarity, see [Ehmki2019]_, annotated on this edge."""
    mcssim = Column(Float(), nullable=False)
    """The statistical pattern similarity, see [Ehmki2019]_, annotated on this edge."""
    spsim = Column(Float(), nullable=False)

    def __repr__(self):
        return f"<UndirectedEdge({self.low_smarts} <-> {self.high_smarts} "\
               f"@ {self.mcssim},{self.spsim}>"

    def __init__(self, low_smarts, high_smarts, mcssim, spsim):
        """
        Creates a new DirectedEdge.
        :param low_smarts: The SMARTS object this edge belongs to, having the smaller ID.
        :param high_smarts: The SMARTS object this edge belongs to, having the larger ID.
        :param mcssim: The maximum common subgraph similarity, see [Ehmki2019]_, of this edge.
        :param spsim: The statistical pattern similarity, see [Ehmki2019]_, of this edge.
        """
        if low_smarts.id is not None and high_smarts.id is not None:
            assert low_smarts.id < high_smarts.id
        self.low_smarts = low_smarts
        self.high_smarts = high_smarts
        self.mcssim = mcssim
        self.spsim = spsim


class DirectedEdge(Base):
    """
    A directed edge between two :class:`SMARTS`, describing a **subset** relationship as
    determined by SMARTScompare, along with an MCS similarity value and an SP similarity value,
    see [Ehmki2019]_.
    """
    __tablename__ = 'smarts_directed_edges'
    __table_args__ = (
        UniqueConstraint('from_id', 'to_id', name='_unique_directed_edge'),
    )

    """The unique ID (primary key) of this directed edge."""
    id = Column(Integer, primary_key=True)
    """The ID of the SMARTS this edge comes from."""
    from_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)
    """The ID of the SMARTS this edge goes to."""
    to_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)
    """The SMARTS this edge comes from."""
    from_smarts = relationship(SMARTS, foreign_keys=[from_id])
    """The SMARTS this edge goes to."""
    to_smarts = relationship(SMARTS, foreign_keys=[to_id])
    """The maximum common subgraph similarity, see [Ehmki2019]_, annotated on this edge."""
    mcssim = Column(Float(), nullable=False)
    """The statistical pattern similarity, see [Ehmki2019]_, annotated on this edge."""
    spsim = Column(Float(), nullable=False)

    def __repr__(self):
        return f"<DirectedEdge({self.from_smarts} --> {self.to_smarts} "\
               f"@ {self.mcssim},{self.spsim}>"

    def __init__(self, from_smarts: SMARTS, to_smarts: SMARTS, mcssim: float, spsim: float):
        """
        Creates a new DirectedEdge.
        :param from_smarts: The SMARTS object this edge comes from.
        :param to_smarts: The SMARTS object this edge goes to.
        :param mcssim: The maximum common subgraph similarity, see [Ehmki2019]_, of this edge.
        :param spsim: The statistical pattern similarity, see [Ehmki2019]_, of this edge.
        """
        if (from_smarts.id is not None) and (to_smarts.id is not None):
            assert from_smarts.id != to_smarts.id
        self.from_smarts = from_smarts
        self.to_smarts = to_smarts
        self.mcssim = mcssim
        self.spsim = spsim


### Models for Molecule-SMARTS matches ###

class Match(Base):
    """
    A successful match of a :class:`SMARTS` to a :class:`Molecule`.
    """
    __tablename__ = 'molecule_smarts_matches'
    __table_args__ = (
        UniqueConstraint('molecule_id', 'smarts_id', name='_unique_molecule_smarts'),
    )

    """The unique ID of this SMARTS--Molecule match."""
    id = Column(Integer, primary_key=True)
    """The ID of the molecule this match refers to."""
    molecule_id = Column(Integer, ForeignKey('molecules.id'), nullable=False)
    """The ID of the SMARTS this match refers to."""
    smarts_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)
    """The molecule this match refers to."""
    molecule = relationship(Molecule, foreign_keys=[molecule_id])
    """The SMARTS this match refers to."""
    smarts = relationship(SMARTS, foreign_keys=[smarts_id])

    def __repr__(self):
        return f"<Match({self.molecule} --> {self.smarts})>"

    def __init__(self, molecule, smarts):
        """
        Creates a new Match between a SMARTS and a Molecule.
        :param molecule: The molecule this match refers to.
        :param smarts: The SMARTS this match refers to.
        """
        self.molecule = molecule
        self.smarts = smarts