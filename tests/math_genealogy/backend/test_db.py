from datetime import date

import pytest

from math_genealogy.backend.db import Mathematician
from math_genealogy.backend.models import PydanticMathematician


class TestMathematicianModel:

    mathematician = Mathematician(
        id=10847,
        name="John Allen Taylor",
        school="University of North Texas",
        graduated="1991",
        thesis="Aspects of Universality In Function Iteration",
        country="UnitedStates",
        subject=None,
        math_genealogy_url="https://www.mathgenealogy.org/id.php?id=10847",
        math_sci_net_url="http://www.ams.org/mathscinet/MRAuthorID/316489",
        publications=1,
        citations=None,
    )

    pydantic_mathematician = PydanticMathematician(
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

    def test_as_dict(self):
        assert self.mathematician.as_dict == dict(
            id=10847,
            name="John Allen Taylor",
            school="University of North Texas",
            graduated="1991",
            thesis="Aspects of Universality In Function Iteration",
            country="UnitedStates",
            subject=None,
            math_genealogy_url="https://www.mathgenealogy.org/id.php?id=10847",
            math_sci_net_url="http://www.ams.org/mathscinet/MRAuthorID/316489",
            publications=1,
            citations=None,
        )

    def test_as_pydantic(self):
        assert self.mathematician.as_pydantic == self.pydantic_mathematician

    def test_from_pydantic(self):
        mathematician = Mathematician.from_pydantic(self.pydantic_mathematician)
        for field in [
            "id",
            "name",
            "school",
            "graduated",
            "thesis",
            "country",
            "subject",
            "math_genealogy_url",
            "math_sci_net_url",
            "publications",
            "citations",
        ]:
            assert getattr(mathematician, field) == getattr(self.mathematician, field)
