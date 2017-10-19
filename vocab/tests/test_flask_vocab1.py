
from flask_vocab import repeated

import nose    # Testing framework
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

# repeated(text, src)


def test_both_empty():
    assert repeated('', []) == False


def test_left_empty():
    assert repeated('', []) == False
    assert repeated('', ['']) == True
    assert repeated('', ['', '123', 'abc']) == True


def test_right_empty():
    assert repeated('something', []) == False


def test_simple():
    assert repeated('child', ['parent_and_child', 'child']) == True
    assert repeated('i\'m not there', ['SW']) == False
    assert repeated('', ['', '123', 'abc']) == True
    assert repeated('', ['123', 'abc']) == False
    assert repeated('something', ['something']) == True
    assert repeated('something', ['something', '123', '']) == True
    assert repeated('something', ['123', '']) == False
