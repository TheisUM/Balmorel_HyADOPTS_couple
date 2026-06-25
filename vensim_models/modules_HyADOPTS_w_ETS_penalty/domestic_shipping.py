"""
Module domestic_shipping
Translated using PySD version 3.14.3
"""

@component.add(
    name="domestic shipping average cost",
    units="€/GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_ds_sector_share": 1,
        "hfo_ship_cost": 1,
        "meoh_ship_cost": 1,
        "meoh_ds_sector_share": 1,
        "be_ship_cost": 1,
        "electric_ds_sector_share": 1,
        "fc_ship_cost": 1,
        "h2fc_ds_sector_share": 1,
        "yearly_hfo_consumption": 1,
    },
)
def domestic_shipping_average_cost():
    """
    €/GWh of HFO input energy equivalent. (Total operational costs, some CAPEX included (not ship hull)).
    """
    return (
        hfo_ds_sector_share() * hfo_ship_cost()
        + meoh_ds_sector_share() * meoh_ship_cost()
        + electric_ds_sector_share() * be_ship_cost()
        + h2fc_ds_sector_share() * fc_ship_cost()
    ) / (yearly_hfo_consumption() / 1000)


@component.add(
    name="domestic shipping biomass demand",
    units="GWh Biomass",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_ds": 1, "biomeoh_biomass_usage": 1},
)
def domestic_shipping_biomass_demand():
    """
    Convert from GWh MeOH to GWh biomass
    """
    return meoh_ds() * biomeoh_biomass_usage()


@component.add(
    name="domestic shipping emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_emission_factor": 1, "hfo_ds": 1},
)
def domestic_shipping_emissions():
    return hfo_emission_factor() * hfo_ds() * 3600


@component.add(
    name="domestic shipping FC hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2fc_ds": 1, "ice_efficiency": 1, "fc_efficiency": 1, "h2_lhv": 1},
)
def domestic_shipping_fc_hydrogen_demand():
    return (h2fc_ds() * ice_efficiency() / fc_efficiency()) * 3600 / h2_lhv()


@component.add(
    name="domestic shipping hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_shipping_fc_hydrogen_demand": 1,
        "domestic_shipping_meoh_hydrogen_demand": 1,
    },
)
def domestic_shipping_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return (
        domestic_shipping_fc_hydrogen_demand()
        + domestic_shipping_meoh_hydrogen_demand()
    )


@component.add(
    name="domestic shipping MeOH hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_ds": 1, "meoh_lhv": 1, "biomeoh_h2_usage": 1},
)
def domestic_shipping_meoh_hydrogen_demand():
    return meoh_ds() * 3600 / meoh_lhv() / biomeoh_h2_usage()


@component.add(
    name="DS allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "initial_ds_emissions": 1,
        "time": 1,
        "shipping_relative_emissions_reduction_lookup": 1,
    },
)
def ds_allocated_emissions():
    return initial_ds_emissions() * (
        1 - shipping_relative_emissions_reduction_lookup(time())
    )


@component.add(
    name="DS backlog",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ds_backlog": 1},
    other_deps={
        "_integ_ds_backlog": {
            "initial": {"sum_ds_activity": 1},
            "step": {"ds_current_demand": 1, "sum_ds_activity": 1},
        }
    },
)
def ds_backlog():
    return _integ_ds_backlog()


_integ_ds_backlog = Integ(
    lambda: ds_current_demand() - sum_ds_activity(),
    lambda: sum_ds_activity() * 0.018,
    "_integ_ds_backlog",
)


@component.add(
    name="DS continuous investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ds_forecast_demand": 1,
        "sum_ds_decommissioning": 1,
        "ds_backlog": 1,
        "ship_construction_time": 1,
        "sum_ds_activity": 1,
        "innovators": 1,
    },
)
def ds_continuous_investment():
    return float(
        np.maximum(
            (
                ds_forecast_demand()
                + sum_ds_decommissioning()
                + ds_backlog() / ship_construction_time() / 3
                - sum_ds_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="DS current demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fuel_use_index": 1, "time": 1, "ds_projected_demand": 1},
)
def ds_current_demand():
    return fuel_use_index() * ds_projected_demand(time())


@component.add(
    name="DS effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"domestic_shipping_average_cost": 1, "ds_current_demand": 1},
)
def ds_effective_cost():
    return domestic_shipping_average_cost() * ds_current_demand() / 1000000000.0


@component.add(
    name="DS equalizer",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_ds_h2_subsidy": 1,
        "electric_ds_level": 4,
        "h2fc_ds_level": 2,
        "h2fc_ds_h2_subsidy": 2,
        "hfo_ds_level": 4,
        "h2fc_ds_bid_share": 2,
        "meoh_ds_bid_share": 2,
        "meoh_ds_level": 2,
    },
)
def ds_equalizer():
    return if_then_else(
        meoh_ds_h2_subsidy() > 0.01,
        lambda: if_then_else(
            h2fc_ds_h2_subsidy() > 0.01,
            lambda: (1 - h2fc_ds_bid_share() - meoh_ds_bid_share())
            / (hfo_ds_level() + electric_ds_level()),
            lambda: (1 - meoh_ds_bid_share())
            / (h2fc_ds_level() + hfo_ds_level() + electric_ds_level()),
        ),
        lambda: if_then_else(
            h2fc_ds_h2_subsidy() > 0.01,
            lambda: (1 - h2fc_ds_bid_share())
            / (meoh_ds_level() + hfo_ds_level() + electric_ds_level()),
            lambda: 1
            / (
                hfo_ds_level() + meoh_ds_level() + electric_ds_level() + h2fc_ds_level()
            ),
        ),
    )


@component.add(
    name="DS excess activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ds_excess_emissions": 1,
        "hfo_emission_factor": 1,
        "hard_regulation": 1,
    },
)
def ds_excess_activity():
    return ds_excess_emissions() / hfo_emission_factor() / 3600 * hard_regulation()


@component.add(
    name="DS excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"domestic_shipping_emissions": 1, "ds_allocated_emissions": 1},
)
def ds_excess_emissions():
    return domestic_shipping_emissions() - ds_allocated_emissions()


@component.add(
    name="DS forecast demand",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_ds_forecast_demand": 1},
    other_deps={
        "_forecast_ds_forecast_demand": {
            "initial": {"ds_current_demand": 1},
            "step": {"ds_current_demand": 1, "ship_construction_time": 2},
        }
    },
)
def ds_forecast_demand():
    return _forecast_ds_forecast_demand()


_forecast_ds_forecast_demand = Forecast(
    lambda: ds_current_demand(),
    lambda: 3 * ship_construction_time(),
    lambda: ship_construction_time(),
    lambda: 0,
    "_forecast_ds_forecast_demand",
)


@component.add(
    name="DS initial sector activity",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_ds_initial_sector_activity": 1},
    other_deps={
        "_initial_ds_initial_sector_activity": {
            "initial": {"ds_current_demand": 1},
            "step": {},
        }
    },
)
def ds_initial_sector_activity():
    return _initial_ds_initial_sector_activity()


_initial_ds_initial_sector_activity = Initial(
    lambda: ds_current_demand(), "_initial_ds_initial_sector_activity"
)


@component.add(
    name="DS innovator pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_continuous_investment": 1, "innovators": 2},
)
def ds_innovator_pipeline():
    return ds_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="DS innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_ds_inno_switch": 1,
        "electric_ds_inno_switch": 1,
        "h2fc_ds_inno_switch": 1,
    },
)
def ds_innovators():
    return float(
        np.maximum(
            meoh_ds_inno_switch() + electric_ds_inno_switch() + h2fc_ds_inno_switch(), 1
        )
    )


@component.add(
    name="DS investment pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_continuous_investment": 1},
)
def ds_investment_pipeline():
    return ds_continuous_investment()


@component.add(
    name="DS projected demand",
    units="GWh",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_ds_projected_demand"},
)
def ds_projected_demand(x, final_subs=None):
    """
    Considering an annual growth of 1,79%/year linearly compared to year 2019. Consumption is amount of fuel bunkered. Pre efficiency losses.
    """
    return _hardcodedlookup_ds_projected_demand(x, final_subs)


_hardcodedlookup_ds_projected_demand = HardcodedLookups(
    [
        1990.0,
        1991.0,
        1992.0,
        1993.0,
        1994.0,
        1995.0,
        1996.0,
        1997.0,
        1998.0,
        1999.0,
        2000.0,
        2001.0,
        2002.0,
        2003.0,
        2004.0,
        2005.0,
        2006.0,
        2007.0,
        2008.0,
        2009.0,
        2010.0,
        2011.0,
        2012.0,
        2013.0,
        2014.0,
        2015.0,
        2016.0,
        2017.0,
        2018.0,
        2019.0,
        2020.0,
        2021.0,
        2022.0,
        2023.0,
        2024.0,
        2025.0,
        2026.0,
        2027.0,
        2028.0,
        2029.0,
        2030.0,
        2031.0,
        2032.0,
        2033.0,
        2034.0,
        2035.0,
        2036.0,
        2037.0,
        2038.0,
        2039.0,
        2040.0,
        2041.0,
        2042.0,
        2043.0,
        2044.0,
        2045.0,
        2046.0,
        2047.0,
        2048.0,
        2049.0,
        2050.0,
    ],
    [
        83165.6,
        84798.6,
        84955.6,
        82767.0,
        82592.5,
        80043.4,
        86680.5,
        84451.0,
        84946.0,
        90256.1,
        80252.8,
        78781.5,
        78382.3,
        88114.3,
        88870.9,
        90189.4,
        97089.0,
        93154.9,
        85130.5,
        81783.4,
        83212.7,
        76752.4,
        74662.0,
        68486.8,
        64589.7,
        70277.9,
        72092.9,
        74424.0,
        72910.5,
        74002.5,
        75482.6,
        76962.6,
        78442.7,
        79922.7,
        81402.8,
        82882.8,
        84362.9,
        85842.9,
        87323.0,
        88803.0,
        90283.1,
        91763.1,
        93243.2,
        94723.2,
        96203.3,
        97683.4,
        99163.4,
        100643.0,
        102124.0,
        103604.0,
        105084.0,
        106564.0,
        108044.0,
        109524.0,
        111004.0,
        112484.0,
        113964.0,
        115444.0,
        116924.0,
        118404.0,
        119884.0,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_ds_projected_demand",
)


@component.add(
    name="Electric DS",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_electric_ds": 1},
    other_deps={
        "_integ_electric_ds": {
            "initial": {},
            "step": {"electric_ds_commissioning": 1, "electric_ds_decommissioning": 1},
        }
    },
)
def electric_ds():
    return _integ_electric_ds()


_integ_electric_ds = Integ(
    lambda: electric_ds_commissioning() - electric_ds_decommissioning(),
    lambda: 0,
    "_integ_electric_ds",
)


@component.add(
    name="Electric DS Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"electric_ds_construction": 1, "ship_construction_time": 1},
)
def electric_ds_commissioning():
    return electric_ds_construction() / ship_construction_time()


@component.add(
    name="Electric DS competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fc_ship_cost": 1,
        "be_ship_cost": 3,
        "hfo_ship_cost": 1,
        "meoh_ship_cost": 1,
    },
)
def electric_ds_competitiveness():
    return float(
        np.minimum(
            fc_ship_cost() / be_ship_cost(),
            float(
                np.minimum(
                    hfo_ship_cost() / be_ship_cost(), meoh_ship_cost() / be_ship_cost()
                )
            ),
        )
    )


@component.add(
    name="Electric DS Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_electric_ds_construction": 1},
    other_deps={
        "_integ_electric_ds_construction": {
            "initial": {},
            "step": {
                "electric_ds_innovators": 1,
                "electric_ds_investment": 1,
                "electric_ds_commissioning": 1,
            },
        }
    },
)
def electric_ds_construction():
    return _integ_electric_ds_construction()


_integ_electric_ds_construction = Integ(
    lambda: electric_ds_innovators()
    + electric_ds_investment()
    - electric_ds_commissioning(),
    lambda: 0,
    "_integ_electric_ds_construction",
)


@component.add(
    name="Electric DS Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"electric_ds": 1, "ship_lifetime": 1},
)
def electric_ds_decommissioning():
    return electric_ds() / ship_lifetime()


@component.add(
    name="Electric DS inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"electric_ds_competitiveness": 1, "inno_switch_level": 1},
)
def electric_ds_inno_switch():
    return if_then_else(
        electric_ds_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="Electric DS innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"electric_ds_inno_switch": 1, "ds_innovators": 1},
)
def electric_ds_innovator_share():
    return electric_ds_inno_switch() / ds_innovators()


@component.add(
    name="Electric DS Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_innovator_pipeline": 1, "electric_ds_innovator_share": 1},
)
def electric_ds_innovators():
    return ds_innovator_pipeline() * electric_ds_innovator_share()


@component.add(
    name="Electric DS Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_investment_pipeline": 1, "electric_ds_investment_share": 1},
)
def electric_ds_investment():
    return ds_investment_pipeline() * electric_ds_investment_share()


@component.add(
    name="Electric DS investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_equalizer": 1, "electric_ds_level": 1},
)
def electric_ds_investment_share():
    return ds_equalizer() * electric_ds_level()


@component.add(
    name="Electric DS level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "electric_ds_competitiveness": 2,
        "electric_ds_sector_share": 1,
    },
)
def electric_ds_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - electric_ds_competitiveness()))))
        * float(np.maximum(0.1, electric_ds_sector_share()))
        + electric_ds_competitiveness() * 0.001
    )


@component.add(
    name="Electric DS sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"electric_ds": 1, "sum_ds_activity": 1},
)
def electric_ds_sector_share():
    return electric_ds() / sum_ds_activity()


@component.add(
    name="FC ship H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_ship_cost": 1,
        "fc_ship_cost_without_h2": 1,
        "h2_lhv": 1,
        "yearly_h2_consumption": 1,
    },
)
def fc_ship_h2_wtp():
    return (
        (hfo_ship_cost() - fc_ship_cost_without_h2())
        * h2_lhv()
        / yearly_h2_consumption()
        / 1000
        * 10**6
    )


@component.add(
    name="H2FC DS",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_h2fc_ds": 1},
    other_deps={
        "_integ_h2fc_ds": {
            "initial": {},
            "step": {"h2fc_ds_commissioning": 1, "h2fc_ds_decommissioning": 1},
        }
    },
)
def h2fc_ds():
    return _integ_h2fc_ds()


_integ_h2fc_ds = Integ(
    lambda: h2fc_ds_commissioning() - h2fc_ds_decommissioning(),
    lambda: 0,
    "_integ_h2fc_ds",
)


@component.add(
    name="H2FC DS bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2fc_ds_desired_investment": 1},
)
def h2fc_ds_bid_share():
    return h2fc_ds_desired_investment()


@component.add(
    name="H2FC DS Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2fc_ds_construction": 1, "ship_construction_time": 1},
)
def h2fc_ds_commissioning():
    return h2fc_ds_construction() / ship_construction_time()


@component.add(
    name="H2FC DS Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_h2fc_ds_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_h2fc_ds_commissioning_subsidy_level": {
            "initial": {"ship_construction_time": 1},
            "step": {"h2fc_ds_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def h2fc_ds_commissioning_subsidy_level():
    return _delayfixed_h2fc_ds_commissioning_subsidy_level()


_delayfixed_h2fc_ds_commissioning_subsidy_level = DelayFixed(
    lambda: h2fc_ds_h2_subsidy() + green_h2_subsidy(),
    lambda: ship_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_h2fc_ds_commissioning_subsidy_level",
)


@component.add(
    name="H2FC DS competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_ship_cost": 1,
        "fc_ship_cost": 3,
        "hfo_ship_cost": 1,
        "be_ship_cost": 1,
    },
)
def h2fc_ds_competitiveness():
    return float(
        np.minimum(
            meoh_ship_cost() / fc_ship_cost(),
            float(
                np.minimum(
                    hfo_ship_cost() / fc_ship_cost(), be_ship_cost() / fc_ship_cost()
                )
            ),
        )
    )


@component.add(
    name="H2FC DS Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_h2fc_ds_construction": 1},
    other_deps={
        "_integ_h2fc_ds_construction": {
            "initial": {},
            "step": {
                "h2fc_ds_innovators": 1,
                "h2fc_ds_investment": 1,
                "h2fc_ds_commissioning": 1,
            },
        }
    },
)
def h2fc_ds_construction():
    return _integ_h2fc_ds_construction()


_integ_h2fc_ds_construction = Integ(
    lambda: h2fc_ds_innovators() + h2fc_ds_investment() - h2fc_ds_commissioning(),
    lambda: 0,
    "_integ_h2fc_ds_construction",
)


@component.add(
    name="H2FC DS Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2fc_ds": 1, "ship_lifetime": 1},
)
def h2fc_ds_decommissioning():
    return h2fc_ds() / ship_lifetime()


@component.add(
    name="H2FC DS Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_h2fc_ds_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_h2fc_ds_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"h2fc_ds_commissioning_subsidy_level": 1},
        }
    },
)
def h2fc_ds_decommissioning_subsidy_level():
    return _delayfixed_h2fc_ds_decommissioning_subsidy_level()


_delayfixed_h2fc_ds_decommissioning_subsidy_level = DelayFixed(
    lambda: h2fc_ds_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_h2fc_ds_decommissioning_subsidy_level",
)


@component.add(
    name="H2FC DS desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_h2fc_ds_desired_investment": 1},
    other_deps={
        "_smooth_h2fc_ds_desired_investment": {
            "initial": {
                "h2fc_ds_level": 2,
                "hfo_ds_level": 1,
                "meoh_ds_level": 1,
                "electric_ds_level": 1,
            },
            "step": {
                "h2fc_ds_level": 2,
                "hfo_ds_level": 1,
                "meoh_ds_level": 1,
                "electric_ds_level": 1,
            },
        }
    },
)
def h2fc_ds_desired_investment():
    return _smooth_h2fc_ds_desired_investment()


_smooth_h2fc_ds_desired_investment = Smooth(
    lambda: h2fc_ds_level()
    / (electric_ds_level() + h2fc_ds_level() + hfo_ds_level() + meoh_ds_level()),
    lambda: 2,
    lambda: h2fc_ds_level()
    / (electric_ds_level() + h2fc_ds_level() + hfo_ds_level() + meoh_ds_level()),
    lambda: 1,
    "_smooth_h2fc_ds_desired_investment",
)


@component.add(
    name="H2FC DS HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ds_continuous_investment": 1,
        "ice_efficiency": 1,
        "fc_efficiency": 1,
        "h2_lhv": 1,
        "h2fc_ds_bid_share": 1,
    },
)
def h2fc_ds_hba_volume():
    return (
        ds_continuous_investment()
        * ice_efficiency()
        / fc_efficiency()
        * 3600
        / h2_lhv()
        * h2fc_ds_bid_share()
    )


@component.add(
    name="H2FC DS inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2fc_ds_competitiveness": 1, "inno_switch_level": 1},
)
def h2fc_ds_inno_switch():
    return if_then_else(
        h2fc_ds_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="H2FC DS innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2fc_ds_inno_switch": 1, "ds_innovators": 1},
)
def h2fc_ds_innovator_share():
    return h2fc_ds_inno_switch() / ds_innovators()


@component.add(
    name="H2FC DS Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_innovator_pipeline": 1, "h2fc_ds_innovator_share": 1},
)
def h2fc_ds_innovators():
    return ds_innovator_pipeline() * h2fc_ds_innovator_share()


@component.add(
    name="H2FC DS Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_investment_pipeline": 1, "h2fc_ds_investment_share": 1},
)
def h2fc_ds_investment():
    return ds_investment_pipeline() * h2fc_ds_investment_share()


@component.add(
    name="H2FC DS investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2fc_ds_h2_subsidy": 1,
        "h2fc_ds_bid_share": 1,
        "h2fc_ds_level": 1,
        "ds_equalizer": 1,
    },
)
def h2fc_ds_investment_share():
    return if_then_else(
        h2fc_ds_h2_subsidy() > 0.01,
        lambda: h2fc_ds_bid_share(),
        lambda: ds_equalizer() * h2fc_ds_level(),
    )


@component.add(
    name="H2FC DS level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "h2fc_ds_competitiveness": 2, "h2fc_ds_sector_share": 1},
)
def h2fc_ds_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - h2fc_ds_competitiveness()))))
        * float(np.maximum(0.1, h2fc_ds_sector_share()))
        + h2fc_ds_competitiveness() * 0.001
    )


@component.add(
    name="H2FC DS sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2fc_ds": 1, "sum_ds_activity": 1},
)
def h2fc_ds_sector_share():
    return h2fc_ds() / sum_ds_activity()


@component.add(
    name="H2FC DS subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_h2fc_ds_subsidy_cost": 1},
    other_deps={
        "_integ_h2fc_ds_subsidy_cost": {
            "initial": {},
            "step": {
                "h2fc_ds_commissioning_subsidy_level": 1,
                "subsidized_h2fc_ds_commissioning": 1,
                "h2fc_ds_decommissioning_subsidy_level": 1,
                "subsidized_h2fc_ds_decommissioning": 1,
            },
        }
    },
)
def h2fc_ds_subsidy_cost():
    return _integ_h2fc_ds_subsidy_cost()


_integ_h2fc_ds_subsidy_cost = Integ(
    lambda: h2fc_ds_commissioning_subsidy_level() * subsidized_h2fc_ds_commissioning()
    - h2fc_ds_decommissioning_subsidy_level() * subsidized_h2fc_ds_decommissioning(),
    lambda: 0,
    "_integ_h2fc_ds_subsidy_cost",
)


@component.add(
    name="HFO DS",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hfo_ds": 1},
    other_deps={
        "_integ_hfo_ds": {
            "initial": {"ds_initial_sector_activity": 1},
            "step": {
                "hfo_ds_commissioning": 1,
                "hfo_ds_decommissioning": 1,
                "hfo_ds_economic_decommissioning": 1,
            },
        }
    },
)
def hfo_ds():
    return _integ_hfo_ds()


_integ_hfo_ds = Integ(
    lambda: hfo_ds_commissioning()
    - hfo_ds_decommissioning()
    - hfo_ds_economic_decommissioning(),
    lambda: ds_initial_sector_activity(),
    "_integ_hfo_ds",
)


@component.add(
    name="HFO DS Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_ds_construction": 1, "ship_construction_time": 1},
)
def hfo_ds_commissioning():
    return hfo_ds_construction() / ship_construction_time()


@component.add(
    name="HFO DS competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fc_ship_cost": 1,
        "hfo_ship_cost": 3,
        "be_ship_cost": 1,
        "meoh_ship_cost": 1,
    },
)
def hfo_ds_competitiveness():
    return float(
        np.minimum(
            fc_ship_cost() / hfo_ship_cost(),
            float(
                np.minimum(
                    be_ship_cost() / hfo_ship_cost(), meoh_ship_cost() / hfo_ship_cost()
                )
            ),
        )
    )


@component.add(
    name="HFO DS Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hfo_ds_construction": 1},
    other_deps={
        "_integ_hfo_ds_construction": {
            "initial": {
                "ds_initial_sector_activity": 1,
                "ship_lifetime": 1,
                "ship_construction_time": 1,
            },
            "step": {"hfo_ds_investment": 1, "hfo_ds_commissioning": 1},
        }
    },
)
def hfo_ds_construction():
    return _integ_hfo_ds_construction()


_integ_hfo_ds_construction = Integ(
    lambda: hfo_ds_investment() - hfo_ds_commissioning(),
    lambda: ds_initial_sector_activity()
    / ship_lifetime()
    * ship_construction_time()
    * 1.2,
    "_integ_hfo_ds_construction",
)


@component.add(
    name="HFO DS cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_ship_cost": 1, "min_green_ship_cost": 1},
)
def hfo_ds_cost_difference():
    return hfo_ship_cost() / min_green_ship_cost()


@component.add(
    name="HFO DS Decommissioning",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_hfo_ds_decommissioning": 1, "hfo_ds": 1},
    other_deps={
        "_smooth_hfo_ds_decommissioning": {
            "initial": {
                "hfo_ds_delayed": 1,
                "hfo_ds_economic_decommissioning_delayed": 1,
            },
            "step": {"hfo_ds_delayed": 1, "hfo_ds_economic_decommissioning_delayed": 1},
        }
    },
)
def hfo_ds_decommissioning():
    return float(
        np.maximum(0, float(np.minimum(_smooth_hfo_ds_decommissioning(), hfo_ds())))
    )


_smooth_hfo_ds_decommissioning = Smooth(
    lambda: hfo_ds_delayed() - hfo_ds_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: hfo_ds_delayed() - hfo_ds_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_hfo_ds_decommissioning",
)


@component.add(
    name="HFO DS delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_hfo_ds_delayed": 1},
    other_deps={
        "_delayfixed_hfo_ds_delayed": {
            "initial": {"ds_initial_sector_activity": 1, "ship_lifetime": 2},
            "step": {"hfo_ds_commissioning": 1},
        }
    },
)
def hfo_ds_delayed():
    return _delayfixed_hfo_ds_delayed()


_delayfixed_hfo_ds_delayed = DelayFixed(
    lambda: hfo_ds_commissioning(),
    lambda: ship_lifetime(),
    lambda: ds_initial_sector_activity() / ship_lifetime(),
    time_step,
    "_delayfixed_hfo_ds_delayed",
)


@component.add(
    name="HFO DS economic decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_ds_cost_difference": 2,
        "slope_decom": 1,
        "hfo_ds": 1,
        "ship_lifetime": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def hfo_ds_economic_decommissioning():
    return (
        if_then_else(
            hfo_ds_cost_difference() > 1,
            lambda: (hfo_ds() / ship_lifetime() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (hfo_ds_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="HFO DS economic decommissioning delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_hfo_ds_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_hfo_ds_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"hfo_ds_economic_decommissioning": 1},
        }
    },
)
def hfo_ds_economic_decommissioning_delayed():
    return _delayn_hfo_ds_economic_decommissioning_delayed()


_delayn_hfo_ds_economic_decommissioning_delayed = DelayN(
    lambda: hfo_ds_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_hfo_ds_economic_decommissioning_delayed",
)


@component.add(
    name="HFO DS Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_investment_pipeline": 1, "hfo_ds_investment_share": 1},
)
def hfo_ds_investment():
    return ds_investment_pipeline() * hfo_ds_investment_share()


@component.add(
    name="HFO DS investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_equalizer": 1, "hfo_ds_level": 1},
)
def hfo_ds_investment_share():
    return ds_equalizer() * hfo_ds_level()


@component.add(
    name="HFO DS level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "hfo_ds_competitiveness": 2,
        "hfo_ds_sector_share": 1,
        "ds_excess_activity": 1,
    },
)
def hfo_ds_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - hfo_ds_competitiveness()))))
        * float(np.maximum(0.1, hfo_ds_sector_share()))
        * if_then_else(ds_excess_activity() > 0, lambda: 0, lambda: 1)
        + hfo_ds_competitiveness() * 0.001
    )


@component.add(
    name="HFO DS sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_ds": 1, "sum_ds_activity": 1},
)
def hfo_ds_sector_share():
    return hfo_ds() / sum_ds_activity()


@component.add(
    name="Initial DS emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_ds_emissions": 1},
    other_deps={
        "_initial_initial_ds_emissions": {
            "initial": {"domestic_shipping_emissions": 1},
            "step": {},
        }
    },
)
def initial_ds_emissions():
    return _initial_initial_ds_emissions()


_initial_initial_ds_emissions = Initial(
    lambda: domestic_shipping_emissions(), "_initial_initial_ds_emissions"
)


@component.add(
    name="MeOH DS",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_meoh_ds": 1},
    other_deps={
        "_integ_meoh_ds": {
            "initial": {},
            "step": {"meoh_ds_commissioning": 1, "meoh_ds_decommissioning": 1},
        }
    },
)
def meoh_ds():
    return _integ_meoh_ds()


_integ_meoh_ds = Integ(
    lambda: meoh_ds_commissioning() - meoh_ds_decommissioning(),
    lambda: 0,
    "_integ_meoh_ds",
)


@component.add(
    name="MeOH DS bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_ds_desired_investment": 1},
)
def meoh_ds_bid_share():
    return meoh_ds_desired_investment()


@component.add(
    name="MeOH DS Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_ds_construction": 1, "ship_construction_time": 1},
)
def meoh_ds_commissioning():
    return meoh_ds_construction() / ship_construction_time()


@component.add(
    name="MeOH DS Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_meoh_ds_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_meoh_ds_commissioning_subsidy_level": {
            "initial": {"ship_construction_time": 1},
            "step": {"meoh_ds_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def meoh_ds_commissioning_subsidy_level():
    return _delayfixed_meoh_ds_commissioning_subsidy_level()


_delayfixed_meoh_ds_commissioning_subsidy_level = DelayFixed(
    lambda: meoh_ds_h2_subsidy() + green_h2_subsidy(),
    lambda: ship_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_meoh_ds_commissioning_subsidy_level",
)


@component.add(
    name="MeOH DS competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fc_ship_cost": 1,
        "meoh_ship_cost": 3,
        "hfo_ship_cost": 1,
        "be_ship_cost": 1,
    },
)
def meoh_ds_competitiveness():
    return float(
        np.minimum(
            fc_ship_cost() / meoh_ship_cost(),
            float(
                np.minimum(
                    hfo_ship_cost() / meoh_ship_cost(),
                    be_ship_cost() / meoh_ship_cost(),
                )
            ),
        )
    )


@component.add(
    name="MeOH DS Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_meoh_ds_construction": 1},
    other_deps={
        "_integ_meoh_ds_construction": {
            "initial": {},
            "step": {
                "meoh_ds_innovators": 1,
                "meoh_ds_investment": 1,
                "meoh_ds_commissioning": 1,
            },
        }
    },
)
def meoh_ds_construction():
    return _integ_meoh_ds_construction()


_integ_meoh_ds_construction = Integ(
    lambda: meoh_ds_innovators() + meoh_ds_investment() - meoh_ds_commissioning(),
    lambda: 0,
    "_integ_meoh_ds_construction",
)


@component.add(
    name="MeOH DS Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_ds": 1, "ship_lifetime": 1},
)
def meoh_ds_decommissioning():
    return meoh_ds() / ship_lifetime()


@component.add(
    name="MeOH DS Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_meoh_ds_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_meoh_ds_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"meoh_ds_commissioning_subsidy_level": 1},
        }
    },
)
def meoh_ds_decommissioning_subsidy_level():
    return _delayfixed_meoh_ds_decommissioning_subsidy_level()


_delayfixed_meoh_ds_decommissioning_subsidy_level = DelayFixed(
    lambda: meoh_ds_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_meoh_ds_decommissioning_subsidy_level",
)


@component.add(
    name="MeOH DS desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_meoh_ds_desired_investment": 1},
    other_deps={
        "_smooth_meoh_ds_desired_investment": {
            "initial": {
                "meoh_ds_level": 2,
                "hfo_ds_level": 1,
                "electric_ds_level": 1,
                "h2fc_ds_level": 1,
            },
            "step": {
                "meoh_ds_level": 2,
                "hfo_ds_level": 1,
                "electric_ds_level": 1,
                "h2fc_ds_level": 1,
            },
        }
    },
)
def meoh_ds_desired_investment():
    return _smooth_meoh_ds_desired_investment()


_smooth_meoh_ds_desired_investment = Smooth(
    lambda: meoh_ds_level()
    / (electric_ds_level() + h2fc_ds_level() + hfo_ds_level() + meoh_ds_level()),
    lambda: 2,
    lambda: meoh_ds_level()
    / (electric_ds_level() + h2fc_ds_level() + hfo_ds_level() + meoh_ds_level()),
    lambda: 1,
    "_smooth_meoh_ds_desired_investment",
)


@component.add(
    name="MeOH DS HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ds_continuous_investment": 1,
        "meoh_lhv": 1,
        "biomeoh_h2_usage": 1,
        "meoh_ds_bid_share": 1,
    },
)
def meoh_ds_hba_volume():
    return (
        ds_continuous_investment()
        * 3600
        / meoh_lhv()
        / biomeoh_h2_usage()
        * meoh_ds_bid_share()
    )


@component.add(
    name="MeOH DS inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_ds_competitiveness": 1, "inno_switch_level": 1},
)
def meoh_ds_inno_switch():
    return if_then_else(
        meoh_ds_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="MeOH DS innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_ds_inno_switch": 1, "ds_innovators": 1},
)
def meoh_ds_innovator_share():
    return meoh_ds_inno_switch() / ds_innovators()


@component.add(
    name="MeOH DS Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_innovator_pipeline": 1, "meoh_ds_innovator_share": 1},
)
def meoh_ds_innovators():
    return ds_innovator_pipeline() * meoh_ds_innovator_share()


@component.add(
    name="MeOH DS Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ds_investment_pipeline": 1, "meoh_ds_investment_share": 1},
)
def meoh_ds_investment():
    return ds_investment_pipeline() * meoh_ds_investment_share()


@component.add(
    name="MeOH DS investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_ds_h2_subsidy": 1,
        "meoh_ds_bid_share": 1,
        "meoh_ds_level": 1,
        "ds_equalizer": 1,
    },
)
def meoh_ds_investment_share():
    return if_then_else(
        meoh_ds_h2_subsidy() > 0.01,
        lambda: meoh_ds_bid_share(),
        lambda: ds_equalizer() * meoh_ds_level(),
    )


@component.add(
    name="MeOH DS level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "meoh_ds_competitiveness": 2, "meoh_ds_sector_share": 1},
)
def meoh_ds_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - meoh_ds_competitiveness()))))
        * float(np.maximum(0.1, meoh_ds_sector_share()))
        + meoh_ds_competitiveness() * 0.001
    )


@component.add(
    name="MeOH DS sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_ds": 1, "sum_ds_activity": 1},
)
def meoh_ds_sector_share():
    return meoh_ds() / sum_ds_activity()


@component.add(
    name="MeOH DS subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_meoh_ds_subsidy_cost": 1},
    other_deps={
        "_integ_meoh_ds_subsidy_cost": {
            "initial": {},
            "step": {
                "meoh_ds_commissioning_subsidy_level": 1,
                "subsidized_meoh_ds_commissioning": 1,
                "meoh_ds_decommissioning_subsidy_level": 1,
                "subsidized_meoh_ds_decommissioning": 1,
            },
        }
    },
)
def meoh_ds_subsidy_cost():
    return _integ_meoh_ds_subsidy_cost()


_integ_meoh_ds_subsidy_cost = Integ(
    lambda: meoh_ds_commissioning_subsidy_level() * subsidized_meoh_ds_commissioning()
    - meoh_ds_decommissioning_subsidy_level() * subsidized_meoh_ds_decommissioning(),
    lambda: 0,
    "_integ_meoh_ds_subsidy_cost",
)


@component.add(
    name="MeOH ship H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hfo_ship_cost": 1,
        "meoh_ship_cost_without_meoh": 1,
        "yearly_hfo_consumption": 1,
        "biomeoh_cost_without_h2": 1,
        "biomeoh_h2_usage": 1,
        "meoh_lhv": 1,
    },
)
def meoh_ship_h2_wtp():
    return (
        (
            (hfo_ship_cost() - meoh_ship_cost_without_meoh())
            / 3.6
            / yearly_hfo_consumption()
            * 10**6
            - biomeoh_cost_without_h2()
        )
        * biomeoh_h2_usage()
        * meoh_lhv()
        / 1000
    )


@component.add(
    name="min green ship cost",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"be_ship_cost": 1, "fc_ship_cost": 1, "meoh_ship_cost": 1},
)
def min_green_ship_cost():
    return float(
        np.minimum(be_ship_cost(), float(np.minimum(fc_ship_cost(), meoh_ship_cost())))
    )


@component.add(
    name="ship construction time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ship_construction_time():
    return 2


@component.add(
    name="ship lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def ship_lifetime():
    return 15


@component.add(
    name="Subsidized H2FC DS Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_h2fc_ds_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_h2fc_ds_commissioning": {
            "initial": {"ship_construction_time": 1},
            "step": {"subsidized_h2fc_ds_investment": 1},
        }
    },
)
def subsidized_h2fc_ds_commissioning():
    return _delayfixed_subsidized_h2fc_ds_commissioning()


_delayfixed_subsidized_h2fc_ds_commissioning = DelayFixed(
    lambda: subsidized_h2fc_ds_investment(),
    lambda: ship_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_h2fc_ds_commissioning",
)


@component.add(
    name="Subsidized H2FC DS Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_h2fc_ds_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_h2fc_ds_decommissioning": {
            "initial": {},
            "step": {"subsidized_h2fc_ds_commissioning": 1},
        }
    },
)
def subsidized_h2fc_ds_decommissioning():
    return _delayfixed_subsidized_h2fc_ds_decommissioning()


_delayfixed_subsidized_h2fc_ds_decommissioning = DelayFixed(
    lambda: subsidized_h2fc_ds_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_h2fc_ds_decommissioning",
)


@component.add(
    name="Subsidized H2FC DS Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2fc_ds_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "h2fc_ds_investment": 1,
        "ice_efficiency": 1,
        "fc_efficiency": 1,
        "h2_lhv": 1,
    },
)
def subsidized_h2fc_ds_investment():
    return (
        if_then_else(
            h2fc_ds_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: h2fc_ds_investment(),
            lambda: 0,
        )
        * ice_efficiency()
        / fc_efficiency()
        / h2_lhv()
        / 1000
    )


@component.add(
    name="Subsidized MeOH DS Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_meoh_ds_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_meoh_ds_commissioning": {
            "initial": {"ship_construction_time": 1},
            "step": {"subsidized_meoh_ds_investment": 1},
        }
    },
)
def subsidized_meoh_ds_commissioning():
    return _delayfixed_subsidized_meoh_ds_commissioning()


_delayfixed_subsidized_meoh_ds_commissioning = DelayFixed(
    lambda: subsidized_meoh_ds_investment(),
    lambda: ship_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_meoh_ds_commissioning",
)


@component.add(
    name="Subsidized MeOH DS Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_meoh_ds_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_meoh_ds_decommissioning": {
            "initial": {},
            "step": {"subsidized_meoh_ds_commissioning": 1},
        }
    },
)
def subsidized_meoh_ds_decommissioning():
    return _delayfixed_subsidized_meoh_ds_decommissioning()


_delayfixed_subsidized_meoh_ds_decommissioning = DelayFixed(
    lambda: subsidized_meoh_ds_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_meoh_ds_decommissioning",
)


@component.add(
    name="Subsidized MeOH DS Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_ds_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "meoh_ds_investment": 1,
        "meoh_lhv": 1,
        "biomeoh_h2_usage": 1,
    },
)
def subsidized_meoh_ds_investment():
    return (
        if_then_else(
            meoh_ds_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: meoh_ds_investment(),
            lambda: 0,
        )
        * 3600
        / meoh_lhv()
        / biomeoh_h2_usage()
        / 10**6
    )


@component.add(
    name="sum DS activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_ds": 1, "meoh_ds": 1, "electric_ds": 1, "h2fc_ds": 1},
)
def sum_ds_activity():
    return hfo_ds() + meoh_ds() + electric_ds() + h2fc_ds()


@component.add(
    name="sum DS decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_ds_decommissioning": 1,
        "hfo_ds_decommissioning": 1,
        "electric_ds_decommissioning": 1,
        "h2fc_ds_decommissioning": 1,
        "hfo_ds_economic_decommissioning": 1,
    },
)
def sum_ds_decommissioning():
    return (
        meoh_ds_decommissioning()
        + hfo_ds_decommissioning()
        + electric_ds_decommissioning()
        + h2fc_ds_decommissioning()
        + hfo_ds_economic_decommissioning()
    )


@component.add(
    name="Support H2FC DS",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_h2fc_ds_investment": 1,
        "green_h2_subsidy": 1,
        "h2fc_ds_h2_subsidy": 1,
    },
)
def support_h2fc_ds():
    return (
        subsidized_h2fc_ds_investment()
        * (green_h2_subsidy() + h2fc_ds_h2_subsidy())
        * 10
    )


@component.add(
    name="Support MeOH DS",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_meoh_ds_investment": 1,
        "meoh_ds_h2_subsidy": 1,
        "green_h2_subsidy": 1,
    },
)
def support_meoh_ds():
    return (
        subsidized_meoh_ds_investment()
        * (green_h2_subsidy() + meoh_ds_h2_subsidy())
        * 10
    )
