"""
Module fertilizer_nh3
Translated using PySD version 3.14.3
"""

@component.add(
    name="alternative fertilizer cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3_cost": 1, "fertilizer_nh3_cost": 1},
)
def alternative_fertilizer_cost():
    return float(np.minimum(blue_nh3_cost(), fertilizer_nh3_cost()))


@component.add(
    name="blue fertilizer emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3": 1, "blue_nh3_ef": 1},
)
def blue_fertilizer_emissions():
    return blue_nh3() * blue_nh3_ef() * 10**6


@component.add(
    name="Blue NH3",
    units="MT NH3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_blue_nh3": 1},
    other_deps={
        "_integ_blue_nh3": {
            "initial": {},
            "step": {"blue_nh3_commissioning": 1, "blue_nh3_decommissioning": 1},
        }
    },
)
def blue_nh3():
    return _integ_blue_nh3()


_integ_blue_nh3 = Integ(
    lambda: blue_nh3_commissioning() - blue_nh3_decommissioning(),
    lambda: 0,
    "_integ_blue_nh3",
)


@component.add(
    name="Blue NH3 Commissioning",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3_construction": 1, "fertilizer_construction_time": 1},
)
def blue_nh3_commissioning():
    return blue_nh3_construction() / fertilizer_construction_time()


@component.add(
    name="Blue NH3 competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_nh3_cost": 1, "blue_nh3_cost": 2, "fertilizer_nh3_cost": 1},
)
def blue_nh3_competitiveness():
    return float(
        np.minimum(
            grey_nh3_cost() / blue_nh3_cost(), fertilizer_nh3_cost() / blue_nh3_cost()
        )
    )


@component.add(
    name="Blue NH3 Construction",
    units="MT NH3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_blue_nh3_construction": 1},
    other_deps={
        "_integ_blue_nh3_construction": {
            "initial": {},
            "step": {
                "blue_nh3_innovators": 1,
                "blue_nh3_investment": 1,
                "blue_nh3_commissioning": 1,
            },
        }
    },
)
def blue_nh3_construction():
    return _integ_blue_nh3_construction()


_integ_blue_nh3_construction = Integ(
    lambda: blue_nh3_innovators() + blue_nh3_investment() - blue_nh3_commissioning(),
    lambda: 0,
    "_integ_blue_nh3_construction",
)


@component.add(
    name="Blue NH3 Decommissioning",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3": 1, "smr_lifetime": 1},
)
def blue_nh3_decommissioning():
    return blue_nh3() / smr_lifetime()


@component.add(
    name="Blue NH3 inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3_competitiveness": 1, "inno_switch_level": 1},
)
def blue_nh3_inno_switch():
    return if_then_else(
        blue_nh3_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="Blue NH3 innovator share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3_inno_switch": 1, "nh3_fertilizer_innovators": 1},
)
def blue_nh3_innovator_share():
    return blue_nh3_inno_switch() * nh3_fertilizer_innovators()


@component.add(
    name="Blue NH3 Innovators",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fertilizer_innovator_pipeline": 1, "blue_nh3_innovator_share": 1},
)
def blue_nh3_innovators():
    return float(
        np.maximum(0, fertilizer_innovator_pipeline() * blue_nh3_innovator_share())
    )


@component.add(
    name="Blue NH3 Investment",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fertilizer_investment_pipeline": 1, "blue_nh3_investment_share": 1},
)
def blue_nh3_investment():
    return float(
        np.maximum(0, fertilizer_investment_pipeline() * blue_nh3_investment_share())
    )


@component.add(
    name="Blue NH3 investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nh3_equalizer": 1, "blue_nh3_level": 1},
)
def blue_nh3_investment_share():
    return nh3_equalizer() * blue_nh3_level()


@component.add(
    name="Blue NH3 level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "blue_nh3_competitiveness": 2, "blue_nh3_sector_share": 1},
)
def blue_nh3_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - blue_nh3_competitiveness()))))
        * float(np.maximum(0.1, blue_nh3_sector_share()))
        + blue_nh3_competitiveness() * 0.001
    )


@component.add(
    name="Blue NH3 sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3": 1, "sum_fertilizer_activity": 1},
)
def blue_nh3_sector_share():
    return blue_nh3() / sum_fertilizer_activity()


@component.add(
    name="fertilizer allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "initial_fertilizer_emissions": 1,
        "emissions_cap_lookup": 1,
        "time": 1,
    },
)
def fertilizer_allocated_emissions():
    return initial_fertilizer_emissions() * emissions_cap_lookup(time())


@component.add(
    name="fertilizer average cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_nh3_sector_share": 1,
        "blue_nh3_cost": 1,
        "fertilizer_nh3_cost": 1,
        "green_nh3_sector_share": 1,
        "grey_nh3_sector_share": 1,
        "grey_nh3_cost": 1,
    },
)
def fertilizer_average_cost():
    return (
        blue_nh3_sector_share() * blue_nh3_cost()
        + green_nh3_sector_share() * fertilizer_nh3_cost()
        + grey_nh3_sector_share() * grey_nh3_cost()
    )


@component.add(
    name="fertilizer backlog",
    units="MT NH3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_fertilizer_backlog": 1},
    other_deps={
        "_integ_fertilizer_backlog": {
            "initial": {},
            "step": {"fertilizer_current_demand": 1, "sum_fertilizer_activity": 1},
        }
    },
)
def fertilizer_backlog():
    return _integ_fertilizer_backlog()


_integ_fertilizer_backlog = Integ(
    lambda: fertilizer_current_demand() - sum_fertilizer_activity(),
    lambda: 0,
    "_integ_fertilizer_backlog",
)


@component.add(
    name="fertilizer blue hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3": 1, "nh3_h2_usage": 1},
)
def fertilizer_blue_hydrogen_demand():
    return blue_nh3() * 10**6 / nh3_h2_usage()


@component.add(
    name="fertilizer construction time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def fertilizer_construction_time():
    return 3


@component.add(
    name="fertilizer continuous investment",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_forecast_demand": 1,
        "sum_fertilizer_decommissioning": 1,
        "fertilizer_construction_time": 1,
        "fertilizer_backlog": 1,
        "sum_fertilizer_activity": 1,
        "innovators": 1,
    },
)
def fertilizer_continuous_investment():
    return float(
        np.maximum(
            (
                fertilizer_forecast_demand()
                + sum_fertilizer_decommissioning()
                + fertilizer_backlog() / fertilizer_construction_time() / 3
                - sum_fertilizer_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="fertilizer current demand",
    units="MT NH3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "fertilizer_projected_demand": 1},
)
def fertilizer_current_demand():
    """
    19.1 MT/year - assumed constant moving forward. EHB European Backbone Report: 19.1 Mt/year CEPS Report: 21 Mt/year (capacity)
    """
    return fertilizer_projected_demand(time())


@component.add(
    name="fertilizer effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_average_cost": 1,
        "nh3_lhv": 1,
        "fertilizer_current_demand": 1,
    },
)
def fertilizer_effective_cost():
    """
    €/GJ -> €/tNH3 = B€/MtNH3 * activity (MtNH3)
    """
    return (fertilizer_average_cost() * nh3_lhv()) / 1000 * fertilizer_current_demand()


@component.add(
    name="fertilizer emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_fertilizer_emissions": 1, "grey_fertilizer_emissions": 1},
)
def fertilizer_emissions():
    return blue_fertilizer_emissions() + grey_fertilizer_emissions()


@component.add(
    name="fertilizer excess activity",
    units="MT NH3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_excess_emissions": 1,
        "grey_nh3_ef": 1,
        "ets": 1,
        "hard_regulation": 1,
    },
)
def fertilizer_excess_activity():
    return float(
        np.maximum(fertilizer_excess_emissions() / grey_nh3_ef() / 10**6, 0)
    ) * float(np.minimum(hard_regulation() + ets(), 1))


@component.add(
    name="fertilizer excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fertilizer_emissions": 1, "fertilizer_allocated_emissions": 1},
)
def fertilizer_excess_emissions():
    return fertilizer_emissions() - fertilizer_allocated_emissions()


@component.add(
    name="fertilizer forecast demand",
    units="MT NH3",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_fertilizer_forecast_demand": 1},
    other_deps={
        "_forecast_fertilizer_forecast_demand": {
            "initial": {"fertilizer_current_demand": 1},
            "step": {"fertilizer_current_demand": 1, "fertilizer_construction_time": 2},
        }
    },
)
def fertilizer_forecast_demand():
    return _forecast_fertilizer_forecast_demand()


_forecast_fertilizer_forecast_demand = Forecast(
    lambda: fertilizer_current_demand(),
    lambda: 3 * fertilizer_construction_time(),
    lambda: fertilizer_construction_time(),
    lambda: 0,
    "_forecast_fertilizer_forecast_demand",
)


@component.add(
    name="fertilizer grey hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_nh3": 1, "nh3_h2_usage": 1},
)
def fertilizer_grey_hydrogen_demand():
    return grey_nh3() * 10**6 / nh3_h2_usage()


@component.add(
    name="fertilizer hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_nh3": 1, "nh3_h2_usage": 1},
)
def fertilizer_hydrogen_demand():
    """
    Convert from MT to T NH3, then from T NH3 to T H2.
    """
    return green_nh3() * 10**6 / nh3_h2_usage()


@component.add(
    name="fertilizer initial sector activity",
    units="MT NH3",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_fertilizer_initial_sector_activity": 1},
    other_deps={
        "_initial_fertilizer_initial_sector_activity": {
            "initial": {"fertilizer_current_demand": 1},
            "step": {},
        }
    },
)
def fertilizer_initial_sector_activity():
    return _initial_fertilizer_initial_sector_activity()


_initial_fertilizer_initial_sector_activity = Initial(
    lambda: fertilizer_current_demand(), "_initial_fertilizer_initial_sector_activity"
)


@component.add(
    name="fertilizer innovator pipeline",
    units="MT NH3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fertilizer_continuous_investment": 1, "innovators": 2},
)
def fertilizer_innovator_pipeline():
    return fertilizer_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="fertilizer investment pipeline",
    units="MT NH3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fertilizer_continuous_investment": 1},
)
def fertilizer_investment_pipeline():
    return fertilizer_continuous_investment()


@component.add(
    name="fertilizer projected demand",
    units="MT NH3",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_fertilizer_projected_demand"},
)
def fertilizer_projected_demand(x, final_subs=None):
    return _hardcodedlookup_fertilizer_projected_demand(x, final_subs)


_hardcodedlookup_fertilizer_projected_demand = HardcodedLookups(
    [2000.0, 2070.0],
    [19.1, 19.1],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_fertilizer_projected_demand",
)


@component.add(
    name="Green NH3",
    units="MT NH3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_green_nh3": 1},
    other_deps={
        "_integ_green_nh3": {
            "initial": {},
            "step": {"green_nh3_commissioning": 1, "green_nh3_decommissioning": 1},
        }
    },
)
def green_nh3():
    return _integ_green_nh3()


_integ_green_nh3 = Integ(
    lambda: green_nh3_commissioning() - green_nh3_decommissioning(),
    lambda: 0,
    "_integ_green_nh3",
)


@component.add(
    name="Green NH3 bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_nh3_desired_investment": 1},
)
def green_nh3_bid_share():
    return green_nh3_desired_investment()


@component.add(
    name="Green NH3 Commissioning",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_nh3_construction": 1, "fertilizer_construction_time": 1},
)
def green_nh3_commissioning():
    return green_nh3_construction() / fertilizer_construction_time()


@component.add(
    name="Green NH3 Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_green_nh3_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_green_nh3_commissioning_subsidy_level": {
            "initial": {"fertilizer_construction_time": 1},
            "step": {"fertilizer_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def green_nh3_commissioning_subsidy_level():
    return _delayfixed_green_nh3_commissioning_subsidy_level()


_delayfixed_green_nh3_commissioning_subsidy_level = DelayFixed(
    lambda: fertilizer_h2_subsidy() + green_h2_subsidy(),
    lambda: fertilizer_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_green_nh3_commissioning_subsidy_level",
)


@component.add(
    name="Green NH3 competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3_cost": 1, "fertilizer_nh3_cost": 2, "grey_nh3_cost": 1},
)
def green_nh3_competitiveness():
    return float(
        np.minimum(
            blue_nh3_cost() / fertilizer_nh3_cost(),
            grey_nh3_cost() / fertilizer_nh3_cost(),
        )
    )


@component.add(
    name="Green NH3 Construction",
    units="MT NH3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_green_nh3_construction": 1},
    other_deps={
        "_integ_green_nh3_construction": {
            "initial": {},
            "step": {
                "green_nh3_innovators": 1,
                "green_nh3_investment": 1,
                "green_nh3_commissioning": 1,
            },
        }
    },
)
def green_nh3_construction():
    return _integ_green_nh3_construction()


_integ_green_nh3_construction = Integ(
    lambda: green_nh3_innovators() + green_nh3_investment() - green_nh3_commissioning(),
    lambda: 0,
    "_integ_green_nh3_construction",
)


@component.add(
    name="Green NH3 Decommissioning",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_nh3": 1, "aec_lifetime": 1},
)
def green_nh3_decommissioning():
    return green_nh3() / aec_lifetime()


@component.add(
    name="Green NH3 Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_green_nh3_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_green_nh3_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"green_nh3_commissioning_subsidy_level": 1},
        }
    },
)
def green_nh3_decommissioning_subsidy_level():
    return _delayfixed_green_nh3_decommissioning_subsidy_level()


_delayfixed_green_nh3_decommissioning_subsidy_level = DelayFixed(
    lambda: green_nh3_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_green_nh3_decommissioning_subsidy_level",
)


@component.add(
    name="Green NH3 desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_green_nh3_desired_investment": 1},
    other_deps={
        "_smooth_green_nh3_desired_investment": {
            "initial": {"green_nh3_level": 2, "blue_nh3_level": 1, "grey_nh3_level": 1},
            "step": {
                "green_nh3_level": 2,
                "blue_nh3_level": 1,
                "grey_nh3_level": 1,
                "hba_stabilizer": 1,
            },
        }
    },
)
def green_nh3_desired_investment():
    return _smooth_green_nh3_desired_investment()


_smooth_green_nh3_desired_investment = Smooth(
    lambda: green_nh3_level()
    / (blue_nh3_level() + green_nh3_level() + grey_nh3_level()),
    lambda: hba_stabilizer(),
    lambda: green_nh3_level()
    / (blue_nh3_level() + green_nh3_level() + grey_nh3_level()),
    lambda: 1,
    "_smooth_green_nh3_desired_investment",
)


@component.add(
    name="Green NH3 HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_continuous_investment": 1,
        "nh3_h2_usage": 1,
        "green_nh3_bid_share": 1,
    },
)
def green_nh3_hba_volume():
    return (
        fertilizer_continuous_investment()
        * 10**6
        / nh3_h2_usage()
        * green_nh3_bid_share()
    )


@component.add(
    name="Green NH3 inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_nh3_competitiveness": 1, "inno_switch_level": 1},
)
def green_nh3_inno_switch():
    return if_then_else(
        green_nh3_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="Green NH3 innovator share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_nh3_inno_switch": 1, "nh3_fertilizer_innovators": 1},
)
def green_nh3_innovator_share():
    return green_nh3_inno_switch() * nh3_fertilizer_innovators()


@component.add(
    name="Green NH3 Innovators",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fertilizer_innovator_pipeline": 1, "green_nh3_innovator_share": 1},
)
def green_nh3_innovators():
    return float(
        np.maximum(0, fertilizer_innovator_pipeline() * green_nh3_innovator_share())
    )


@component.add(
    name="Green NH3 Investment",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fertilizer_investment_pipeline": 1, "green_nh3_investment_share": 1},
)
def green_nh3_investment():
    return float(
        np.maximum(0, fertilizer_investment_pipeline() * green_nh3_investment_share())
    )


@component.add(
    name="Green NH3 investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_h2_subsidy": 1,
        "green_nh3_bid_share": 1,
        "nh3_equalizer": 1,
        "green_nh3_level": 1,
    },
)
def green_nh3_investment_share():
    return if_then_else(
        fertilizer_h2_subsidy() > 0.01,
        lambda: green_nh3_bid_share(),
        lambda: nh3_equalizer() * green_nh3_level(),
    )


@component.add(
    name="Green NH3 level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "green_nh3_competitiveness": 2,
        "green_nh3_sector_share": 1,
    },
)
def green_nh3_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - green_nh3_competitiveness()))))
        * float(np.maximum(0.1, green_nh3_sector_share()))
        + green_nh3_competitiveness() * 0.001
    )


@component.add(
    name="Green NH3 sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_nh3": 1, "sum_fertilizer_activity": 1},
)
def green_nh3_sector_share():
    return green_nh3() / sum_fertilizer_activity()


@component.add(
    name="Green NH3 subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_green_nh3_subsidy_cost": 1},
    other_deps={
        "_integ_green_nh3_subsidy_cost": {
            "initial": {},
            "step": {
                "green_nh3_commissioning_subsidy_level": 1,
                "subsidized_green_nh3_commissioning": 1,
                "green_nh3_decommissioning_subsidy_level": 1,
                "subsidized_green_nh3_decommissioning": 1,
            },
        }
    },
)
def green_nh3_subsidy_cost():
    return _integ_green_nh3_subsidy_cost()


_integ_green_nh3_subsidy_cost = Integ(
    lambda: green_nh3_commissioning_subsidy_level()
    * subsidized_green_nh3_commissioning()
    - green_nh3_decommissioning_subsidy_level()
    * subsidized_green_nh3_decommissioning(),
    lambda: 0,
    "_integ_green_nh3_subsidy_cost",
)


@component.add(
    name="grey fertilizer emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_nh3": 1, "grey_nh3_ef": 1},
)
def grey_fertilizer_emissions():
    return grey_nh3() * grey_nh3_ef() * 10**6


@component.add(
    name="Grey NH3",
    units="MT NH3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_grey_nh3": 1},
    other_deps={
        "_integ_grey_nh3": {
            "initial": {"fertilizer_initial_sector_activity": 1},
            "step": {
                "grey_nh3_commissioning": 1,
                "grey_nh3_decommissioning": 1,
                "grey_nh3_economic_decommissioning": 1,
            },
        }
    },
)
def grey_nh3():
    return _integ_grey_nh3()


_integ_grey_nh3 = Integ(
    lambda: grey_nh3_commissioning()
    - grey_nh3_decommissioning()
    - grey_nh3_economic_decommissioning(),
    lambda: fertilizer_initial_sector_activity(),
    "_integ_grey_nh3",
)


@component.add(
    name="Grey NH3 Commissioning",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_nh3_construction": 1, "fertilizer_construction_time": 1},
)
def grey_nh3_commissioning():
    return grey_nh3_construction() / fertilizer_construction_time()


@component.add(
    name="Grey NH3 competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3_cost": 1, "grey_nh3_cost": 2, "fertilizer_nh3_cost": 1},
)
def grey_nh3_competitiveness():
    return float(
        np.minimum(
            blue_nh3_cost() / grey_nh3_cost(), fertilizer_nh3_cost() / grey_nh3_cost()
        )
    )


@component.add(
    name="Grey NH3 Construction",
    units="MT NH3",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_grey_nh3_construction": 1},
    other_deps={
        "_integ_grey_nh3_construction": {
            "initial": {
                "fertilizer_initial_sector_activity": 1,
                "smr_lifetime": 1,
                "fertilizer_construction_time": 1,
            },
            "step": {"grey_nh3_investment": 1, "grey_nh3_commissioning": 1},
        }
    },
)
def grey_nh3_construction():
    return _integ_grey_nh3_construction()


_integ_grey_nh3_construction = Integ(
    lambda: grey_nh3_investment() - grey_nh3_commissioning(),
    lambda: fertilizer_initial_sector_activity()
    / smr_lifetime()
    * fertilizer_construction_time(),
    "_integ_grey_nh3_construction",
)


@component.add(
    name="Grey NH3 cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_nh3_cost_marginal": 1, "alternative_fertilizer_cost": 1},
)
def grey_nh3_cost_difference():
    return grey_nh3_cost_marginal() / alternative_fertilizer_cost()


@component.add(
    name="Grey NH3 Decommissioning",
    units="MT NH3/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_grey_nh3_decommissioning": 1, "grey_nh3": 1},
    other_deps={
        "_smooth_grey_nh3_decommissioning": {
            "initial": {
                "grey_nh3_delayed": 1,
                "grey_nh3_economic_decommissioning_delayed": 1,
            },
            "step": {
                "grey_nh3_delayed": 1,
                "grey_nh3_economic_decommissioning_delayed": 1,
            },
        }
    },
)
def grey_nh3_decommissioning():
    return float(
        np.maximum(0, float(np.minimum(_smooth_grey_nh3_decommissioning(), grey_nh3())))
    )


_smooth_grey_nh3_decommissioning = Smooth(
    lambda: grey_nh3_delayed() - grey_nh3_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: grey_nh3_delayed() - grey_nh3_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_grey_nh3_decommissioning",
)


@component.add(
    name="Grey NH3 delayed",
    units="MT NH3/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_grey_nh3_delayed": 1},
    other_deps={
        "_delayfixed_grey_nh3_delayed": {
            "initial": {"fertilizer_initial_sector_activity": 1, "smr_lifetime": 2},
            "step": {"grey_nh3_commissioning": 1},
        }
    },
)
def grey_nh3_delayed():
    return _delayfixed_grey_nh3_delayed()


_delayfixed_grey_nh3_delayed = DelayFixed(
    lambda: grey_nh3_commissioning(),
    lambda: smr_lifetime(),
    lambda: fertilizer_initial_sector_activity() / smr_lifetime(),
    time_step,
    "_delayfixed_grey_nh3_delayed",
)


@component.add(
    name="Grey NH3 economic decommissioning",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "grey_nh3_cost_difference": 2,
        "grey_nh3": 1,
        "smr_lifetime": 1,
        "slope_decom": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def grey_nh3_economic_decommissioning():
    return (
        if_then_else(
            grey_nh3_cost_difference() > 1,
            lambda: (grey_nh3() / smr_lifetime() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (grey_nh3_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="Grey NH3 economic decommissioning delayed",
    units="MT NH3/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_grey_nh3_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_grey_nh3_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"grey_nh3_economic_decommissioning": 1},
        }
    },
)
def grey_nh3_economic_decommissioning_delayed():
    return _delayn_grey_nh3_economic_decommissioning_delayed()


_delayn_grey_nh3_economic_decommissioning_delayed = DelayN(
    lambda: grey_nh3_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_grey_nh3_economic_decommissioning_delayed",
)


@component.add(
    name="Grey NH3 Investment",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fertilizer_investment_pipeline": 1, "grey_nh3_investment_share": 1},
)
def grey_nh3_investment():
    return float(
        np.maximum(0, fertilizer_investment_pipeline() * grey_nh3_investment_share())
    )


@component.add(
    name="Grey NH3 investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nh3_equalizer": 1, "grey_nh3_level": 1},
)
def grey_nh3_investment_share():
    return nh3_equalizer() * grey_nh3_level()


@component.add(
    name="Grey NH3 level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "grey_nh3_competitiveness": 2,
        "grey_nh3_sector_share": 1,
        "fertilizer_excess_activity": 1,
    },
)
def grey_nh3_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - grey_nh3_competitiveness()))))
        * float(np.maximum(0.1, grey_nh3_sector_share()))
        * if_then_else(fertilizer_excess_activity() > 0, lambda: 0, lambda: 1)
        + grey_nh3_competitiveness() * 0.001
    )


@component.add(
    name="Grey NH3 sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_nh3": 1, "sum_fertilizer_activity": 1},
)
def grey_nh3_sector_share():
    return grey_nh3() / sum_fertilizer_activity()


@component.add(
    name="Initial fertilizer emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_fertilizer_emissions": 1},
    other_deps={
        "_initial_initial_fertilizer_emissions": {
            "initial": {"fertilizer_emissions": 1},
            "step": {},
        }
    },
)
def initial_fertilizer_emissions():
    return _initial_initial_fertilizer_emissions()


_initial_initial_fertilizer_emissions = Initial(
    lambda: fertilizer_emissions(), "_initial_initial_fertilizer_emissions"
)


@component.add(
    name="NH3 equalizer",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_h2_subsidy": 1,
        "blue_nh3_level": 2,
        "grey_nh3_level": 2,
        "green_nh3_bid_share": 1,
        "green_nh3_level": 1,
    },
)
def nh3_equalizer():
    return if_then_else(
        fertilizer_h2_subsidy() > 0.01,
        lambda: (1 - green_nh3_bid_share()) / (blue_nh3_level() + grey_nh3_level()),
        lambda: 1 / (grey_nh3_level() + green_nh3_level() + blue_nh3_level()),
    )


@component.add(
    name="NH3 fertilizer innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_nh3_inno_switch": 1, "green_nh3_inno_switch": 1},
)
def nh3_fertilizer_innovators():
    return float(np.maximum(blue_nh3_inno_switch() + green_nh3_inno_switch(), 1))


@component.add(
    name="Subsidized Green NH3 Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_green_nh3_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_green_nh3_commissioning": {
            "initial": {"fertilizer_construction_time": 1},
            "step": {"subsidized_green_nh3_investment": 1},
        }
    },
)
def subsidized_green_nh3_commissioning():
    return _delayfixed_subsidized_green_nh3_commissioning()


_delayfixed_subsidized_green_nh3_commissioning = DelayFixed(
    lambda: subsidized_green_nh3_investment(),
    lambda: fertilizer_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_green_nh3_commissioning",
)


@component.add(
    name="Subsidized Green NH3 Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_green_nh3_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_green_nh3_decommissioning": {
            "initial": {},
            "step": {"subsidized_green_nh3_commissioning": 1},
        }
    },
)
def subsidized_green_nh3_decommissioning():
    return _delayfixed_subsidized_green_nh3_decommissioning()


_delayfixed_subsidized_green_nh3_decommissioning = DelayFixed(
    lambda: subsidized_green_nh3_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_green_nh3_decommissioning",
)


@component.add(
    name="Subsidized Green NH3 Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "green_nh3_investment": 1,
        "nh3_h2_usage": 1,
    },
)
def subsidized_green_nh3_investment():
    return (
        if_then_else(
            fertilizer_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: green_nh3_investment(),
            lambda: 0,
        )
        / nh3_h2_usage()
    )


@component.add(
    name="sum fertilizer activity",
    units="MT NH3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_nh3": 1, "green_nh3": 1, "blue_nh3": 1},
)
def sum_fertilizer_activity():
    return grey_nh3() + green_nh3() + blue_nh3()


@component.add(
    name="sum fertilizer construction",
    units="MT NH3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_nh3_construction": 1,
        "green_nh3_construction": 1,
        "grey_nh3_construction": 1,
    },
)
def sum_fertilizer_construction():
    return blue_nh3_construction() + green_nh3_construction() + grey_nh3_construction()


@component.add(
    name="sum fertilizer decommissioning",
    units="MT NH3/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_nh3_decommissioning": 1,
        "green_nh3_decommissioning": 1,
        "grey_nh3_decommissioning": 1,
        "grey_nh3_economic_decommissioning": 1,
    },
)
def sum_fertilizer_decommissioning():
    return (
        blue_nh3_decommissioning()
        + green_nh3_decommissioning()
        + grey_nh3_decommissioning()
        + grey_nh3_economic_decommissioning()
    )


@component.add(
    name="Support Green NH3",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_green_nh3_investment": 1,
        "fertilizer_h2_subsidy": 1,
        "green_h2_subsidy": 1,
    },
)
def support_green_nh3():
    return (
        subsidized_green_nh3_investment()
        * (green_h2_subsidy() + fertilizer_h2_subsidy())
        * 10
    )
