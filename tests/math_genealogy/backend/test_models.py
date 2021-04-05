from datetime import date

import pytest

from math_genealogy.backend.models import PydanticMathematician


@pytest.fixture(scope="module")
def pydantic_mathematician():
    return PydanticMathematician(
        id=10847,
        name="John Allen Taylor",
        school="University of North Texas",
        graduated=1991,
        thesis="Aspects of Universality In Function Iteration",
        country="UnitedStates",
        subject=None,
        math_genealogy_url="https://www.mathgenealogy.org/id.php?id=10847",
        math_sci_net_url="http://www.ams.org/mathscinet/MRAuthorID/316489",
        publications=1,
        citations=None,
    )


def test_pydantic_mathematician_datetime_fields(pydantic_mathematician):
    assert pydantic_mathematician.graduated == 1991
