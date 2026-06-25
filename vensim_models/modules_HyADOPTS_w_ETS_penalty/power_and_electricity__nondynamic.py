"""
Module power_and_electricity__nondynamic
Translated using PySD version 3.14.3
"""

@component.add(
    name="power H2 lookup",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def power_h2_lookup():
    return np.interp(time(), [2022.0, 2030.0, 2040.0, 2050.0], [0.0, 6.6, 66.1, 163.6])


@component.add(
    name="power hydrogen demand",
    units="t H2",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_power_hydrogen_demand": 1},
    other_deps={
        "_smooth_power_hydrogen_demand": {
            "initial": {"power_h2_lookup": 1, "h2_lhv": 1},
            "step": {"power_h2_lookup": 1, "h2_lhv": 1},
        }
    },
)
def power_hydrogen_demand():
    """
    Get this from Balmorel or have a range of possible scenarios?
    """
    return _smooth_power_hydrogen_demand()


_smooth_power_hydrogen_demand = Smooth(
    lambda: power_h2_lookup() / h2_lhv() * 10**6,
    lambda: 2,
    lambda: power_h2_lookup() / h2_lhv() * 10**6,
    lambda: 1,
    "_smooth_power_hydrogen_demand",
)
