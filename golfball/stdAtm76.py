#pylint: disable=C0103
# TODO: (esb) rename things so they match snake case.

"""Module for querying the 1976 US Standard Atmosphere."""

import numpy as np   # needed for np.sqrt() and np.exp()


def getGeopotential(altitude, units='km', earth_radius=6356.766):
    """Return the geopotential altitude in the units specified.

    Current units supported are 'm' and 'km'

    geopot_height = earth_radius * altitude / (earth_radius + altitude)

    computations done in km.
    """

    if units == 'm':
        altitude_km = altitude/1000.0
    elif units == 'km':
        altitude_km = altitude
    else:
        raise ValueError('units must be specified as "m" or "km".')

    return earth_radius * altitude_km / (earth_radius + altitude_km)

def getStandardTemperature(geopot_height=0.0):
    """Get the Standard Temparature from a given Geopotential Height.

    Standard atmospheric temperature, in kelvins (273.15 + Celsius)
    Below 51 km: Practical Meteorology by Roland Stull, pg 12
    Above 51 km: http://www.braeunig.us/space/atmmodel.htm
    """
    if geopot_height <= 11:       # Troposphere
        temperature = 288.15 - (6.5 * geopot_height)
    elif geopot_height <= 20:     # Stratosphere starts
        temperature = 216.65
    elif geopot_height <= 32:
        temperature = 196.65 + geopot_height
    elif geopot_height <= 47:
        temperature = 228.65 + 2.8 * (geopot_height - 32)
    elif geopot_height <= 51:     # Mesosphere starts
        temperature = 270.65
    elif geopot_height <= 71:
        temperature = 270.65 - 2.8 * (geopot_height - 51)
    elif geopot_height <= 84.85:
        temperature = 214.65 - 2 * (geopot_height - 71)
    # Thermosphere has high kinetic temperature (500 C to 2000 C) but temperature
    # as measured by a thermometer would be very low because of almost vacuum.
    else:
        raise ValueError('geopot_height must be less than 84.85 km.')

    return temperature

def getStandardPressure(altitude=0.0, units='km'):
    """Get the standard Pressure given an altitude.

    Below 51 km: Practical Meteorology by Roland Stull, pg 12
    Above 51 km: http://www.braeunig.us/space/atmmodel.htm

    Validation data:
    https://www.avs.org/AVS/files/c7/c7edaedb-95b2-438f-adfb-36de54f87b9e.pdf
    """

    geopot_height = getGeopotential(altitude, units=units)

    t = getStandardTemperature(geopot_height)

    if geopot_height <= 11:
        pressure = 101325.0 * (288.15 / t) ** -5.255877
    elif geopot_height <= 20:
        pressure = 22632.06 * np.exp(-0.1577 * (geopot_height - 11))
    elif geopot_height <= 32:
        pressure = 5474.889 * (216.65 / t) ** 34.16319
    elif geopot_height <= 47:
        pressure = 868.0187 * (228.65 / t) ** 12.2011
    elif geopot_height <= 51:
        pressure = 110.9063 * np.exp(-0.1262 * (geopot_height - 47))
    elif geopot_height <= 71:
        pressure = 66.93887 * (270.65 / t) ** -12.2011
    elif geopot_height <= 84.85:
        pressure = 3.956420 * (214.65 / t) ** -17.0816
    else:
        raise ValueError('altitude must be less than 84.85 km.')

    return pressure

def getStandardDensity(altitude=0.0, units='km'):
    """Get the Standard Density given an altitude.

    Returns density as a function of altitude from the
    Standard Pressure and Standard Temperature using the
    Ideal Gas Law
    """

    M = 0.0289644 # kg/mol
    R = 8.3144598 # N*m/(mol*K) -- for air
    return (M * getStandardPressure(altitude, units=units))/ \
           (R * getStandardTemperature(getGeopotential(altitude,
                                                       units=units)))

def getSpeedOfSound(altitude=0.0, units='km'):
    """Calculate the speed of sound.

    Assumes units are 'km', unless otherwise specified in 'm'.
    """

    dens = getStandardDensity(altitude, units=units)
    pres = getStandardPressure(altitude, units=units)
    gamma = 1.4

    return np.sqrt(gamma * pres/dens)

def getDynViscosity(T):
    """Return the dynamic viscosity in Pascal-Seconds.

    - of a air (80% N2 20% 02)
    - at a specified temperature in Kelvin.

    Inputs
    ------
    T: int or float (in degrees K)
       specified temperature

    Returns
    -------
    Dynamnic viscosity: float (in Pa*s)

    """

    mu_0 = 18.27   # uPa*s
    T_0 = 291.15  # K
    C = 120.0   # K

    return mu_0/1e6 * (T_0 + C)/(T + C) * (T/T_0)**1.5

def getReynoldsNumber(velocity, rho, l_ref, temp):
    """Compute the reynolds number (unitless).

    Inputs
    -------
    velocity: fluid-relative velocity
    rho:      fluid density [kg/m^3]
    l_ref:    reference length [meters]
    temp:     fluid temperature [Kelvin]
    """

    return velocity * rho * l_ref / getDynViscosity(temp)
