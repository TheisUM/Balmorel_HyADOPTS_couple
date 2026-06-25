"""
Module international_aviation
Translated using PySD version 3.14.3
"""

@component.add(
    name="alternative Jetfuel cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_cost": 1, "synkero_cost": 1},
)
def alternative_jetfuel_cost():
    return float(np.minimum(biokero_cost(), synkero_cost()))


@component.add(
    name="aviation excess activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sum_ia_activity": 1, "jetfuel_excess_share": 1},
)
def aviation_excess_activity():
    return sum_ia_activity() * jetfuel_excess_share()


@component.add(
    name="BioKero IA",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biokero_ia": 1},
    other_deps={
        "_integ_biokero_ia": {
            "initial": {},
            "step": {"biokero_ia_commissioning": 1, "biokero_ia_decommissioning": 1},
        }
    },
)
def biokero_ia():
    return _integ_biokero_ia()


_integ_biokero_ia = Integ(
    lambda: biokero_ia_commissioning() - biokero_ia_decommissioning(),
    lambda: 0,
    "_integ_biokero_ia",
)


@component.add(
    name="BioKero IA bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia_desired_investment": 1},
)
def biokero_ia_bid_share():
    return biokero_ia_desired_investment()


@component.add(
    name="BioKero IA Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia_construction": 1, "ia_fuel_switch_time": 1},
)
def biokero_ia_commissioning():
    return biokero_ia_construction() / ia_fuel_switch_time()


@component.add(
    name="BioKero IA Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_biokero_ia_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_biokero_ia_commissioning_subsidy_level": {
            "initial": {"ia_fuel_switch_time": 1},
            "step": {"biokero_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def biokero_ia_commissioning_subsidy_level():
    return _delayfixed_biokero_ia_commissioning_subsidy_level()


_delayfixed_biokero_ia_commissioning_subsidy_level = DelayFixed(
    lambda: biokero_h2_subsidy() + green_h2_subsidy(),
    lambda: ia_fuel_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_biokero_ia_commissioning_subsidy_level",
)


@component.add(
    name="BioKero IA competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_cost": 1, "biokero_cost": 2, "jetfuel_cost": 1},
)
def biokero_ia_competitiveness():
    return float(
        np.minimum(synkero_cost() / biokero_cost(), jetfuel_cost() / biokero_cost())
    )


@component.add(
    name="BioKero IA Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biokero_ia_construction": 1},
    other_deps={
        "_integ_biokero_ia_construction": {
            "initial": {},
            "step": {
                "biokero_ia_innovators": 1,
                "biokero_ia_investment": 1,
                "biokero_ia_commissioning": 1,
            },
        }
    },
)
def biokero_ia_construction():
    return _integ_biokero_ia_construction()


_integ_biokero_ia_construction = Integ(
    lambda: biokero_ia_innovators()
    + biokero_ia_investment()
    - biokero_ia_commissioning(),
    lambda: 0,
    "_integ_biokero_ia_construction",
)


@component.add(
    name="BioKero IA Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia": 1, "jetfuel_lockin_period": 1},
)
def biokero_ia_decommissioning():
    return biokero_ia() / jetfuel_lockin_period()


@component.add(
    name="BioKero IA Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_biokero_ia_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_biokero_ia_decommissioning_subsidy_level": {
            "initial": {"jetfuel_lockin_period": 1},
            "step": {"biokero_ia_commissioning_subsidy_level": 1},
        }
    },
)
def biokero_ia_decommissioning_subsidy_level():
    return _delayfixed_biokero_ia_decommissioning_subsidy_level()


_delayfixed_biokero_ia_decommissioning_subsidy_level = DelayFixed(
    lambda: biokero_ia_commissioning_subsidy_level(),
    lambda: jetfuel_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_biokero_ia_decommissioning_subsidy_level",
)


@component.add(
    name="BioKero IA desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_biokero_ia_desired_investment": 1},
    other_deps={
        "_smooth_biokero_ia_desired_investment": {
            "initial": {
                "biokero_ia_level": 2,
                "synkero_ia_level": 1,
                "jetfuel_ia_level": 1,
            },
            "step": {
                "biokero_ia_level": 2,
                "synkero_ia_level": 1,
                "jetfuel_ia_level": 1,
            },
        }
    },
)
def biokero_ia_desired_investment():
    return _smooth_biokero_ia_desired_investment()


_smooth_biokero_ia_desired_investment = Smooth(
    lambda: biokero_ia_level()
    / (biokero_ia_level() + jetfuel_ia_level() + synkero_ia_level()),
    lambda: 2,
    lambda: biokero_ia_level()
    / (biokero_ia_level() + jetfuel_ia_level() + synkero_ia_level()),
    lambda: 1,
    "_smooth_biokero_ia_desired_investment",
)


@component.add(
    name="BioKero IA extra investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_ia_level": 2,
        "synkero_ia_level": 1,
        "saf_missing_share": 1,
        "sum_ia_activity": 1,
    },
)
def biokero_ia_extra_investment():
    """
    The extra investment into SAF, which does not have to be synthetic fuels, is divided between synth and bio SAF according to their usual investment levels.
    """
    return (
        zidz(biokero_ia_level(), biokero_ia_level() + synkero_ia_level())
        * saf_missing_share()
        * sum_ia_activity()
    )


@component.add(
    name="BioKero IA HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ia_continuous_investment": 1,
        "hvo_kerosene_h2_cost_scaler": 1,
        "biokero_ia_bid_share": 1,
    },
)
def biokero_ia_hba_volume():
    return (
        ia_continuous_investment()
        * hvo_kerosene_h2_cost_scaler()
        * 3.6
        * biokero_ia_bid_share()
    )


@component.add(
    name="BioKero IA inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia_competitiveness": 1, "inno_switch_level": 1},
)
def biokero_ia_inno_switch():
    return if_then_else(
        biokero_ia_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="BioKero IA innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia_inno_switch": 1, "ia_innovators": 1},
)
def biokero_ia_innovator_share():
    return biokero_ia_inno_switch() / ia_innovators()


@component.add(
    name="BioKero IA Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ia_innovator_pipeline": 1, "biokero_ia_innovator_share": 1},
)
def biokero_ia_innovators():
    return ia_innovator_pipeline() * biokero_ia_innovator_share()


@component.add(
    name="BioKero IA Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ia_investment_pipeline": 1,
        "biokero_ia_investment_share": 1,
        "biokero_ia_extra_investment": 1,
    },
)
def biokero_ia_investment():
    return (
        ia_investment_pipeline() * biokero_ia_investment_share()
        + biokero_ia_extra_investment()
    )


@component.add(
    name="BioKero IA investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_h2_subsidy": 1,
        "biokero_ia_bid_share": 1,
        "ia_equalizer": 1,
        "biokero_ia_level": 1,
    },
)
def biokero_ia_investment_share():
    return if_then_else(
        biokero_h2_subsidy() > 0.01,
        lambda: biokero_ia_bid_share(),
        lambda: ia_equalizer() * biokero_ia_level(),
    )


@component.add(
    name="BioKero IA level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "biokero_ia_competitiveness": 2,
        "biokero_ia_sector_share": 1,
    },
)
def biokero_ia_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - biokero_ia_competitiveness()))))
        * float(np.maximum(0.1, biokero_ia_sector_share()))
        + biokero_ia_competitiveness() * 0.001
    )


@component.add(
    name="BioKero IA sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia": 1, "sum_ia_activity": 1},
)
def biokero_ia_sector_share():
    return biokero_ia() / sum_ia_activity()


@component.add(
    name="BioKero IA subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biokero_ia_subsidy_cost": 1},
    other_deps={
        "_integ_biokero_ia_subsidy_cost": {
            "initial": {},
            "step": {
                "biokero_ia_commissioning_subsidy_level": 1,
                "subsidized_biokero_ia_commissioning": 1,
                "biokero_ia_decommissioning_subsidy_level": 1,
                "subsidized_biokero_ia_decommissioning": 1,
            },
        }
    },
)
def biokero_ia_subsidy_cost():
    return _integ_biokero_ia_subsidy_cost()


_integ_biokero_ia_subsidy_cost = Integ(
    lambda: biokero_ia_commissioning_subsidy_level()
    * subsidized_biokero_ia_commissioning()
    - biokero_ia_decommissioning_subsidy_level()
    * subsidized_biokero_ia_decommissioning(),
    lambda: 0,
    "_integ_biokero_ia_subsidy_cost",
)


@component.add(
    name="IA allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_ia_emissions": 1, "time": 1, "emissions_cap_lookup": 1},
)
def ia_allocated_emissions():
    return initial_ia_emissions() * emissions_cap_lookup(time())


@component.add(
    name="IA backlog",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ia_backlog": 1},
    other_deps={
        "_integ_ia_backlog": {
            "initial": {"sum_ia_activity": 1},
            "step": {"ia_current_demand": 1, "sum_ia_activity": 1},
        }
    },
)
def ia_backlog():
    return _integ_ia_backlog()


_integ_ia_backlog = Integ(
    lambda: ia_current_demand() - sum_ia_activity(),
    lambda: sum_ia_activity() * 0.012 * 0.5,
    "_integ_ia_backlog",
)


@component.add(
    name="IA continuous investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ia_forecast_demand": 1,
        "sum_ia_decommissioning": 1,
        "ia_backlog": 1,
        "ia_fuel_switch_time": 1,
        "sum_ia_activity": 1,
        "sum_aviation_extra_investment": 1,
        "innovators": 1,
    },
)
def ia_continuous_investment():
    return float(
        np.maximum(
            (
                ia_forecast_demand()
                + sum_ia_decommissioning()
                + ia_backlog() / ia_fuel_switch_time() / 3
                - sum_ia_activity()
                - sum_aviation_extra_investment()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="IA current demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "ia_projected_demand": 1},
)
def ia_current_demand():
    return ia_projected_demand(time())


@component.add(
    name="IA effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"international_aviation_average_cost": 1, "ia_current_demand": 1},
)
def ia_effective_cost():
    return international_aviation_average_cost() * ia_current_demand() / 1000000000.0


@component.add(
    name="IA equalizer",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_h2_subsidy": 1,
        "synkero_h2_subsidy": 2,
        "biokero_ia_bid_share": 2,
        "jetfuel_ia_level": 4,
        "synkero_ia_bid_share": 2,
        "synkero_ia_level": 2,
        "biokero_ia_level": 2,
    },
)
def ia_equalizer():
    return if_then_else(
        biokero_h2_subsidy() > 0.01,
        lambda: if_then_else(
            synkero_h2_subsidy() > 0.01,
            lambda: (1 - synkero_ia_bid_share() - biokero_ia_bid_share())
            / jetfuel_ia_level(),
            lambda: (1 - biokero_ia_bid_share())
            / (synkero_ia_level() + jetfuel_ia_level()),
        ),
        lambda: if_then_else(
            synkero_h2_subsidy() > 0.01,
            lambda: (1 - synkero_ia_bid_share())
            / (biokero_ia_level() + jetfuel_ia_level()),
            lambda: 1 / (biokero_ia_level() + synkero_ia_level() + jetfuel_ia_level()),
        ),
    )


@component.add(
    name="IA excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"international_aviation_emissions": 1, "ia_allocated_emissions": 1},
)
def ia_excess_emissions():
    return international_aviation_emissions() - ia_allocated_emissions()


@component.add(
    name="IA forecast demand",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_ia_forecast_demand": 1},
    other_deps={
        "_forecast_ia_forecast_demand": {
            "initial": {"ia_current_demand": 1},
            "step": {"ia_current_demand": 1, "ia_fuel_switch_time": 2},
        }
    },
)
def ia_forecast_demand():
    return _forecast_ia_forecast_demand()


_forecast_ia_forecast_demand = Forecast(
    lambda: ia_current_demand(),
    lambda: 3 * ia_fuel_switch_time(),
    lambda: ia_fuel_switch_time(),
    lambda: 0,
    "_forecast_ia_forecast_demand",
)


@component.add(
    name="IA fuel switch time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ia_fuel_switch_time():
    return 0.5


@component.add(
    name="IA initial sector activity",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_ia_initial_sector_activity": 1},
    other_deps={
        "_initial_ia_initial_sector_activity": {
            "initial": {"ia_current_demand": 1},
            "step": {},
        }
    },
)
def ia_initial_sector_activity():
    return _initial_ia_initial_sector_activity()


_initial_ia_initial_sector_activity = Initial(
    lambda: ia_current_demand(), "_initial_ia_initial_sector_activity"
)


@component.add(
    name="IA innovator pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ia_continuous_investment": 1, "innovators": 2},
)
def ia_innovator_pipeline():
    return ia_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="IA innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia_inno_switch": 1, "synkero_ia_inno_switch": 1},
)
def ia_innovators():
    return float(np.maximum(biokero_ia_inno_switch() + synkero_ia_inno_switch(), 1))


@component.add(
    name="IA investment pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ia_continuous_investment": 1},
)
def ia_investment_pipeline():
    return ia_continuous_investment()


@component.add(
    name="IA projected demand",
    units="GWh",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_ia_projected_demand"},
)
def ia_projected_demand(x, final_subs=None):
    """
    Considering an annual growth of 1,2% from year 2019.
    """
    return _hardcodedlookup_ia_projected_demand(x, final_subs)


_hardcodedlookup_ia_projected_demand = HardcodedLookups(
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
        295302,
        286815,
        307477,
        322972,
        340650,
        356308,
        370663,
        387639,
        411181,
        442206,
        463700,
        453780,
        447489,
        454576,
        486965,
        512323,
        533393,
        548726,
        551816,
        509099,
        508465,
        525469,
        516769,
        519055,
        524542,
        541947,
        563051,
        606262,
        632335,
        641196,
        648890,
        656677,
        664557,
        672531,
        680602,
        688769,
        697034,
        705399,
        713863,
        722430,
        731099,
        739872,
        748751,
        757736,
        766828,
        776030,
        785343,
        794767,
        804304,
        813956,
        823723,
        833608,
        843611,
        853734,
        863979,
        874347,
        884839,
        895457,
        906203,
        917077,
        928082,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_ia_projected_demand",
)


@component.add(
    name="Initial IA emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_ia_emissions": 1},
    other_deps={
        "_initial_initial_ia_emissions": {
            "initial": {"international_aviation_emissions": 1},
            "step": {},
        }
    },
)
def initial_ia_emissions():
    return _initial_initial_ia_emissions()


_initial_initial_ia_emissions = Initial(
    lambda: international_aviation_emissions(), "_initial_initial_ia_emissions"
)


@component.add(
    name="international aviation average cost",
    units="€/GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_ia_sector_share": 1,
        "biokero_cost": 1,
        "jetfuel_ia_sector_share": 1,
        "jetfuel_cost": 1,
        "synkero_ia_sector_share": 1,
        "synkero_cost": 1,
    },
)
def international_aviation_average_cost():
    """
    €/GWh of jetfuel input equivalent. (Fuel cost only)
    """
    return (
        biokero_ia_sector_share() * biokero_cost()
        + jetfuel_ia_sector_share() * jetfuel_cost()
        + synkero_ia_sector_share() * synkero_cost()
    ) * 3600


@component.add(
    name="international aviation BioKero hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia": 1, "hvo_kerosene_h2_cost_scaler": 1},
)
def international_aviation_biokero_hydrogen_demand():
    """
    Convert from GWh jetfuel to GWh G2 - then to MWh H2 - then to tons H2
    """
    return biokero_ia() * hvo_kerosene_h2_cost_scaler() * 3.6


@component.add(
    name="international aviation biomass demand",
    units="GWh Biomass",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_ia": 1,
        "hvo_jet_kerosene_fraction": 1,
        "hvo_jet_biomass_usage": 1,
    },
)
def international_aviation_biomass_demand():
    """
    Convert to GWh biomass
    """
    return biokero_ia() / hvo_jet_kerosene_fraction() * hvo_jet_biomass_usage()


@component.add(
    name="international aviation emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_emission_factor": 1, "jetfuel_ia": 1},
)
def international_aviation_emissions():
    return jetfuel_emission_factor() * jetfuel_ia() * 3600


@component.add(
    name="international aviation hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "international_aviation_synkero_hydrogen_demand": 1,
        "international_aviation_biokero_hydrogen_demand": 1,
    },
)
def international_aviation_hydrogen_demand():
    """
    Convert from GWh jetfuel to GWh G2 - then to MWh H2 - then to tons H2
    """
    return (
        international_aviation_synkero_hydrogen_demand()
        + international_aviation_biokero_hydrogen_demand()
    )


@component.add(
    name="international aviation SynKero hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_ia": 1, "htj_kerosene_h2_cost_scaler": 1},
)
def international_aviation_synkero_hydrogen_demand():
    """
    Convert from GWh jetfuel to GWh G2 - then to MWh H2 - then to tons H2
    """
    return synkero_ia() * htj_kerosene_h2_cost_scaler() * 3.6


@component.add(
    name="Jetfuel CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_cost": 1,
        "synkero_cost": 1,
        "jetfuel_cost_wo_co2": 1,
        "jetfuel_emission_factor": 1,
    },
)
def jetfuel_co2_wtp():
    return (
        float(np.minimum(biokero_cost(), synkero_cost())) - jetfuel_cost_wo_co2()
    ) / jetfuel_emission_factor()


@component.add(
    name="Jetfuel cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_cost": 1, "alternative_jetfuel_cost": 1},
)
def jetfuel_cost_difference():
    return jetfuel_cost() / alternative_jetfuel_cost()


@component.add(
    name="Jetfuel excess share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_ia_sector_share": 1, "saf_min_share": 1},
)
def jetfuel_excess_share():
    return float(np.maximum(0, jetfuel_ia_sector_share() - (1 - saf_min_share())))


@component.add(
    name="Jetfuel IA",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_jetfuel_ia": 1},
    other_deps={
        "_integ_jetfuel_ia": {
            "initial": {"ia_initial_sector_activity": 1},
            "step": {
                "jetfuel_ia_commissioning": 1,
                "jetfuel_ia_decommissioning": 1,
                "jetfuel_ia_economic_decommissioning": 1,
            },
        }
    },
)
def jetfuel_ia():
    return _integ_jetfuel_ia()


_integ_jetfuel_ia = Integ(
    lambda: jetfuel_ia_commissioning()
    - jetfuel_ia_decommissioning()
    - jetfuel_ia_economic_decommissioning(),
    lambda: ia_initial_sector_activity(),
    "_integ_jetfuel_ia",
)


@component.add(
    name="Jetfuel IA Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_ia_construction": 1, "ia_fuel_switch_time": 1},
)
def jetfuel_ia_commissioning():
    return jetfuel_ia_construction() / ia_fuel_switch_time()


@component.add(
    name="Jetfuel IA competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_cost": 1, "jetfuel_cost": 2, "biokero_cost": 1},
)
def jetfuel_ia_competitiveness():
    return float(
        np.minimum(synkero_cost() / jetfuel_cost(), biokero_cost() / jetfuel_cost())
    )


@component.add(
    name="Jetfuel IA Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_jetfuel_ia_construction": 1},
    other_deps={
        "_integ_jetfuel_ia_construction": {
            "initial": {
                "ia_initial_sector_activity": 1,
                "jetfuel_lockin_period": 1,
                "ia_fuel_switch_time": 1,
            },
            "step": {"jetfuel_ia_investment": 1, "jetfuel_ia_commissioning": 1},
        }
    },
)
def jetfuel_ia_construction():
    return _integ_jetfuel_ia_construction()


_integ_jetfuel_ia_construction = Integ(
    lambda: jetfuel_ia_investment() - jetfuel_ia_commissioning(),
    lambda: ia_initial_sector_activity()
    / jetfuel_lockin_period()
    * ia_fuel_switch_time()
    * 1.04,
    "_integ_jetfuel_ia_construction",
)


@component.add(
    name="Jetfuel IA Decommissioning",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_jetfuel_ia_decommissioning": 1, "jetfuel_ia": 1},
    other_deps={
        "_smooth_jetfuel_ia_decommissioning": {
            "initial": {
                "jetfuel_ia_delayed": 1,
                "jetfuel_ia_economic_decommissioning_delayed": 1,
            },
            "step": {
                "jetfuel_ia_delayed": 1,
                "jetfuel_ia_economic_decommissioning_delayed": 1,
            },
        }
    },
)
def jetfuel_ia_decommissioning():
    return float(
        np.maximum(
            0, float(np.minimum(_smooth_jetfuel_ia_decommissioning(), jetfuel_ia()))
        )
    )


_smooth_jetfuel_ia_decommissioning = Smooth(
    lambda: jetfuel_ia_delayed() - jetfuel_ia_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: jetfuel_ia_delayed() - jetfuel_ia_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_jetfuel_ia_decommissioning",
)


@component.add(
    name="Jetfuel IA delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_jetfuel_ia_delayed": 1},
    other_deps={
        "_delayfixed_jetfuel_ia_delayed": {
            "initial": {"ia_initial_sector_activity": 1, "jetfuel_lockin_period": 2},
            "step": {"jetfuel_ia_commissioning": 1},
        }
    },
)
def jetfuel_ia_delayed():
    return _delayfixed_jetfuel_ia_delayed()


_delayfixed_jetfuel_ia_delayed = DelayFixed(
    lambda: jetfuel_ia_commissioning(),
    lambda: jetfuel_lockin_period(),
    lambda: ia_initial_sector_activity() / jetfuel_lockin_period(),
    time_step,
    "_delayfixed_jetfuel_ia_delayed",
)


@component.add(
    name="Jetfuel IA economic decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "jetfuel_cost_difference": 2,
        "slope_decom": 1,
        "jetfuel_lockin_period": 1,
        "intersec_decom": 1,
        "jetfuel_ia": 1,
        "economic_decommissioning": 1,
    },
)
def jetfuel_ia_economic_decommissioning():
    return (
        if_then_else(
            jetfuel_cost_difference() > 1,
            lambda: (jetfuel_ia() / jetfuel_lockin_period() * 3)
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
    name="Jetfuel IA economic decommissioning delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_jetfuel_ia_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_jetfuel_ia_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"jetfuel_ia_economic_decommissioning": 1},
        }
    },
)
def jetfuel_ia_economic_decommissioning_delayed():
    return _delayn_jetfuel_ia_economic_decommissioning_delayed()


_delayn_jetfuel_ia_economic_decommissioning_delayed = DelayN(
    lambda: jetfuel_ia_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_jetfuel_ia_economic_decommissioning_delayed",
)


@component.add(
    name="Jetfuel IA Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ia_investment_pipeline": 1, "jetfuel_ia_investment_share": 1},
)
def jetfuel_ia_investment():
    return ia_investment_pipeline() * jetfuel_ia_investment_share()


@component.add(
    name="Jetfuel IA investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ia_equalizer": 1, "jetfuel_ia_level": 1},
)
def jetfuel_ia_investment_share():
    return ia_equalizer() * jetfuel_ia_level()


@component.add(
    name="Jetfuel IA level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "jetfuel_ia_competitiveness": 2,
        "jetfuel_ia_sector_share": 1,
        "aviation_excess_activity": 1,
    },
)
def jetfuel_ia_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - jetfuel_ia_competitiveness()))))
        * float(np.maximum(0.1, jetfuel_ia_sector_share()))
        * if_then_else(aviation_excess_activity() > 0, lambda: 0, lambda: 1)
        + jetfuel_ia_competitiveness() * 0.001
    )


@component.add(
    name="Jetfuel IA sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_ia": 1, "sum_ia_activity": 1},
)
def jetfuel_ia_sector_share():
    return jetfuel_ia() / sum_ia_activity()


@component.add(
    name="jetfuel lockin period",
    units="years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def jetfuel_lockin_period():
    return 5


@component.add(
    name="SAF min share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "saf_min_share_lookup": 1, "hard_regulation": 1},
)
def saf_min_share():
    return saf_min_share_lookup(time()) * hard_regulation()


@component.add(
    name="SAF min share LOOKUP",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_saf_min_share_lookup"},
)
def saf_min_share_lookup(x, final_subs=None):
    return _hardcodedlookup_saf_min_share_lookup(x, final_subs)


_hardcodedlookup_saf_min_share_lookup = HardcodedLookups(
    [2022.0, 2030.0, 2050.0],
    [0.0, 0.02, 0.7],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_saf_min_share_lookup",
)


@component.add(
    name="SAF missing share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"saf_min_share": 1, "saf_sector_share": 1, "synsaf_missing_share": 1},
)
def saf_missing_share():
    return float(
        np.maximum(saf_min_share() - saf_sector_share() - synsaf_missing_share(), 0)
    )


@component.add(
    name="SAF sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia_sector_share": 1, "synkero_ia_sector_share": 1},
)
def saf_sector_share():
    return biokero_ia_sector_share() + synkero_ia_sector_share()


@component.add(
    name="Subsidized BioKero IA Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_biokero_ia_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_biokero_ia_commissioning": {
            "initial": {"ia_fuel_switch_time": 1},
            "step": {"subsidized_biokero_ia_investment": 1},
        }
    },
)
def subsidized_biokero_ia_commissioning():
    return _delayfixed_subsidized_biokero_ia_commissioning()


_delayfixed_subsidized_biokero_ia_commissioning = DelayFixed(
    lambda: subsidized_biokero_ia_investment(),
    lambda: ia_fuel_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_biokero_ia_commissioning",
)


@component.add(
    name="Subsidized BioKero IA Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_biokero_ia_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_biokero_ia_decommissioning": {
            "initial": {"jetfuel_lockin_period": 1},
            "step": {"subsidized_biokero_ia_commissioning": 1},
        }
    },
)
def subsidized_biokero_ia_decommissioning():
    return _delayfixed_subsidized_biokero_ia_decommissioning()


_delayfixed_subsidized_biokero_ia_decommissioning = DelayFixed(
    lambda: subsidized_biokero_ia_commissioning(),
    lambda: jetfuel_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_biokero_ia_decommissioning",
)


@component.add(
    name="Subsidized BioKero IA Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "biokero_ia_investment": 1,
        "hvo_kerosene_h2_cost_scaler": 1,
    },
)
def subsidized_biokero_ia_investment():
    return (
        if_then_else(
            biokero_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: biokero_ia_investment(),
            lambda: 0,
        )
        * 3600
        * hvo_kerosene_h2_cost_scaler()
        / 10**9
    )


@component.add(
    name="Subsidized SynKero IA Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_synkero_ia_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_synkero_ia_commissioning": {
            "initial": {"ia_fuel_switch_time": 1},
            "step": {"subsidized_synkero_ia_investment": 1},
        }
    },
)
def subsidized_synkero_ia_commissioning():
    return _delayfixed_subsidized_synkero_ia_commissioning()


_delayfixed_subsidized_synkero_ia_commissioning = DelayFixed(
    lambda: subsidized_synkero_ia_investment(),
    lambda: ia_fuel_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_synkero_ia_commissioning",
)


@component.add(
    name="Subsidized SynKero IA Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_synkero_ia_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_synkero_ia_decommissioning": {
            "initial": {"jetfuel_lockin_period": 1},
            "step": {"subsidized_synkero_ia_commissioning": 1},
        }
    },
)
def subsidized_synkero_ia_decommissioning():
    return _delayfixed_subsidized_synkero_ia_decommissioning()


_delayfixed_subsidized_synkero_ia_decommissioning = DelayFixed(
    lambda: subsidized_synkero_ia_commissioning(),
    lambda: jetfuel_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_synkero_ia_decommissioning",
)


@component.add(
    name="Subsidized SynKero IA Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synkero_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "synkero_ia_investment": 1,
        "htj_kerosene_h2_cost_scaler": 1,
    },
)
def subsidized_synkero_ia_investment():
    return (
        if_then_else(
            synkero_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: synkero_ia_investment(),
            lambda: 0,
        )
        * 3600
        * htj_kerosene_h2_cost_scaler()
        / 10**9
    )


@component.add(
    name="sum aviation extra investment",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_ia_extra_investment": 1, "synkero_ia_extra_investment": 1},
)
def sum_aviation_extra_investment():
    return biokero_ia_extra_investment() + synkero_ia_extra_investment()


@component.add(
    name="sum IA activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_ia": 1, "biokero_ia": 1, "synkero_ia": 1},
)
def sum_ia_activity():
    return jetfuel_ia() + biokero_ia() + synkero_ia()


@component.add(
    name="sum IA decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_ia_decommissioning": 1,
        "jetfuel_ia_decommissioning": 1,
        "synkero_ia_decommissioning": 1,
        "jetfuel_ia_economic_decommissioning": 1,
    },
)
def sum_ia_decommissioning():
    return (
        biokero_ia_decommissioning()
        + jetfuel_ia_decommissioning()
        + synkero_ia_decommissioning()
        + jetfuel_ia_economic_decommissioning()
    )


@component.add(
    name="Support BioKero IA",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_biokero_ia_investment": 1,
        "biokero_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "jetfuel_lockin_period": 1,
    },
)
def support_biokero_ia():
    return (
        subsidized_biokero_ia_investment()
        * (green_h2_subsidy() + biokero_h2_subsidy())
        * jetfuel_lockin_period()
    )


@component.add(
    name="Support SynKero IA",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_synkero_ia_investment": 1,
        "synkero_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "jetfuel_lockin_period": 1,
    },
)
def support_synkero_ia():
    return (
        subsidized_synkero_ia_investment()
        * (green_h2_subsidy() + synkero_h2_subsidy())
        * jetfuel_lockin_period()
    )


@component.add(
    name="SynKero IA",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_synkero_ia": 1},
    other_deps={
        "_integ_synkero_ia": {
            "initial": {},
            "step": {"synkero_ia_commissioning": 1, "synkero_ia_decommissioning": 1},
        }
    },
)
def synkero_ia():
    return _integ_synkero_ia()


_integ_synkero_ia = Integ(
    lambda: synkero_ia_commissioning() - synkero_ia_decommissioning(),
    lambda: 0,
    "_integ_synkero_ia",
)


@component.add(
    name="SynKero IA bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_ia_desired_investment": 1},
)
def synkero_ia_bid_share():
    return synkero_ia_desired_investment()


@component.add(
    name="SynKero IA Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_ia_construction": 1, "ia_fuel_switch_time": 1},
)
def synkero_ia_commissioning():
    return synkero_ia_construction() / ia_fuel_switch_time()


@component.add(
    name="SynKero IA Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_synkero_ia_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_synkero_ia_commissioning_subsidy_level": {
            "initial": {"ia_fuel_switch_time": 1},
            "step": {"synkero_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def synkero_ia_commissioning_subsidy_level():
    return _delayfixed_synkero_ia_commissioning_subsidy_level()


_delayfixed_synkero_ia_commissioning_subsidy_level = DelayFixed(
    lambda: synkero_h2_subsidy() + green_h2_subsidy(),
    lambda: ia_fuel_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_synkero_ia_commissioning_subsidy_level",
)


@component.add(
    name="SynKero IA competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_cost": 1, "synkero_cost": 2, "biokero_cost": 1},
)
def synkero_ia_competitiveness():
    return float(
        np.minimum(jetfuel_cost() / synkero_cost(), biokero_cost() / synkero_cost())
    )


@component.add(
    name="SynKero IA Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_synkero_ia_construction": 1},
    other_deps={
        "_integ_synkero_ia_construction": {
            "initial": {},
            "step": {
                "synkero_ia_innovators": 1,
                "synkero_ia_investment": 1,
                "synkero_ia_commissioning": 1,
            },
        }
    },
)
def synkero_ia_construction():
    return _integ_synkero_ia_construction()


_integ_synkero_ia_construction = Integ(
    lambda: synkero_ia_innovators()
    + synkero_ia_investment()
    - synkero_ia_commissioning(),
    lambda: 0,
    "_integ_synkero_ia_construction",
)


@component.add(
    name="SynKero IA Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_ia": 1, "jetfuel_lockin_period": 1},
)
def synkero_ia_decommissioning():
    return synkero_ia() / jetfuel_lockin_period()


@component.add(
    name="SynKero IA Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_synkero_ia_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_synkero_ia_decommissioning_subsidy_level": {
            "initial": {"jetfuel_lockin_period": 1},
            "step": {"synkero_ia_commissioning_subsidy_level": 1},
        }
    },
)
def synkero_ia_decommissioning_subsidy_level():
    return _delayfixed_synkero_ia_decommissioning_subsidy_level()


_delayfixed_synkero_ia_decommissioning_subsidy_level = DelayFixed(
    lambda: synkero_ia_commissioning_subsidy_level(),
    lambda: jetfuel_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_synkero_ia_decommissioning_subsidy_level",
)


@component.add(
    name="SynKero IA desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_synkero_ia_desired_investment": 1},
    other_deps={
        "_smooth_synkero_ia_desired_investment": {
            "initial": {
                "synkero_ia_level": 2,
                "biokero_ia_level": 1,
                "jetfuel_ia_level": 1,
            },
            "step": {
                "synkero_ia_level": 2,
                "biokero_ia_level": 1,
                "jetfuel_ia_level": 1,
            },
        }
    },
)
def synkero_ia_desired_investment():
    return _smooth_synkero_ia_desired_investment()


_smooth_synkero_ia_desired_investment = Smooth(
    lambda: synkero_ia_level()
    / (biokero_ia_level() + jetfuel_ia_level() + synkero_ia_level()),
    lambda: 2,
    lambda: synkero_ia_level()
    / (biokero_ia_level() + jetfuel_ia_level() + synkero_ia_level()),
    lambda: 1,
    "_smooth_synkero_ia_desired_investment",
)


@component.add(
    name="SynKero IA extra investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synsaf_missing_share": 1,
        "saf_missing_share": 1,
        "sum_ia_activity": 1,
        "biokero_ia_extra_investment": 1,
    },
)
def synkero_ia_extra_investment():
    return (
        synsaf_missing_share() + saf_missing_share()
    ) * sum_ia_activity() - biokero_ia_extra_investment()


@component.add(
    name="SynKero IA HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ia_continuous_investment": 1,
        "htj_kerosene_h2_cost_scaler": 1,
        "synkero_ia_bid_share": 1,
    },
)
def synkero_ia_hba_volume():
    return (
        ia_continuous_investment()
        * htj_kerosene_h2_cost_scaler()
        * 3.6
        * synkero_ia_bid_share()
    )


@component.add(
    name="SynKero IA inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_ia_competitiveness": 1, "inno_switch_level": 1},
)
def synkero_ia_inno_switch():
    return if_then_else(
        synkero_ia_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="SynKero IA innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_ia_inno_switch": 1, "ia_innovators": 1},
)
def synkero_ia_innovator_share():
    return synkero_ia_inno_switch() / ia_innovators()


@component.add(
    name="SynKero IA Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ia_innovator_pipeline": 1, "synkero_ia_innovator_share": 1},
)
def synkero_ia_innovators():
    return ia_innovator_pipeline() * synkero_ia_innovator_share()


@component.add(
    name="SynKero IA Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ia_investment_pipeline": 1,
        "synkero_ia_investment_share": 1,
        "synkero_ia_extra_investment": 1,
    },
)
def synkero_ia_investment():
    return (
        ia_investment_pipeline() * synkero_ia_investment_share()
        + synkero_ia_extra_investment()
    )


@component.add(
    name="SynKero IA investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synkero_h2_subsidy": 1,
        "synkero_ia_bid_share": 1,
        "synkero_ia_level": 1,
        "ia_equalizer": 1,
    },
)
def synkero_ia_investment_share():
    return if_then_else(
        synkero_h2_subsidy() > 0.01,
        lambda: synkero_ia_bid_share(),
        lambda: ia_equalizer() * synkero_ia_level(),
    )


@component.add(
    name="SynKero IA level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "synkero_ia_competitiveness": 2,
        "synkero_ia_sector_share": 1,
    },
)
def synkero_ia_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - synkero_ia_competitiveness()))))
        * float(np.maximum(0.1, synkero_ia_sector_share()))
        + synkero_ia_competitiveness() * 0.001
    )


@component.add(
    name="SynKero IA sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_ia": 1, "sum_ia_activity": 1},
)
def synkero_ia_sector_share():
    return synkero_ia() / sum_ia_activity()


@component.add(
    name="SynKero IA subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_synkero_ia_subsidy_cost": 1},
    other_deps={
        "_integ_synkero_ia_subsidy_cost": {
            "initial": {},
            "step": {
                "synkero_ia_commissioning_subsidy_level": 1,
                "subsidized_synkero_ia_commissioning": 1,
                "synkero_ia_decommissioning_subsidy_level": 1,
                "subsidized_synkero_ia_decommissioning": 1,
            },
        }
    },
)
def synkero_ia_subsidy_cost():
    return _integ_synkero_ia_subsidy_cost()


_integ_synkero_ia_subsidy_cost = Integ(
    lambda: synkero_ia_commissioning_subsidy_level()
    * subsidized_synkero_ia_commissioning()
    - synkero_ia_decommissioning_subsidy_level()
    * subsidized_synkero_ia_decommissioning(),
    lambda: 0,
    "_integ_synkero_ia_subsidy_cost",
)


@component.add(
    name="SynSAF min share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "synsaf_min_share_lookup": 1, "hard_regulation": 1},
)
def synsaf_min_share():
    return synsaf_min_share_lookup(time()) * hard_regulation()


@component.add(
    name="SynSAF min share LOOKUP",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_synsaf_min_share_lookup"},
)
def synsaf_min_share_lookup(x, final_subs=None):
    return _hardcodedlookup_synsaf_min_share_lookup(x, final_subs)


_hardcodedlookup_synsaf_min_share_lookup = HardcodedLookups(
    [2022.0, 2030.0, 2050.0],
    [0.0, 0.012, 0.35],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_synsaf_min_share_lookup",
)


@component.add(
    name="SynSAF missing share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synsaf_min_share": 1, "synkero_ia_sector_share": 1},
)
def synsaf_missing_share():
    return float(np.maximum(synsaf_min_share() - synkero_ia_sector_share(), 0))
