"""
Module international_shipping
Translated using PySD version 3.14.3
"""

@component.add(
    name="containership construction time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def containership_construction_time():
    return 2


@component.add(
    name="containership lifetime",
    units="years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def containership_lifetime():
    return 15


@component.add(
    name="EU reference value",
    units="tCO2/GJ",
    comp_type="Constant",
    comp_subtype="Normal",
)
def eu_reference_value():
    """
    FuelEU Maritime
    """
    return 91.16 / 1000


@component.add(
    name="HFO IS",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hfo_is": 1},
    other_deps={
        "_integ_hfo_is": {
            "initial": {"is_initial_sector_activity": 1},
            "step": {
                "hfo_is_commissioning": 1,
                "hfo_is_decommissioning": 1,
                "hfo_is_economic_decommissioning": 1,
            },
        }
    },
)
def hfo_is():
    return _integ_hfo_is()


_integ_hfo_is = Integ(
    lambda: hfo_is_commissioning()
    - hfo_is_decommissioning()
    - hfo_is_economic_decommissioning(),
    lambda: is_initial_sector_activity(),
    "_integ_hfo_is",
)


@component.add(
    name="HFO IS Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_is_construction": 1, "containership_construction_time": 1},
)
def hfo_is_commissioning():
    return hfo_is_construction() / containership_construction_time()


@component.add(
    name="HFO IS competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nh3_containership_cost": 1,
        "hfo_containership_cost": 2,
        "meoh_containership_cost": 1,
    },
)
def hfo_is_competitiveness():
    return float(
        np.minimum(
            nh3_containership_cost() / hfo_containership_cost(),
            meoh_containership_cost() / hfo_containership_cost(),
        )
    )


@component.add(
    name="HFO IS Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hfo_is_construction": 1},
    other_deps={
        "_integ_hfo_is_construction": {
            "initial": {
                "is_initial_sector_activity": 1,
                "containership_lifetime": 1,
                "containership_construction_time": 1,
            },
            "step": {"hfo_is_investment": 1, "hfo_is_commissioning": 1},
        }
    },
)
def hfo_is_construction():
    return _integ_hfo_is_construction()


_integ_hfo_is_construction = Integ(
    lambda: hfo_is_investment() - hfo_is_commissioning(),
    lambda: is_initial_sector_activity()
    / containership_lifetime()
    * containership_construction_time()
    * 1.2,
    "_integ_hfo_is_construction",
)


@component.add(
    name="HFO IS cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_containership_cost_marginal": 1,
        "min_green_containership_cost": 1,
    },
)
def hfo_is_cost_difference():
    return hfo_containership_cost_marginal() / min_green_containership_cost()


@component.add(
    name="HFO IS Decommissioning",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_hfo_is_decommissioning": 1, "hfo_is": 1},
    other_deps={
        "_smooth_hfo_is_decommissioning": {
            "initial": {
                "hfo_is_delayed": 1,
                "hfo_is_economic_decommissioning_delayed": 1,
            },
            "step": {"hfo_is_delayed": 1, "hfo_is_economic_decommissioning_delayed": 1},
        }
    },
)
def hfo_is_decommissioning():
    return float(
        np.maximum(0, float(np.minimum(_smooth_hfo_is_decommissioning(), hfo_is())))
    )


_smooth_hfo_is_decommissioning = Smooth(
    lambda: hfo_is_delayed() - hfo_is_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: hfo_is_delayed() - hfo_is_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_hfo_is_decommissioning",
)


@component.add(
    name="HFO IS delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_hfo_is_delayed": 1},
    other_deps={
        "_delayfixed_hfo_is_delayed": {
            "initial": {"is_initial_sector_activity": 1, "containership_lifetime": 2},
            "step": {"hfo_is_commissioning": 1},
        }
    },
)
def hfo_is_delayed():
    return _delayfixed_hfo_is_delayed()


_delayfixed_hfo_is_delayed = DelayFixed(
    lambda: hfo_is_commissioning(),
    lambda: containership_lifetime(),
    lambda: is_initial_sector_activity() / containership_lifetime(),
    time_step,
    "_delayfixed_hfo_is_delayed",
)


@component.add(
    name="HFO IS economic decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_is_cost_difference": 2,
        "containership_lifetime": 1,
        "hfo_is": 1,
        "slope_decom": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def hfo_is_economic_decommissioning():
    return (
        if_then_else(
            hfo_is_cost_difference() > 1,
            lambda: (hfo_is() / containership_lifetime() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (hfo_is_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="HFO IS economic decommissioning delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_hfo_is_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_hfo_is_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"hfo_is_economic_decommissioning": 1},
        }
    },
)
def hfo_is_economic_decommissioning_delayed():
    return _delayn_hfo_is_economic_decommissioning_delayed()


_delayn_hfo_is_economic_decommissioning_delayed = DelayN(
    lambda: hfo_is_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_hfo_is_economic_decommissioning_delayed",
)


@component.add(
    name="HFO IS Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"is_investment_pipeline": 1, "hfo_is_investment_share": 1},
)
def hfo_is_investment():
    return is_investment_pipeline() * hfo_is_investment_share()


@component.add(
    name="HFO IS investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"is_equalizer": 1, "hfo_is_level": 1},
)
def hfo_is_investment_share():
    return is_equalizer() * hfo_is_level()


@component.add(
    name="HFO IS level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "hfo_is_competitiveness": 2,
        "hfo_is_sector_share": 1,
        "is_excess_activity": 1,
    },
)
def hfo_is_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - hfo_is_competitiveness()))))
        * float(np.maximum(0.1, hfo_is_sector_share()))
        * if_then_else(is_excess_activity() > 0, lambda: 0, lambda: 1)
        + hfo_is_competitiveness() * 0.001
    )


@component.add(
    name="HFO IS sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_is": 1, "sum_is_activity": 1},
)
def hfo_is_sector_share():
    return hfo_is() / sum_is_activity()


@component.add(
    name="Initial IS emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_is_emissions": 1},
    other_deps={
        "_initial_initial_is_emissions": {
            "initial": {"international_shipping_emissions": 1},
            "step": {},
        }
    },
)
def initial_is_emissions():
    return _initial_initial_is_emissions()


_initial_initial_is_emissions = Initial(
    lambda: international_shipping_emissions(), "_initial_initial_is_emissions"
)


@component.add(
    name="international shipping average cost",
    units="€/GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_is_sector_share": 1,
        "hfo_containership_cost": 1,
        "meoh_is_sector_share": 1,
        "meoh_containership_cost": 1,
        "nh3_is_sector_share": 1,
        "nh3_containership_cost": 1,
        "yearly_containership_consumption": 1,
    },
)
def international_shipping_average_cost():
    """
    €/GWh of HFO input equivalent. (Total ship ownership costs).
    """
    return (
        (
            hfo_is_sector_share() * hfo_containership_cost()
            + meoh_is_sector_share() * meoh_containership_cost()
            + nh3_is_sector_share() * nh3_containership_cost()
        )
        / yearly_containership_consumption()
        * 10**6
    )


@component.add(
    name="international shipping biomass demand",
    units="GWh Biomass",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_is": 1, "biomeoh_biomass_usage": 1},
)
def international_shipping_biomass_demand():
    """
    Convert from GWh MeOH to GWh biomass
    """
    return meoh_is() * biomeoh_biomass_usage()


@component.add(
    name="international shipping emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_emission_factor": 1, "hfo_is": 1},
)
def international_shipping_emissions():
    return hfo_emission_factor() * hfo_is() * 3600


@component.add(
    name="international shipping hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "international_shipping_meoh_hydrogen_demand": 1,
        "international_shipping_nh3_hydrogen_demand": 1,
    },
)
def international_shipping_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return (
        international_shipping_meoh_hydrogen_demand()
        + international_shipping_nh3_hydrogen_demand()
    )


@component.add(
    name="international shipping MeOH hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_is": 1, "meoh_lhv": 1, "biomeoh_h2_usage": 1},
)
def international_shipping_meoh_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return meoh_is() * 3600 / meoh_lhv() / biomeoh_h2_usage()


@component.add(
    name="international shipping NH3 hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nh3_is": 1, "nh3_lhv": 1, "nh3_h2_usage": 1},
)
def international_shipping_nh3_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return nh3_is() * 3600 / nh3_lhv() / nh3_h2_usage()


@component.add(
    name="IS allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "initial_is_emissions": 1,
        "shipping_relative_emissions_reduction_lookup": 1,
        "time": 1,
    },
)
def is_allocated_emissions():
    return initial_is_emissions() * (
        1 - shipping_relative_emissions_reduction_lookup(time())
    )


@component.add(
    name="IS backlog",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_is_backlog": 1},
    other_deps={
        "_integ_is_backlog": {
            "initial": {"sum_is_activity": 1},
            "step": {"is_current_demand": 1, "sum_is_activity": 1},
        }
    },
)
def is_backlog():
    return _integ_is_backlog()


_integ_is_backlog = Integ(
    lambda: is_current_demand() - sum_is_activity(),
    lambda: sum_is_activity() * 0.018,
    "_integ_is_backlog",
)


@component.add(
    name="IS continuous investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "is_forecast_demand": 1,
        "sum_is_decommissioning": 1,
        "containership_construction_time": 1,
        "is_backlog": 1,
        "sum_is_activity": 1,
        "innovators": 1,
    },
)
def is_continuous_investment():
    return float(
        np.maximum(
            (
                is_forecast_demand()
                + sum_is_decommissioning()
                + is_backlog() / containership_construction_time() / 3
                - sum_is_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="IS current demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fuel_use_index": 1, "is_projected_demand": 1, "time": 1},
)
def is_current_demand():
    return fuel_use_index() * is_projected_demand(time())


@component.add(
    name="IS effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"international_shipping_average_cost": 1, "is_current_demand": 1},
)
def is_effective_cost():
    return international_shipping_average_cost() * is_current_demand() / 1000000000.0


@component.add(
    name="IS equalizer",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_is_h2_subsidy": 1,
        "nh3_is_h2_subsidy": 2,
        "nh3_is_bid_share": 2,
        "meoh_is_bid_share": 2,
        "nh3_is_level": 2,
        "hfo_is_level": 4,
        "meoh_is_level": 2,
    },
)
def is_equalizer():
    return if_then_else(
        meoh_is_h2_subsidy() > 0.01,
        lambda: if_then_else(
            nh3_is_h2_subsidy() > 0.01,
            lambda: (1 - nh3_is_bid_share() - meoh_is_bid_share()) / hfo_is_level(),
            lambda: (1 - meoh_is_bid_share()) / (nh3_is_level() + hfo_is_level()),
        ),
        lambda: if_then_else(
            nh3_is_h2_subsidy() > 0.01,
            lambda: (1 - nh3_is_bid_share()) / (meoh_is_level() + hfo_is_level()),
            lambda: 1 / (meoh_is_level() + nh3_is_level() + hfo_is_level()),
        ),
    )


@component.add(
    name="IS excess activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "is_excess_emissions": 1,
        "hfo_emission_factor": 1,
        "hard_regulation": 1,
    },
)
def is_excess_activity():
    return is_excess_emissions() / hfo_emission_factor() / 3600 * hard_regulation()


@component.add(
    name="IS excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"international_shipping_emissions": 1, "is_allocated_emissions": 1},
)
def is_excess_emissions():
    return international_shipping_emissions() - is_allocated_emissions()


@component.add(
    name="IS forecast demand",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_is_forecast_demand": 1},
    other_deps={
        "_forecast_is_forecast_demand": {
            "initial": {"is_current_demand": 1},
            "step": {"is_current_demand": 1, "containership_construction_time": 2},
        }
    },
)
def is_forecast_demand():
    return _forecast_is_forecast_demand()


_forecast_is_forecast_demand = Forecast(
    lambda: is_current_demand(),
    lambda: 3 * containership_construction_time(),
    lambda: containership_construction_time(),
    lambda: 0,
    "_forecast_is_forecast_demand",
)


@component.add(
    name="IS initial sector activity",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_is_initial_sector_activity": 1},
    other_deps={
        "_initial_is_initial_sector_activity": {
            "initial": {"is_current_demand": 1},
            "step": {},
        }
    },
)
def is_initial_sector_activity():
    return _initial_is_initial_sector_activity()


_initial_is_initial_sector_activity = Initial(
    lambda: is_current_demand(), "_initial_is_initial_sector_activity"
)


@component.add(
    name="IS innovator pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"is_continuous_investment": 1, "innovators": 2},
)
def is_innovator_pipeline():
    return is_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="IS innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_is_inno_switch": 1, "nh3_is_inno_switch": 1},
)
def is_innovators():
    return float(np.maximum(meoh_is_inno_switch() + nh3_is_inno_switch(), 1))


@component.add(
    name="IS investment pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"is_continuous_investment": 1},
)
def is_investment_pipeline():
    return is_continuous_investment()


@component.add(
    name="IS projected demand",
    units="GWh",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_is_projected_demand"},
)
def is_projected_demand(x, final_subs=None):
    """
    Considering an annual growth of 1,79%/year linearly compared to year 2019. Consumption is amount of fuel bunkered. Pre efficiency losses.
    """
    return _hardcodedlookup_is_projected_demand(x, final_subs)


_hardcodedlookup_is_projected_demand = HardcodedLookups(
    [
        1990,
        1991,
        1992,
        1993,
        1994,
        1995,
        1996,
        1997,
        1998,
        1999,
        2000,
        2001,
        2002,
        2003,
        2004,
        2005,
        2006,
        2007,
        2008,
        2009,
        2010,
        2011,
        2012,
        2013,
        2014,
        2015,
        2016,
        2017,
        2018,
        2019,
        2020,
        2021,
        2022,
        2023,
        2024,
        2025,
        2026,
        2027,
        2028,
        2029,
        2030,
        2031,
        2032,
        2033,
        2034,
        2035,
        2036,
        2037,
        2038,
        2039,
        2040,
        2041,
        2042,
        2043,
        2044,
        2045,
        2046,
        2047,
        2048,
        2049,
        2050,
    ],
    [
        420443,
        416041,
        421378,
        419745,
        412997,
        418664,
        441341,
        476294,
        497165,
        471125,
        504202,
        519926,
        528817,
        540227,
        569438,
        581506,
        618546,
        645924,
        649579,
        583112,
        581223,
        583251,
        542692,
        514524,
        499874,
        494726,
        519189,
        522157,
        539450,
        534033,
        543592,
        553151,
        562710,
        572270,
        581829,
        591388,
        600947,
        610506,
        620066,
        629625,
        639184,
        648743,
        658302,
        667862,
        677421,
        686980,
        696539,
        706098,
        715657,
        725217,
        734776,
        744335,
        753894,
        763453,
        773013,
        782572,
        792131,
        801690,
        811249,
        820809,
        830368,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_is_projected_demand",
)


@component.add(
    name="MeOH containership H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_containership_cost": 1,
        "meoh_ship_capex": 1,
        "containership_opex": 1,
        "ship_engine_af": 1,
        "yearly_containership_consumption": 1,
        "biomeoh_cost_without_h2": 1,
        "biomeoh_h2_usage": 1,
        "meoh_lhv": 1,
    },
)
def meoh_containership_h2_wtp():
    return (
        (
            (
                hfo_containership_cost()
                - (containership_opex() + meoh_ship_capex() * ship_engine_af())
            )
            / 3.6
            / yearly_containership_consumption()
            * 1000
            - biomeoh_cost_without_h2()
        )
        * biomeoh_h2_usage()
        * meoh_lhv()
        / 1000
    )


@component.add(
    name="MeOH IS",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_meoh_is": 1},
    other_deps={
        "_integ_meoh_is": {
            "initial": {},
            "step": {"meoh_is_commissioning": 1, "meoh_is_decommissioning": 1},
        }
    },
)
def meoh_is():
    return _integ_meoh_is()


_integ_meoh_is = Integ(
    lambda: meoh_is_commissioning() - meoh_is_decommissioning(),
    lambda: 0,
    "_integ_meoh_is",
)


@component.add(
    name="MeOH IS bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_is_desired_investment": 1},
)
def meoh_is_bid_share():
    return meoh_is_desired_investment()


@component.add(
    name="MeOH IS Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_is_construction": 1, "containership_construction_time": 1},
)
def meoh_is_commissioning():
    return meoh_is_construction() / containership_construction_time()


@component.add(
    name="MeOH IS Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_meoh_is_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_meoh_is_commissioning_subsidy_level": {
            "initial": {"containership_construction_time": 1},
            "step": {"meoh_is_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def meoh_is_commissioning_subsidy_level():
    return _delayfixed_meoh_is_commissioning_subsidy_level()


_delayfixed_meoh_is_commissioning_subsidy_level = DelayFixed(
    lambda: meoh_is_h2_subsidy() + green_h2_subsidy(),
    lambda: containership_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_meoh_is_commissioning_subsidy_level",
)


@component.add(
    name="MeOH IS competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nh3_containership_cost": 1,
        "meoh_containership_cost": 2,
        "hfo_containership_cost": 1,
    },
)
def meoh_is_competitiveness():
    return float(
        np.minimum(
            nh3_containership_cost() / meoh_containership_cost(),
            hfo_containership_cost() / meoh_containership_cost(),
        )
    )


@component.add(
    name="MeOH IS Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_meoh_is_construction": 1},
    other_deps={
        "_integ_meoh_is_construction": {
            "initial": {},
            "step": {
                "meoh_is_innovators": 1,
                "meoh_is_investment": 1,
                "meoh_is_commissioning": 1,
            },
        }
    },
)
def meoh_is_construction():
    return _integ_meoh_is_construction()


_integ_meoh_is_construction = Integ(
    lambda: meoh_is_innovators() + meoh_is_investment() - meoh_is_commissioning(),
    lambda: 0,
    "_integ_meoh_is_construction",
)


@component.add(
    name="MeOH IS Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_is": 1, "containership_lifetime": 1},
)
def meoh_is_decommissioning():
    return meoh_is() / containership_lifetime()


@component.add(
    name="MeOH IS Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_meoh_is_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_meoh_is_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"meoh_is_commissioning_subsidy_level": 1},
        }
    },
)
def meoh_is_decommissioning_subsidy_level():
    return _delayfixed_meoh_is_decommissioning_subsidy_level()


_delayfixed_meoh_is_decommissioning_subsidy_level = DelayFixed(
    lambda: meoh_is_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_meoh_is_decommissioning_subsidy_level",
)


@component.add(
    name="MeOH IS desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_meoh_is_desired_investment": 1},
    other_deps={
        "_smooth_meoh_is_desired_investment": {
            "initial": {"meoh_is_level": 2, "hfo_is_level": 1, "nh3_is_level": 1},
            "step": {"meoh_is_level": 2, "hfo_is_level": 1, "nh3_is_level": 1},
        }
    },
)
def meoh_is_desired_investment():
    return _smooth_meoh_is_desired_investment()


_smooth_meoh_is_desired_investment = Smooth(
    lambda: meoh_is_level() / (hfo_is_level() + meoh_is_level() + nh3_is_level()),
    lambda: 2,
    lambda: meoh_is_level() / (hfo_is_level() + meoh_is_level() + nh3_is_level()),
    lambda: 1,
    "_smooth_meoh_is_desired_investment",
)


@component.add(
    name="MeOH IS HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "is_continuous_investment": 1,
        "meoh_lhv": 1,
        "biomeoh_h2_usage": 1,
        "meoh_is_bid_share": 1,
    },
)
def meoh_is_hba_volume():
    return (
        is_continuous_investment()
        * 3600
        / meoh_lhv()
        / biomeoh_h2_usage()
        * meoh_is_bid_share()
    )


@component.add(
    name="MeOH IS inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_is_competitiveness": 1, "inno_switch_level": 1},
)
def meoh_is_inno_switch():
    return if_then_else(
        meoh_is_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="MeOH IS innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_is_inno_switch": 1, "is_innovators": 1},
)
def meoh_is_innovator_share():
    return meoh_is_inno_switch() / is_innovators()


@component.add(
    name="MeOH IS Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"is_innovator_pipeline": 1, "meoh_is_innovator_share": 1},
)
def meoh_is_innovators():
    return is_innovator_pipeline() * meoh_is_innovator_share()


@component.add(
    name="MeOH IS Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"is_investment_pipeline": 1, "meoh_is_investment_share": 1},
)
def meoh_is_investment():
    return is_investment_pipeline() * meoh_is_investment_share()


@component.add(
    name="MeOH IS investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_is_h2_subsidy": 1,
        "meoh_is_bid_share": 1,
        "meoh_is_level": 1,
        "is_equalizer": 1,
    },
)
def meoh_is_investment_share():
    return if_then_else(
        meoh_is_h2_subsidy() > 0.01,
        lambda: meoh_is_bid_share(),
        lambda: is_equalizer() * meoh_is_level(),
    )


@component.add(
    name="MeOH IS level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "meoh_is_competitiveness": 2, "meoh_is_sector_share": 1},
)
def meoh_is_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - meoh_is_competitiveness()))))
        * float(np.maximum(0.1, meoh_is_sector_share()))
        + meoh_is_competitiveness() * 0.001
    )


@component.add(
    name="MeOH IS sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_is": 1, "sum_is_activity": 1},
)
def meoh_is_sector_share():
    return meoh_is() / sum_is_activity()


@component.add(
    name="MeOH IS subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_meoh_is_subsidy_cost": 1},
    other_deps={
        "_integ_meoh_is_subsidy_cost": {
            "initial": {},
            "step": {
                "meoh_is_commissioning_subsidy_level": 1,
                "subsidized_meoh_is_commissioning": 1,
                "meoh_is_decommissioning_subsidy_level": 1,
                "subsidized_meoh_is_decommissioning": 1,
            },
        }
    },
)
def meoh_is_subsidy_cost():
    return _integ_meoh_is_subsidy_cost()


_integ_meoh_is_subsidy_cost = Integ(
    lambda: meoh_is_commissioning_subsidy_level() * subsidized_meoh_is_commissioning()
    - meoh_is_decommissioning_subsidy_level() * subsidized_meoh_is_decommissioning(),
    lambda: 0,
    "_integ_meoh_is_subsidy_cost",
)


@component.add(
    name="min green containership cost",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_containership_cost": 1, "nh3_containership_cost": 1},
)
def min_green_containership_cost():
    return float(np.minimum(meoh_containership_cost(), nh3_containership_cost()))


@component.add(
    name="NH3 containership H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_containership_cost": 1,
        "ship_engine_af": 1,
        "containership_opex": 1,
        "nh3_ship_capex": 1,
        "yearly_containership_consumption": 1,
        "green_nh3_cost_without_h2": 1,
        "nh3_h2_usage": 1,
        "nh3_lhv": 1,
    },
)
def nh3_containership_h2_wtp():
    return (
        (
            (
                hfo_containership_cost()
                - (containership_opex() + nh3_ship_capex() * ship_engine_af())
            )
            / 3.6
            / yearly_containership_consumption()
            * 1000
            - green_nh3_cost_without_h2()
        )
        * nh3_h2_usage()
        * nh3_lhv()
        / 1000
    )


@component.add(
    name="NH3 IS",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_nh3_is": 1},
    other_deps={
        "_integ_nh3_is": {
            "initial": {},
            "step": {"nh3_is_commissioning": 1, "nh3_is_decommissioning": 1},
        }
    },
)
def nh3_is():
    return _integ_nh3_is()


_integ_nh3_is = Integ(
    lambda: nh3_is_commissioning() - nh3_is_decommissioning(),
    lambda: 0,
    "_integ_nh3_is",
)


@component.add(
    name="NH3 IS bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nh3_is_desired_investment": 1},
)
def nh3_is_bid_share():
    return nh3_is_desired_investment()


@component.add(
    name="NH3 IS Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nh3_is_construction": 1, "containership_construction_time": 1},
)
def nh3_is_commissioning():
    return nh3_is_construction() / containership_construction_time()


@component.add(
    name="NH3 IS Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_nh3_is_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_nh3_is_commissioning_subsidy_level": {
            "initial": {"containership_construction_time": 1},
            "step": {"nh3_is_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def nh3_is_commissioning_subsidy_level():
    return _delayfixed_nh3_is_commissioning_subsidy_level()


_delayfixed_nh3_is_commissioning_subsidy_level = DelayFixed(
    lambda: nh3_is_h2_subsidy() + green_h2_subsidy(),
    lambda: containership_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_nh3_is_commissioning_subsidy_level",
)


@component.add(
    name="NH3 IS competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_containership_cost": 1,
        "nh3_containership_cost": 2,
        "meoh_containership_cost": 1,
    },
)
def nh3_is_competitiveness():
    return float(
        np.minimum(
            hfo_containership_cost() / nh3_containership_cost(),
            meoh_containership_cost() / nh3_containership_cost(),
        )
    )


@component.add(
    name="NH3 IS Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_nh3_is_construction": 1},
    other_deps={
        "_integ_nh3_is_construction": {
            "initial": {},
            "step": {
                "nh3_is_innovators": 1,
                "nh3_is_investment": 1,
                "nh3_is_commissioning": 1,
            },
        }
    },
)
def nh3_is_construction():
    return _integ_nh3_is_construction()


_integ_nh3_is_construction = Integ(
    lambda: nh3_is_innovators() + nh3_is_investment() - nh3_is_commissioning(),
    lambda: 0,
    "_integ_nh3_is_construction",
)


@component.add(
    name="NH3 IS Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nh3_is": 1, "containership_lifetime": 1},
)
def nh3_is_decommissioning():
    return nh3_is() / containership_lifetime()


@component.add(
    name="NH3 IS Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_nh3_is_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_nh3_is_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"nh3_is_commissioning_subsidy_level": 1},
        }
    },
)
def nh3_is_decommissioning_subsidy_level():
    return _delayfixed_nh3_is_decommissioning_subsidy_level()


_delayfixed_nh3_is_decommissioning_subsidy_level = DelayFixed(
    lambda: nh3_is_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_nh3_is_decommissioning_subsidy_level",
)


@component.add(
    name="NH3 IS desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_nh3_is_desired_investment": 1},
    other_deps={
        "_smooth_nh3_is_desired_investment": {
            "initial": {"nh3_is_level": 2, "hfo_is_level": 1, "meoh_is_level": 1},
            "step": {"nh3_is_level": 2, "hfo_is_level": 1, "meoh_is_level": 1},
        }
    },
)
def nh3_is_desired_investment():
    return _smooth_nh3_is_desired_investment()


_smooth_nh3_is_desired_investment = Smooth(
    lambda: nh3_is_level() / (hfo_is_level() + meoh_is_level() + nh3_is_level()),
    lambda: 2,
    lambda: nh3_is_level() / (hfo_is_level() + meoh_is_level() + nh3_is_level()),
    lambda: 1,
    "_smooth_nh3_is_desired_investment",
)


@component.add(
    name="NH3 IS HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "is_continuous_investment": 1,
        "nh3_lhv": 1,
        "nh3_h2_usage": 1,
        "nh3_is_bid_share": 1,
    },
)
def nh3_is_hba_volume():
    return (
        is_continuous_investment()
        * 3600
        / nh3_lhv()
        / nh3_h2_usage()
        * nh3_is_bid_share()
    )


@component.add(
    name="NH3 IS inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nh3_is_competitiveness": 1, "inno_switch_level": 1},
)
def nh3_is_inno_switch():
    return if_then_else(
        nh3_is_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="NH3 IS innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nh3_is_inno_switch": 1, "is_innovators": 1},
)
def nh3_is_innovator_share():
    return nh3_is_inno_switch() / is_innovators()


@component.add(
    name="NH3 IS Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"is_innovator_pipeline": 1, "nh3_is_innovator_share": 1},
)
def nh3_is_innovators():
    return is_innovator_pipeline() * nh3_is_innovator_share()


@component.add(
    name="NH3 IS Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"is_investment_pipeline": 1, "nh3_is_investment_share": 1},
)
def nh3_is_investment():
    return is_investment_pipeline() * nh3_is_investment_share()


@component.add(
    name="NH3 IS investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nh3_is_h2_subsidy": 1,
        "nh3_is_bid_share": 1,
        "is_equalizer": 1,
        "nh3_is_level": 1,
    },
)
def nh3_is_investment_share():
    return if_then_else(
        nh3_is_h2_subsidy() > 0.01,
        lambda: nh3_is_bid_share(),
        lambda: is_equalizer() * nh3_is_level(),
    )


@component.add(
    name="NH3 IS level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "nh3_is_competitiveness": 2, "nh3_is_sector_share": 1},
)
def nh3_is_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - nh3_is_competitiveness()))))
        * float(np.maximum(0.1, nh3_is_sector_share()))
        + nh3_is_competitiveness() * 0.001
    )


@component.add(
    name="NH3 IS sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nh3_is": 1, "sum_is_activity": 1},
)
def nh3_is_sector_share():
    return nh3_is() / sum_is_activity()


@component.add(
    name="NH3 IS subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_nh3_is_subsidy_cost": 1},
    other_deps={
        "_integ_nh3_is_subsidy_cost": {
            "initial": {},
            "step": {
                "nh3_is_commissioning_subsidy_level": 1,
                "subsidized_nh3_is_commissioning": 1,
                "nh3_is_decommissioning_subsidy_level": 1,
                "subsidized_nh3_is_decommissioning": 1,
            },
        }
    },
)
def nh3_is_subsidy_cost():
    return _integ_nh3_is_subsidy_cost()


_integ_nh3_is_subsidy_cost = Integ(
    lambda: nh3_is_commissioning_subsidy_level() * subsidized_nh3_is_commissioning()
    - nh3_is_decommissioning_subsidy_level() * subsidized_nh3_is_decommissioning(),
    lambda: 0,
    "_integ_nh3_is_subsidy_cost",
)


@component.add(
    name="shipping current emissions cap",
    units="tCO2/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "eu_reference_value": 1,
        "hard_regulation": 1,
        "shipping_relative_emissions_reduction_lookup": 1,
        "time": 1,
    },
)
def shipping_current_emissions_cap():
    return eu_reference_value() * (
        1 - shipping_relative_emissions_reduction_lookup(time()) * hard_regulation()
    )


@component.add(
    name="shipping HFO biooil share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"shipping_current_emissions_cap": 1, "hfo_emission_factor": 1},
)
def shipping_hfo_biooil_share():
    return 1 - shipping_current_emissions_cap() / hfo_emission_factor()


@component.add(
    name="SHIPPING RELATIVE EMISSIONS REDUCTION LOOKUP",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_shipping_relative_emissions_reduction_lookup"
    },
)
def shipping_relative_emissions_reduction_lookup(x, final_subs=None):
    """
    percent reduction
    """
    return _hardcodedlookup_shipping_relative_emissions_reduction_lookup(x, final_subs)


_hardcodedlookup_shipping_relative_emissions_reduction_lookup = HardcodedLookups(
    [2020.0, 2025.0, 2030.0, 2035.0, 2040.0, 2045.0, 2050.0],
    [0.0, 0.02, 0.06, 0.145, 0.31, 0.62, 0.8],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_shipping_relative_emissions_reduction_lookup",
)


@component.add(
    name="Subsidized MeOH IS Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_meoh_is_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_meoh_is_commissioning": {
            "initial": {"containership_construction_time": 1},
            "step": {"subsidized_meoh_is_investment": 1},
        }
    },
)
def subsidized_meoh_is_commissioning():
    return _delayfixed_subsidized_meoh_is_commissioning()


_delayfixed_subsidized_meoh_is_commissioning = DelayFixed(
    lambda: subsidized_meoh_is_investment(),
    lambda: containership_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_meoh_is_commissioning",
)


@component.add(
    name="Subsidized MeOH IS Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_meoh_is_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_meoh_is_decommissioning": {
            "initial": {},
            "step": {"subsidized_meoh_is_commissioning": 1},
        }
    },
)
def subsidized_meoh_is_decommissioning():
    return _delayfixed_subsidized_meoh_is_decommissioning()


_delayfixed_subsidized_meoh_is_decommissioning = DelayFixed(
    lambda: subsidized_meoh_is_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_meoh_is_decommissioning",
)


@component.add(
    name="Subsidized MeOH IS Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_is_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "meoh_is_investment": 1,
        "meoh_lhv": 1,
        "biomeoh_h2_usage": 1,
    },
)
def subsidized_meoh_is_investment():
    return (
        if_then_else(
            meoh_is_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: meoh_is_investment(),
            lambda: 0,
        )
        * 3600
        / meoh_lhv()
        / biomeoh_h2_usage()
        / 10**6
    )


@component.add(
    name="Subsidized NH3 IS Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_nh3_is_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_nh3_is_commissioning": {
            "initial": {"containership_construction_time": 1},
            "step": {"subsidized_nh3_is_investment": 1},
        }
    },
)
def subsidized_nh3_is_commissioning():
    return _delayfixed_subsidized_nh3_is_commissioning()


_delayfixed_subsidized_nh3_is_commissioning = DelayFixed(
    lambda: subsidized_nh3_is_investment(),
    lambda: containership_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_nh3_is_commissioning",
)


@component.add(
    name="Subsidized NH3 IS Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_nh3_is_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_nh3_is_decommissioning": {
            "initial": {},
            "step": {"subsidized_nh3_is_commissioning": 1},
        }
    },
)
def subsidized_nh3_is_decommissioning():
    return _delayfixed_subsidized_nh3_is_decommissioning()


_delayfixed_subsidized_nh3_is_decommissioning = DelayFixed(
    lambda: subsidized_nh3_is_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_nh3_is_decommissioning",
)


@component.add(
    name="Subsidized NH3 IS Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nh3_is_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "nh3_is_investment": 1,
        "nh3_lhv": 1,
        "nh3_h2_usage": 1,
    },
)
def subsidized_nh3_is_investment():
    return (
        if_then_else(
            nh3_is_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: nh3_is_investment(),
            lambda: 0,
        )
        * 3600
        / nh3_lhv()
        / nh3_h2_usage()
        / 10**6
    )


@component.add(
    name="sum IS activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_is": 1, "meoh_is": 1, "nh3_is": 1},
)
def sum_is_activity():
    return hfo_is() + meoh_is() + nh3_is()


@component.add(
    name="sum IS decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_is_decommissioning": 1,
        "hfo_is_decommissioning": 1,
        "nh3_is_decommissioning": 1,
        "hfo_is_economic_decommissioning": 1,
    },
)
def sum_is_decommissioning():
    return (
        meoh_is_decommissioning()
        + hfo_is_decommissioning()
        + nh3_is_decommissioning()
        + hfo_is_economic_decommissioning()
    )


@component.add(
    name="Support MeOH IS",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_meoh_is_investment": 1,
        "green_h2_subsidy": 1,
        "meoh_is_h2_subsidy": 1,
    },
)
def support_meoh_is():
    return (
        subsidized_meoh_is_investment()
        * (green_h2_subsidy() + meoh_is_h2_subsidy())
        * 10
    )


@component.add(
    name="Support NH3 IS",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_nh3_is_investment": 1,
        "nh3_is_h2_subsidy": 1,
        "green_h2_subsidy": 1,
    },
)
def support_nh3_is():
    return (
        subsidized_nh3_is_investment() * (green_h2_subsidy() + nh3_is_h2_subsidy()) * 10
    )
