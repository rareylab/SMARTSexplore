from backend.database import MoleculeSet


def test_session_is_unique_per_test_1(session):
    """
    This, together with its two identical copies, tests the ``session`` fixture by indirectly
    asserting that the session is unique per test function and indeed works on a newly created
    database each time. If that weren't so, the first assertion in at least one of these tests
    should fail, since there would be previously created MoleculeSet instances in the database,
    no matter the order in which these tests are executed.

    :Authors:
        Simon Welker
    """
    assert session.query(MoleculeSet).count() == 0  # uses MoleculeSet only as simple example model
    session.add(MoleculeSet())
    session.commit()
    assert session.query(MoleculeSet).count() == 1


# Copy the test to run three times independently overall
test_session_is_unique_per_test_2 = test_session_is_unique_per_test_1
test_session_is_unique_per_test_3 = test_session_is_unique_per_test_2
