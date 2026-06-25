"""
Module oil_refining
Translated using PySD version 3.14.3
"""

@component.add(
    name="alternative H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_h2_cost": 1, "refinery_h2_cost": 1},
)
def alternative_h2_cost():
    return float(np.minimum(blue_h2_cost(), refinery_h2_cost()))


@component.add(
    name="Blue Refinery",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_blue_refinery": 1},
    other_deps={
        "_integ_blue_refinery": {
            "initial": {},
            "step": {
                "blue_refinery_commissioning": 1,
                "blue_refinery_decommissioning": 1,
            },
        }
    },
)
def blue_refinery():
    return _integ_blue_refinery()


_integ_blue_refinery = Integ(
    lambda: blue_refinery_commissioning() - blue_refinery_decommissioning(),
    lambda: 0,
    "_integ_blue_refinery",
)


@component.add(
    name="Blue refinery CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_h2_co2_wtp": 1},
)
def blue_refinery_co2_wtp():
    return blue_h2_co2_wtp()


@component.add(
    name="Blue Refinery Commissioning",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_refinery_construction": 1, "refinery_construction_time": 1},
)
def blue_refinery_commissioning():
    return blue_refinery_construction() / refinery_construction_time()


@component.add(
    name="Blue refinery competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_h2_cost": 1, "blue_h2_cost": 2, "refinery_h2_cost": 1},
)
def blue_refinery_competitiveness():
    """
    Old: MIN( Grey H2 cost / Blue H2 cost , refinery H2 cost / Blue H2 cost )
    """
    return float(
        np.minimum(grey_h2_cost() / blue_h2_cost(), refinery_h2_cost() / blue_h2_cost())
    )


@component.add(
    name="Blue Refinery Construction",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_blue_refinery_construction": 1},
    other_deps={
        "_integ_blue_refinery_construction": {
            "initial": {},
            "step": {
                "blue_refinery_innovators": 1,
                "blue_refinery_investment": 1,
                "blue_refinery_commissioning": 1,
            },
        }
    },
)
def blue_refinery_construction():
    return _integ_blue_refinery_construction()


_integ_blue_refinery_construction = Integ(
    lambda: blue_refinery_innovators()
    + blue_refinery_investment()
    - blue_refinery_commissioning(),
    lambda: 0,
    "_integ_blue_refinery_construction",
)


@component.add(
    name="Blue Refinery Decommissioning",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_refinery_delayed": 2, "blue_refinery": 2},
)
def blue_refinery_decommissioning():
    return if_then_else(
        blue_refinery_delayed() > blue_refinery(),
        lambda: blue_refinery(),
        lambda: blue_refinery_delayed(),
    )


@component.add(
    name="Blue Refinery delayed",
    units="MtH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_blue_refinery_delayed": 1},
    other_deps={
        "_delayfixed_blue_refinery_delayed": {
            "initial": {"smr_lifetime": 1},
            "step": {"blue_refinery_commissioning": 1},
        }
    },
)
def blue_refinery_delayed():
    return _delayfixed_blue_refinery_delayed()


_delayfixed_blue_refinery_delayed = DelayFixed(
    lambda: blue_refinery_commissioning(),
    lambda: smr_lifetime(),
    lambda: 0,
    time_step,
    "_delayfixed_blue_refinery_delayed",
)


@component.add(
    name="blue refinery emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_refinery": 1, "blue_h2_ef": 1},
)
def blue_refinery_emissions():
    return blue_refinery() * blue_h2_ef() * 10**6


@component.add(
    name="Blue refinery inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_refinery_competitiveness": 1, "inno_switch_level": 1},
)
def blue_refinery_inno_switch():
    return if_then_else(
        blue_refinery_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="Blue refinery innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_refinery_inno_switch": 1, "refinery_innovators": 1},
)
def blue_refinery_innovator_share():
    return blue_refinery_inno_switch() / refinery_innovators()


@component.add(
    name="Blue Refinery Innovators",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_innovator_pipeline": 1, "blue_refinery_innovator_share": 1},
)
def blue_refinery_innovators():
    return refinery_innovator_pipeline() * blue_refinery_innovator_share()


@component.add(
    name="Blue Refinery Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_investment_pipeline": 1, "blue_refinery_investment_share": 1},
)
def blue_refinery_investment():
    return refinery_investment_pipeline() * blue_refinery_investment_share()


@component.add(
    name="Blue refinery investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_equalizer": 1, "blue_refinery_level": 1},
)
def blue_refinery_investment_share():
    return refinery_equalizer() * blue_refinery_level()


@component.add(
    name="Blue refinery level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "blue_refinery_competitiveness": 2,
        "blue_refinery_sector_share": 1,
    },
)
def blue_refinery_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - blue_refinery_competitiveness()))))
        * float(np.maximum(0.1, blue_refinery_sector_share()))
        + blue_refinery_competitiveness() * 0.001
    )


@component.add(
    name="Blue refinery sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_refinery": 1, "sum_refinery_activity": 1},
)
def blue_refinery_sector_share():
    return blue_refinery() / sum_refinery_activity()


@component.add(
    name="Green Refinery",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_green_refinery": 1},
    other_deps={
        "_integ_green_refinery": {
            "initial": {},
            "step": {
                "green_refinery_commissioning": 1,
                "green_refinery_decommissioning": 1,
            },
        }
    },
)
def green_refinery():
    return _integ_green_refinery()


_integ_green_refinery = Integ(
    lambda: green_refinery_commissioning() - green_refinery_decommissioning(),
    lambda: 0,
    "_integ_green_refinery",
)


@component.add(
    name="Green Refinery bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_refinery_desired_investment": 1},
)
def green_refinery_bid_share():
    return green_refinery_desired_investment()


@component.add(
    name="Green Refinery Commissioning",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_refinery_construction": 1, "refinery_construction_time": 1},
)
def green_refinery_commissioning():
    return green_refinery_construction() / refinery_construction_time()


@component.add(
    name="Green Refinery Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_green_refinery_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_green_refinery_commissioning_subsidy_level": {
            "initial": {"refinery_construction_time": 1},
            "step": {"refinery_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def green_refinery_commissioning_subsidy_level():
    return _delayfixed_green_refinery_commissioning_subsidy_level()


_delayfixed_green_refinery_commissioning_subsidy_level = DelayFixed(
    lambda: refinery_h2_subsidy() + green_h2_subsidy(),
    lambda: refinery_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_green_refinery_commissioning_subsidy_level",
)


@component.add(
    name="Green refinery competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_h2_cost": 1, "refinery_h2_cost": 2, "grey_h2_cost": 1},
)
def green_refinery_competitiveness():
    """
    MIN( Blue H2 cost / refinery H2 cost , Grey H2 cost / refinery H2 cost )
    """
    return float(
        np.minimum(
            blue_h2_cost() / refinery_h2_cost(), grey_h2_cost() / refinery_h2_cost()
        )
    )


@component.add(
    name="Green Refinery Construction",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_green_refinery_construction": 1},
    other_deps={
        "_integ_green_refinery_construction": {
            "initial": {},
            "step": {
                "green_refinery_innovators": 1,
                "green_refinery_investment": 1,
                "green_refinery_commissioning": 1,
            },
        }
    },
)
def green_refinery_construction():
    return _integ_green_refinery_construction()


_integ_green_refinery_construction = Integ(
    lambda: green_refinery_innovators()
    + green_refinery_investment()
    - green_refinery_commissioning(),
    lambda: 0,
    "_integ_green_refinery_construction",
)


@component.add(
    name="Green Refinery Decommissioning",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_refinery_delayed": 2, "green_refinery": 2},
)
def green_refinery_decommissioning():
    return if_then_else(
        green_refinery_delayed() > green_refinery(),
        lambda: green_refinery(),
        lambda: green_refinery_delayed(),
    )


@component.add(
    name="Green Refinery Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_green_refinery_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_green_refinery_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"green_refinery_commissioning_subsidy_level": 1},
        }
    },
)
def green_refinery_decommissioning_subsidy_level():
    return _delayfixed_green_refinery_decommissioning_subsidy_level()


_delayfixed_green_refinery_decommissioning_subsidy_level = DelayFixed(
    lambda: green_refinery_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_green_refinery_decommissioning_subsidy_level",
)


@component.add(
    name="Green Refinery delayed",
    units="MtH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_green_refinery_delayed": 1},
    other_deps={
        "_delayfixed_green_refinery_delayed": {
            "initial": {"aec_lifetime": 1},
            "step": {"green_refinery_commissioning": 1},
        }
    },
)
def green_refinery_delayed():
    return _delayfixed_green_refinery_delayed()


_delayfixed_green_refinery_delayed = DelayFixed(
    lambda: green_refinery_commissioning(),
    lambda: aec_lifetime(),
    lambda: 0,
    time_step,
    "_delayfixed_green_refinery_delayed",
)


@component.add(
    name="Green Refinery desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_green_refinery_desired_investment": 1},
    other_deps={
        "_smooth_green_refinery_desired_investment": {
            "initial": {
                "green_refinery_level": 2,
                "blue_refinery_level": 1,
                "grey_refinery_level": 1,
            },
            "step": {
                "green_refinery_level": 2,
                "blue_refinery_level": 1,
                "grey_refinery_level": 1,
                "hba_stabilizer": 1,
            },
        }
    },
)
def green_refinery_desired_investment():
    return _smooth_green_refinery_desired_investment()


_smooth_green_refinery_desired_investment = Smooth(
    lambda: green_refinery_level()
    / (green_refinery_level() + grey_refinery_level() + blue_refinery_level()),
    lambda: hba_stabilizer(),
    lambda: green_refinery_level()
    / (green_refinery_level() + grey_refinery_level() + blue_refinery_level()),
    lambda: 1,
    "_smooth_green_refinery_desired_investment",
)


@component.add(
    name="Green Refinery HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_continuous_investment": 1, "green_refinery_bid_share": 1},
)
def green_refinery_hba_volume():
    return refinery_continuous_investment() * 10**6 * green_refinery_bid_share()


@component.add(
    name="Green refinery inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_refinery_competitiveness": 1, "inno_switch_level": 1},
)
def green_refinery_inno_switch():
    return if_then_else(
        green_refinery_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="Green refinery innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_refinery_inno_switch": 1, "refinery_innovators": 1},
)
def green_refinery_innovator_share():
    return green_refinery_inno_switch() / refinery_innovators()


@component.add(
    name="Green Refinery Innovators",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_innovator_pipeline": 1, "green_refinery_innovator_share": 1},
)
def green_refinery_innovators():
    return refinery_innovator_pipeline() * green_refinery_innovator_share()


@component.add(
    name="Green Refinery Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "refinery_investment_pipeline": 1,
        "green_refinery_investment_share": 1,
    },
)
def green_refinery_investment():
    return refinery_investment_pipeline() * green_refinery_investment_share()


@component.add(
    name="Green refinery investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "refinery_h2_subsidy": 1,
        "green_refinery_bid_share": 1,
        "refinery_equalizer": 1,
        "green_refinery_level": 1,
    },
)
def green_refinery_investment_share():
    return if_then_else(
        refinery_h2_subsidy() > 0.01,
        lambda: green_refinery_bid_share(),
        lambda: refinery_equalizer() * green_refinery_level(),
    )


@component.add(
    name="Green refinery level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "green_refinery_competitiveness": 2,
        "green_refinery_sector_share": 1,
    },
)
def green_refinery_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - green_refinery_competitiveness()))))
        * float(np.maximum(0.1, green_refinery_sector_share()))
        + green_refinery_competitiveness() * 0.001
    )


@component.add(
    name="Green refinery sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_refinery": 1, "sum_refinery_activity": 1},
)
def green_refinery_sector_share():
    return green_refinery() / sum_refinery_activity()


@component.add(
    name="Green Refinery subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_green_refinery_subsidy_cost": 1},
    other_deps={
        "_integ_green_refinery_subsidy_cost": {
            "initial": {},
            "step": {
                "green_refinery_commissioning_subsidy_level": 1,
                "subsidized_green_refinery_commissioning": 1,
                "green_refinery_decommissioning_subsidy_level": 1,
                "subsidized_green_refinery_decommissioning": 1,
            },
        }
    },
)
def green_refinery_subsidy_cost():
    return _integ_green_refinery_subsidy_cost()


_integ_green_refinery_subsidy_cost = Integ(
    lambda: green_refinery_commissioning_subsidy_level()
    * subsidized_green_refinery_commissioning()
    - green_refinery_decommissioning_subsidy_level()
    * subsidized_green_refinery_decommissioning(),
    lambda: 0,
    "_integ_green_refinery_subsidy_cost",
)


@component.add(
    name="Grey H2 cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_h2_cost_marginal": 1, "alternative_h2_cost": 1},
)
def grey_h2_cost_difference():
    return grey_h2_cost_marginal() / alternative_h2_cost()


@component.add(
    name="Grey Refinery",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_grey_refinery": 1},
    other_deps={
        "_integ_grey_refinery": {
            "initial": {"refinery_initial_sector_activity": 1},
            "step": {
                "grey_refinery_commissioning": 1,
                "grey_refinery_decommissioning": 1,
                "grey_refinery_economic_decommissioning": 1,
            },
        }
    },
)
def grey_refinery():
    return _integ_grey_refinery()


_integ_grey_refinery = Integ(
    lambda: grey_refinery_commissioning()
    - grey_refinery_decommissioning()
    - grey_refinery_economic_decommissioning(),
    lambda: refinery_initial_sector_activity(),
    "_integ_grey_refinery",
)


@component.add(
    name="Grey refinery CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_h2_co2_wtp": 1},
)
def grey_refinery_co2_wtp():
    return grey_h2_co2_wtp()


@component.add(
    name="Grey Refinery Commissioning",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_refinery_construction": 1, "refinery_construction_time": 1},
)
def grey_refinery_commissioning():
    return grey_refinery_construction() / refinery_construction_time()


@component.add(
    name="Grey refinery competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_h2_cost": 1, "grey_h2_cost": 2, "refinery_h2_cost": 1},
)
def grey_refinery_competitiveness():
    return float(
        np.minimum(blue_h2_cost() / grey_h2_cost(), refinery_h2_cost() / grey_h2_cost())
    )


@component.add(
    name="Grey Refinery Construction",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_grey_refinery_construction": 1},
    other_deps={
        "_integ_grey_refinery_construction": {
            "initial": {
                "refinery_initial_sector_activity": 1,
                "smr_lifetime": 1,
                "refinery_construction_time": 2,
            },
            "step": {"grey_refinery_investment": 1, "grey_refinery_commissioning": 1},
        }
    },
)
def grey_refinery_construction():
    return _integ_grey_refinery_construction()


_integ_grey_refinery_construction = Integ(
    lambda: grey_refinery_investment() - grey_refinery_commissioning(),
    lambda: refinery_initial_sector_activity()
    / smr_lifetime()
    * refinery_construction_time()
    * (1 - 0.048 * refinery_construction_time()),
    "_integ_grey_refinery_construction",
)


@component.add(
    name="Grey Refinery Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_grey_refinery_decommissioning": 1, "grey_refinery": 1},
    other_deps={
        "_smooth_grey_refinery_decommissioning": {
            "initial": {
                "grey_refinery_delayed": 1,
                "grey_refinery_economic_decommissioning_delayed": 1,
            },
            "step": {
                "grey_refinery_delayed": 1,
                "grey_refinery_economic_decommissioning_delayed": 1,
            },
        }
    },
)
def grey_refinery_decommissioning():
    return float(
        np.maximum(
            0,
            float(np.minimum(_smooth_grey_refinery_decommissioning(), grey_refinery())),
        )
    )


_smooth_grey_refinery_decommissioning = Smooth(
    lambda: grey_refinery_delayed() - grey_refinery_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: grey_refinery_delayed() - grey_refinery_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_grey_refinery_decommissioning",
)


@component.add(
    name="Grey Refinery delayed",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_grey_refinery_delayed": 1},
    other_deps={
        "_delayfixed_grey_refinery_delayed": {
            "initial": {"refinery_initial_sector_activity": 1, "smr_lifetime": 2},
            "step": {"grey_refinery_commissioning": 1},
        }
    },
)
def grey_refinery_delayed():
    return _delayfixed_grey_refinery_delayed()


_delayfixed_grey_refinery_delayed = DelayFixed(
    lambda: grey_refinery_commissioning(),
    lambda: smr_lifetime(),
    lambda: refinery_initial_sector_activity() / smr_lifetime(),
    time_step,
    "_delayfixed_grey_refinery_delayed",
)


@component.add(
    name="Grey Refinery Economic Decommissioning",
    units="MT H2 / Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "grey_h2_cost_difference": 2,
        "grey_refinery": 1,
        "smr_lifetime": 1,
        "slope_decom": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def grey_refinery_economic_decommissioning():
    return (
        if_then_else(
            grey_h2_cost_difference() > 1,
            lambda: (grey_refinery() / smr_lifetime() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (grey_h2_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="Grey Refinery Economic Decommissioning delayed",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_grey_refinery_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_grey_refinery_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"grey_refinery_economic_decommissioning": 1},
        }
    },
)
def grey_refinery_economic_decommissioning_delayed():
    return _delayn_grey_refinery_economic_decommissioning_delayed()


_delayn_grey_refinery_economic_decommissioning_delayed = DelayN(
    lambda: grey_refinery_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_grey_refinery_economic_decommissioning_delayed",
)


@component.add(
    name="grey refinery emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_refinery": 1, "grey_h2_ef": 1},
)
def grey_refinery_emissions():
    return grey_refinery() * grey_h2_ef() * 10**6


@component.add(
    name="Grey Refinery Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_investment_pipeline": 1, "grey_refinery_investment_share": 1},
)
def grey_refinery_investment():
    return refinery_investment_pipeline() * grey_refinery_investment_share()


@component.add(
    name="Grey refinery investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_equalizer": 1, "grey_refinery_level": 1},
)
def grey_refinery_investment_share():
    return refinery_equalizer() * grey_refinery_level()


@component.add(
    name="Grey refinery level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "grey_refinery_competitiveness": 2,
        "grey_refinery_sector_share": 1,
        "refinery_excess_activity": 1,
    },
)
def grey_refinery_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - grey_refinery_competitiveness()))))
        * float(np.maximum(0.1, grey_refinery_sector_share()))
        * if_then_else(refinery_excess_activity() > 0, lambda: 0, lambda: 1)
        + grey_refinery_competitiveness() * 0.001
    )


@component.add(
    name="Grey refinery sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_refinery": 1, "sum_refinery_activity": 1},
)
def grey_refinery_sector_share():
    return grey_refinery() / sum_refinery_activity()


@component.add(name="HBA stabilizer", comp_type="Constant", comp_subtype="Normal")
def hba_stabilizer():
    return 0.5


@component.add(
    name="Initial refinery emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_refinery_emissions": 1},
    other_deps={
        "_initial_initial_refinery_emissions": {
            "initial": {"refinery_emissions": 1},
            "step": {},
        }
    },
)
def initial_refinery_emissions():
    return _initial_initial_refinery_emissions()


_initial_initial_refinery_emissions = Initial(
    lambda: refinery_emissions(), "_initial_initial_refinery_emissions"
)


@component.add(
    name="refinery allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_refinery_emissions": 1, "emissions_cap_lookup": 1, "time": 1},
)
def refinery_allocated_emissions():
    return initial_refinery_emissions() * emissions_cap_lookup(time())


@component.add(
    name="refinery average cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_refinery_sector_share": 1,
        "blue_h2_cost": 1,
        "green_refinery_sector_share": 1,
        "refinery_h2_cost": 1,
        "grey_refinery_sector_share": 1,
        "grey_h2_cost": 1,
    },
)
def refinery_average_cost():
    return (
        blue_refinery_sector_share() * blue_h2_cost()
        + green_refinery_sector_share() * refinery_h2_cost()
        + grey_refinery_sector_share() * grey_h2_cost()
    )


@component.add(
    name="refinery backlog",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_refinery_backlog": 1},
    other_deps={
        "_integ_refinery_backlog": {
            "initial": {"sum_refinery_activity": 1},
            "step": {"refinery_current_demand": 1, "sum_refinery_activity": 1},
        }
    },
)
def refinery_backlog():
    return _integ_refinery_backlog()


_integ_refinery_backlog = Integ(
    lambda: refinery_current_demand() - sum_refinery_activity(),
    lambda: -sum_refinery_activity() * 0.048 * 3,
    "_integ_refinery_backlog",
)


@component.add(
    name="refinery blue hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_refinery": 1},
)
def refinery_blue_hydrogen_demand():
    return blue_refinery() * 10**6


@component.add(
    name="refinery construction time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def refinery_construction_time():
    return 2


@component.add(
    name="refinery continuous investment",
    units="MT H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "refinery_forecast_demand": 1,
        "sum_refinery_decommissioning": 1,
        "refinery_backlog": 1,
        "refinery_construction_time": 1,
        "sum_refinery_activity": 1,
        "innovators": 1,
    },
)
def refinery_continuous_investment():
    return float(
        np.maximum(
            (
                refinery_forecast_demand()
                + sum_refinery_decommissioning()
                + refinery_backlog() / refinery_construction_time() / 3
                - sum_refinery_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="refinery current demand",
    units="MT H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "refinery_projected_demand": 1},
)
def refinery_current_demand():
    """
    19.1 MT/year - assumed constant moving forward. EHB European Backbone Report: 19.1 Mt/year CEPS Report: 21 Mt/year (capacity)
    """
    return refinery_projected_demand(time())


@component.add(
    name="refinery effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_average_cost": 1, "refinery_current_demand": 1},
)
def refinery_effective_cost():
    """
    kgH2 -> MtH2 conversion and € to B€ cancel out.
    """
    return refinery_average_cost() * refinery_current_demand()


@component.add(
    name="refinery emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_refinery_emissions": 1, "grey_refinery_emissions": 1},
)
def refinery_emissions():
    return blue_refinery_emissions() + grey_refinery_emissions()


@component.add(
    name="Refinery equalizer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "refinery_h2_subsidy": 1,
        "blue_refinery_level": 2,
        "green_refinery_bid_share": 1,
        "grey_refinery_level": 2,
        "green_refinery_level": 1,
    },
)
def refinery_equalizer():
    return if_then_else(
        refinery_h2_subsidy() > 0.01,
        lambda: (1 - green_refinery_bid_share())
        / (grey_refinery_level() + blue_refinery_level()),
        lambda: 1
        / (grey_refinery_level() + green_refinery_level() + blue_refinery_level()),
    )


@component.add(
    name="refinery excess activity",
    units="MT H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_excess_emissions": 1, "grey_h2_ef": 1, "hard_regulation": 1},
)
def refinery_excess_activity():
    return (
        float(np.maximum(refinery_excess_emissions() / grey_h2_ef() / 10**6, 0))
        * hard_regulation()
    )


@component.add(
    name="refinery excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_emissions": 1, "refinery_allocated_emissions": 1},
)
def refinery_excess_emissions():
    return refinery_emissions() - refinery_allocated_emissions()


@component.add(
    name="refinery forecast demand",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_refinery_forecast_demand": 1},
    other_deps={
        "_forecast_refinery_forecast_demand": {
            "initial": {"refinery_current_demand": 1},
            "step": {"refinery_current_demand": 1, "refinery_construction_time": 2},
        }
    },
)
def refinery_forecast_demand():
    return _forecast_refinery_forecast_demand()


_forecast_refinery_forecast_demand = Forecast(
    lambda: refinery_current_demand(),
    lambda: 3 * refinery_construction_time(),
    lambda: refinery_construction_time(),
    lambda: 0,
    "_forecast_refinery_forecast_demand",
)


@component.add(
    name="refinery grey hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_refinery": 1},
)
def refinery_grey_hydrogen_demand():
    return grey_refinery() * 10**6


@component.add(
    name="refinery H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_h2_wtp": 1},
)
def refinery_h2_wtp():
    return green_h2_h2_wtp()


@component.add(
    name="refinery hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_refinery": 1},
)
def refinery_hydrogen_demand():
    """
    Convert from MT to T NH3, then from T NH3 to T H2.
    """
    return green_refinery() * 10**6


@component.add(
    name="refinery initial sector activity",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_refinery_initial_sector_activity": 1},
    other_deps={
        "_initial_refinery_initial_sector_activity": {
            "initial": {"refinery_current_demand": 1},
            "step": {},
        }
    },
)
def refinery_initial_sector_activity():
    return _initial_refinery_initial_sector_activity()


_initial_refinery_initial_sector_activity = Initial(
    lambda: refinery_current_demand(), "_initial_refinery_initial_sector_activity"
)


@component.add(
    name="refinery innovator pipeline",
    units="MT H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_continuous_investment": 1, "innovators": 2},
)
def refinery_innovator_pipeline():
    return refinery_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="refinery innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_refinery_inno_switch": 1, "green_refinery_inno_switch": 1},
)
def refinery_innovators():
    return float(
        np.maximum(blue_refinery_inno_switch() + green_refinery_inno_switch(), 1)
    )


@component.add(
    name="refinery investment pipeline",
    units="MT H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_continuous_investment": 1},
)
def refinery_investment_pipeline():
    return refinery_continuous_investment()


@component.add(
    name="refinery projected demand",
    units="MT H2",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_refinery_projected_demand"},
)
def refinery_projected_demand(x, final_subs=None):
    """
    2.4 MT/year in 2022. Linearly decreasing. https://www.petrochemistry.eu/wp-content/uploads/2021/03/Petrochemicals_Pap er_hydrogen-1.pdf
    """
    return _hardcodedlookup_refinery_projected_demand(x, final_subs)


_hardcodedlookup_refinery_projected_demand = HardcodedLookups(
    [
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
        2.4,
        2.352,
        2.30496,
        2.25886,
        2.21368,
        2.16941,
        2.12602,
        2.0835,
        2.04183,
        2.00099,
        1.96097,
        1.92176,
        1.88332,
        1.84565,
        1.80874,
        1.77257,
        1.73711,
        1.70237,
        1.66832,
        1.63496,
        1.60226,
        1.57021,
        1.53881,
        1.50803,
        1.47787,
        1.44832,
        1.41935,
        1.39096,
        1.36314,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_refinery_projected_demand",
)


@component.add(
    name="Subsidized Green Refinery Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_green_refinery_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_green_refinery_commissioning": {
            "initial": {"refinery_construction_time": 1},
            "step": {"subsidized_green_refinery_investment": 1},
        }
    },
)
def subsidized_green_refinery_commissioning():
    return _delayfixed_subsidized_green_refinery_commissioning()


_delayfixed_subsidized_green_refinery_commissioning = DelayFixed(
    lambda: subsidized_green_refinery_investment(),
    lambda: refinery_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_green_refinery_commissioning",
)


@component.add(
    name="Subsidized Green Refinery Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_green_refinery_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_green_refinery_decommissioning": {
            "initial": {},
            "step": {"subsidized_green_refinery_commissioning": 1},
        }
    },
)
def subsidized_green_refinery_decommissioning():
    return _delayfixed_subsidized_green_refinery_decommissioning()


_delayfixed_subsidized_green_refinery_decommissioning = DelayFixed(
    lambda: subsidized_green_refinery_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_green_refinery_decommissioning",
)


@component.add(
    name="Subsidized Green Refinery Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "refinery_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "green_refinery_investment": 1,
    },
)
def subsidized_green_refinery_investment():
    return if_then_else(
        refinery_h2_subsidy() + green_h2_subsidy() > 0,
        lambda: green_refinery_investment(),
        lambda: 0,
    )


@component.add(
    name="sum refinery activity",
    units="MT H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_refinery": 1, "green_refinery": 1, "blue_refinery": 1},
)
def sum_refinery_activity():
    return grey_refinery() + green_refinery() + blue_refinery()


@component.add(
    name="sum refinery construction",
    units="MT H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_refinery_construction": 1,
        "grey_refinery_construction": 1,
        "green_refinery_construction": 1,
    },
)
def sum_refinery_construction():
    return (
        blue_refinery_construction()
        + grey_refinery_construction()
        + green_refinery_construction()
    )


@component.add(
    name="sum refinery decommissioning",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_refinery_decommissioning": 1,
        "green_refinery_decommissioning": 1,
        "grey_refinery_decommissioning": 1,
        "grey_refinery_economic_decommissioning": 1,
    },
)
def sum_refinery_decommissioning():
    return (
        blue_refinery_decommissioning()
        + green_refinery_decommissioning()
        + grey_refinery_decommissioning()
        + grey_refinery_economic_decommissioning()
    )


@component.add(
    name="Support Green Refinery",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_green_refinery_investment": 1,
        "green_h2_subsidy": 1,
        "refinery_h2_subsidy": 1,
    },
)
def support_green_refinery():
    return (
        subsidized_green_refinery_investment()
        * (green_h2_subsidy() + refinery_h2_subsidy())
        * 10
    )
