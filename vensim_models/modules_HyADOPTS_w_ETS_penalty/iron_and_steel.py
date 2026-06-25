"""
Module iron_and_steel
Translated using PySD version 3.14.3
"""

@component.add(
    name="alternative steel cost",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof_ccs_cost": 1, "h2dri_cost": 1},
)
def alternative_steel_cost():
    return float(np.minimum(bf_bof_ccs_cost(), h2dri_cost()))


@component.add(
    name="BF BOF",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_bf_bof": 1},
    other_deps={
        "_integ_bf_bof": {
            "initial": {"steel_initial_sector_activity": 1},
            "step": {
                "bf_bof_commissioning": 1,
                "bf_bof_decommissioning": 1,
                "bf_bof_economic_decommissioning": 1,
            },
        }
    },
)
def bf_bof():
    return _integ_bf_bof()


_integ_bf_bof = Integ(
    lambda: bf_bof_commissioning()
    - bf_bof_decommissioning()
    - bf_bof_economic_decommissioning(),
    lambda: steel_initial_sector_activity(),
    "_integ_bf_bof",
)


@component.add(
    name="BF BOF CCS",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_bf_bof_ccs": 1},
    other_deps={
        "_integ_bf_bof_ccs": {
            "initial": {},
            "step": {"bf_bof_ccs_commissioning": 1, "bf_bof_ccs_decommissioning": 1},
        }
    },
)
def bf_bof_ccs():
    return _integ_bf_bof_ccs()


_integ_bf_bof_ccs = Integ(
    lambda: bf_bof_ccs_commissioning() - bf_bof_ccs_decommissioning(),
    lambda: 0,
    "_integ_bf_bof_ccs",
)


@component.add(
    name="BF BOF CCS Commissioning",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof_ccs_construction": 1, "foundry_construction_time": 1},
)
def bf_bof_ccs_commissioning():
    return bf_bof_ccs_construction() / foundry_construction_time()


@component.add(
    name="BF BOF CCS competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ngdri_cost": 1,
        "bf_bof_ccs_cost": 3,
        "bf_bof_cost": 1,
        "h2dri_cost": 1,
    },
)
def bf_bof_ccs_competitiveness():
    return float(
        np.minimum(
            ngdri_cost() / bf_bof_ccs_cost(),
            float(
                np.minimum(
                    bf_bof_cost() / bf_bof_ccs_cost(), h2dri_cost() / bf_bof_ccs_cost()
                )
            ),
        )
    )


@component.add(
    name="BF BOF CCS Construction",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_bf_bof_ccs_construction": 1},
    other_deps={
        "_integ_bf_bof_ccs_construction": {
            "initial": {},
            "step": {
                "bf_bof_ccs_innovators": 1,
                "bf_bof_ccs_investment": 1,
                "bf_bof_ccs_commissioning": 1,
            },
        }
    },
)
def bf_bof_ccs_construction():
    return _integ_bf_bof_ccs_construction()


_integ_bf_bof_ccs_construction = Integ(
    lambda: bf_bof_ccs_innovators()
    + bf_bof_ccs_investment()
    - bf_bof_ccs_commissioning(),
    lambda: 0,
    "_integ_bf_bof_ccs_construction",
)


@component.add(
    name="BF BOF CCS Decommissioning",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof_ccs": 1, "foundry_lifetime": 1},
)
def bf_bof_ccs_decommissioning():
    return bf_bof_ccs() / foundry_lifetime()


@component.add(
    name="BF BOF CCS EF",
    units="tCO2/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "el_to_steel_bf_coal": 1,
        "electricity_emission_factor": 1,
        "bf_coal_emission_factor": 1,
        "cc_capture_rate": 1,
    },
)
def bf_bof_ccs_ef():
    return (
        el_to_steel_bf_coal() * electricity_emission_factor()
        + bf_coal_emission_factor() * (1 - cc_capture_rate())
    )


@component.add(
    name="BF BOF CCS emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof_ccs": 1, "bf_bof_ccs_ef": 1},
)
def bf_bof_ccs_emissions():
    return bf_bof_ccs() * bf_bof_ccs_ef() * 10**6


@component.add(
    name="BF BOF CCS Innovators",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_innovator_pipeline": 1, "bf_ccs_innovator_share": 1},
)
def bf_bof_ccs_innovators():
    return steel_innovator_pipeline() * bf_ccs_innovator_share()


@component.add(
    name="BF BOF CCS Investment",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_investment_pipeline": 1, "bf_bof_ccs_investment_share": 1},
)
def bf_bof_ccs_investment():
    return steel_investment_pipeline() * bf_bof_ccs_investment_share()


@component.add(
    name="BF BOF CCS investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_equalizer": 1, "bf_bof_ccs_level": 1},
)
def bf_bof_ccs_investment_share():
    return steel_equalizer() * bf_bof_ccs_level()


@component.add(
    name="BF BOF CCS level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "bf_bof_ccs_competitiveness": 2,
        "bf_bof_ccs_sector_share": 1,
    },
)
def bf_bof_ccs_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - bf_bof_ccs_competitiveness()))))
        * float(np.maximum(0.1, bf_bof_ccs_sector_share()))
        + bf_bof_ccs_competitiveness() * 0.001
    )


@component.add(
    name="BF BOF CCS sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof_ccs": 1, "sum_steel_activity": 1},
)
def bf_bof_ccs_sector_share():
    return bf_bof_ccs() / sum_steel_activity()


@component.add(
    name="BF BOF Commissioning",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof_construction": 1, "foundry_construction_time": 1},
)
def bf_bof_commissioning():
    return bf_bof_construction() / foundry_construction_time()


@component.add(
    name="BF BOF competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ngdri_cost": 1,
        "bf_bof_cost": 3,
        "bf_bof_ccs_cost": 1,
        "h2dri_cost": 1,
    },
)
def bf_bof_competitiveness():
    return float(
        np.minimum(
            ngdri_cost() / bf_bof_cost(),
            float(
                np.minimum(
                    bf_bof_ccs_cost() / bf_bof_cost(), h2dri_cost() / bf_bof_cost()
                )
            ),
        )
    )


@component.add(
    name="BF BOF Construction",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_bf_bof_construction": 1},
    other_deps={
        "_integ_bf_bof_construction": {
            "initial": {
                "steel_initial_sector_activity": 1,
                "foundry_lifetime": 1,
                "foundry_construction_time": 1,
            },
            "step": {"bf_bof_investment": 1, "bf_bof_commissioning": 1},
        }
    },
)
def bf_bof_construction():
    return _integ_bf_bof_construction()


_integ_bf_bof_construction = Integ(
    lambda: bf_bof_investment() - bf_bof_commissioning(),
    lambda: steel_initial_sector_activity()
    / foundry_lifetime()
    * foundry_construction_time(),
    "_integ_bf_bof_construction",
)


@component.add(
    name="BF BOF cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof_cost_marginal": 1, "alternative_steel_cost": 1},
)
def bf_bof_cost_difference():
    return bf_bof_cost_marginal() / alternative_steel_cost()


@component.add(
    name="BF BOF Decommissioning",
    units="MT steel/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_bf_bof_decommissioning": 1, "bf_bof": 1},
    other_deps={
        "_smooth_bf_bof_decommissioning": {
            "initial": {
                "bf_bof_delayed": 1,
                "bf_bof_economic_decommissioning_delayed": 1,
            },
            "step": {"bf_bof_delayed": 1, "bf_bof_economic_decommissioning_delayed": 1},
        }
    },
)
def bf_bof_decommissioning():
    return float(
        np.maximum(0, float(np.minimum(_smooth_bf_bof_decommissioning(), bf_bof())))
    )


_smooth_bf_bof_decommissioning = Smooth(
    lambda: bf_bof_delayed() - bf_bof_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: bf_bof_delayed() - bf_bof_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_bf_bof_decommissioning",
)


@component.add(
    name="BF BOF delayed",
    units="MT steel/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_bf_bof_delayed": 1},
    other_deps={
        "_delayfixed_bf_bof_delayed": {
            "initial": {"steel_initial_sector_activity": 1, "foundry_lifetime": 2},
            "step": {"bf_bof_commissioning": 1},
        }
    },
)
def bf_bof_delayed():
    return _delayfixed_bf_bof_delayed()


_delayfixed_bf_bof_delayed = DelayFixed(
    lambda: bf_bof_commissioning(),
    lambda: foundry_lifetime(),
    lambda: steel_initial_sector_activity() / foundry_lifetime(),
    time_step,
    "_delayfixed_bf_bof_delayed",
)


@component.add(
    name="BF BOF economic decommissioning",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_bof_cost_difference": 2,
        "slope_decom": 1,
        "foundry_lifetime": 1,
        "bf_bof": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def bf_bof_economic_decommissioning():
    return (
        if_then_else(
            bf_bof_cost_difference() > 1,
            lambda: (bf_bof() / foundry_lifetime() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (bf_bof_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="BF BOF economic decommissioning delayed",
    units="MT steel/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_bf_bof_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_bf_bof_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"bf_bof_economic_decommissioning": 1},
        }
    },
)
def bf_bof_economic_decommissioning_delayed():
    return _delayn_bf_bof_economic_decommissioning_delayed()


_delayn_bf_bof_economic_decommissioning_delayed = DelayN(
    lambda: bf_bof_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_bf_bof_economic_decommissioning_delayed",
)


@component.add(
    name="BF BOF EF",
    units="tCO2/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "el_to_steel_bf_coal": 1,
        "electricity_emission_factor": 1,
        "bf_coal_emission_factor": 1,
    },
)
def bf_bof_ef():
    return (
        el_to_steel_bf_coal() * electricity_emission_factor()
        + bf_coal_emission_factor()
    )


@component.add(
    name="BF BOF emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof": 1, "bf_bof_ef": 1},
)
def bf_bof_emissions():
    return bf_bof() * bf_bof_ef() * 10**6


@component.add(
    name="BF BOF Investment",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_investment_pipeline": 1, "bf_bof_investment_share": 1},
)
def bf_bof_investment():
    return steel_investment_pipeline() * bf_bof_investment_share()


@component.add(
    name="BF BOF investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_equalizer": 1, "bf_bof_level": 1},
)
def bf_bof_investment_share():
    return steel_equalizer() * bf_bof_level()


@component.add(
    name="BF BOF level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "bf_bof_competitiveness": 2,
        "bf_bof_sector_share": 1,
        "steel_excess_activity": 1,
    },
)
def bf_bof_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - bf_bof_competitiveness()))))
        * float(np.maximum(0.1, bf_bof_sector_share()))
        * if_then_else(steel_excess_activity() > 0, lambda: 0, lambda: 1)
        + bf_bof_competitiveness() * 0.001
    )


@component.add(
    name="BF BOF sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof": 1, "sum_steel_activity": 1},
)
def bf_bof_sector_share():
    return bf_bof() / sum_steel_activity()


@component.add(
    name="BF CCS inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof_ccs_competitiveness": 1, "inno_switch_level": 1},
)
def bf_ccs_inno_switch():
    return if_then_else(
        bf_bof_ccs_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="BF CCS innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_ccs_inno_switch": 1, "steel_innovators": 1},
)
def bf_ccs_innovator_share():
    return bf_ccs_inno_switch() / steel_innovators()


@component.add(
    name="foundry construction time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def foundry_construction_time():
    return 3


@component.add(
    name="foundry lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def foundry_lifetime():
    return 25


@component.add(
    name="H2 to steel", units="tH2/tsteel", comp_type="Constant", comp_subtype="Normal"
)
def h2_to_steel():
    return 0.0563


@component.add(
    name="H2DRI EAF",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_h2dri_eaf": 1},
    other_deps={
        "_integ_h2dri_eaf": {
            "initial": {},
            "step": {"h2dri_eaf_commissioning": 1, "h2dri_eaf_decommissioning": 1},
        }
    },
)
def h2dri_eaf():
    return _integ_h2dri_eaf()


_integ_h2dri_eaf = Integ(
    lambda: h2dri_eaf_commissioning() - h2dri_eaf_decommissioning(),
    lambda: 0,
    "_integ_h2dri_eaf",
)


@component.add(
    name="H2DRI EAF bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_eaf_desired_investment": 1},
)
def h2dri_eaf_bid_share():
    return h2dri_eaf_desired_investment()


@component.add(
    name="H2DRI EAF Commissioning",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_eaf_construction": 1, "foundry_construction_time": 1},
)
def h2dri_eaf_commissioning():
    return h2dri_eaf_construction() / foundry_construction_time()


@component.add(
    name="H2DRI EAF Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_h2dri_eaf_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_h2dri_eaf_commissioning_subsidy_level": {
            "initial": {"foundry_construction_time": 1},
            "step": {"steel_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def h2dri_eaf_commissioning_subsidy_level():
    return _delayfixed_h2dri_eaf_commissioning_subsidy_level()


_delayfixed_h2dri_eaf_commissioning_subsidy_level = DelayFixed(
    lambda: steel_h2_subsidy() + green_h2_subsidy(),
    lambda: foundry_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_h2dri_eaf_commissioning_subsidy_level",
)


@component.add(
    name="H2DRI EAF competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ngdri_cost": 1,
        "h2dri_cost": 3,
        "bf_bof_cost": 1,
        "bf_bof_ccs_cost": 1,
    },
)
def h2dri_eaf_competitiveness():
    return float(
        np.minimum(
            ngdri_cost() / h2dri_cost(),
            float(
                np.minimum(
                    bf_bof_cost() / h2dri_cost(), bf_bof_ccs_cost() / h2dri_cost()
                )
            ),
        )
    )


@component.add(
    name="H2DRI EAF Construction",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_h2dri_eaf_construction": 1},
    other_deps={
        "_integ_h2dri_eaf_construction": {
            "initial": {},
            "step": {
                "h2dri_eaf_innovators": 1,
                "h2dri_eaf_investment": 1,
                "h2dri_eaf_commissioning": 1,
            },
        }
    },
)
def h2dri_eaf_construction():
    return _integ_h2dri_eaf_construction()


_integ_h2dri_eaf_construction = Integ(
    lambda: h2dri_eaf_innovators() + h2dri_eaf_investment() - h2dri_eaf_commissioning(),
    lambda: 0,
    "_integ_h2dri_eaf_construction",
)


@component.add(
    name="H2DRI EAF Decommissioning",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_eaf": 1, "foundry_lifetime": 1},
)
def h2dri_eaf_decommissioning():
    return h2dri_eaf() / foundry_lifetime()


@component.add(
    name="H2DRI EAF Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_h2dri_eaf_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_h2dri_eaf_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"h2dri_eaf_commissioning_subsidy_level": 1},
        }
    },
)
def h2dri_eaf_decommissioning_subsidy_level():
    return _delayfixed_h2dri_eaf_decommissioning_subsidy_level()


_delayfixed_h2dri_eaf_decommissioning_subsidy_level = DelayFixed(
    lambda: h2dri_eaf_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_h2dri_eaf_decommissioning_subsidy_level",
)


@component.add(
    name="H2DRI EAF desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_h2dri_eaf_desired_investment": 1},
    other_deps={
        "_smooth_h2dri_eaf_desired_investment": {
            "initial": {
                "h2dri_eaf_level": 2,
                "ngdri_eaf_level": 1,
                "bf_bof_ccs_level": 1,
                "bf_bof_level": 1,
            },
            "step": {
                "h2dri_eaf_level": 2,
                "ngdri_eaf_level": 1,
                "bf_bof_ccs_level": 1,
                "bf_bof_level": 1,
                "hba_stabilizer": 1,
            },
        }
    },
)
def h2dri_eaf_desired_investment():
    return _smooth_h2dri_eaf_desired_investment()


_smooth_h2dri_eaf_desired_investment = Smooth(
    lambda: h2dri_eaf_level()
    / (bf_bof_ccs_level() + bf_bof_level() + h2dri_eaf_level() + ngdri_eaf_level()),
    lambda: hba_stabilizer(),
    lambda: h2dri_eaf_level()
    / (bf_bof_ccs_level() + bf_bof_level() + h2dri_eaf_level() + ngdri_eaf_level()),
    lambda: 1,
    "_smooth_h2dri_eaf_desired_investment",
)


@component.add(
    name="H2DRI EAF EF",
    units="tCO2/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"el_to_steel_h2dri": 1, "electricity_emission_factor": 1},
)
def h2dri_eaf_ef():
    return el_to_steel_h2dri() / 3.6 * electricity_emission_factor()


@component.add(
    name="H2DRI EAF emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_eaf": 1, "h2dri_eaf_ef": 1},
)
def h2dri_eaf_emissions():
    return h2dri_eaf() * h2dri_eaf_ef() * 10**6


@component.add(
    name="H2DRI EAF HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "steel_continuous_investment": 1,
        "h2_to_steel": 1,
        "h2dri_eaf_bid_share": 1,
    },
)
def h2dri_eaf_hba_volume():
    return steel_continuous_investment() * 10**6 * h2_to_steel() * h2dri_eaf_bid_share()


@component.add(
    name="H2DRI EAF inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_eaf_competitiveness": 1, "inno_switch_level": 1},
)
def h2dri_eaf_inno_switch():
    return if_then_else(
        h2dri_eaf_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="H2DRI EAF innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_eaf_inno_switch": 1, "steel_innovators": 1},
)
def h2dri_eaf_innovator_share():
    return h2dri_eaf_inno_switch() / steel_innovators()


@component.add(
    name="H2DRI EAF Innovators",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_innovator_pipeline": 1, "h2dri_eaf_innovator_share": 1},
)
def h2dri_eaf_innovators():
    return steel_innovator_pipeline() * h2dri_eaf_innovator_share()


@component.add(
    name="H2DRI EAF Investment",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_investment_pipeline": 1, "h2dri_eaf_investment_share": 1},
)
def h2dri_eaf_investment():
    return steel_investment_pipeline() * h2dri_eaf_investment_share()


@component.add(
    name="H2DRI EAF investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "steel_h2_subsidy": 1,
        "h2dri_eaf_bid_share": 1,
        "steel_equalizer": 1,
        "h2dri_eaf_level": 1,
    },
)
def h2dri_eaf_investment_share():
    return if_then_else(
        steel_h2_subsidy() > 0.01,
        lambda: h2dri_eaf_bid_share(),
        lambda: steel_equalizer() * h2dri_eaf_level(),
    )


@component.add(
    name="H2DRI EAF level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "h2dri_eaf_competitiveness": 2,
        "h2dri_eaf_sector_share": 1,
    },
)
def h2dri_eaf_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - h2dri_eaf_competitiveness()))))
        * float(np.maximum(0.1, h2dri_eaf_sector_share()))
        + h2dri_eaf_competitiveness() * 0.001
    )


@component.add(
    name="H2DRI EAF sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_eaf": 1, "sum_steel_activity": 1},
)
def h2dri_eaf_sector_share():
    return h2dri_eaf() / sum_steel_activity()


@component.add(
    name="H2DRI EAF subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_h2dri_eaf_subsidy_cost": 1},
    other_deps={
        "_integ_h2dri_eaf_subsidy_cost": {
            "initial": {},
            "step": {
                "h2dri_eaf_commissioning_subsidy_level": 1,
                "subsidized_h2dri_eaf_commissioning": 1,
                "h2dri_eaf_decommissioning_subsidy_level": 1,
                "subsidized_h2dri_eaf_decommissioning": 1,
            },
        }
    },
)
def h2dri_eaf_subsidy_cost():
    return _integ_h2dri_eaf_subsidy_cost()


_integ_h2dri_eaf_subsidy_cost = Integ(
    lambda: h2dri_eaf_commissioning_subsidy_level()
    * subsidized_h2dri_eaf_commissioning()
    - h2dri_eaf_decommissioning_subsidy_level()
    * subsidized_h2dri_eaf_decommissioning(),
    lambda: 0,
    "_integ_h2dri_eaf_subsidy_cost",
)


@component.add(
    name="Initial steel emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_steel_emissions": 1},
    other_deps={
        "_initial_initial_steel_emissions": {
            "initial": {"steel_emissions": 1},
            "step": {},
        }
    },
)
def initial_steel_emissions():
    return _initial_initial_steel_emissions()


_initial_initial_steel_emissions = Initial(
    lambda: steel_emissions(), "_initial_initial_steel_emissions"
)


@component.add(
    name="NGDRI EAF",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ngdri_eaf": 1},
    other_deps={
        "_integ_ngdri_eaf": {
            "initial": {},
            "step": {"ngdri_eaf_commissioning": 1, "ngdri_eaf_decommissioning": 1},
        }
    },
)
def ngdri_eaf():
    return _integ_ngdri_eaf()


_integ_ngdri_eaf = Integ(
    lambda: ngdri_eaf_commissioning() - ngdri_eaf_decommissioning(),
    lambda: 0,
    "_integ_ngdri_eaf",
)


@component.add(
    name="NGDRI EAF Commissioning",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ngdri_eaf_construction": 1, "foundry_construction_time": 1},
)
def ngdri_eaf_commissioning():
    return ngdri_eaf_construction() / foundry_construction_time()


@component.add(
    name="NGDRI EAF competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2dri_cost": 1,
        "ngdri_cost": 3,
        "bf_bof_cost": 1,
        "bf_bof_ccs_cost": 1,
    },
)
def ngdri_eaf_competitiveness():
    return float(
        np.minimum(
            h2dri_cost() / ngdri_cost(),
            float(
                np.minimum(
                    bf_bof_cost() / ngdri_cost(), bf_bof_ccs_cost() / ngdri_cost()
                )
            ),
        )
    )


@component.add(
    name="NGDRI EAF Construction",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ngdri_eaf_construction": 1},
    other_deps={
        "_integ_ngdri_eaf_construction": {
            "initial": {},
            "step": {
                "ngdri_eaf_innovators": 1,
                "ngdri_eaf_investment": 1,
                "ngdri_eaf_commissioning": 1,
            },
        }
    },
)
def ngdri_eaf_construction():
    return _integ_ngdri_eaf_construction()


_integ_ngdri_eaf_construction = Integ(
    lambda: ngdri_eaf_innovators() + ngdri_eaf_investment() - ngdri_eaf_commissioning(),
    lambda: 0,
    "_integ_ngdri_eaf_construction",
)


@component.add(
    name="NGDRI EAF Decommissioning",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ngdri_eaf": 1, "foundry_lifetime": 1},
)
def ngdri_eaf_decommissioning():
    return ngdri_eaf() / foundry_lifetime()


@component.add(
    name="NGDRI EAF EF",
    units="tCO2/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "electricity_emission_factor": 1,
        "el_to_steel_ngdri": 1,
        "ngdri_emission_factor": 1,
    },
)
def ngdri_eaf_ef():
    return electricity_emission_factor() * el_to_steel_ngdri() + ngdri_emission_factor()


@component.add(
    name="NGDRI EAF emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ngdri_eaf": 1, "ngdri_eaf_ef": 1},
)
def ngdri_eaf_emissions():
    return ngdri_eaf() * ngdri_eaf_ef() * 10**6


@component.add(
    name="NGDRI EAF inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ngdri_eaf_competitiveness": 1, "inno_switch_level": 1},
)
def ngdri_eaf_inno_switch():
    return if_then_else(
        ngdri_eaf_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="NGDRI EAF innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ngdri_eaf_inno_switch": 1, "steel_innovators": 1},
)
def ngdri_eaf_innovator_share():
    return ngdri_eaf_inno_switch() / steel_innovators()


@component.add(
    name="NGDRI EAF Innovators",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_innovator_pipeline": 1, "ngdri_eaf_innovator_share": 1},
)
def ngdri_eaf_innovators():
    return steel_innovator_pipeline() * ngdri_eaf_innovator_share()


@component.add(
    name="NGDRI EAF Investment",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_investment_pipeline": 1, "ngdri_eaf_investment_share": 1},
)
def ngdri_eaf_investment():
    return steel_investment_pipeline() * ngdri_eaf_investment_share()


@component.add(
    name="NGDRI EAF investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_equalizer": 1, "ngdri_eaf_level": 1},
)
def ngdri_eaf_investment_share():
    return steel_equalizer() * ngdri_eaf_level()


@component.add(
    name="NGDRI EAF level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "ngdri_eaf_competitiveness": 2,
        "ngdri_eaf_sector_share": 1,
        "steel_excess_activity": 1,
    },
)
def ngdri_eaf_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - ngdri_eaf_competitiveness()))))
        * float(np.maximum(0.1, ngdri_eaf_sector_share()))
        * if_then_else(steel_excess_activity() > 0, lambda: 0, lambda: 1)
        + ngdri_eaf_competitiveness() * 0.001
    )


@component.add(
    name="NGDRI EAF sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ngdri_eaf": 1, "sum_steel_activity": 1},
)
def ngdri_eaf_sector_share():
    return ngdri_eaf() / sum_steel_activity()


@component.add(
    name="secondary sector",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_production_forecast": 1, "secondary_sector_growth": 1},
)
def secondary_sector():
    return steel_production_forecast() * secondary_sector_growth()


@component.add(
    name="secondary sector growth",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def secondary_sector_growth():
    """
    At the same time, the share of secondary steel production is expected to increase to 50%, as less scrap will be exported out of Europe to now serve decarbonisation of steel production in the European market
    !year
    !share of steel production
    """
    return np.interp(time(), [2019.0, 2050.0], [0.4, 0.5])


@component.add(
    name="steel allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_steel_emissions": 1, "time": 1, "emissions_cap_lookup": 1},
)
def steel_allocated_emissions():
    return initial_steel_emissions() * emissions_cap_lookup(time())


@component.add(
    name="steel average cost",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_bof_sector_share": 1,
        "bf_bof_cost": 1,
        "bf_bof_ccs_sector_share": 1,
        "bf_bof_ccs_cost": 1,
        "h2dri_eaf_sector_share": 1,
        "h2dri_cost": 1,
        "ngdri_cost": 1,
        "ngdri_eaf_sector_share": 1,
    },
)
def steel_average_cost():
    """
    €/kgH2 equivalent necessary in the HDRI production pathway of steel.
    """
    return (
        bf_bof_sector_share() * bf_bof_cost()
        + bf_bof_ccs_sector_share() * bf_bof_ccs_cost()
        + h2dri_eaf_sector_share() * h2dri_cost()
        + ngdri_eaf_sector_share() * ngdri_cost()
    )


@component.add(
    name="steel backlog",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_steel_backlog": 1},
    other_deps={
        "_integ_steel_backlog": {
            "initial": {},
            "step": {"steel_current_demand": 1, "sum_steel_activity": 1},
        }
    },
)
def steel_backlog():
    return _integ_steel_backlog()


_integ_steel_backlog = Integ(
    lambda: steel_current_demand() - sum_steel_activity(),
    lambda: 0,
    "_integ_steel_backlog",
)


@component.add(
    name="steel continuous investment",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "steel_forecast_demand": 1,
        "sum_steel_decommissioning": 1,
        "foundry_construction_time": 1,
        "steel_backlog": 1,
        "sum_steel_activity": 1,
        "innovators": 1,
    },
)
def steel_continuous_investment():
    return float(
        np.maximum(
            (
                steel_forecast_demand()
                + sum_steel_decommissioning()
                + steel_backlog() / foundry_construction_time() / 3
                - sum_steel_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="steel current demand",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_projected_demand": 1},
)
def steel_current_demand():
    return steel_projected_demand()


@component.add(
    name="steel effective cost",
    units="B€ / Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_average_cost": 1, "steel_current_demand": 1},
)
def steel_effective_cost():
    """
    €/ton to €/Mt to B€/Mt * activity(Mt steel)
    """
    return (steel_average_cost() / 1000) * steel_current_demand()


@component.add(
    name="steel emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_bof_ccs_emissions": 1,
        "bf_bof_emissions": 1,
        "h2dri_eaf_emissions": 1,
        "ngdri_eaf_emissions": 1,
    },
)
def steel_emissions():
    return (
        bf_bof_ccs_emissions()
        + bf_bof_emissions()
        + h2dri_eaf_emissions()
        + ngdri_eaf_emissions()
    )


@component.add(
    name="steel equalizer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "steel_h2_subsidy": 1,
        "ngdri_eaf_level": 2,
        "bf_bof_ccs_level": 2,
        "h2dri_eaf_bid_share": 1,
        "bf_bof_level": 2,
        "h2dri_eaf_level": 1,
    },
)
def steel_equalizer():
    return if_then_else(
        steel_h2_subsidy() > 0.01,
        lambda: (1 - h2dri_eaf_bid_share())
        / (bf_bof_level() + bf_bof_ccs_level() + ngdri_eaf_level()),
        lambda: 1
        / (bf_bof_level() + h2dri_eaf_level() + bf_bof_ccs_level() + ngdri_eaf_level()),
    )


@component.add(
    name="steel excess activity",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_excess_emissions": 1, "bf_bof_ef": 1, "hard_regulation": 1},
)
def steel_excess_activity():
    return (
        float(np.maximum(steel_excess_emissions() / bf_bof_ef() / 10**6, 0))
        * hard_regulation()
    )


@component.add(
    name="steel excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_emissions": 1, "steel_allocated_emissions": 1},
)
def steel_excess_emissions():
    return steel_emissions() - steel_allocated_emissions()


@component.add(
    name="steel forecast demand",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_steel_forecast_demand": 1},
    other_deps={
        "_forecast_steel_forecast_demand": {
            "initial": {"steel_current_demand": 1},
            "step": {"steel_current_demand": 1, "foundry_construction_time": 2},
        }
    },
)
def steel_forecast_demand():
    return _forecast_steel_forecast_demand()


_forecast_steel_forecast_demand = Forecast(
    lambda: steel_current_demand(),
    lambda: 3 * foundry_construction_time(),
    lambda: foundry_construction_time(),
    lambda: 0,
    "_forecast_steel_forecast_demand",
)


@component.add(
    name="steel hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_eaf": 1, "h2_to_steel": 1},
)
def steel_hydrogen_demand():
    return h2dri_eaf() * 10**6 * h2_to_steel()


@component.add(
    name="steel initial sector activity",
    units="MT steel",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_steel_initial_sector_activity": 1},
    other_deps={
        "_initial_steel_initial_sector_activity": {
            "initial": {"steel_current_demand": 1},
            "step": {},
        }
    },
)
def steel_initial_sector_activity():
    return _initial_steel_initial_sector_activity()


_initial_steel_initial_sector_activity = Initial(
    lambda: steel_current_demand(), "_initial_steel_initial_sector_activity"
)


@component.add(
    name="steel innovator pipeline",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_continuous_investment": 1, "innovators": 2},
)
def steel_innovator_pipeline():
    return steel_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="steel innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_ccs_inno_switch": 1,
        "h2dri_eaf_inno_switch": 1,
        "ngdri_eaf_inno_switch": 1,
    },
)
def steel_innovators():
    return float(
        np.maximum(
            bf_ccs_inno_switch() + h2dri_eaf_inno_switch() + ngdri_eaf_inno_switch(), 1
        )
    )


@component.add(
    name="steel investment pipeline",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_continuous_investment": 1},
)
def steel_investment_pipeline():
    return steel_continuous_investment()


@component.add(
    name="Steel Production Forecast",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def steel_production_forecast():
    """
    The change in European steel production is taken from Material Economics’ modelling based on EUROFER, which yields a 0.6% yearly increase in the steel stock/capacity up to the 2040s, when it stabilises at 193 million tonnes per year, up from 170 million tonnes per year today.
    !year
    !Mt steel
    """
    return np.interp(time(), [2019, 2040, 2050], [170, 193, 193])


@component.add(
    name="steel projected demand",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_production_forecast": 1, "secondary_sector_growth": 1},
)
def steel_projected_demand():
    return steel_production_forecast() * (1 - secondary_sector_growth())


@component.add(
    name="Subsidized H2DRI EAF Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_h2dri_eaf_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_h2dri_eaf_commissioning": {
            "initial": {"foundry_construction_time": 1},
            "step": {"subsidized_h2dri_eaf_investment": 1},
        }
    },
)
def subsidized_h2dri_eaf_commissioning():
    return _delayfixed_subsidized_h2dri_eaf_commissioning()


_delayfixed_subsidized_h2dri_eaf_commissioning = DelayFixed(
    lambda: subsidized_h2dri_eaf_investment(),
    lambda: foundry_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_h2dri_eaf_commissioning",
)


@component.add(
    name="Subsidized H2DRI EAF Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_h2dri_eaf_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_h2dri_eaf_decommissioning": {
            "initial": {},
            "step": {"subsidized_h2dri_eaf_commissioning": 1},
        }
    },
)
def subsidized_h2dri_eaf_decommissioning():
    return _delayfixed_subsidized_h2dri_eaf_decommissioning()


_delayfixed_subsidized_h2dri_eaf_decommissioning = DelayFixed(
    lambda: subsidized_h2dri_eaf_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_h2dri_eaf_decommissioning",
)


@component.add(
    name="Subsidized H2DRI EAF Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "steel_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "h2dri_eaf_investment": 1,
        "h2_to_steel": 1,
    },
)
def subsidized_h2dri_eaf_investment():
    return (
        if_then_else(
            steel_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: h2dri_eaf_investment(),
            lambda: 0,
        )
        * h2_to_steel()
    )


@component.add(
    name="sum steel activity",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof": 1, "h2dri_eaf": 1, "bf_bof_ccs": 1, "ngdri_eaf": 1},
)
def sum_steel_activity():
    return bf_bof() + h2dri_eaf() + bf_bof_ccs() + ngdri_eaf()


@component.add(
    name="sum steel construction",
    units="MT steel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_bof_ccs_construction": 1,
        "bf_bof_construction": 1,
        "h2dri_eaf_construction": 1,
        "ngdri_eaf_construction": 1,
    },
)
def sum_steel_construction():
    return (
        bf_bof_ccs_construction()
        + bf_bof_construction()
        + h2dri_eaf_construction()
        + ngdri_eaf_construction()
    )


@component.add(
    name="sum steel decommissioning",
    units="MT steel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_bof_ccs_decommissioning": 1,
        "bf_bof_decommissioning": 1,
        "h2dri_eaf_decommissioning": 1,
        "ngdri_eaf_decommissioning": 1,
        "bf_bof_economic_decommissioning": 1,
    },
)
def sum_steel_decommissioning():
    return (
        bf_bof_ccs_decommissioning()
        + bf_bof_decommissioning()
        + h2dri_eaf_decommissioning()
        + ngdri_eaf_decommissioning()
        + bf_bof_economic_decommissioning()
    )


@component.add(
    name="Support H2DRI EAF",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_h2dri_eaf_investment": 1,
        "steel_h2_subsidy": 1,
        "green_h2_subsidy": 1,
    },
)
def support_h2dri_eaf():
    return (
        subsidized_h2dri_eaf_investment()
        * (green_h2_subsidy() + steel_h2_subsidy())
        * 10
    )
