import logging
import os

# turn on exceptionally verbose logging!!!
logging.basicConfig(level=logging.DEBUG)

import tecplot
from tecplot.exception import *

'''
Calling tecplot.session.acquire_license() is optional.
If you do not call it, it will be called automatically for you
the first time you call any PyTecplot API.

acquire_license() may also be called manually. It will raise an exception
if Tecplot cannot be initialized. The most common reason that
Tecplot cannot be initialized is if a valid license is not found.
If you call start yourself, you can catch and recover from the
exception.

Note that calling tecplot.session.stop() will release the license acquired
when calling tecplot.session.connect().

Also note that once tecplot.session.stop() is called, the Tecplot Engine
cannot be restarted again during the current python session.
'''
try:
    tecplot.session.acquire_license()
except TecplotLicenseError:
    logging.exception('Missing or invalid license:')
except TecplotLogicError:
    # It is a logic error when acquiring license when
    # already connected to Tecplot 360 TecUtil Server
    if not tecplot.session.connected():
        raise
except TecplotError:
    logging.exception('Could not initialize pytecplot')
    exit(1)

examples_dir = tecplot.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'SpaceShip.lpk')
outfile = 'spaceship.png'

try:
    logging.info('Opening layout file: ' + infile)
    tecplot.load_layout(infile)

    logging.info('Exporting Image: ' + outfile)
    tecplot.export.save_png(outfile, 600, supersample=3)

    logging.info('Finished, no errors')

except IOError:
    logging.debug("I/O Error: Check disk space and permissions")
except TecplotSystemError:
    logging.exception('Failed to export image: ' + outfile)
finally:
    # tecplot.session.stop() may be called manually to
    # shut down Tecplot and release the license.
    # If tecplot.session.stop() is not called manually
    # it will be called automatically when the script exits.
    tecplot.session.stop()

logging.info('Done')
