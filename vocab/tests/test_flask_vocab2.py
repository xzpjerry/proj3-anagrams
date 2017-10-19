import config
from flask_vocab import matched
from vocab import Vocab

import nose    # Testing framework
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

# matched(text, WORDS)
CONFIG = config.configuration()
WORDS = Vocab(CONFIG.VOCAB)

def test_empty():
	assert matched('', WORDS) == False


def test_simple():
	assert matched('child',WORDS) == False
	assert matched('i\'m not there', WORDS) == False
	assert matched('has', WORDS) == True