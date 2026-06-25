"""
Module ets_approximation__not_developed
Translated using PySD version 3.14.3
"""

@component.add(
    name="CARBON COST",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ps_cc_cost": 1,
        "cc_capture_rate": 1,
        "carbon_storage_cost": 1,
        "carbon_tax": 1,
    },
)
def carbon_cost():
    return ps_cc_cost() / cc_capture_rate() + (carbon_tax() - carbon_storage_cost())


@component.add(
    name="EMISSIONS CAP LOOKUP",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_emissions_cap_lookup"},
)
def emissions_cap_lookup(x, final_subs=None):
    return _hardcodedlookup_emissions_cap_lookup(x, final_subs)


_hardcodedlookup_emissions_cap_lookup = HardcodedLookups(
    [2022.0, 2030.0, 2050.0],
    [1.0, 0.45, 0.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_emissions_cap_lookup",
)


@component.add(
    name="ETS allowance debt",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ets_allowance_debt": 1},
    other_deps={
        "_integ_ets_allowance_debt": {
            "initial": {},
            "step": {"total_emissions": 1, "ets_allowances": 1},
        }
    },
)
def ets_allowance_debt():
    return _integ_ets_allowance_debt()


_integ_ets_allowance_debt = Integ(
    lambda: total_emissions() - ets_allowances(), lambda: 0, "_integ_ets_allowance_debt"
)


@component.add(
    name="ETS allowances",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_emissions": 1, "relative_ets_allowance_cap": 1},
)
def ets_allowances():
    return initial_emissions() * relative_ets_allowance_cap()


@component.add(
    name="ETS debt CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"carbon_tax": 1},
)
def ets_debt_co2_wtp():
    return carbon_tax() + 100


@component.add(
    name="relative ETS allowance cap",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "emissions_cap_lookup": 1},
)
def relative_ets_allowance_cap():
    return emissions_cap_lookup(time())
