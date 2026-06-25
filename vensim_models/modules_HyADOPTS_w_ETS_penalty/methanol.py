"""
Module methanol
Translated using PySD version 3.14.3
"""

@component.add(
    name="alternative MeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_meoh_cost": 1, "green_emeoh_cost": 1, "green_biomeoh_cost": 1},
)
def alternative_meoh_cost():
    return float(
        np.minimum(
            blue_meoh_cost(),
            float(np.minimum(green_biomeoh_cost(), green_emeoh_cost())),
        )
    )


@component.add(
    name="BioMeOH",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biomeoh": 1},
    other_deps={
        "_integ_biomeoh": {
            "initial": {},
            "step": {"biomeoh_commissioning": 1, "biomeoh_decommissioning": 1},
        }
    },
)
def biomeoh():
    return _integ_biomeoh()


_integ_biomeoh = Integ(
    lambda: biomeoh_commissioning() - biomeoh_decommissioning(),
    lambda: 0,
    "_integ_biomeoh",
)


@component.add(
    name="BioMeOH bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh_desired_investment": 1},
)
def biomeoh_bid_share():
    return biomeoh_desired_investment()


@component.add(
    name="BioMeOH Commissioning",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh_construction": 1, "meoh_construction_time": 1},
)
def biomeoh_commissioning():
    return biomeoh_construction() / meoh_construction_time()


@component.add(
    name="BioMeOH Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_biomeoh_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_biomeoh_commissioning_subsidy_level": {
            "initial": {"meoh_construction_time": 1},
            "step": {"biomeoh_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def biomeoh_commissioning_subsidy_level():
    return _delayfixed_biomeoh_commissioning_subsidy_level()


_delayfixed_biomeoh_commissioning_subsidy_level = DelayFixed(
    lambda: biomeoh_h2_subsidy() + green_h2_subsidy(),
    lambda: meoh_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_biomeoh_commissioning_subsidy_level",
)


@component.add(
    name="BioMeOH competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_meoh_cost": 1,
        "green_biomeoh_cost": 3,
        "convmeoh_cost": 1,
        "green_emeoh_cost": 1,
    },
)
def biomeoh_competitiveness():
    return float(
        np.minimum(
            float(
                np.minimum(
                    blue_meoh_cost() / green_biomeoh_cost(),
                    convmeoh_cost() / green_biomeoh_cost(),
                )
            ),
            green_emeoh_cost() / green_biomeoh_cost(),
        )
    )


@component.add(
    name="BioMeOH Construction",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biomeoh_construction": 1},
    other_deps={
        "_integ_biomeoh_construction": {
            "initial": {},
            "step": {
                "biomeoh_innovators": 1,
                "biomeoh_investment": 1,
                "biomeoh_commissioning": 1,
            },
        }
    },
)
def biomeoh_construction():
    return _integ_biomeoh_construction()


_integ_biomeoh_construction = Integ(
    lambda: biomeoh_innovators() + biomeoh_investment() - biomeoh_commissioning(),
    lambda: 0,
    "_integ_biomeoh_construction",
)


@component.add(
    name="BioMeOH Decommissioning",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh": 1, "meoh_plant_lifetime": 1},
)
def biomeoh_decommissioning():
    return biomeoh() / meoh_plant_lifetime()


@component.add(
    name="BioMeOH Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_biomeoh_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_biomeoh_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"biomeoh_commissioning_subsidy_level": 1},
        }
    },
)
def biomeoh_decommissioning_subsidy_level():
    return _delayfixed_biomeoh_decommissioning_subsidy_level()


_delayfixed_biomeoh_decommissioning_subsidy_level = DelayFixed(
    lambda: biomeoh_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_biomeoh_decommissioning_subsidy_level",
)


@component.add(
    name="BioMeOH desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_biomeoh_desired_investment": 1},
    other_deps={
        "_smooth_biomeoh_desired_investment": {
            "initial": {
                "biomeoh_level": 2,
                "blue_meoh_level": 1,
                "grey_meoh_level": 1,
                "emeoh_level": 1,
            },
            "step": {
                "biomeoh_level": 2,
                "blue_meoh_level": 1,
                "grey_meoh_level": 1,
                "emeoh_level": 1,
            },
        }
    },
)
def biomeoh_desired_investment():
    return _smooth_biomeoh_desired_investment()


_smooth_biomeoh_desired_investment = Smooth(
    lambda: biomeoh_level()
    / (biomeoh_level() + blue_meoh_level() + emeoh_level() + grey_meoh_level()),
    lambda: 2,
    lambda: biomeoh_level()
    / (biomeoh_level() + blue_meoh_level() + emeoh_level() + grey_meoh_level()),
    lambda: 1,
    "_smooth_biomeoh_desired_investment",
)


@component.add(
    name="BioMeOH HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_continuous_investment": 1,
        "biomeoh_h2_usage": 1,
        "biomeoh_bid_share": 1,
    },
)
def biomeoh_hba_volume():
    return (
        meoh_continuous_investment() / biomeoh_h2_usage() * 10**6 * biomeoh_bid_share()
    )


@component.add(
    name="bioMeOH hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh": 1, "biomeoh_h2_usage": 1},
)
def biomeoh_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return biomeoh() / biomeoh_h2_usage() * 10**6


@component.add(
    name="BioMeOH inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh_competitiveness": 1, "inno_switch_level": 1},
)
def biomeoh_inno_switch():
    return if_then_else(
        biomeoh_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="BioMeOH innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh_inno_switch": 1, "meoh_innovators": 1},
)
def biomeoh_innovator_share():
    return biomeoh_inno_switch() / meoh_innovators()


@component.add(
    name="BioMeOH Innovators",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_innovator_pipeline": 1, "biomeoh_innovator_share": 1},
)
def biomeoh_innovators():
    return meoh_innovator_pipeline() * biomeoh_innovator_share()


@component.add(
    name="BioMeOH Investment",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_investment_pipeline": 1, "biomeoh_investment_share": 1},
)
def biomeoh_investment():
    return meoh_investment_pipeline() * biomeoh_investment_share()


@component.add(
    name="BioMeOH investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_h2_subsidy": 1,
        "biomeoh_bid_share": 1,
        "biomeoh_level": 1,
        "equalizer_meoh": 1,
    },
)
def biomeoh_investment_share():
    return if_then_else(
        biomeoh_h2_subsidy() > 0.01,
        lambda: biomeoh_bid_share(),
        lambda: equalizer_meoh() * biomeoh_level(),
    )


@component.add(
    name="BioMeOH level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "biomeoh_competitiveness": 2, "biomeoh_sector_share": 1},
)
def biomeoh_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - biomeoh_competitiveness()))))
        * float(np.maximum(0.1, biomeoh_sector_share()))
        + biomeoh_competitiveness() * 0.001
    )


@component.add(
    name="BioMeOH sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh": 1, "sum_meoh_activity": 1},
)
def biomeoh_sector_share():
    return biomeoh() / sum_meoh_activity()


@component.add(
    name="BioMeOH subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biomeoh_subsidy_cost": 1},
    other_deps={
        "_integ_biomeoh_subsidy_cost": {
            "initial": {},
            "step": {
                "biomeoh_commissioning_subsidy_level": 1,
                "subsidized_biomeoh_commissioning": 1,
                "subsidized_biomeoh_decommissioning": 1,
                "biomeoh_decommissioning_subsidy_level": 1,
            },
        }
    },
)
def biomeoh_subsidy_cost():
    return _integ_biomeoh_subsidy_cost()


_integ_biomeoh_subsidy_cost = Integ(
    lambda: biomeoh_commissioning_subsidy_level() * subsidized_biomeoh_commissioning()
    - biomeoh_decommissioning_subsidy_level() * subsidized_biomeoh_decommissioning(),
    lambda: 0,
    "_integ_biomeoh_subsidy_cost",
)


@component.add(
    name="Blue MeOH",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_blue_meoh": 1},
    other_deps={
        "_integ_blue_meoh": {
            "initial": {},
            "step": {"blue_meoh_commissioning": 1, "blue_meoh_decommissioning": 1},
        }
    },
)
def blue_meoh():
    return _integ_blue_meoh()


_integ_blue_meoh = Integ(
    lambda: blue_meoh_commissioning() - blue_meoh_decommissioning(),
    lambda: 0,
    "_integ_blue_meoh",
)


@component.add(
    name="Blue MeOH Commissioning",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_meoh_construction": 1, "meoh_construction_time": 1},
)
def blue_meoh_commissioning():
    return blue_meoh_construction() / meoh_construction_time()


@component.add(
    name="Blue MeOH competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "convmeoh_cost": 1,
        "blue_meoh_cost": 3,
        "green_biomeoh_cost": 1,
        "green_emeoh_cost": 1,
    },
)
def blue_meoh_competitiveness():
    return float(
        np.minimum(
            float(
                np.minimum(
                    convmeoh_cost() / blue_meoh_cost(),
                    green_biomeoh_cost() / blue_meoh_cost(),
                )
            ),
            green_emeoh_cost() / blue_meoh_cost(),
        )
    )


@component.add(
    name="Blue MeOH Construction",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_blue_meoh_construction": 1},
    other_deps={
        "_integ_blue_meoh_construction": {
            "initial": {},
            "step": {
                "blue_meoh_innovators": 1,
                "blue_meoh_investment": 1,
                "blue_meoh_commissioning": 1,
            },
        }
    },
)
def blue_meoh_construction():
    return _integ_blue_meoh_construction()


_integ_blue_meoh_construction = Integ(
    lambda: blue_meoh_innovators() + blue_meoh_investment() - blue_meoh_commissioning(),
    lambda: 0,
    "_integ_blue_meoh_construction",
)


@component.add(
    name="Blue MeOH Decommissioning",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_meoh": 1, "meoh_plant_lifetime": 1},
)
def blue_meoh_decommissioning():
    return blue_meoh() / meoh_plant_lifetime()


@component.add(
    name="Blue MeOH EF",
    units="tCO2/tMeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "electricity_emission_factor": 1,
        "convmeoh_electricity_usage": 1,
        "convmeoh_emission_factor": 1,
        "cc_capture_rate": 1,
    },
)
def blue_meoh_ef():
    return (
        electricity_emission_factor() * convmeoh_electricity_usage()
        + convmeoh_emission_factor() * (1 - cc_capture_rate())
    )


@component.add(
    name="Blue MeOH emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_meoh": 1, "blue_meoh_ef": 1},
)
def blue_meoh_emissions():
    return blue_meoh() * blue_meoh_ef() * 10**6


@component.add(
    name="Blue MeOH inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_meoh_competitiveness": 1, "inno_switch_level": 1},
)
def blue_meoh_inno_switch():
    return if_then_else(
        blue_meoh_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="Blue MeOH innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_meoh_inno_switch": 1, "meoh_innovators": 1},
)
def blue_meoh_innovator_share():
    return blue_meoh_inno_switch() / meoh_innovators()


@component.add(
    name="Blue MeOH Innovators",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_innovator_pipeline": 1, "blue_meoh_innovator_share": 1},
)
def blue_meoh_innovators():
    return meoh_innovator_pipeline() * blue_meoh_innovator_share()


@component.add(
    name="Blue MeOH Investment",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_investment_pipeline": 1, "blue_meoh_investment_share": 1},
)
def blue_meoh_investment():
    return meoh_investment_pipeline() * blue_meoh_investment_share()


@component.add(
    name="Blue MeOH investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"equalizer_meoh": 1, "blue_meoh_level": 1},
)
def blue_meoh_investment_share():
    return equalizer_meoh() * blue_meoh_level()


@component.add(
    name="Blue MeOH level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "blue_meoh_competitiveness": 2,
        "blue_meoh_sector_share": 1,
    },
)
def blue_meoh_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - blue_meoh_competitiveness()))))
        * float(np.maximum(0.1, blue_meoh_sector_share()))
        + blue_meoh_competitiveness() * 0.001
    )


@component.add(
    name="Blue MeOH sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_meoh": 1, "sum_meoh_activity": 1},
)
def blue_meoh_sector_share():
    return blue_meoh() / sum_meoh_activity()


@component.add(
    name="eMeOH",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_emeoh": 1},
    other_deps={
        "_integ_emeoh": {
            "initial": {},
            "step": {"emeoh_commissioning": 1, "emeoh_decommissioning": 1},
        }
    },
)
def emeoh():
    return _integ_emeoh()


_integ_emeoh = Integ(
    lambda: emeoh_commissioning() - emeoh_decommissioning(), lambda: 0, "_integ_emeoh"
)


@component.add(
    name="eMeOH bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh_desired_investment": 1},
)
def emeoh_bid_share():
    return emeoh_desired_investment()


@component.add(
    name="eMeOH Commissioning",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh_construction": 1, "meoh_construction_time": 1},
)
def emeoh_commissioning():
    return emeoh_construction() / meoh_construction_time()


@component.add(
    name="eMeOH Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_emeoh_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_emeoh_commissioning_subsidy_level": {
            "initial": {"meoh_construction_time": 1},
            "step": {"emeoh_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def emeoh_commissioning_subsidy_level():
    return _delayfixed_emeoh_commissioning_subsidy_level()


_delayfixed_emeoh_commissioning_subsidy_level = DelayFixed(
    lambda: emeoh_h2_subsidy() + green_h2_subsidy(),
    lambda: meoh_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_emeoh_commissioning_subsidy_level",
)


@component.add(
    name="eMeOH competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_meoh_cost": 1,
        "green_emeoh_cost": 3,
        "convmeoh_cost": 1,
        "green_biomeoh_cost": 1,
    },
)
def emeoh_competitiveness():
    return float(
        np.minimum(
            float(
                np.minimum(
                    blue_meoh_cost() / green_emeoh_cost(),
                    convmeoh_cost() / green_emeoh_cost(),
                )
            ),
            green_biomeoh_cost() / green_emeoh_cost(),
        )
    )


@component.add(
    name="eMeOH Construction",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_emeoh_construction": 1},
    other_deps={
        "_integ_emeoh_construction": {
            "initial": {},
            "step": {
                "emeoh_innovators": 1,
                "emeoh_investment": 1,
                "emeoh_commissioning": 1,
            },
        }
    },
)
def emeoh_construction():
    return _integ_emeoh_construction()


_integ_emeoh_construction = Integ(
    lambda: emeoh_innovators() + emeoh_investment() - emeoh_commissioning(),
    lambda: 0,
    "_integ_emeoh_construction",
)


@component.add(
    name="eMeOH Decommissioning",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh": 1, "meoh_plant_lifetime": 1},
)
def emeoh_decommissioning():
    return emeoh() / meoh_plant_lifetime()


@component.add(
    name="eMeOH Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_emeoh_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_emeoh_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"emeoh_commissioning_subsidy_level": 1},
        }
    },
)
def emeoh_decommissioning_subsidy_level():
    return _delayfixed_emeoh_decommissioning_subsidy_level()


_delayfixed_emeoh_decommissioning_subsidy_level = DelayFixed(
    lambda: emeoh_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_emeoh_decommissioning_subsidy_level",
)


@component.add(
    name="eMeOH desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_emeoh_desired_investment": 1},
    other_deps={
        "_smooth_emeoh_desired_investment": {
            "initial": {
                "emeoh_level": 2,
                "biomeoh_level": 1,
                "grey_meoh_level": 1,
                "blue_meoh_level": 1,
            },
            "step": {
                "emeoh_level": 2,
                "biomeoh_level": 1,
                "grey_meoh_level": 1,
                "blue_meoh_level": 1,
            },
        }
    },
)
def emeoh_desired_investment():
    return _smooth_emeoh_desired_investment()


_smooth_emeoh_desired_investment = Smooth(
    lambda: emeoh_level()
    / (biomeoh_level() + blue_meoh_level() + emeoh_level() + grey_meoh_level()),
    lambda: 2,
    lambda: emeoh_level()
    / (biomeoh_level() + blue_meoh_level() + emeoh_level() + grey_meoh_level()),
    lambda: 1,
    "_smooth_emeoh_desired_investment",
)


@component.add(
    name="eMeOH HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_continuous_investment": 1,
        "emeoh_h2_usage": 1,
        "emeoh_bid_share": 1,
    },
)
def emeoh_hba_volume():
    return meoh_continuous_investment() / emeoh_h2_usage() * 10**6 * emeoh_bid_share()


@component.add(
    name="eMeOH hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh": 1, "emeoh_h2_usage": 1},
)
def emeoh_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return emeoh() / emeoh_h2_usage() * 10**6


@component.add(
    name="eMeOH inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh_competitiveness": 1, "inno_switch_level": 1},
)
def emeoh_inno_switch():
    return if_then_else(
        emeoh_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="eMeOH innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh_inno_switch": 1, "meoh_innovators": 1},
)
def emeoh_innovator_share():
    return emeoh_inno_switch() / meoh_innovators()


@component.add(
    name="eMeOH Innovators",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_innovator_pipeline": 1, "emeoh_innovator_share": 1},
)
def emeoh_innovators():
    return meoh_innovator_pipeline() * emeoh_innovator_share()


@component.add(
    name="eMeOH Investment",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_investment_pipeline": 1, "emeoh_investment_share": 1},
)
def emeoh_investment():
    return meoh_investment_pipeline() * emeoh_investment_share()


@component.add(
    name="eMeOH investment share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "emeoh_h2_subsidy": 1,
        "emeoh_bid_share": 1,
        "equalizer_meoh": 1,
        "emeoh_level": 1,
    },
)
def emeoh_investment_share():
    return if_then_else(
        emeoh_h2_subsidy() > 0.01,
        lambda: emeoh_bid_share(),
        lambda: equalizer_meoh() * emeoh_level(),
    )


@component.add(
    name="eMeOH level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "emeoh_competitiveness": 2, "emeoh_sector_share": 1},
)
def emeoh_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - emeoh_competitiveness()))))
        * float(np.maximum(0.1, emeoh_sector_share()))
        + emeoh_competitiveness() * 0.001
    )


@component.add(
    name="eMeOH sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh": 1, "sum_meoh_activity": 1},
)
def emeoh_sector_share():
    return emeoh() / sum_meoh_activity()


@component.add(
    name="eMeOH subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_emeoh_subsidy_cost": 1},
    other_deps={
        "_integ_emeoh_subsidy_cost": {
            "initial": {},
            "step": {
                "emeoh_commissioning_subsidy_level": 1,
                "subsidized_emeoh_commissioning": 1,
                "emeoh_decommissioning_subsidy_level": 1,
                "subsidized_emeoh_decommissioning": 1,
            },
        }
    },
)
def emeoh_subsidy_cost():
    return _integ_emeoh_subsidy_cost()


_integ_emeoh_subsidy_cost = Integ(
    lambda: emeoh_commissioning_subsidy_level() * subsidized_emeoh_commissioning()
    - emeoh_decommissioning_subsidy_level() * subsidized_emeoh_decommissioning(),
    lambda: 0,
    "_integ_emeoh_subsidy_cost",
)


@component.add(
    name="equalizer MeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_h2_subsidy": 1,
        "emeoh_bid_share": 2,
        "blue_meoh_level": 4,
        "biomeoh_bid_share": 2,
        "grey_meoh_level": 4,
        "emeoh_h2_subsidy": 2,
        "emeoh_level": 2,
        "biomeoh_level": 2,
    },
)
def equalizer_meoh():
    return if_then_else(
        biomeoh_h2_subsidy() > 0.01,
        lambda: if_then_else(
            emeoh_h2_subsidy() > 0.01,
            lambda: (1 - emeoh_bid_share() - biomeoh_bid_share())
            / (grey_meoh_level() + blue_meoh_level()),
            lambda: (1 - biomeoh_bid_share())
            / (emeoh_level() + grey_meoh_level() + blue_meoh_level()),
        ),
        lambda: if_then_else(
            emeoh_h2_subsidy() > 0.01,
            lambda: (1 - emeoh_bid_share())
            / (biomeoh_level() + grey_meoh_level() + blue_meoh_level()),
            lambda: 1
            / (biomeoh_level() + emeoh_level() + grey_meoh_level() + blue_meoh_level()),
        ),
    )


@component.add(
    name="Green BioMeOH weight",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh": 2, "biomeoh": 2},
)
def green_biomeoh_weight():
    return if_then_else(
        emeoh() > 0, lambda: biomeoh() / (biomeoh() + emeoh()), lambda: 1
    )


@component.add(
    name="Green MeOH av cost",
    units="€/MJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "green_biomeoh_weight": 2,
        "green_biomeoh_cost": 1,
        "green_emeoh_cost": 1,
    },
)
def green_meoh_av_cost():
    return (
        green_biomeoh_weight() * green_biomeoh_cost()
        + (1 - green_biomeoh_weight()) * green_emeoh_cost()
    )


@component.add(
    name="Grey MeOH",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_grey_meoh": 1},
    other_deps={
        "_integ_grey_meoh": {
            "initial": {"meoh_initial_sector_activity": 1},
            "step": {
                "grey_meoh_commissioning": 1,
                "grey_meoh_decommissioning": 1,
                "grey_meoh_economic_decommissioning": 1,
            },
        }
    },
)
def grey_meoh():
    return _integ_grey_meoh()


_integ_grey_meoh = Integ(
    lambda: grey_meoh_commissioning()
    - grey_meoh_decommissioning()
    - grey_meoh_economic_decommissioning(),
    lambda: meoh_initial_sector_activity(),
    "_integ_grey_meoh",
)


@component.add(
    name="Grey MeOH Commissioning",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_meoh_construction": 1, "meoh_construction_time": 1},
)
def grey_meoh_commissioning():
    return grey_meoh_construction() / meoh_construction_time()


@component.add(
    name="Grey MeOH competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_meoh_cost": 1,
        "convmeoh_cost": 3,
        "green_biomeoh_cost": 1,
        "green_emeoh_cost": 1,
    },
)
def grey_meoh_competitiveness():
    return float(
        np.minimum(
            float(
                np.minimum(
                    blue_meoh_cost() / convmeoh_cost(),
                    green_biomeoh_cost() / convmeoh_cost(),
                )
            ),
            green_emeoh_cost() / convmeoh_cost(),
        )
    )


@component.add(
    name="Grey MeOH Construction",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_grey_meoh_construction": 1},
    other_deps={
        "_integ_grey_meoh_construction": {
            "initial": {
                "meoh_initial_sector_activity": 1,
                "meoh_plant_lifetime": 1,
                "meoh_construction_time": 1,
            },
            "step": {"grey_meoh_investment": 1, "grey_meoh_commissioning": 1},
        }
    },
)
def grey_meoh_construction():
    return _integ_grey_meoh_construction()


_integ_grey_meoh_construction = Integ(
    lambda: grey_meoh_investment() - grey_meoh_commissioning(),
    lambda: meoh_initial_sector_activity()
    / meoh_plant_lifetime()
    * meoh_construction_time(),
    "_integ_grey_meoh_construction",
)


@component.add(
    name="Grey MeOH cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"convmeoh_cost_marginal": 1, "alternative_meoh_cost": 1},
)
def grey_meoh_cost_difference():
    return convmeoh_cost_marginal() / alternative_meoh_cost()


@component.add(
    name="Grey MeOH Decommissioning",
    units="MT MeOH/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_grey_meoh_decommissioning": 1, "grey_meoh": 1},
    other_deps={
        "_smooth_grey_meoh_decommissioning": {
            "initial": {
                "grey_meoh_delayed": 1,
                "grey_meoh_economic_decommissioning_delayed": 1,
            },
            "step": {
                "grey_meoh_delayed": 1,
                "grey_meoh_economic_decommissioning_delayed": 1,
            },
        }
    },
)
def grey_meoh_decommissioning():
    return float(
        np.maximum(
            0, float(np.minimum(_smooth_grey_meoh_decommissioning(), grey_meoh()))
        )
    )


_smooth_grey_meoh_decommissioning = Smooth(
    lambda: grey_meoh_delayed() - grey_meoh_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: grey_meoh_delayed() - grey_meoh_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_grey_meoh_decommissioning",
)


@component.add(
    name="Grey MeOH delayed",
    units="MT MeOH/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_grey_meoh_delayed": 1},
    other_deps={
        "_delayfixed_grey_meoh_delayed": {
            "initial": {"meoh_initial_sector_activity": 1, "meoh_plant_lifetime": 2},
            "step": {"grey_meoh_commissioning": 1},
        }
    },
)
def grey_meoh_delayed():
    return _delayfixed_grey_meoh_delayed()


_delayfixed_grey_meoh_delayed = DelayFixed(
    lambda: grey_meoh_commissioning(),
    lambda: meoh_plant_lifetime(),
    lambda: meoh_initial_sector_activity() / meoh_plant_lifetime(),
    time_step,
    "_delayfixed_grey_meoh_delayed",
)


@component.add(
    name="Grey MeOH economic decommissioning",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "grey_meoh_cost_difference": 2,
        "slope_decom": 1,
        "grey_meoh": 1,
        "meoh_plant_lifetime": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def grey_meoh_economic_decommissioning():
    return (
        if_then_else(
            grey_meoh_cost_difference() > 1,
            lambda: (grey_meoh() / meoh_plant_lifetime() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (grey_meoh_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="Grey MeOH economic decommissioning delayed",
    units="MT MeOH/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_grey_meoh_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_grey_meoh_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"grey_meoh_economic_decommissioning": 1},
        }
    },
)
def grey_meoh_economic_decommissioning_delayed():
    return _delayn_grey_meoh_economic_decommissioning_delayed()


_delayn_grey_meoh_economic_decommissioning_delayed = DelayN(
    lambda: grey_meoh_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_grey_meoh_economic_decommissioning_delayed",
)


@component.add(
    name="Grey MeOH EF",
    units="tCO2/tMeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "convmeoh_electricity_usage": 1,
        "electricity_emission_factor": 1,
        "convmeoh_emission_factor": 1,
    },
)
def grey_meoh_ef():
    return (
        convmeoh_electricity_usage() * electricity_emission_factor()
        + convmeoh_emission_factor()
    )


@component.add(
    name="Grey MeOH emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_meoh": 1, "grey_meoh_ef": 1},
)
def grey_meoh_emissions():
    return grey_meoh() * grey_meoh_ef() * 10**6


@component.add(
    name="Grey MeOH Investment",
    units="MT MeOH/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_investment_pipeline": 1, "grey_meoh_investment_share": 1},
)
def grey_meoh_investment():
    return meoh_investment_pipeline() * grey_meoh_investment_share()


@component.add(
    name="Grey MeOH investment share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"equalizer_meoh": 1, "grey_meoh_level": 1},
)
def grey_meoh_investment_share():
    return equalizer_meoh() * grey_meoh_level()


@component.add(
    name="Grey MeOH level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "grey_meoh_competitiveness": 2,
        "grey_meoh_sector_share": 1,
        "meoh_excess_activity": 1,
    },
)
def grey_meoh_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - grey_meoh_competitiveness()))))
        * float(np.maximum(0.1, grey_meoh_sector_share()))
        * if_then_else(meoh_excess_activity() > 0, lambda: 0, lambda: 1)
        + grey_meoh_competitiveness() * 0.001
    )


@component.add(
    name="Grey MeOH sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_meoh": 1, "sum_meoh_activity": 1},
)
def grey_meoh_sector_share():
    return grey_meoh() / sum_meoh_activity()


@component.add(
    name="Initial MeOH emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_meoh_emissions": 1},
    other_deps={
        "_initial_initial_meoh_emissions": {
            "initial": {"meoh_emissions": 1},
            "step": {},
        }
    },
)
def initial_meoh_emissions():
    return _initial_initial_meoh_emissions()


_initial_initial_meoh_emissions = Initial(
    lambda: meoh_emissions(), "_initial_initial_meoh_emissions"
)


@component.add(
    name="MeOH allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_meoh_emissions": 1, "time": 1, "emissions_cap_lookup": 1},
)
def meoh_allocated_emissions():
    return initial_meoh_emissions() * emissions_cap_lookup(time())


@component.add(
    name="MeOH average cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_sector_share": 1,
        "green_biomeoh_cost": 1,
        "blue_meoh_sector_share": 1,
        "blue_meoh_cost": 1,
        "grey_meoh_sector_share": 1,
        "convmeoh_cost": 1,
        "green_emeoh_cost": 1,
        "emeoh_sector_share": 1,
    },
)
def meoh_average_cost():
    return (
        biomeoh_sector_share() * green_biomeoh_cost()
        + blue_meoh_sector_share() * blue_meoh_cost()
        + grey_meoh_sector_share() * convmeoh_cost()
        + emeoh_sector_share() * green_emeoh_cost()
    )


@component.add(
    name="MeOH backlog",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_meoh_backlog": 1},
    other_deps={
        "_integ_meoh_backlog": {
            "initial": {},
            "step": {"meoh_current_demand": 1, "sum_meoh_activity": 1},
        }
    },
)
def meoh_backlog():
    return _integ_meoh_backlog()


_integ_meoh_backlog = Integ(
    lambda: meoh_current_demand() - sum_meoh_activity(),
    lambda: 0,
    "_integ_meoh_backlog",
)


@component.add(
    name="MeOH biomass demand",
    units="GWh Biomass",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh": 1, "meoh_lhv": 1, "biomeoh_biomass_usage": 1},
)
def meoh_biomass_demand():
    """
    Convert from MT MeOH to GWh MeOH to GWh biomass
    """
    return biomeoh() * (meoh_lhv() / 3.6 * 1000) * biomeoh_biomass_usage()


@component.add(
    name="MeOH construction time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def meoh_construction_time():
    return 3


@component.add(
    name="MeOH continuous investment",
    units="MT MeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_forecast_demand": 1,
        "sum_meoh_decommissioning": 1,
        "meoh_construction_time": 1,
        "meoh_backlog": 1,
        "sum_meoh_activity": 1,
        "innovators": 1,
    },
)
def meoh_continuous_investment():
    return float(
        np.maximum(
            (
                meoh_forecast_demand()
                + sum_meoh_decommissioning()
                + meoh_backlog() / meoh_construction_time() / 3
                - sum_meoh_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="MeOH current demand",
    units="MT MeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"methanol_projected_production": 1},
)
def meoh_current_demand():
    return methanol_projected_production()


@component.add(
    name="MeOH effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_average_cost": 1, "meoh_lhv": 1, "meoh_current_demand": 1},
)
def meoh_effective_cost():
    return ((meoh_average_cost() * meoh_lhv()) / 1000) * meoh_current_demand()


@component.add(
    name="MeOH emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_meoh_emissions": 1, "grey_meoh_emissions": 1},
)
def meoh_emissions():
    return blue_meoh_emissions() + grey_meoh_emissions()


@component.add(
    name="MeOH excess activity",
    units="MT MeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_excess_emissions": 1, "grey_meoh_ef": 1, "hard_regulation": 1},
)
def meoh_excess_activity():
    return (
        float(np.maximum(meoh_excess_emissions() / grey_meoh_ef() / 10**6, 0))
        * hard_regulation()
    )


@component.add(
    name="MeOH excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_emissions": 1, "meoh_allocated_emissions": 1},
)
def meoh_excess_emissions():
    return meoh_emissions() - meoh_allocated_emissions()


@component.add(
    name="MeOH forecast demand",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_meoh_forecast_demand": 1},
    other_deps={
        "_forecast_meoh_forecast_demand": {
            "initial": {"meoh_current_demand": 1},
            "step": {"meoh_current_demand": 1, "meoh_construction_time": 2},
        }
    },
)
def meoh_forecast_demand():
    return _forecast_meoh_forecast_demand()


_forecast_meoh_forecast_demand = Forecast(
    lambda: meoh_current_demand(),
    lambda: 3 * meoh_construction_time(),
    lambda: meoh_construction_time(),
    lambda: 0,
    "_forecast_meoh_forecast_demand",
)


@component.add(
    name="MeOH hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh_hydrogen_demand": 1, "emeoh_hydrogen_demand": 1},
)
def meoh_hydrogen_demand():
    """
    Convert from GWh to GJ, then from GJ to tons fuel, then from tons fuel to tons H2. Example 1: MeOH cons. [GWh] * 3600 [GJ/GWh] / 19.9 [GJ/t] / 15.7 [t MeOH/t H2] Example 2: NH3 cons. [GWh] * 3600 [GJ/GWh] / 18.6 [GJ/t] / 5.56 [t NH3/t H2]
    """
    return biomeoh_hydrogen_demand() + emeoh_hydrogen_demand()


@component.add(
    name="MeOH initial sector activity",
    units="MT MeOH",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_meoh_initial_sector_activity": 1},
    other_deps={
        "_initial_meoh_initial_sector_activity": {
            "initial": {"meoh_current_demand": 1},
            "step": {},
        }
    },
)
def meoh_initial_sector_activity():
    return _initial_meoh_initial_sector_activity()


_initial_meoh_initial_sector_activity = Initial(
    lambda: meoh_current_demand(), "_initial_meoh_initial_sector_activity"
)


@component.add(
    name="MeOH innovator pipeline",
    units="MT MeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_continuous_investment": 1, "innovators": 2},
)
def meoh_innovator_pipeline():
    return meoh_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="MeOH innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_inno_switch": 1,
        "blue_meoh_inno_switch": 1,
        "emeoh_inno_switch": 1,
    },
)
def meoh_innovators():
    return float(
        np.maximum(
            biomeoh_inno_switch() + blue_meoh_inno_switch() + emeoh_inno_switch(), 1
        )
    )


@component.add(
    name="MeOH investment pipeline",
    units="MT MeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_continuous_investment": 1},
)
def meoh_investment_pipeline():
    return meoh_continuous_investment()


@component.add(
    name="MeOH plant lifetime",
    units="years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def meoh_plant_lifetime():
    return 20


@component.add(
    name="methanol projected production",
    units="MT MeOH",
    comp_type="Constant",
    comp_subtype="Normal",
)
def methanol_projected_production():
    """
    Domestic European MeOH production. Primary assumption: To not double count MeOH demand for chemicals, plastics, and fuels the demand is assumed constant moving forward. Source: Deloitte - Clean Hydrogen Europe. (https://www.clean-hydrogen.europa.eu/document/download/9fef29ac-6f95-465b- bb6e-1365526f43c4_en?filename=Study%20on%20hydrogen%20in%20ports%20and%20in dustrial%20coastal%20areas.pdf) Based on 2023 level of 11.3 MT. Forecasted 3.96% CAGR from 2023 to 2034. Assumed 3% CAGR from 2034 to 2050. Extrapolated back to 2019 with same growth as forecast (3.96%). Source: https://www.chemanalyst.com/industry-report/europe-methanol-market-215
    """
    return 2.3


@component.add(
    name="min green MeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_biomeoh_cost": 1, "green_emeoh_cost": 1},
)
def min_green_meoh_cost():
    return float(np.minimum(green_biomeoh_cost(), green_emeoh_cost()))


@component.add(
    name="Subsidized BioMeOH Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_biomeoh_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_biomeoh_commissioning": {
            "initial": {"meoh_construction_time": 1},
            "step": {"subsidized_biomeoh_investment": 1},
        }
    },
)
def subsidized_biomeoh_commissioning():
    return _delayfixed_subsidized_biomeoh_commissioning()


_delayfixed_subsidized_biomeoh_commissioning = DelayFixed(
    lambda: subsidized_biomeoh_investment(),
    lambda: meoh_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_biomeoh_commissioning",
)


@component.add(
    name="Subsidized BioMeOH Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_biomeoh_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_biomeoh_decommissioning": {
            "initial": {},
            "step": {"subsidized_biomeoh_commissioning": 1},
        }
    },
)
def subsidized_biomeoh_decommissioning():
    return _delayfixed_subsidized_biomeoh_decommissioning()


_delayfixed_subsidized_biomeoh_decommissioning = DelayFixed(
    lambda: subsidized_biomeoh_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_biomeoh_decommissioning",
)


@component.add(
    name="Subsidized BioMeOH Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "biomeoh_investment": 1,
        "biomeoh_h2_usage": 1,
    },
)
def subsidized_biomeoh_investment():
    return (
        if_then_else(
            biomeoh_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: biomeoh_investment(),
            lambda: 0,
        )
        / biomeoh_h2_usage()
    )


@component.add(
    name="Subsidized eMeOH Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_emeoh_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_emeoh_commissioning": {
            "initial": {"meoh_construction_time": 1},
            "step": {"subsidized_emeoh_investment": 1},
        }
    },
)
def subsidized_emeoh_commissioning():
    return _delayfixed_subsidized_emeoh_commissioning()


_delayfixed_subsidized_emeoh_commissioning = DelayFixed(
    lambda: subsidized_emeoh_investment(),
    lambda: meoh_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_emeoh_commissioning",
)


@component.add(
    name="Subsidized eMeOH Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_emeoh_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_emeoh_decommissioning": {
            "initial": {},
            "step": {"subsidized_emeoh_commissioning": 1},
        }
    },
)
def subsidized_emeoh_decommissioning():
    return _delayfixed_subsidized_emeoh_decommissioning()


_delayfixed_subsidized_emeoh_decommissioning = DelayFixed(
    lambda: subsidized_emeoh_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_emeoh_decommissioning",
)


@component.add(
    name="Subsidized eMeOH Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "emeoh_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "emeoh_investment": 1,
        "emeoh_h2_usage": 1,
    },
)
def subsidized_emeoh_investment():
    return (
        if_then_else(
            emeoh_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: emeoh_investment(),
            lambda: 0,
        )
        / emeoh_h2_usage()
    )


@component.add(
    name="sum MeOH activity",
    units="MT MeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_meoh": 1, "biomeoh": 1, "blue_meoh": 1, "emeoh": 1},
)
def sum_meoh_activity():
    return grey_meoh() + biomeoh() + blue_meoh() + emeoh()


@component.add(
    name="sum MeOH decommissioning",
    units="MT MeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_decommissioning": 1,
        "blue_meoh_decommissioning": 1,
        "emeoh_decommissioning": 1,
        "grey_meoh_decommissioning": 1,
        "grey_meoh_economic_decommissioning": 1,
    },
)
def sum_meoh_decommissioning():
    return (
        biomeoh_decommissioning()
        + blue_meoh_decommissioning()
        + emeoh_decommissioning()
        + grey_meoh_decommissioning()
        + grey_meoh_economic_decommissioning()
    )


@component.add(
    name="Support BioMeOH",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_biomeoh_investment": 1,
        "green_h2_subsidy": 1,
        "biomeoh_h2_subsidy": 1,
    },
)
def support_biomeoh():
    return (
        subsidized_biomeoh_investment()
        * (green_h2_subsidy() + biomeoh_h2_subsidy())
        * 10
    )


@component.add(
    name="Support eMeOH",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_emeoh_investment": 1,
        "green_h2_subsidy": 1,
        "emeoh_h2_subsidy": 1,
    },
)
def support_emeoh():
    return (
        subsidized_emeoh_investment() * (green_h2_subsidy() + emeoh_h2_subsidy()) * 10
    )


@component.add(
    name="xx",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh_investment": 1, "biomeoh_h2_usage": 1},
)
def xx():
    return biomeoh_investment() / biomeoh_h2_usage() * 10**6
