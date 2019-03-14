from nose.tools import *
from kazookid import Substitute

from prompt import Date, NotADate

def test_date():
    # Arrange
    import datetime
    input_string = '13.03.2019'
    expected_date = datetime.date(2019, 3, 13)

    # System under Test
    requirement = Date()

    # Act
    date = requirement.meet(input_string)

    # Assert
    assert_equal(date, expected_date)

@raises(NotADate)
def test_bad_date():
    # Arrange
    import datetime
    input_string = '03.13.2019'
    expected_date = datetime.date(2019, 3, 13)

    # System under Test
    requirement = Date()

    # Act
    requirement.meet(input_string)

    # Assert: Raises

