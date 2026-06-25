"""
Module naphtha_for_hvc
Translated using PySD version 3.14.3
"""

@component.add(
    name="alternative naphtha cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha_cost": 1, "synnaphtha_cost": 1},
)
def alternative_naphtha_cost():
    return float(np.minimum(bionaphtha_cost(), synnaphtha_cost()))


@component.add(
    name="BioNaphtha",
    units="MT naphtha",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_bionaphtha": 1},
    other_deps={
        "_integ_bionaphtha": {
            "initial": {},
            "step": {"bionaphtha_commissioning": 1, "bionaphtha_decommissioning": 1},
        }
    },
)
def bionaphtha():
    return _integ_bionaphtha()


_integ_bionaphtha = Integ(
    lambda: bionaphtha_commissioning() - bionaphtha_decommissioning(),
    lambda: 0,
    "_integ_bionaphtha",
)


@component.add(
    name="BioNaphtha bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha_desired_investment": 1},
)
def bionaphtha_bid_share():
    return bionaphtha_desired_investment()


@component.add(
    name="BioNaphtha Commissioning",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha_construction": 1, "feedstock_switch_time": 1},
)
def bionaphtha_commissioning():
    return bionaphtha_construction() / feedstock_switch_time()


@component.add(
    name="BioNaphtha Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_bionaphtha_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_bionaphtha_commissioning_subsidy_level": {
            "initial": {"feedstock_switch_time": 1},
            "step": {"bionaphtha_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def bionaphtha_commissioning_subsidy_level():
    return _delayfixed_bionaphtha_commissioning_subsidy_level()


_delayfixed_bionaphtha_commissioning_subsidy_level = DelayFixed(
    lambda: bionaphtha_h2_subsidy() + green_h2_subsidy(),
    lambda: feedstock_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_bionaphtha_commissioning_subsidy_level",
)


@component.add(
    name="BioNaphtha competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_cost": 1, "bionaphtha_cost": 2, "synnaphtha_cost": 1},
)
def bionaphtha_competitiveness():
    return float(
        np.minimum(
            naphtha_cost() / bionaphtha_cost(), synnaphtha_cost() / bionaphtha_cost()
        )
    )


@component.add(
    name="BioNaphtha Construction",
    units="MT naphtha",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_bionaphtha_construction": 1},
    other_deps={
        "_integ_bionaphtha_construction": {
            "initial": {},
            "step": {
                "bionaphtha_innovators": 1,
                "bionaphtha_investment": 1,
                "bionaphtha_commissioning": 1,
            },
        }
    },
)
def bionaphtha_construction():
    return _integ_bionaphtha_construction()


_integ_bionaphtha_construction = Integ(
    lambda: bionaphtha_innovators()
    + bionaphtha_investment()
    - bionaphtha_commissioning(),
    lambda: 0,
    "_integ_bionaphtha_construction",
)


@component.add(
    name="BioNaphtha Decommissioning",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha": 1, "feedstock_lockin_period": 1},
)
def bionaphtha_decommissioning():
    return bionaphtha() / feedstock_lockin_period()


@component.add(
    name="BioNaphtha Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_bionaphtha_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_bionaphtha_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"bionaphtha_commissioning_subsidy_level": 1},
        }
    },
)
def bionaphtha_decommissioning_subsidy_level():
    return _delayfixed_bionaphtha_decommissioning_subsidy_level()


_delayfixed_bionaphtha_decommissioning_subsidy_level = DelayFixed(
    lambda: bionaphtha_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_bionaphtha_decommissioning_subsidy_level",
)


@component.add(
    name="BioNaphtha desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_bionaphtha_desired_investment": 1},
    other_deps={
        "_smooth_bionaphtha_desired_investment": {
            "initial": {
                "bionaphtha_level": 2,
                "fossil_naphtha_level": 1,
                "synnaphtha_level": 1,
            },
            "step": {
                "bionaphtha_level": 2,
                "fossil_naphtha_level": 1,
                "synnaphtha_level": 1,
            },
        }
    },
)
def bionaphtha_desired_investment():
    return _smooth_bionaphtha_desired_investment()


_smooth_bionaphtha_desired_investment = Smooth(
    lambda: bionaphtha_level()
    / (bionaphtha_level() + fossil_naphtha_level() + synnaphtha_level()),
    lambda: 2,
    lambda: bionaphtha_level()
    / (bionaphtha_level() + fossil_naphtha_level() + synnaphtha_level()),
    lambda: 1,
    "_smooth_bionaphtha_desired_investment",
)


@component.add(
    name="BioNaphtha H2 Usage",
    units="MWh H2/t Naphtha",
    comp_type="Constant",
    comp_subtype="Normal",
)
def bionaphtha_h2_usage():
    return 0.78


@component.add(
    name="BioNaphtha HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "naphtha_continuous_investment": 1,
        "bionaphtha_h2_usage": 1,
        "bionaphtha_bid_share": 1,
    },
)
def bionaphtha_hba_volume():
    return (
        naphtha_continuous_investment()
        * bionaphtha_h2_usage()
        / 33.33
        * 10**6
        * bionaphtha_bid_share()
    )


@component.add(
    name="BioNaphtha hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha": 1, "bionaphtha_h2_usage": 1},
)
def bionaphtha_hydrogen_demand():
    return bionaphtha() * bionaphtha_h2_usage() / 33.33 * 10**6


@component.add(
    name="BioNaphtha inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha_competitiveness": 1, "inno_switch_level": 1},
)
def bionaphtha_inno_switch():
    return if_then_else(
        bionaphtha_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="BioNaphtha innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha_inno_switch": 1, "naphtha_innovators": 1},
)
def bionaphtha_innovator_share():
    return bionaphtha_inno_switch() / naphtha_innovators()


@component.add(
    name="BioNaphtha Innovators",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_innovator_pipeline": 1, "bionaphtha_innovator_share": 1},
)
def bionaphtha_innovators():
    return naphtha_innovator_pipeline() * bionaphtha_innovator_share()


@component.add(
    name="BioNaphtha Investment",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_investment_pipeline": 1, "bionaphtha_investment_share": 1},
)
def bionaphtha_investment():
    return naphtha_investment_pipeline() * bionaphtha_investment_share()


@component.add(
    name="BioNaphtha investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bionaphtha_h2_subsidy": 1,
        "bionaphtha_bid_share": 1,
        "bionaphtha_level": 1,
        "naphtha_equalizer": 1,
    },
)
def bionaphtha_investment_share():
    return if_then_else(
        bionaphtha_h2_subsidy() > 0.01,
        lambda: bionaphtha_bid_share(),
        lambda: bionaphtha_level() * naphtha_equalizer(),
    )


@component.add(
    name="BioNaphtha level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "bionaphtha_competitiveness": 2,
        "bionaphtha_sector_share": 1,
    },
)
def bionaphtha_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - bionaphtha_competitiveness()))))
        * float(np.maximum(0.1, bionaphtha_sector_share()))
        + bionaphtha_competitiveness() * 0.001
    )


@component.add(
    name="BioNaphtha sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha": 1, "sum_naphtha_activity": 1},
)
def bionaphtha_sector_share():
    return bionaphtha() / sum_naphtha_activity()


@component.add(
    name="BioNaphtha subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_bionaphtha_subsidy_cost": 1},
    other_deps={
        "_integ_bionaphtha_subsidy_cost": {
            "initial": {},
            "step": {
                "bionaphtha_commissioning_subsidy_level": 1,
                "subsidized_bionaphtha_commissioning": 1,
                "bionaphtha_decommissioning_subsidy_level": 1,
                "subsidized_bionaphtha_decommissioning": 1,
            },
        }
    },
)
def bionaphtha_subsidy_cost():
    return _integ_bionaphtha_subsidy_cost()


_integ_bionaphtha_subsidy_cost = Integ(
    lambda: bionaphtha_commissioning_subsidy_level()
    * subsidized_bionaphtha_commissioning()
    - bionaphtha_decommissioning_subsidy_level()
    * subsidized_bionaphtha_decommissioning(),
    lambda: 0,
    "_integ_bionaphtha_subsidy_cost",
)


@component.add(
    name="feedstock lockin period",
    units="years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def feedstock_lockin_period():
    return 10


@component.add(
    name="feedstock switch time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def feedstock_switch_time():
    return 0.5


@component.add(
    name="Fossil naphtha",
    units="MT naphtha",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_fossil_naphtha": 1},
    other_deps={
        "_integ_fossil_naphtha": {
            "initial": {"naphtha_initial_sector_activity": 1},
            "step": {
                "fossil_naphtha_commissioning": 1,
                "fossil_naphtha_decommissioning": 1,
                "fossil_naphtha_economic_decommissioning": 1,
            },
        }
    },
)
def fossil_naphtha():
    return _integ_fossil_naphtha()


_integ_fossil_naphtha = Integ(
    lambda: fossil_naphtha_commissioning()
    - fossil_naphtha_decommissioning()
    - fossil_naphtha_economic_decommissioning(),
    lambda: naphtha_initial_sector_activity(),
    "_integ_fossil_naphtha",
)


@component.add(
    name="Fossil naphtha Commissioning",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fossil_naphtha_construction": 1, "feedstock_switch_time": 1},
)
def fossil_naphtha_commissioning():
    return fossil_naphtha_construction() / feedstock_switch_time()


@component.add(
    name="Fossil naphtha competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha_cost": 1, "naphtha_cost": 2, "synnaphtha_cost": 1},
)
def fossil_naphtha_competitiveness():
    return float(
        np.minimum(
            bionaphtha_cost() / naphtha_cost(), synnaphtha_cost() / naphtha_cost()
        )
    )


@component.add(
    name="Fossil naphtha Construction",
    units="MT naphtha",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_fossil_naphtha_construction": 1},
    other_deps={
        "_integ_fossil_naphtha_construction": {
            "initial": {
                "naphtha_initial_sector_activity": 1,
                "feedstock_lockin_period": 1,
                "feedstock_switch_time": 1,
            },
            "step": {"fossil_naphtha_investment": 1, "fossil_naphtha_commissioning": 1},
        }
    },
)
def fossil_naphtha_construction():
    return _integ_fossil_naphtha_construction()


_integ_fossil_naphtha_construction = Integ(
    lambda: fossil_naphtha_investment() - fossil_naphtha_commissioning(),
    lambda: naphtha_initial_sector_activity()
    / feedstock_lockin_period()
    * feedstock_switch_time(),
    "_integ_fossil_naphtha_construction",
)


@component.add(
    name="Fossil naphtha cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_cost": 1, "alternative_naphtha_cost": 1},
)
def fossil_naphtha_cost_difference():
    return naphtha_cost() / alternative_naphtha_cost()


@component.add(
    name="Fossil naphtha Decommissioning",
    units="MT naphtha/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_fossil_naphtha_decommissioning": 1, "fossil_naphtha": 1},
    other_deps={
        "_smooth_fossil_naphtha_decommissioning": {
            "initial": {
                "fossil_naphtha_delayed": 1,
                "fossil_naphtha_economic_decommissioning_delayed": 1,
            },
            "step": {
                "fossil_naphtha_delayed": 1,
                "fossil_naphtha_economic_decommissioning_delayed": 1,
            },
        }
    },
)
def fossil_naphtha_decommissioning():
    return float(
        np.maximum(
            0,
            float(
                np.minimum(_smooth_fossil_naphtha_decommissioning(), fossil_naphtha())
            ),
        )
    )


_smooth_fossil_naphtha_decommissioning = Smooth(
    lambda: fossil_naphtha_delayed()
    - fossil_naphtha_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: fossil_naphtha_delayed()
    - fossil_naphtha_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_fossil_naphtha_decommissioning",
)


@component.add(
    name="Fossil Naphtha delayed",
    units="MT naphtha/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_fossil_naphtha_delayed": 1},
    other_deps={
        "_delayfixed_fossil_naphtha_delayed": {
            "initial": {
                "naphtha_initial_sector_activity": 1,
                "feedstock_lockin_period": 2,
            },
            "step": {"fossil_naphtha_commissioning": 1},
        }
    },
)
def fossil_naphtha_delayed():
    return _delayfixed_fossil_naphtha_delayed()


_delayfixed_fossil_naphtha_delayed = DelayFixed(
    lambda: fossil_naphtha_commissioning(),
    lambda: feedstock_lockin_period(),
    lambda: naphtha_initial_sector_activity() / feedstock_lockin_period(),
    time_step,
    "_delayfixed_fossil_naphtha_delayed",
)


@component.add(
    name="Fossil naphtha economic decommissioning",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fossil_naphtha_cost_difference": 2,
        "intersec_decom": 1,
        "fossil_naphtha": 1,
        "slope_decom": 1,
        "feedstock_lockin_period": 1,
        "economic_decommissioning": 1,
    },
)
def fossil_naphtha_economic_decommissioning():
    return (
        if_then_else(
            fossil_naphtha_cost_difference() > 1,
            lambda: (fossil_naphtha() / feedstock_lockin_period() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (fossil_naphtha_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="Fossil naphtha economic decommissioning delayed",
    units="MT naphtha/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_fossil_naphtha_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_fossil_naphtha_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"fossil_naphtha_economic_decommissioning": 1},
        }
    },
)
def fossil_naphtha_economic_decommissioning_delayed():
    return _delayn_fossil_naphtha_economic_decommissioning_delayed()


_delayn_fossil_naphtha_economic_decommissioning_delayed = DelayN(
    lambda: fossil_naphtha_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_fossil_naphtha_economic_decommissioning_delayed",
)


@component.add(
    name="Fossil naphtha EF",
    units="tCO2/MT naphtha",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_lhv": 1, "naphtha_emission_factor": 1},
)
def fossil_naphtha_ef():
    return naphtha_lhv() * naphtha_emission_factor() * 10**6


@component.add(
    name="Fossil naphtha Investment",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_investment_pipeline": 1, "fossil_naphtha_investment_share": 1},
)
def fossil_naphtha_investment():
    return naphtha_investment_pipeline() * fossil_naphtha_investment_share()


@component.add(
    name="Fossil naphtha investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_equalizer": 1, "fossil_naphtha_level": 1},
)
def fossil_naphtha_investment_share():
    return naphtha_equalizer() * fossil_naphtha_level()


@component.add(
    name="Fossil naphtha level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "fossil_naphtha_competitiveness": 2,
        "fossil_naphtha_sector_share": 1,
        "naphtha_excess_activity": 1,
    },
)
def fossil_naphtha_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - fossil_naphtha_competitiveness()))))
        * float(np.maximum(0.1, fossil_naphtha_sector_share()))
        * if_then_else(naphtha_excess_activity() > 0, lambda: 0, lambda: 1)
        + fossil_naphtha_competitiveness() * 0.001
    )


@component.add(
    name="Fossil naphtha sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fossil_naphtha": 1, "sum_naphtha_activity": 1},
)
def fossil_naphtha_sector_share():
    return fossil_naphtha() / sum_naphtha_activity()


@component.add(
    name="Initial naphtha emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_naphtha_emissions": 1},
    other_deps={
        "_initial_initial_naphtha_emissions": {
            "initial": {"naphtha_emissions": 1},
            "step": {},
        }
    },
)
def initial_naphtha_emissions():
    return _initial_initial_naphtha_emissions()


_initial_initial_naphtha_emissions = Initial(
    lambda: naphtha_emissions(), "_initial_initial_naphtha_emissions"
)


@component.add(
    name="naphta olefin rate",
    units="t Naphfta / t HVC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def naphta_olefin_rate():
    return 1.66


@component.add(
    name="naphtha allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_naphtha_emissions": 1, "emissions_cap_lookup": 1, "time": 1},
)
def naphtha_allocated_emissions():
    return initial_naphtha_emissions() * emissions_cap_lookup(time())


@component.add(
    name="naphtha average cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bionaphtha_sector_share": 1,
        "bionaphtha_cost": 1,
        "naphtha_cost": 1,
        "fossil_naphtha_sector_share": 1,
        "synnaphtha_sector_share": 1,
        "synnaphtha_cost": 1,
    },
)
def naphtha_average_cost():
    return (
        bionaphtha_sector_share() * bionaphtha_cost()
        + fossil_naphtha_sector_share() * naphtha_cost()
        + synnaphtha_sector_share() * synnaphtha_cost()
    )


@component.add(
    name="naphtha backlog",
    units="MT naphtha",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_naphtha_backlog": 1},
    other_deps={
        "_integ_naphtha_backlog": {
            "initial": {},
            "step": {"naphtha_current_demand": 1, "sum_naphtha_activity": 1},
        }
    },
)
def naphtha_backlog():
    return _integ_naphtha_backlog()


_integ_naphtha_backlog = Integ(
    lambda: naphtha_current_demand() - sum_naphtha_activity(),
    lambda: 0,
    "_integ_naphtha_backlog",
)


@component.add(
    name="naphtha biomass demand",
    units="GWh Biomass",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha": 1, "naphtha_lhv": 1},
)
def naphtha_biomass_demand():
    return bionaphtha() * (naphtha_lhv() / 3600) * 10**6


@component.add(
    name="Naphtha CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bionaphtha_cost": 1,
        "synnaphtha_cost": 1,
        "naphtha_cost_wo_co2": 1,
        "naphtha_emission_factor": 1,
    },
)
def naphtha_co2_wtp():
    """
    €/GJ / (tCO2/GJ)
    """
    return (
        float(np.minimum(bionaphtha_cost(), synnaphtha_cost())) - naphtha_cost_wo_co2()
    ) / naphtha_emission_factor()


@component.add(
    name="naphtha continuous investment",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "naphtha_forecast_demand": 1,
        "sum_naphtha_decommissioning": 1,
        "feedstock_switch_time": 1,
        "naphtha_backlog": 1,
        "sum_naphtha_activity": 1,
        "innovators": 1,
    },
)
def naphtha_continuous_investment():
    return float(
        np.maximum(
            (
                naphtha_forecast_demand()
                + sum_naphtha_decommissioning()
                + naphtha_backlog() / feedstock_switch_time() / 3
                - sum_naphtha_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="naphtha current demand",
    units="MT naphtha",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_projected_demand": 1},
)
def naphtha_current_demand():
    return naphtha_projected_demand()


@component.add(
    name="naphtha effective cost",
    units="B€ / Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "naphtha_average_cost": 1,
        "naphtha_lhv": 1,
        "naphtha_current_demand": 1,
    },
)
def naphtha_effective_cost():
    """
    €/GJ -> €/ton -> B€/Mt * activity (Mt)
    """
    return ((naphtha_average_cost() * naphtha_lhv()) / 1000) * naphtha_current_demand()


@component.add(
    name="naphtha emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fossil_naphtha": 1, "fossil_naphtha_ef": 1},
)
def naphtha_emissions():
    """
    https://www.eea.europa.eu/publications/managing-the-systemic-use-of This article cites a plastic industry pollution of 208 MT CO2eq in 2018. Really close to what is predicted here.
    """
    return fossil_naphtha() * fossil_naphtha_ef()


@component.add(
    name="naphtha equalizer",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bionaphtha_h2_subsidy": 1,
        "bionaphtha_bid_share": 2,
        "fossil_naphtha_level": 4,
        "synnaphtha_level": 2,
        "synnaphtha_h2_subsidy": 2,
        "synnaphtha_bid_share": 2,
        "bionaphtha_level": 2,
    },
)
def naphtha_equalizer():
    return if_then_else(
        bionaphtha_h2_subsidy() > 0.01,
        lambda: if_then_else(
            synnaphtha_h2_subsidy() > 0.01,
            lambda: (1 - synnaphtha_bid_share() - bionaphtha_bid_share())
            / fossil_naphtha_level(),
            lambda: (1 - bionaphtha_bid_share())
            / (synnaphtha_level() + fossil_naphtha_level()),
        ),
        lambda: if_then_else(
            synnaphtha_h2_subsidy() > 0.01,
            lambda: (1 - synnaphtha_bid_share())
            / (bionaphtha_level() + fossil_naphtha_level()),
            lambda: 1
            / (bionaphtha_level() + synnaphtha_level() + fossil_naphtha_level()),
        ),
    )


@component.add(
    name="naphtha excess activity",
    units="MT naphtha",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "naphtha_excess_emissions": 1,
        "fossil_naphtha_ef": 1,
        "hard_regulation": 1,
    },
)
def naphtha_excess_activity():
    return (
        float(np.maximum(naphtha_excess_emissions() / fossil_naphtha_ef(), 0))
        * hard_regulation()
    )


@component.add(
    name="naphtha excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_emissions": 1, "naphtha_allocated_emissions": 1},
)
def naphtha_excess_emissions():
    return naphtha_emissions() - naphtha_allocated_emissions()


@component.add(
    name="naphtha forecast demand",
    units="MT naphtha",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_naphtha_forecast_demand": 1},
    other_deps={
        "_forecast_naphtha_forecast_demand": {
            "initial": {"naphtha_current_demand": 1},
            "step": {"naphtha_current_demand": 1, "feedstock_switch_time": 2},
        }
    },
)
def naphtha_forecast_demand():
    return _forecast_naphtha_forecast_demand()


_forecast_naphtha_forecast_demand = Forecast(
    lambda: naphtha_current_demand(),
    lambda: 3 * feedstock_switch_time(),
    lambda: feedstock_switch_time(),
    lambda: 0,
    "_forecast_naphtha_forecast_demand",
)


@component.add(
    name="naphtha hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha_hydrogen_demand": 1, "synnaphtha_hydrogen_demand": 1},
)
def naphtha_hydrogen_demand():
    return bionaphtha_hydrogen_demand() + synnaphtha_hydrogen_demand()


@component.add(
    name="naphtha initial sector activity",
    units="MT naphtha",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_naphtha_initial_sector_activity": 1},
    other_deps={
        "_initial_naphtha_initial_sector_activity": {
            "initial": {"naphtha_current_demand": 1},
            "step": {},
        }
    },
)
def naphtha_initial_sector_activity():
    return _initial_naphtha_initial_sector_activity()


_initial_naphtha_initial_sector_activity = Initial(
    lambda: naphtha_current_demand(), "_initial_naphtha_initial_sector_activity"
)


@component.add(
    name="naphtha innovator pipeline",
    units="MT naphtha",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_continuous_investment": 1, "innovators": 2},
)
def naphtha_innovator_pipeline():
    return naphtha_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="naphtha innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha_inno_switch": 1, "synnaphtha_inno_switch": 1},
)
def naphtha_innovators():
    return float(np.maximum(bionaphtha_inno_switch() + synnaphtha_inno_switch(), 1))


@component.add(
    name="naphtha investment pipeline",
    units="MT naphtha",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_continuous_investment": 1},
)
def naphtha_investment_pipeline():
    return naphtha_continuous_investment()


@component.add(
    name="Naphtha LHV", units="GJ/t", comp_type="Constant", comp_subtype="Normal"
)
def naphtha_lhv():
    return 44.9


@component.add(
    name="naphtha projected demand",
    units="MT naphtha",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"olefin_production": 1, "naphta_olefin_rate": 1},
)
def naphtha_projected_demand():
    """
    Based on a 65.7% yield in the naphtha to olefin conversion: https://doi.org/10.1016/j.enconman.2017.10.061
    """
    return olefin_production() * naphta_olefin_rate() / 10**6


@component.add(
    name="Subsidized BioNaphtha Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_bionaphtha_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_bionaphtha_commissioning": {
            "initial": {"feedstock_switch_time": 1},
            "step": {"subsidized_bionaphtha_investment": 1},
        }
    },
)
def subsidized_bionaphtha_commissioning():
    return _delayfixed_subsidized_bionaphtha_commissioning()


_delayfixed_subsidized_bionaphtha_commissioning = DelayFixed(
    lambda: subsidized_bionaphtha_investment(),
    lambda: feedstock_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_bionaphtha_commissioning",
)


@component.add(
    name="Subsidized BioNaphtha Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_bionaphtha_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_bionaphtha_decommissioning": {
            "initial": {},
            "step": {"subsidized_bionaphtha_commissioning": 1},
        }
    },
)
def subsidized_bionaphtha_decommissioning():
    return _delayfixed_subsidized_bionaphtha_decommissioning()


_delayfixed_subsidized_bionaphtha_decommissioning = DelayFixed(
    lambda: subsidized_bionaphtha_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_bionaphtha_decommissioning",
)


@component.add(
    name="Subsidized BioNaphtha Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bionaphtha_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "bionaphtha_investment": 1,
        "bionaphtha_h2_usage": 1,
    },
)
def subsidized_bionaphtha_investment():
    return (
        if_then_else(
            bionaphtha_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: bionaphtha_investment(),
            lambda: 0,
        )
        * bionaphtha_h2_usage()
        / 33.33
    )


@component.add(
    name="Subsidized SynNaphtha Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_synnaphtha_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_synnaphtha_commissioning": {
            "initial": {"feedstock_switch_time": 1},
            "step": {"subsidized_synnaphtha_investment": 1},
        }
    },
)
def subsidized_synnaphtha_commissioning():
    return _delayfixed_subsidized_synnaphtha_commissioning()


_delayfixed_subsidized_synnaphtha_commissioning = DelayFixed(
    lambda: subsidized_synnaphtha_investment(),
    lambda: feedstock_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_synnaphtha_commissioning",
)


@component.add(
    name="Subsidized SynNaphtha Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_synnaphtha_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_synnaphtha_decommissioning": {
            "initial": {},
            "step": {"subsidized_synnaphtha_commissioning": 1},
        }
    },
)
def subsidized_synnaphtha_decommissioning():
    return _delayfixed_subsidized_synnaphtha_decommissioning()


_delayfixed_subsidized_synnaphtha_decommissioning = DelayFixed(
    lambda: subsidized_synnaphtha_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_synnaphtha_decommissioning",
)


@component.add(
    name="Subsidized SynNaphtha Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synnaphtha_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "synnaphtha_investment": 1,
        "synnaphtha_h2_usage": 1,
    },
)
def subsidized_synnaphtha_investment():
    return (
        if_then_else(
            synnaphtha_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: synnaphtha_investment(),
            lambda: 0,
        )
        * synnaphtha_h2_usage()
        / 33.33
    )


@component.add(
    name="sum naphtha activity",
    units="MT naphtha",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha": 1, "synnaphtha": 1, "fossil_naphtha": 1},
)
def sum_naphtha_activity():
    return bionaphtha() + synnaphtha() + fossil_naphtha()


@component.add(
    name="sum naphtha decommissioning",
    units="MT naphtha",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bionaphtha_decommissioning": 1,
        "fossil_naphtha_decommissioning": 1,
        "synnaphtha_decommissioning": 1,
        "fossil_naphtha_economic_decommissioning": 1,
    },
)
def sum_naphtha_decommissioning():
    return (
        bionaphtha_decommissioning()
        + fossil_naphtha_decommissioning()
        + synnaphtha_decommissioning()
        + fossil_naphtha_economic_decommissioning()
    )


@component.add(
    name="Support BioNaphtha",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_bionaphtha_investment": 1,
        "green_h2_subsidy": 1,
        "bionaphtha_h2_subsidy": 1,
    },
)
def support_bionaphtha():
    return (
        subsidized_bionaphtha_investment()
        * (green_h2_subsidy() + bionaphtha_h2_subsidy())
        * 10
    )


@component.add(
    name="Support SynNaphtha",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_synnaphtha_investment": 1,
        "green_h2_subsidy": 1,
        "synnaphtha_h2_subsidy": 1,
    },
)
def support_synnaphtha():
    return (
        subsidized_synnaphtha_investment()
        * (green_h2_subsidy() + synnaphtha_h2_subsidy())
        * 10
    )


@component.add(
    name="SynNaphtha",
    units="MT naphtha",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_synnaphtha": 1},
    other_deps={
        "_integ_synnaphtha": {
            "initial": {},
            "step": {"synnaphtha_commissioning": 1, "synnaphtha_decommissioning": 1},
        }
    },
)
def synnaphtha():
    return _integ_synnaphtha()


_integ_synnaphtha = Integ(
    lambda: synnaphtha_commissioning() - synnaphtha_decommissioning(),
    lambda: 0,
    "_integ_synnaphtha",
)


@component.add(
    name="SynNaphtha bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synnaphtha_desired_investment": 1},
)
def synnaphtha_bid_share():
    return synnaphtha_desired_investment()


@component.add(
    name="SynNaphtha Commissioning",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synnaphtha_construction": 1, "feedstock_switch_time": 1},
)
def synnaphtha_commissioning():
    return synnaphtha_construction() / feedstock_switch_time()


@component.add(
    name="SynNaphtha Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_synnaphtha_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_synnaphtha_commissioning_subsidy_level": {
            "initial": {"feedstock_switch_time": 1},
            "step": {"synnaphtha_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def synnaphtha_commissioning_subsidy_level():
    return _delayfixed_synnaphtha_commissioning_subsidy_level()


_delayfixed_synnaphtha_commissioning_subsidy_level = DelayFixed(
    lambda: synnaphtha_h2_subsidy() + green_h2_subsidy(),
    lambda: feedstock_switch_time(),
    lambda: 0,
    time_step,
    "_delayfixed_synnaphtha_commissioning_subsidy_level",
)


@component.add(
    name="SynNaphtha competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_cost": 1, "synnaphtha_cost": 2, "bionaphtha_cost": 1},
)
def synnaphtha_competitiveness():
    return float(
        np.minimum(
            naphtha_cost() / synnaphtha_cost(), bionaphtha_cost() / synnaphtha_cost()
        )
    )


@component.add(
    name="SynNaphtha Construction",
    units="MT naphtha",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_synnaphtha_construction": 1},
    other_deps={
        "_integ_synnaphtha_construction": {
            "initial": {},
            "step": {
                "synnaphtha_innovators": 1,
                "synnaphtha_investment": 1,
                "synnaphtha_commissioning": 1,
            },
        }
    },
)
def synnaphtha_construction():
    return _integ_synnaphtha_construction()


_integ_synnaphtha_construction = Integ(
    lambda: synnaphtha_innovators()
    + synnaphtha_investment()
    - synnaphtha_commissioning(),
    lambda: 0,
    "_integ_synnaphtha_construction",
)


@component.add(
    name="SynNaphtha Decommissioning",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synnaphtha": 1, "feedstock_lockin_period": 1},
)
def synnaphtha_decommissioning():
    return synnaphtha() / feedstock_lockin_period()


@component.add(
    name="SynNaphtha Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_synnaphtha_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_synnaphtha_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"synnaphtha_commissioning_subsidy_level": 1},
        }
    },
)
def synnaphtha_decommissioning_subsidy_level():
    return _delayfixed_synnaphtha_decommissioning_subsidy_level()


_delayfixed_synnaphtha_decommissioning_subsidy_level = DelayFixed(
    lambda: synnaphtha_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_synnaphtha_decommissioning_subsidy_level",
)


@component.add(
    name="SynNaphtha desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_synnaphtha_desired_investment": 1},
    other_deps={
        "_smooth_synnaphtha_desired_investment": {
            "initial": {
                "synnaphtha_level": 2,
                "bionaphtha_level": 1,
                "fossil_naphtha_level": 1,
            },
            "step": {
                "synnaphtha_level": 2,
                "bionaphtha_level": 1,
                "fossil_naphtha_level": 1,
            },
        }
    },
)
def synnaphtha_desired_investment():
    return _smooth_synnaphtha_desired_investment()


_smooth_synnaphtha_desired_investment = Smooth(
    lambda: synnaphtha_level()
    / (bionaphtha_level() + fossil_naphtha_level() + synnaphtha_level()),
    lambda: 2,
    lambda: synnaphtha_level()
    / (bionaphtha_level() + fossil_naphtha_level() + synnaphtha_level()),
    lambda: 1,
    "_smooth_synnaphtha_desired_investment",
)


@component.add(
    name="SynNaphtha H2 Usage",
    units="MWh H2/t Naphfta",
    comp_type="Constant",
    comp_subtype="Normal",
)
def synnaphtha_h2_usage():
    return 5.85


@component.add(
    name="SynNaphtha HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "naphtha_continuous_investment": 1,
        "synnaphtha_h2_usage": 1,
        "synnaphtha_bid_share": 1,
    },
)
def synnaphtha_hba_volume():
    return (
        naphtha_continuous_investment()
        * synnaphtha_h2_usage()
        / 33.33
        * 10**6
        * synnaphtha_bid_share()
    )


@component.add(
    name="SynNaphtha hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synnaphtha": 1, "synnaphtha_h2_usage": 1},
)
def synnaphtha_hydrogen_demand():
    return synnaphtha() * synnaphtha_h2_usage() / 33.33 * 10**6


@component.add(
    name="SynNaphtha inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synnaphtha_competitiveness": 1, "inno_switch_level": 1},
)
def synnaphtha_inno_switch():
    return if_then_else(
        synnaphtha_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="SynNaphtha innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synnaphtha_inno_switch": 1, "naphtha_innovators": 1},
)
def synnaphtha_innovator_share():
    return synnaphtha_inno_switch() / naphtha_innovators()


@component.add(
    name="SynNaphtha Innovators",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_innovator_pipeline": 1, "synnaphtha_innovator_share": 1},
)
def synnaphtha_innovators():
    return naphtha_innovator_pipeline() * synnaphtha_innovator_share()


@component.add(
    name="SynNaphtha Investment",
    units="MT naphtha/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_investment_pipeline": 1, "synnaphtha_investment_share": 1},
)
def synnaphtha_investment():
    return naphtha_investment_pipeline() * synnaphtha_investment_share()


@component.add(
    name="SynNaphtha investment share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synnaphtha_h2_subsidy": 1,
        "synnaphtha_bid_share": 1,
        "synnaphtha_level": 1,
        "naphtha_equalizer": 1,
    },
)
def synnaphtha_investment_share():
    return if_then_else(
        synnaphtha_h2_subsidy() > 0.01,
        lambda: synnaphtha_bid_share(),
        lambda: synnaphtha_level() * naphtha_equalizer(),
    )


@component.add(
    name="SynNaphtha level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "synnaphtha_competitiveness": 2,
        "synnaphtha_sector_share": 1,
    },
)
def synnaphtha_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - synnaphtha_competitiveness()))))
        * float(np.maximum(0.1, synnaphtha_sector_share()))
        + synnaphtha_competitiveness() * 0.001
    )


@component.add(
    name="SynNaphtha sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synnaphtha": 1, "sum_naphtha_activity": 1},
)
def synnaphtha_sector_share():
    return synnaphtha() / sum_naphtha_activity()


@component.add(
    name="SynNaphtha subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_synnaphtha_subsidy_cost": 1},
    other_deps={
        "_integ_synnaphtha_subsidy_cost": {
            "initial": {},
            "step": {
                "synnaphtha_commissioning_subsidy_level": 1,
                "subsidized_synnaphtha_commissioning": 1,
                "subsidized_synnaphtha_decommissioning": 1,
                "synnaphtha_decommissioning_subsidy_level": 1,
            },
        }
    },
)
def synnaphtha_subsidy_cost():
    return _integ_synnaphtha_subsidy_cost()


_integ_synnaphtha_subsidy_cost = Integ(
    lambda: synnaphtha_commissioning_subsidy_level()
    * subsidized_synnaphtha_commissioning()
    - synnaphtha_decommissioning_subsidy_level()
    * subsidized_synnaphtha_decommissioning(),
    lambda: 0,
    "_integ_synnaphtha_subsidy_cost",
)


@component.add(
    name="xxx",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bionaphtha_investment": 1, "bionaphtha_h2_usage": 1},
)
def xxx():
    return bionaphtha_investment() * bionaphtha_h2_usage() / 33.33 * 10**6
