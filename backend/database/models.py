from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer, String, Float, UniqueConstraint

Base = declarative_base()


class MoleculeSet(Base):
    __tablename__ = 'molecule_sets'

    id = Column(Integer, primary_key=True)
    molecules = relationship(
        'Molecule', back_populates='molset',
        cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return f"<MoleculeSet ({self.id})>"


class Molecule(Base):
    __tablename__ = 'molecules'

    id = Column(Integer, primary_key=True)
    pattern = Column(String)
    name = Column(String)
    molset_id = Column(Integer, ForeignKey('molecule_sets.id'), nullable=False)
    molset = relationship('MoleculeSet', foreign_keys=[molset_id], back_populates='molecules')

    def __repr__(self):
        return f"<Molecule('{self.name}', molset={self.molset_id}, pattern='{self.pattern}')>"

    def __init__(self, molset: MoleculeSet, name: str, pattern: str):
        self.molset = molset
        self.name = name
        self.pattern = pattern


class SMARTS(Base):
    __tablename__ = 'smarts'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    pattern = Column(String, nullable=False)
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

    id = Column(Integer, primary_key=True)
    """The smaller ID of the connected SMARTS. Used to ensure undirected edge uniqueness."""
    low_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)
    """The larger ID of the connected SMARTS. Used to ensure undirected edge uniqueness."""
    high_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)

    low_smarts = relationship(SMARTS, foreign_keys=[low_id])
    high_smarts = relationship(SMARTS, foreign_keys=[high_id])

    mcssim = Column(Float(), nullable=False)
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
    __tablename__ = 'smarts_directed_edges'
    __table_args__ = (
        UniqueConstraint('from_id', 'to_id', name='_unique_directed_edge'),
    )

    id = Column(Integer, primary_key=True)

    from_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)
    to_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)

    from_smarts = relationship(SMARTS, foreign_keys=[from_id])
    to_smarts = relationship(SMARTS, foreign_keys=[to_id])

    mcssim = Column(Float(), nullable=False)
    spsim = Column(Float(), nullable=False)

    def __repr__(self):
        return f"<DirectedEdge({self.from_smarts} --> {self.to_smarts} "\
               f"@ {self.mcssim},{self.spsim}>"

    def __init__(self, from_smarts: SMARTS, to_smarts: SMARTS, mcssim: float, spsim: float):
        if (from_smarts.id is not None) and (to_smarts.id is not None):
            assert from_smarts.id != to_smarts.id
        self.from_smarts = from_smarts
        self.to_smarts = to_smarts
        self.mcssim = mcssim
        self.spsim = spsim


# Models for Molecule-SMARTS matches

class Match(Base):
    """
    A successful match of a :class:`SMARTS` to a :class:`Molecule`.
    """
    __tablename__ = 'molecule_smarts_matches'
    __table_args__ = (
        UniqueConstraint('molecule_id', 'smarts_id', name='_unique_molecule_smarts'),
    )

    id = Column(Integer, primary_key=True)
    molecule_id = Column(Integer, ForeignKey('molecules.id'), nullable=False)
    smarts_id = Column(Integer, ForeignKey('smarts.id'), nullable=False)

    """The molecule this match refers to."""
    molecule = relationship(Molecule, foreign_keys=[molecule_id])
    """The SMARTS this match refers to."""
    smarts = relationship(SMARTS, foreign_keys=[smarts_id])

    def __repr__(self):
        return f"<Match({self.molecule} --> {self.smarts})>"

    def __init__(self, molecule, smarts):
        self.molecule = molecule
        self.smarts = smarts


class Node(Base):
    __tablename__ = 'test_nodes'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=30), nullable=False, unique=True)


class Edge(Base):
    __tablename__ = 'test_edges'

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, ForeignKey('test_nodes.id'), nullable=False)
    to_id = Column(Integer, ForeignKey('test_nodes.id'), nullable=False)
