"""Test the 1976 Standard Atmosphere model."""

import pickle
import numpy as np

from golfball.stdAtm76 import getStandardPressure, getSpeedOfSound

PRECISION = 11

# We're using a pickle here to preserve numerical accuracy.
with open('tests/stdAtm76/pressures.pkl', 'rb') as f:
    # NOTE: this data is captured from this very routine, captured 9/1/2020.
    #       valies at: https://en.wikipedia.org/wiki/U.S._Standard_Atmosphere
    #       are not quite what this routine produces, but are close enough
    #       for the demo application intended.  Recommend scrubbing this
    #       routine against [1] for more precise use of this model.
    TRUE_PRESSURES = pickle.load(f)

def test_stdatm76_m():
    """Test stdAtm76 from 0 to 84850 m in increments of 1000m."""

    heights = np.arange(0, 84850, 1000)
    pressures = np.array([getStandardPressure(h, units='m') for h in heights])
    np.testing.assert_array_almost_equal(pressures, TRUE_PRESSURES,
                                         decimal=PRECISION)

def test_stdatm76_km():
    """Test stdAtm76 from 0 to 84.85 km in increments of 1km."""

    heights = np.arange(0, 84.85, 1)
    pressures = np.array([getStandardPressure(h, units='km') for h in heights])
    np.testing.assert_array_almost_equal(pressures, TRUE_PRESSURES,
                                         decimal=PRECISION)

def test_speed_of_sound():
    """Test speed of sound calculation."""
    np.testing.assert_almost_equal(actual=getSpeedOfSound(0),
                                   desired=340.2969686893478,
                                   decimal=PRECISION)


# [1]  https://ntrs.nasa.gov/api/citations/19770009539/downloads/19770009539.pdf?attachment=true
