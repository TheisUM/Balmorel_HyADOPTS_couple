"""
Module domestic_aviation
Translated using PySD version 3.14.3
"""

@component.add(
    name="BioKero DA",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biokero_da": 1},
    other_deps={
        "_integ_biokero_da": {
            "initial": {},
            "step": {"biokero_da_commissioning": 1, "biokero_da_decommissioning": 1},
        }
    },
)
def biokero_da():
    return _integ_biokero_da()


_integ_biokero_da = Integ(
    lambda: biokero_da_commissioning() - biokero_da_decommissioning(),
    lambda: 0,
    "_integ_biokero_da",
)


@component.add(
    name="BioKero DA bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da_desired_investment": 1},
)
def biokero_da_bid_share():
    return biokero_da_desired_investment()


@component.add(
    name="BioKero DA Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da_construction": 1, "da_fuel_switch_time": 1},
)
def biokero_da_commissioning():
    return biokero_da_construction() / da_fuel_switch_time()


@component.add(
    name="BioKero DA Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_biokero_da_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_biokero_da_commissioning_subsidy_level": {
            "initial": {"da_fuel_switch_time": 1},
            "step": {"biokero_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def biokero_da_commissioning_subsidy_level():
    return _delayfixed_biokero_da_commissioning_subsidy_level()


_delayfixed_biokero_da_commissioning_subsidy_level = DelayFixed(
    lambda: biokero_h2_subsidy() + green_h2_subsidy(),
    lambda: da_fuel_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_biokero_da_commissioning_subsidy_level",
)


@component.add(
    name="BioKero DA competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_cost": 1, "biokero_cost": 2, "jetfuel_cost": 1},
)
def biokero_da_competitiveness():
    return float(
        np.minimum(synkero_cost() / biokero_cost(), jetfuel_cost() / biokero_cost())
    )


@component.add(
    name="BioKero DA Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biokero_da_construction": 1},
    other_deps={
        "_integ_biokero_da_construction": {
            "initial": {},
            "step": {
                "biokero_da_innovators": 1,
                "biokero_da_investment": 1,
                "biokero_da_commissioning": 1,
            },
        }
    },
)
def biokero_da_construction():
    return _integ_biokero_da_construction()


_integ_biokero_da_construction = Integ(
    lambda: biokero_da_innovators()
    + biokero_da_investment()
    - biokero_da_commissioning(),
    lambda: 0,
    "_integ_biokero_da_construction",
)


@component.add(
    name="BioKero DA Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da": 1, "jetfuel_lockin_period": 1},
)
def biokero_da_decommissioning():
    return biokero_da() / jetfuel_lockin_period()


@component.add(
    name="BioKero DA Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_biokero_da_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_biokero_da_decommissioning_subsidy_level": {
            "initial": {"jetfuel_lockin_period": 1},
            "step": {"biokero_da_commissioning_subsidy_level": 1},
        }
    },
)
def biokero_da_decommissioning_subsidy_level():
    return _delayfixed_biokero_da_decommissioning_subsidy_level()


_delayfixed_biokero_da_decommissioning_subsidy_level = DelayFixed(
    lambda: biokero_da_commissioning_subsidy_level(),
    lambda: jetfuel_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_biokero_da_decommissioning_subsidy_level",
)


@component.add(
    name="BioKero DA desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_biokero_da_desired_investment": 1},
    other_deps={
        "_smooth_biokero_da_desired_investment": {
            "initial": {
                "biokero_da_level": 2,
                "synkero_da_level": 1,
                "jetfuel_da_level": 1,
            },
            "step": {
                "biokero_da_level": 2,
                "synkero_da_level": 1,
                "jetfuel_da_level": 1,
            },
        }
    },
)
def biokero_da_desired_investment():
    return _smooth_biokero_da_desired_investment()


_smooth_biokero_da_desired_investment = Smooth(
    lambda: biokero_da_level()
    / (biokero_da_level() + jetfuel_da_level() + synkero_da_level()),
    lambda: 2,
    lambda: biokero_da_level()
    / (biokero_da_level() + jetfuel_da_level() + synkero_da_level()),
    lambda: 1,
    "_smooth_biokero_da_desired_investment",
)


@component.add(
    name="BioKero DA extra investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_da_level": 2,
        "synkero_da_level": 1,
        "saf_da_missing_share": 1,
        "sum_da_activity": 1,
    },
)
def biokero_da_extra_investment():
    return (
        zidz(biokero_da_level(), biokero_da_level() + synkero_da_level())
        * saf_da_missing_share()
        * sum_da_activity()
    )


@component.add(
    name="BioKero DA HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "da_continuous_investment": 1,
        "hvo_kerosene_h2_cost_scaler": 1,
        "biokero_da_bid_share": 1,
    },
)
def biokero_da_hba_volume():
    return (
        da_continuous_investment()
        * hvo_kerosene_h2_cost_scaler()
        * 3.6
        * biokero_da_bid_share()
    )


@component.add(
    name="BioKero DA inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da_competitiveness": 1, "inno_switch_level": 1},
)
def biokero_da_inno_switch():
    return if_then_else(
        biokero_da_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="BioKero DA innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da_inno_switch": 1, "da_innovators": 1},
)
def biokero_da_innovator_share():
    return biokero_da_inno_switch() / da_innovators()


@component.add(
    name="BioKero DA Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"da_innovator_pipeline": 1, "biokero_da_innovator_share": 1},
)
def biokero_da_innovators():
    return da_innovator_pipeline() * biokero_da_innovator_share()


@component.add(
    name="BioKero DA Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "da_investment_pipeline": 1,
        "biokero_da_investment_share": 1,
        "biokero_da_extra_investment": 1,
    },
)
def biokero_da_investment():
    return (
        da_investment_pipeline() * biokero_da_investment_share()
        + biokero_da_extra_investment()
    )


@component.add(
    name="BioKero DA investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_h2_subsidy": 1,
        "biokero_da_bid_share": 1,
        "biokero_da_level": 1,
        "da_equalizer": 1,
    },
)
def biokero_da_investment_share():
    return if_then_else(
        biokero_h2_subsidy() > 0.01,
        lambda: biokero_da_bid_share(),
        lambda: da_equalizer() * biokero_da_level(),
    )


@component.add(
    name="BioKero DA level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "biokero_da_competitiveness": 2,
        "biokero_da_sector_share": 1,
    },
)
def biokero_da_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - biokero_da_competitiveness()))))
        * float(np.maximum(0.1, biokero_da_sector_share()))
        + biokero_da_competitiveness() * 0.001
    )


@component.add(
    name="BioKero DA sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da": 1, "sum_da_activity": 1},
)
def biokero_da_sector_share():
    return biokero_da() / sum_da_activity()


@component.add(
    name="BioKero DA subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biokero_da_subsidy_cost": 1},
    other_deps={
        "_integ_biokero_da_subsidy_cost": {
            "initial": {},
            "step": {
                "biokero_da_commissioning_subsidy_level": 1,
                "subsidized_biokero_da_commissioning": 1,
                "biokero_da_decommissioning_subsidy_level": 1,
                "subsidized_biokero_da_decommissioning": 1,
            },
        }
    },
)
def biokero_da_subsidy_cost():
    return _integ_biokero_da_subsidy_cost()


_integ_biokero_da_subsidy_cost = Integ(
    lambda: biokero_da_commissioning_subsidy_level()
    * subsidized_biokero_da_commissioning()
    - biokero_da_decommissioning_subsidy_level()
    * subsidized_biokero_da_decommissioning(),
    lambda: 0,
    "_integ_biokero_da_subsidy_cost",
)


@component.add(
    name="DA allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_da_emissions": 1, "time": 1, "emissions_cap_lookup": 1},
)
def da_allocated_emissions():
    return initial_da_emissions() * emissions_cap_lookup(time())


@component.add(
    name="DA backlog",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_da_backlog": 1},
    other_deps={
        "_integ_da_backlog": {
            "initial": {"sum_da_activity": 1},
            "step": {"da_current_demand": 1, "sum_da_activity": 1},
        }
    },
)
def da_backlog():
    return _integ_da_backlog()


_integ_da_backlog = Integ(
    lambda: da_current_demand() - sum_da_activity(),
    lambda: sum_da_activity() * 0.012,
    "_integ_da_backlog",
)


@component.add(
    name="DA continuous investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "da_forecast_demand": 1,
        "sum_da_decommissioning": 1,
        "da_backlog": 1,
        "da_fuel_switch_time": 1,
        "sum_da_activity": 1,
        "sum_da_extra_investment": 1,
        "innovators": 1,
    },
)
def da_continuous_investment():
    return float(
        np.maximum(
            (
                da_forecast_demand()
                + sum_da_decommissioning()
                + da_backlog() / da_fuel_switch_time() / 3
                - sum_da_activity()
                - sum_da_extra_investment()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="DA current demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "da_projected_demand": 1},
)
def da_current_demand():
    return da_projected_demand(time())


@component.add(
    name="DA effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"domestic_aviation_average_cost": 1, "da_current_demand": 1},
)
def da_effective_cost():
    return domestic_aviation_average_cost() * da_current_demand() / 1000000000.0


@component.add(
    name="DA equalizer",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_h2_subsidy": 1,
        "synkero_h2_subsidy": 2,
        "biokero_da_bid_share": 2,
        "synkero_da_level": 2,
        "jetfuel_da_level": 4,
        "synkero_da_bid_share": 2,
        "biokero_da_level": 2,
    },
)
def da_equalizer():
    return if_then_else(
        biokero_h2_subsidy() > 0.01,
        lambda: if_then_else(
            synkero_h2_subsidy() > 0.01,
            lambda: (1 - synkero_da_bid_share() - biokero_da_bid_share())
            / jetfuel_da_level(),
            lambda: (1 - biokero_da_bid_share())
            / (synkero_da_level() + jetfuel_da_level()),
        ),
        lambda: if_then_else(
            synkero_h2_subsidy() > 0.01,
            lambda: (1 - synkero_da_bid_share())
            / (biokero_da_level() + jetfuel_da_level()),
            lambda: 1 / (biokero_da_level() + synkero_da_level() + jetfuel_da_level()),
        ),
    )


@component.add(
    name="DA excess activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sum_da_activity": 1, "jetfuel_da_excess_share": 1},
)
def da_excess_activity():
    return sum_da_activity() * jetfuel_da_excess_share()


@component.add(
    name="DA excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"domestic_aviation_emissions": 1, "da_allocated_emissions": 1},
)
def da_excess_emissions():
    return domestic_aviation_emissions() - da_allocated_emissions()


@component.add(
    name="DA forecast demand",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_da_forecast_demand": 1},
    other_deps={
        "_forecast_da_forecast_demand": {
            "initial": {"da_current_demand": 1},
            "step": {"da_current_demand": 1, "da_fuel_switch_time": 2},
        }
    },
)
def da_forecast_demand():
    return _forecast_da_forecast_demand()


_forecast_da_forecast_demand = Forecast(
    lambda: da_current_demand(),
    lambda: 3 * da_fuel_switch_time(),
    lambda: da_fuel_switch_time(),
    lambda: 0,
    "_forecast_da_forecast_demand",
)


@component.add(
    name="DA fuel switch time",
    units="Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ia_fuel_switch_time": 1},
)
def da_fuel_switch_time():
    return ia_fuel_switch_time()


@component.add(
    name="DA initial sector activity",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_da_initial_sector_activity": 1},
    other_deps={
        "_initial_da_initial_sector_activity": {
            "initial": {"da_current_demand": 1},
            "step": {},
        }
    },
)
def da_initial_sector_activity():
    return _initial_da_initial_sector_activity()


_initial_da_initial_sector_activity = Initial(
    lambda: da_current_demand(), "_initial_da_initial_sector_activity"
)


@component.add(
    name="DA innovator pipeline",
    units="MT NH3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"da_continuous_investment": 1, "innovators": 2},
)
def da_innovator_pipeline():
    return da_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="DA innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da_inno_switch": 1, "synkero_da_inno_switch": 1},
)
def da_innovators():
    return float(np.maximum(biokero_da_inno_switch() + synkero_da_inno_switch(), 1))


@component.add(
    name="DA investment pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"da_continuous_investment": 1},
)
def da_investment_pipeline():
    return da_continuous_investment()


@component.add(
    name="DA projected demand",
    units="GWh",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_da_projected_demand"},
)
def da_projected_demand(x, final_subs=None):
    """
    Considering an annual growth of 1,2% from year 2019. Consumption is amount of jetfuel used. Pre efficiency losses.
    """
    return _hardcodedlookup_da_projected_demand(x, final_subs)


_hardcodedlookup_da_projected_demand = HardcodedLookups(
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
        64403.4,
        60410.3,
        60537.9,
        58822.8,
        55965.2,
        58015.1,
        62231.0,
        66230.6,
        70683.2,
        74366.6,
        78672.6,
        76667.4,
        72057.9,
        73415.2,
        76228.9,
        80822.1,
        82565.6,
        86139.5,
        83828.4,
        76672.3,
        78203.7,
        82852.8,
        77511.0,
        74449.5,
        74976.4,
        77159.7,
        80670.2,
        84531.2,
        86628.5,
        90415.1,
        91500.1,
        92598.1,
        93709.2,
        94833.7,
        95971.8,
        97123.4,
        98288.9,
        99468.4,
        100662.0,
        101870.0,
        103092.0,
        104329.0,
        105581.0,
        106848.0,
        108131.0,
        109428.0,
        110741.0,
        112070.0,
        113415.0,
        114776.0,
        116153.0,
        117547.0,
        118958.0,
        120385.0,
        121830.0,
        123292.0,
        124771.0,
        126269.0,
        127784.0,
        129317.0,
        130869.0,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_da_projected_demand",
)


@component.add(
    name="domestic aviation average cost",
    units="€/GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_cost": 1,
        "biokero_da_sector_share": 1,
        "jetfuel_da_sector_share": 1,
        "jetfuel_cost": 1,
        "synkero_cost": 1,
        "synkero_da_sector_share": 1,
    },
)
def domestic_aviation_average_cost():
    """
    €/GWh of jetfuel input equivalent. (Fuel cost + O&M).
    """
    return (
        biokero_cost() * biokero_da_sector_share()
        + jetfuel_cost() * jetfuel_da_sector_share()
        + synkero_cost() * synkero_da_sector_share()
    ) * 3600


@component.add(
    name="domestic aviation BioKero hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da": 1, "hvo_kerosene_h2_cost_scaler": 1},
)
def domestic_aviation_biokero_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return biokero_da() * hvo_kerosene_h2_cost_scaler() * 3.6


@component.add(
    name="domestic aviation biomass demand",
    units="GWh Biomass",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_da": 1,
        "hvo_jet_kerosene_fraction": 1,
        "hvo_jet_biomass_usage": 1,
    },
)
def domestic_aviation_biomass_demand():
    """
    Convert from GWh bio-Kerosene to GWh biomass
    """
    return biokero_da() / hvo_jet_kerosene_fraction() * hvo_jet_biomass_usage()


@component.add(
    name="domestic aviation emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_emission_factor": 1, "jetfuel_da": 1},
)
def domestic_aviation_emissions():
    return jetfuel_emission_factor() * jetfuel_da() * 3600


@component.add(
    name="domestic aviation hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_aviation_biokero_hydrogen_demand": 1,
        "domestic_aviation_synkero_hydrogen_demand": 1,
    },
)
def domestic_aviation_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return (
        domestic_aviation_biokero_hydrogen_demand()
        + domestic_aviation_synkero_hydrogen_demand()
    )


@component.add(
    name="domestic aviation SynKero hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_da": 1, "htj_kerosene_h2_cost_scaler": 1},
)
def domestic_aviation_synkero_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return synkero_da() * htj_kerosene_h2_cost_scaler() * 3.6


@component.add(
    name="Initial DA emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_da_emissions": 1},
    other_deps={
        "_initial_initial_da_emissions": {
            "initial": {"domestic_aviation_emissions": 1},
            "step": {},
        }
    },
)
def initial_da_emissions():
    return _initial_initial_da_emissions()


_initial_initial_da_emissions = Initial(
    lambda: domestic_aviation_emissions(), "_initial_initial_da_emissions"
)


@component.add(
    name="Jetfuel DA",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_jetfuel_da": 1},
    other_deps={
        "_integ_jetfuel_da": {
            "initial": {"da_initial_sector_activity": 1},
            "step": {
                "jetfuel_da_commissioning": 1,
                "jetfuel_da_decommissioning": 1,
                "jetfuel_da_economic_decommissioning": 1,
            },
        }
    },
)
def jetfuel_da():
    return _integ_jetfuel_da()


_integ_jetfuel_da = Integ(
    lambda: jetfuel_da_commissioning()
    - jetfuel_da_decommissioning()
    - jetfuel_da_economic_decommissioning(),
    lambda: da_initial_sector_activity(),
    "_integ_jetfuel_da",
)


@component.add(
    name="Jetfuel DA Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_da_construction": 1, "da_fuel_switch_time": 1},
)
def jetfuel_da_commissioning():
    return jetfuel_da_construction() / da_fuel_switch_time()


@component.add(
    name="Jetfuel DA competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_cost": 1, "jetfuel_cost": 2, "biokero_cost": 1},
)
def jetfuel_da_competitiveness():
    return float(
        np.minimum(synkero_cost() / jetfuel_cost(), biokero_cost() / jetfuel_cost())
    )


@component.add(
    name="Jetfuel DA Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_jetfuel_da_construction": 1},
    other_deps={
        "_integ_jetfuel_da_construction": {
            "initial": {
                "da_initial_sector_activity": 1,
                "jetfuel_lockin_period": 1,
                "da_fuel_switch_time": 1,
            },
            "step": {"jetfuel_da_investment": 1, "jetfuel_da_commissioning": 1},
        }
    },
)
def jetfuel_da_construction():
    return _integ_jetfuel_da_construction()


_integ_jetfuel_da_construction = Integ(
    lambda: jetfuel_da_investment() - jetfuel_da_commissioning(),
    lambda: da_initial_sector_activity()
    / jetfuel_lockin_period()
    * da_fuel_switch_time()
    * 1.04,
    "_integ_jetfuel_da_construction",
)


@component.add(
    name="Jetfuel DA Decommissioning",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_jetfuel_da_decommissioning": 1, "jetfuel_da": 1},
    other_deps={
        "_smooth_jetfuel_da_decommissioning": {
            "initial": {
                "jetfuel_da_delayed": 1,
                "jetfuel_da_economic_decommissioning_delayed": 1,
            },
            "step": {
                "jetfuel_da_delayed": 1,
                "jetfuel_da_economic_decommissioning_delayed": 1,
            },
        }
    },
)
def jetfuel_da_decommissioning():
    return float(
        np.maximum(
            0, float(np.minimum(_smooth_jetfuel_da_decommissioning(), jetfuel_da()))
        )
    )


_smooth_jetfuel_da_decommissioning = Smooth(
    lambda: jetfuel_da_delayed() - jetfuel_da_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: jetfuel_da_delayed() - jetfuel_da_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_jetfuel_da_decommissioning",
)


@component.add(
    name="Jetfuel DA delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_jetfuel_da_delayed": 1},
    other_deps={
        "_delayfixed_jetfuel_da_delayed": {
            "initial": {"da_initial_sector_activity": 1, "jetfuel_lockin_period": 2},
            "step": {"jetfuel_da_commissioning": 1},
        }
    },
)
def jetfuel_da_delayed():
    return _delayfixed_jetfuel_da_delayed()


_delayfixed_jetfuel_da_delayed = DelayFixed(
    lambda: jetfuel_da_commissioning(),
    lambda: jetfuel_lockin_period(),
    lambda: da_initial_sector_activity() / jetfuel_lockin_period(),
    time_step,
    "_delayfixed_jetfuel_da_delayed",
)


@component.add(
    name="Jetfuel DA economic decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "jetfuel_cost_difference": 2,
        "slope_decom": 1,
        "jetfuel_da": 1,
        "jetfuel_lockin_period": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def jetfuel_da_economic_decommissioning():
    return (
        if_then_else(
            jetfuel_cost_difference() > 1,
            lambda: (jetfuel_da() / jetfuel_lockin_period() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (jetfuel_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="Jetfuel DA economic decommissioning delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_jetfuel_da_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_jetfuel_da_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"jetfuel_da_economic_decommissioning": 1},
        }
    },
)
def jetfuel_da_economic_decommissioning_delayed():
    return _delayn_jetfuel_da_economic_decommissioning_delayed()


_delayn_jetfuel_da_economic_decommissioning_delayed = DelayN(
    lambda: jetfuel_da_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_jetfuel_da_economic_decommissioning_delayed",
)


@component.add(
    name="Jetfuel DA excess share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_da_sector_share": 1, "saf_min_share": 1},
)
def jetfuel_da_excess_share():
    return float(np.maximum(0, jetfuel_da_sector_share() - (1 - saf_min_share())))


@component.add(
    name="Jetfuel DA Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"da_investment_pipeline": 1, "jetfuel_da_investment_share": 1},
)
def jetfuel_da_investment():
    return da_investment_pipeline() * jetfuel_da_investment_share()


@component.add(
    name="Jetfuel DA investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"da_equalizer": 1, "jetfuel_da_level": 1},
)
def jetfuel_da_investment_share():
    return da_equalizer() * jetfuel_da_level()


@component.add(
    name="Jetfuel DA level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "jetfuel_da_competitiveness": 2,
        "jetfuel_da_sector_share": 1,
        "da_excess_activity": 1,
    },
)
def jetfuel_da_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - jetfuel_da_competitiveness()))))
        * float(np.maximum(0.1, jetfuel_da_sector_share()))
        * if_then_else(da_excess_activity() > 0, lambda: 0, lambda: 1)
        + jetfuel_da_competitiveness() * 0.001
    )


@component.add(
    name="Jetfuel DA sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_da": 1, "sum_da_activity": 1},
)
def jetfuel_da_sector_share():
    return jetfuel_da() / sum_da_activity()


@component.add(
    name="SAF DA missing share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "saf_min_share": 1,
        "saf_da_sector_share": 1,
        "synsaf_da_missing_share": 1,
    },
)
def saf_da_missing_share():
    return float(
        np.maximum(
            saf_min_share() - saf_da_sector_share() - synsaf_da_missing_share(), 0
        )
    )


@component.add(
    name="SAF DA sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da_sector_share": 1, "synkero_da_sector_share": 1},
)
def saf_da_sector_share():
    return biokero_da_sector_share() + synkero_da_sector_share()


@component.add(
    name="Subsidized BioKero DA Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_biokero_da_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_biokero_da_commissioning": {
            "initial": {"da_fuel_switch_time": 1},
            "step": {"subsidized_biokero_da_investment": 1},
        }
    },
)
def subsidized_biokero_da_commissioning():
    return _delayfixed_subsidized_biokero_da_commissioning()


_delayfixed_subsidized_biokero_da_commissioning = DelayFixed(
    lambda: subsidized_biokero_da_investment(),
    lambda: da_fuel_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_biokero_da_commissioning",
)


@component.add(
    name="Subsidized BioKero DA Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_biokero_da_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_biokero_da_decommissioning": {
            "initial": {"jetfuel_lockin_period": 1},
            "step": {"subsidized_biokero_da_commissioning": 1},
        }
    },
)
def subsidized_biokero_da_decommissioning():
    return _delayfixed_subsidized_biokero_da_decommissioning()


_delayfixed_subsidized_biokero_da_decommissioning = DelayFixed(
    lambda: subsidized_biokero_da_commissioning(),
    lambda: jetfuel_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_biokero_da_decommissioning",
)


@component.add(
    name="Subsidized BioKero DA Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "biokero_da_investment": 1,
        "hvo_kerosene_h2_cost_scaler": 1,
    },
)
def subsidized_biokero_da_investment():
    return (
        if_then_else(
            biokero_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: biokero_da_investment(),
            lambda: 0,
        )
        * 3600
        * hvo_kerosene_h2_cost_scaler()
        / 10**9
    )


@component.add(
    name="Subsidized SynKero DA Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_synkero_da_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_synkero_da_commissioning": {
            "initial": {"da_fuel_switch_time": 1},
            "step": {"subsidized_synkero_da_investment": 1},
        }
    },
)
def subsidized_synkero_da_commissioning():
    return _delayfixed_subsidized_synkero_da_commissioning()


_delayfixed_subsidized_synkero_da_commissioning = DelayFixed(
    lambda: subsidized_synkero_da_investment(),
    lambda: da_fuel_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_synkero_da_commissioning",
)


@component.add(
    name="Subsidized SynKero DA Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_synkero_da_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_synkero_da_decommissioning": {
            "initial": {"jetfuel_lockin_period": 1},
            "step": {"subsidized_synkero_da_commissioning": 1},
        }
    },
)
def subsidized_synkero_da_decommissioning():
    return _delayfixed_subsidized_synkero_da_decommissioning()


_delayfixed_subsidized_synkero_da_decommissioning = DelayFixed(
    lambda: subsidized_synkero_da_commissioning(),
    lambda: jetfuel_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_synkero_da_decommissioning",
)


@component.add(
    name="Subsidized SynKero DA Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synkero_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "synkero_da_investment": 1,
        "htj_kerosene_h2_cost_scaler": 1,
    },
)
def subsidized_synkero_da_investment():
    return (
        if_then_else(
            synkero_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: synkero_da_investment(),
            lambda: 0,
        )
        * 3600
        * htj_kerosene_h2_cost_scaler()
        / 10**9
    )


@component.add(
    name="sum DA activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_da": 1, "biokero_da": 1, "synkero_da": 1},
)
def sum_da_activity():
    return jetfuel_da() + biokero_da() + synkero_da()


@component.add(
    name="sum DA decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_da_decommissioning": 1,
        "jetfuel_da_decommissioning": 1,
        "synkero_da_decommissioning": 1,
        "jetfuel_da_economic_decommissioning": 1,
    },
)
def sum_da_decommissioning():
    return (
        biokero_da_decommissioning()
        + jetfuel_da_decommissioning()
        + synkero_da_decommissioning()
        + jetfuel_da_economic_decommissioning()
    )


@component.add(
    name="sum DA extra investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_da_extra_investment": 1, "synkero_da_extra_investment": 1},
)
def sum_da_extra_investment():
    return biokero_da_extra_investment() + synkero_da_extra_investment()


@component.add(
    name="Support BioKero DA",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_biokero_da_investment": 1,
        "biokero_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "jetfuel_lockin_period": 1,
    },
)
def support_biokero_da():
    return (
        subsidized_biokero_da_investment()
        * (green_h2_subsidy() + biokero_h2_subsidy())
        * jetfuel_lockin_period()
    )


@component.add(
    name="Support SynKero DA",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_synkero_da_investment": 1,
        "synkero_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "jetfuel_lockin_period": 1,
    },
)
def support_synkero_da():
    return (
        subsidized_synkero_da_investment()
        * (green_h2_subsidy() + synkero_h2_subsidy())
        * jetfuel_lockin_period()
    )


@component.add(
    name="SynKero DA",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_synkero_da": 1},
    other_deps={
        "_integ_synkero_da": {
            "initial": {},
            "step": {"synkero_da_commissioning": 1, "synkero_da_decommissioning": 1},
        }
    },
)
def synkero_da():
    return _integ_synkero_da()


_integ_synkero_da = Integ(
    lambda: synkero_da_commissioning() - synkero_da_decommissioning(),
    lambda: 0,
    "_integ_synkero_da",
)


@component.add(
    name="SynKero DA bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_da_desired_investment": 1},
)
def synkero_da_bid_share():
    return synkero_da_desired_investment()


@component.add(
    name="SynKero DA Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_da_construction": 1, "da_fuel_switch_time": 1},
)
def synkero_da_commissioning():
    return synkero_da_construction() / da_fuel_switch_time()


@component.add(
    name="SynKero DA Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_synkero_da_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_synkero_da_commissioning_subsidy_level": {
            "initial": {"da_fuel_switch_time": 1},
            "step": {"synkero_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def synkero_da_commissioning_subsidy_level():
    return _delayfixed_synkero_da_commissioning_subsidy_level()


_delayfixed_synkero_da_commissioning_subsidy_level = DelayFixed(
    lambda: synkero_h2_subsidy() + green_h2_subsidy(),
    lambda: da_fuel_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_synkero_da_commissioning_subsidy_level",
)


@component.add(
    name="SynKero DA competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_cost": 1, "synkero_cost": 2, "biokero_cost": 1},
)
def synkero_da_competitiveness():
    return float(
        np.minimum(jetfuel_cost() / synkero_cost(), biokero_cost() / synkero_cost())
    )


@component.add(
    name="SynKero DA Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_synkero_da_construction": 1},
    other_deps={
        "_integ_synkero_da_construction": {
            "initial": {},
            "step": {
                "synkero_da_innovators": 1,
                "synkero_da_investment": 1,
                "synkero_da_commissioning": 1,
            },
        }
    },
)
def synkero_da_construction():
    return _integ_synkero_da_construction()


_integ_synkero_da_construction = Integ(
    lambda: synkero_da_innovators()
    + synkero_da_investment()
    - synkero_da_commissioning(),
    lambda: 0,
    "_integ_synkero_da_construction",
)


@component.add(
    name="SynKero DA Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_da": 1, "jetfuel_lockin_period": 1},
)
def synkero_da_decommissioning():
    return synkero_da() / jetfuel_lockin_period()


@component.add(
    name="SynKero DA Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_synkero_da_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_synkero_da_decommissioning_subsidy_level": {
            "initial": {"jetfuel_lockin_period": 1},
            "step": {"synkero_da_commissioning_subsidy_level": 1},
        }
    },
)
def synkero_da_decommissioning_subsidy_level():
    return _delayfixed_synkero_da_decommissioning_subsidy_level()


_delayfixed_synkero_da_decommissioning_subsidy_level = DelayFixed(
    lambda: synkero_da_commissioning_subsidy_level(),
    lambda: jetfuel_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_synkero_da_decommissioning_subsidy_level",
)


@component.add(
    name="SynKero DA desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_synkero_da_desired_investment": 1},
    other_deps={
        "_smooth_synkero_da_desired_investment": {
            "initial": {
                "synkero_da_level": 2,
                "jetfuel_da_level": 1,
                "biokero_da_level": 1,
            },
            "step": {
                "synkero_da_level": 2,
                "jetfuel_da_level": 1,
                "biokero_da_level": 1,
            },
        }
    },
)
def synkero_da_desired_investment():
    return _smooth_synkero_da_desired_investment()


_smooth_synkero_da_desired_investment = Smooth(
    lambda: synkero_da_level()
    / (biokero_da_level() + jetfuel_da_level() + synkero_da_level()),
    lambda: 2,
    lambda: synkero_da_level()
    / (biokero_da_level() + jetfuel_da_level() + synkero_da_level()),
    lambda: 1,
    "_smooth_synkero_da_desired_investment",
)


@component.add(
    name="SynKero DA extra investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synsaf_da_missing_share": 1,
        "saf_da_missing_share": 1,
        "sum_da_activity": 1,
        "biokero_da_extra_investment": 1,
    },
)
def synkero_da_extra_investment():
    return (
        synsaf_da_missing_share() + saf_da_missing_share()
    ) * sum_da_activity() - biokero_da_extra_investment()


@component.add(
    name="SynKero DA HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "da_continuous_investment": 1,
        "htj_kerosene_h2_cost_scaler": 1,
        "synkero_da_bid_share": 1,
    },
)
def synkero_da_hba_volume():
    return (
        da_continuous_investment()
        * htj_kerosene_h2_cost_scaler()
        * 3.6
        * synkero_da_bid_share()
    )


@component.add(
    name="SynKero DA inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_da_competitiveness": 1, "inno_switch_level": 1},
)
def synkero_da_inno_switch():
    return if_then_else(
        synkero_da_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="SynKero DA innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_da_inno_switch": 1, "da_innovators": 1},
)
def synkero_da_innovator_share():
    return synkero_da_inno_switch() / da_innovators()


@component.add(
    name="SynKero DA Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"da_innovator_pipeline": 1, "synkero_da_innovator_share": 1},
)
def synkero_da_innovators():
    return da_innovator_pipeline() * synkero_da_innovator_share()


@component.add(
    name="SynKero DA Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "da_investment_pipeline": 1,
        "synkero_da_investment_share": 1,
        "synkero_da_extra_investment": 1,
    },
)
def synkero_da_investment():
    return (
        da_investment_pipeline() * synkero_da_investment_share()
        + synkero_da_extra_investment()
    )


@component.add(
    name="SynKero DA investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synkero_h2_subsidy": 1,
        "synkero_da_bid_share": 1,
        "synkero_da_level": 1,
        "da_equalizer": 1,
    },
)
def synkero_da_investment_share():
    return if_then_else(
        synkero_h2_subsidy() > 0.01,
        lambda: synkero_da_bid_share(),
        lambda: da_equalizer() * synkero_da_level(),
    )


@component.add(
    name="SynKero DA level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "synkero_da_competitiveness": 2,
        "synkero_da_sector_share": 1,
    },
)
def synkero_da_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - synkero_da_competitiveness()))))
        * float(np.maximum(0.1, synkero_da_sector_share()))
        + synkero_da_competitiveness() * 0.001
    )


@component.add(
    name="SynKero DA sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_da": 1, "sum_da_activity": 1},
)
def synkero_da_sector_share():
    return synkero_da() / sum_da_activity()


@component.add(
    name="SynKero DA subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_synkero_da_subsidy_cost": 1},
    other_deps={
        "_integ_synkero_da_subsidy_cost": {
            "initial": {},
            "step": {
                "synkero_da_commissioning_subsidy_level": 1,
                "subsidized_synkero_da_commissioning": 1,
                "subsidized_synkero_da_decommissioning": 1,
                "synkero_da_decommissioning_subsidy_level": 1,
            },
        }
    },
)
def synkero_da_subsidy_cost():
    return _integ_synkero_da_subsidy_cost()


_integ_synkero_da_subsidy_cost = Integ(
    lambda: synkero_da_commissioning_subsidy_level()
    * subsidized_synkero_da_commissioning()
    - synkero_da_decommissioning_subsidy_level()
    * subsidized_synkero_da_decommissioning(),
    lambda: 0,
    "_integ_synkero_da_subsidy_cost",
)


@component.add(
    name="SynSAF DA missing share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synsaf_min_share": 1, "synkero_da_sector_share": 1},
)
def synsaf_da_missing_share():
    return float(np.maximum(synsaf_min_share() - synkero_da_sector_share(), 0))
