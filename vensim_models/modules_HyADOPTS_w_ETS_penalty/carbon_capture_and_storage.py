"""
Module carbon_capture_and_storage
Translated using PySD version 3.14.3
"""

@component.add(
    name="Carbon Storage CAPEX",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cs_capex": 1, "cs_proxy_af": 1},
)
def carbon_storage_capex():
    return cs_capex() * cs_proxy_af()


@component.add(
    name="Carbon Storage cost",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"carbon_storage_capex": 1, "carbon_storage_opex": 1},
)
def carbon_storage_cost():
    return carbon_storage_capex() + carbon_storage_opex()


@component.add(
    name="Carbon Storage OPEX",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "cs_decommisioning": 1,
        "cs_fixed_opex": 1,
        "cs_other_expenditures": 1,
        "cs_variable_cost": 1,
    },
)
def carbon_storage_opex():
    return (
        cs_decommisioning()
        + cs_fixed_opex()
        + cs_other_expenditures()
        + cs_variable_cost()
    )


@component.add(
    name="Carbon Transportation cost",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ct_distance": 1,
        "ct_af": 1,
        "ct_opex": 1,
        "ct_capex": 1,
        "ct_capacity_factor": 1,
    },
)
def carbon_transportation_cost():
    return (
        ct_distance()
        * (ct_capex() * ct_af() + ct_opex())
        / (8760 * ct_capacity_factor())
    )


@component.add(
    name="CC AF",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "cc_lifetime": 1},
)
def cc_af():
    return 1 / ((1 - (1 + discount_rate()) ** -cc_lifetime()) / discount_rate())


@component.add(
    name="CC Capacity Factor",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def cc_capacity_factor():
    """
    CF = 1 - Planned Outage - Forced Outage
    """
    return 1 - 0.05 - 3 / 52


@component.add(
    name="CC CAPEX",
    units="M€/(tCO2/h)",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def cc_capex():
    """
    Taken from Technology Catalogue Table. Learning rate is assumed based on time, but is highly relevant for size of unit installed as well.
    """
    return np.interp(
        time(), [2019.0, 2025.0, 2030.0, 2040.0, 2050.0], [4.1, 2.9, 2.3, 2.0, 1.9]
    )


@component.add(
    name="CC Capture Rate", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def cc_capture_rate():
    """
    Assumes a capture rate of 90% for retrofitted CC units.
    """
    return 0.9


@component.add(
    name="CC ELECTRICITY USAGE",
    units="MWh/tCO2",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def cc_electricity_usage():
    """
    Taken from Technology Catalogue Table. Learning rate is assumed based on time.
    """
    return np.interp(
        time(),
        [2019.0, 2025.0, 2030.0, 2040.0, 2050.0],
        [0.03, 0.03, 0.025, 0.023, 0.02],
    )


@component.add(
    name="CC FIXED OPEX", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def cc_fixed_opex():
    """
    Percent of CAPEX
    """
    return 0.03


@component.add(
    name="CC HEAT USAGE",
    units="MWh/tCO2",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def cc_heat_usage():
    """
    Taken from Technology Catalogue Table. Learning rate is assumed based on time.
    """
    return np.interp(
        time(), [2019.0, 2025.0, 2030.0, 2040.0, 2050.0], [0.83, 0.83, 0.72, 0.66, 0.66]
    )


@component.add(
    name="CC Lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def cc_lifetime():
    return 25


@component.add(
    name="CC VARIABLE COST", units="€/tCO2", comp_type="Constant", comp_subtype="Normal"
)
def cc_variable_cost():
    """
    2.0 € for amine. 0.5 € for other chemicals.
    """
    return 2.5


@component.add(
    name="CCS CAPEX",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"carbon_storage_capex": 1, "ps_cc_capex": 1},
)
def ccs_capex():
    return carbon_storage_capex() + ps_cc_capex()


@component.add(
    name="CCS cost",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ccs_capex": 1, "ccs_opex": 1},
)
def ccs_cost():
    return ccs_capex() + ccs_opex()


@component.add(
    name="CCS OPEX",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "carbon_storage_opex": 1,
        "carbon_transportation_cost": 1,
        "ps_cc_opex": 1,
    },
)
def ccs_opex():
    return carbon_storage_opex() + carbon_transportation_cost() + ps_cc_opex()


@component.add(
    name="CS CAPEX",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def cs_capex():
    return np.interp(
        time(), [2019.0, 2025.0, 2030.0, 2040.0, 2050.0], [3.89, 3.7, 3.52, 3.18, 3.18]
    )


@component.add(
    name="CS decommisioning",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def cs_decommisioning():
    return np.interp(
        time(), [2019.0, 2025.0, 2030.0, 2040.0, 2050.0], [0.84, 0.8, 0.76, 0.69, 0.69]
    )


@component.add(
    name="CS FIXED OPEX",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def cs_fixed_opex():
    return np.interp(
        time(), [2019.0, 2025.0, 2030.0, 2040.0, 2050.0], [1.46, 1.39, 1.32, 1.19, 1.19]
    )


@component.add(
    name="CS lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def cs_lifetime():
    return 50


@component.add(
    name="CS OTHER EXPENDITURES",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def cs_other_expenditures():
    return np.interp(
        time(), [2019.0, 2025.0, 2030.0, 2040.0, 2050.0], [0.73, 0.7, 0.66, 0.6, 0.6]
    )


@component.add(
    name="CS proxy AF",
    units="scalar",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "cs_lifetime": 2},
)
def cs_proxy_af():
    return (1 / ((1 - (1 + discount_rate()) ** -cs_lifetime()) / discount_rate())) / (
        1 / ((1 - (1 + 0.08) ** -cs_lifetime()) / 0.08)
    )


@component.add(
    name="CS VARIABLE COST",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def cs_variable_cost():
    return np.interp(
        time(), [2019.0, 2025.0, 2030.0, 2040.0, 2050.0], [10.18, 9.68, 9.2, 8.33, 8.33]
    )


@component.add(
    name="CT AF",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "ct_lifetime": 1},
)
def ct_af():
    return 1 / ((1 - (1 + discount_rate()) ** -ct_lifetime()) / discount_rate())


@component.add(name="CT Capacity Factor", comp_type="Constant", comp_subtype="Normal")
def ct_capacity_factor():
    """
    Own Assumption
    """
    return 0.9


@component.add(
    name="CT CAPEX", units="€/(tCO2/h)/km", comp_type="Constant", comp_subtype="Normal"
)
def ct_capex():
    """
    Technology Catalogue for Carbon Capture and Storage (ENS). Depends on pipeline location/size. Ranges from 13 - 18 - 33 - 53 - 130 €/(tCO2/h)/m
    """
    return 33 * 1000


@component.add(
    name="CT distance", units="km", comp_type="Constant", comp_subtype="Normal"
)
def ct_distance():
    """
    Could be anything.
    """
    return 150


@component.add(
    name="CT lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def ct_lifetime():
    return 50


@component.add(
    name="CT OPEX",
    units="€/(tCO2/h)/km/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ct_opex():
    return 20


@component.add(
    name="HEAT COST", units="€/MWh", comp_type="Constant", comp_subtype="Normal"
)
def heat_cost():
    """
    Assumption for value of waste heat (cheap heat assumption). doi = {https://doi.org/10.1016/j.apenergy.2024.124032},
    """
    return 15


@component.add(
    name="PS CC CAPEX",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cc_capex": 1, "cc_capacity_factor": 1, "cc_fixed_opex": 1, "cc_af": 1},
)
def ps_cc_capex():
    return (
        cc_capex() * 10**6 / (8760 * cc_capacity_factor()) * (cc_fixed_opex() + cc_af())
    )


@component.add(
    name="PS CC cost",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ps_cc_capex": 1, "ps_cc_opex": 1},
)
def ps_cc_cost():
    return ps_cc_capex() + ps_cc_opex()


@component.add(
    name="PS CC OPEX",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "cc_electricity_usage": 1,
        "grid_electricity_price": 1,
        "heat_cost": 1,
        "cc_heat_usage": 1,
        "cc_variable_cost": 1,
    },
)
def ps_cc_opex():
    return (
        cc_electricity_usage() * grid_electricity_price()
        + cc_heat_usage() * heat_cost()
        + cc_variable_cost()
    )
