"""
Module industrial_ht_heat
Translated using PySD version 3.14.3
"""

@component.add(
    name="alternative HT cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biogas_cost": 1, "nm_h2_gj_cost": 1, "blue_ng_cost": 1},
)
def alternative_ht_cost():
    return float(
        np.minimum(biogas_cost(), float(np.minimum(blue_ng_cost(), nm_h2_gj_cost())))
    )


@component.add(
    name="Biogas Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biogas_nm": 1, "gas_lockin_period": 1},
)
def biogas_decommissioning():
    return biogas_nm() / gas_lockin_period()


@component.add(
    name="Biogas NM",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biogas_nm": 1},
    other_deps={
        "_integ_biogas_nm": {
            "initial": {},
            "step": {"biogas_nm_commissioning": 1, "biogas_decommissioning": 1},
        }
    },
)
def biogas_nm():
    return _integ_biogas_nm()


_integ_biogas_nm = Integ(
    lambda: biogas_nm_commissioning() - biogas_decommissioning(),
    lambda: 0,
    "_integ_biogas_nm",
)


@component.add(
    name="Biogas NM Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biogas_nm_construction": 1, "high_temperature_construction_time": 1},
)
def biogas_nm_commissioning():
    return biogas_nm_construction() / high_temperature_construction_time()


@component.add(
    name="Biogas NM competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_ng_cost": 1,
        "biogas_cost": 3,
        "nm_h2_gj_cost": 1,
        "grey_ng_cost": 1,
    },
)
def biogas_nm_competitiveness():
    return float(
        np.minimum(
            float(
                np.minimum(
                    blue_ng_cost() / biogas_cost(), nm_h2_gj_cost() / biogas_cost()
                )
            ),
            grey_ng_cost() / biogas_cost(),
        )
    )


@component.add(
    name="Biogas NM Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_biogas_nm_construction": 1},
    other_deps={
        "_integ_biogas_nm_construction": {
            "initial": {},
            "step": {
                "biogas_nm_innovators": 1,
                "biogas_nm_investment": 1,
                "biogas_nm_commissioning": 1,
            },
        }
    },
)
def biogas_nm_construction():
    return _integ_biogas_nm_construction()


_integ_biogas_nm_construction = Integ(
    lambda: biogas_nm_innovators() + biogas_nm_investment() - biogas_nm_commissioning(),
    lambda: 0,
    "_integ_biogas_nm_construction",
)


@component.add(
    name="Biogas NM inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biogas_nm_competitiveness": 1, "inno_switch_level": 1},
)
def biogas_nm_inno_switch():
    return if_then_else(
        biogas_nm_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="Biogas NM innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biogas_nm_inno_switch": 1, "high_temperature_innovators": 1},
)
def biogas_nm_innovator_share():
    return biogas_nm_inno_switch() / high_temperature_innovators()


@component.add(
    name="Biogas NM Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_innovator_pipeline": 1,
        "biogas_nm_innovator_share": 1,
    },
)
def biogas_nm_innovators():
    return high_temperature_innovator_pipeline() * biogas_nm_innovator_share()


@component.add(
    name="Biogas NM Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_investment_pipeline": 1,
        "biogas_nm_investment_share": 1,
    },
)
def biogas_nm_investment():
    return high_temperature_investment_pipeline() * biogas_nm_investment_share()


@component.add(
    name="Biogas NM investment share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biogas_nm_level": 1, "nm_equalizer": 1},
)
def biogas_nm_investment_share():
    return biogas_nm_level() * nm_equalizer()


@component.add(
    name="Biogas NM level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "biogas_nm_competitiveness": 2,
        "biogas_nm_sector_share": 1,
    },
)
def biogas_nm_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - biogas_nm_competitiveness()))))
        * float(np.maximum(0.1, biogas_nm_sector_share()))
        + biogas_nm_competitiveness() * 0.001
    )


@component.add(
    name="Biogas NM sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biogas_nm": 1, "sum_high_temperature_activity": 1},
)
def biogas_nm_sector_share():
    return biogas_nm() / sum_high_temperature_activity()


@component.add(
    name="Blue NG NM",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_blue_ng_nm": 1},
    other_deps={
        "_integ_blue_ng_nm": {
            "initial": {},
            "step": {"blue_ng_nm_commissioning": 1, "blue_ng_nm_decommissioning": 1},
        }
    },
)
def blue_ng_nm():
    return _integ_blue_ng_nm()


_integ_blue_ng_nm = Integ(
    lambda: blue_ng_nm_commissioning() - blue_ng_nm_decommissioning(),
    lambda: 0,
    "_integ_blue_ng_nm",
)


@component.add(
    name="Blue NG NM CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biogas_cost": 1,
        "nm_h2_gj_cost": 1,
        "grey_ng_cost": 1,
        "blue_ng_cost_wo_co2": 1,
        "blue_ng_nm_ef": 1,
    },
)
def blue_ng_nm_co2_wtp():
    return (
        float(
            np.minimum(
                float(np.minimum(biogas_cost(), nm_h2_gj_cost())), grey_ng_cost()
            )
        )
        - blue_ng_cost_wo_co2()
    ) / blue_ng_nm_ef()


@component.add(
    name="Blue NG NM Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_ng_nm_construction": 1, "high_temperature_construction_time": 1},
)
def blue_ng_nm_commissioning():
    return blue_ng_nm_construction() / high_temperature_construction_time()


@component.add(
    name="Blue NG NM competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "grey_ng_cost": 1,
        "blue_ng_cost": 3,
        "nm_h2_gj_cost": 1,
        "biogas_cost": 1,
    },
)
def blue_ng_nm_competitiveness():
    return float(
        np.minimum(
            float(
                np.minimum(
                    grey_ng_cost() / blue_ng_cost(), nm_h2_gj_cost() / blue_ng_cost()
                )
            ),
            biogas_cost() / blue_ng_cost(),
        )
    )


@component.add(
    name="Blue NG NM Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_blue_ng_nm_construction": 1},
    other_deps={
        "_integ_blue_ng_nm_construction": {
            "initial": {},
            "step": {
                "blue_ng_nm_innovators": 1,
                "blue_ng_nm_investment": 1,
                "blue_ng_nm_commissioning": 1,
            },
        }
    },
)
def blue_ng_nm_construction():
    return _integ_blue_ng_nm_construction()


_integ_blue_ng_nm_construction = Integ(
    lambda: blue_ng_nm_innovators()
    + blue_ng_nm_investment()
    - blue_ng_nm_commissioning(),
    lambda: 0,
    "_integ_blue_ng_nm_construction",
)


@component.add(
    name="Blue NG NM Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_ng_nm": 1, "cc_lifetime": 1},
)
def blue_ng_nm_decommissioning():
    return blue_ng_nm() / cc_lifetime()


@component.add(
    name="Blue NG NM EF",
    units="tCO2/GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cc_capture_rate": 1, "gas_emission_factor": 1},
)
def blue_ng_nm_ef():
    return (1 - cc_capture_rate()) * gas_emission_factor() * 3600


@component.add(
    name="Blue NG NM emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_ng_nm": 1, "blue_ng_nm_ef": 1},
)
def blue_ng_nm_emissions():
    return blue_ng_nm() * blue_ng_nm_ef()


@component.add(
    name="Blue NG NM inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_ng_nm_competitiveness": 1, "inno_switch_level": 1},
)
def blue_ng_nm_inno_switch():
    return if_then_else(
        blue_ng_nm_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="Blue NG NM innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_ng_nm_inno_switch": 1, "high_temperature_innovators": 1},
)
def blue_ng_nm_innovator_share():
    return blue_ng_nm_inno_switch() / high_temperature_innovators()


@component.add(
    name="Blue NG NM Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_innovator_pipeline": 1,
        "blue_ng_nm_innovator_share": 1,
    },
)
def blue_ng_nm_innovators():
    return high_temperature_innovator_pipeline() * blue_ng_nm_innovator_share()


@component.add(
    name="Blue NG NM Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_investment_pipeline": 1,
        "blue_ng_nm_investment_share": 1,
    },
)
def blue_ng_nm_investment():
    return high_temperature_investment_pipeline() * blue_ng_nm_investment_share()


@component.add(
    name="Blue NG NM investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nm_equalizer": 1, "blue_ng_nm_level": 1},
)
def blue_ng_nm_investment_share():
    return nm_equalizer() * blue_ng_nm_level()


@component.add(
    name="Blue NG NM level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "blue_ng_nm_competitiveness": 2, "blue_nm_sector_share": 1},
)
def blue_ng_nm_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - blue_ng_nm_competitiveness()))))
        * float(np.maximum(0.1, blue_nm_sector_share()))
        + blue_ng_nm_competitiveness() * 0.001
    )


@component.add(
    name="Blue NM sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_ng_nm": 1, "sum_high_temperature_activity": 1},
)
def blue_nm_sector_share():
    return blue_ng_nm() / sum_high_temperature_activity()


@component.add(
    name="Gas lockin period", units="years", comp_type="Constant", comp_subtype="Normal"
)
def gas_lockin_period():
    """
    equivalent lifetime of technology - based on assumptions that the same furnaces can run on NG / blue NG / H2.
    """
    return 15


@component.add(
    name="Grey NG NM",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_grey_ng_nm": 1},
    other_deps={
        "_integ_grey_ng_nm": {
            "initial": {"high_temperature_initial_sector_activity": 1},
            "step": {
                "grey_ng_nm_commissioning": 1,
                "grey_ng_nm_decommissioning": 1,
                "grey_ng_nm_economic_decommissioning": 1,
            },
        }
    },
)
def grey_ng_nm():
    return _integ_grey_ng_nm()


_integ_grey_ng_nm = Integ(
    lambda: grey_ng_nm_commissioning()
    - grey_ng_nm_decommissioning()
    - grey_ng_nm_economic_decommissioning(),
    lambda: high_temperature_initial_sector_activity(),
    "_integ_grey_ng_nm",
)


@component.add(
    name="Grey NG NM CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biogas_cost": 1,
        "nm_h2_gj_cost": 1,
        "blue_ng_cost": 1,
        "gas_price": 1,
        "grey_ng_nm_ef": 1,
    },
)
def grey_ng_nm_co2_wtp():
    return (
        float(
            np.minimum(
                float(np.minimum(biogas_cost(), nm_h2_gj_cost())), blue_ng_cost()
            )
        )
        - gas_price()
    ) / grey_ng_nm_ef()


@component.add(
    name="Grey NG NM Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_ng_nm_construction": 1, "high_temperature_construction_time": 1},
)
def grey_ng_nm_commissioning():
    return grey_ng_nm_construction() / high_temperature_construction_time()


@component.add(
    name="Grey NG NM competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_ng_cost": 1,
        "grey_ng_cost": 3,
        "nm_h2_gj_cost": 1,
        "biogas_cost": 1,
    },
)
def grey_ng_nm_competitiveness():
    return float(
        np.minimum(
            float(
                np.minimum(
                    blue_ng_cost() / grey_ng_cost(), nm_h2_gj_cost() / grey_ng_cost()
                )
            ),
            biogas_cost() / grey_ng_cost(),
        )
    )


@component.add(
    name="Grey NG NM Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_grey_ng_nm_construction": 1},
    other_deps={
        "_integ_grey_ng_nm_construction": {
            "initial": {
                "high_temperature_initial_sector_activity": 1,
                "gas_lockin_period": 1,
                "high_temperature_construction_time": 1,
            },
            "step": {"grey_ng_nm_investment": 1, "grey_ng_nm_commissioning": 1},
        }
    },
)
def grey_ng_nm_construction():
    return _integ_grey_ng_nm_construction()


_integ_grey_ng_nm_construction = Integ(
    lambda: grey_ng_nm_investment() - grey_ng_nm_commissioning(),
    lambda: high_temperature_initial_sector_activity()
    / gas_lockin_period()
    * high_temperature_construction_time(),
    "_integ_grey_ng_nm_construction",
)


@component.add(
    name="Grey NG NM cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_ng_cost": 1, "alternative_ht_cost": 1},
)
def grey_ng_nm_cost_difference():
    return grey_ng_cost() / alternative_ht_cost()


@component.add(
    name="Grey NG NM Decommissioning",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_grey_ng_nm_decommissioning": 1, "grey_ng_nm": 1},
    other_deps={
        "_smooth_grey_ng_nm_decommissioning": {
            "initial": {
                "grey_ng_nm_delayed": 1,
                "grey_ng_nm_economic_decommissioning_delayed": 1,
            },
            "step": {
                "grey_ng_nm_delayed": 1,
                "grey_ng_nm_economic_decommissioning_delayed": 1,
            },
        }
    },
)
def grey_ng_nm_decommissioning():
    return float(
        np.maximum(
            0, float(np.minimum(_smooth_grey_ng_nm_decommissioning(), grey_ng_nm()))
        )
    )


_smooth_grey_ng_nm_decommissioning = Smooth(
    lambda: grey_ng_nm_delayed() - grey_ng_nm_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: grey_ng_nm_delayed() - grey_ng_nm_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_grey_ng_nm_decommissioning",
)


@component.add(
    name="Grey NG NM Delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_grey_ng_nm_delayed": 1},
    other_deps={
        "_delayfixed_grey_ng_nm_delayed": {
            "initial": {
                "high_temperature_initial_sector_activity": 1,
                "gas_lockin_period": 2,
            },
            "step": {"grey_ng_nm_commissioning": 1},
        }
    },
)
def grey_ng_nm_delayed():
    return _delayfixed_grey_ng_nm_delayed()


_delayfixed_grey_ng_nm_delayed = DelayFixed(
    lambda: grey_ng_nm_commissioning(),
    lambda: gas_lockin_period(),
    lambda: high_temperature_initial_sector_activity() / gas_lockin_period(),
    time_step,
    "_delayfixed_grey_ng_nm_delayed",
)


@component.add(
    name="Grey NG NM economic decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "grey_ng_nm_cost_difference": 2,
        "grey_ng_nm": 1,
        "gas_lockin_period": 1,
        "slope_decom": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def grey_ng_nm_economic_decommissioning():
    return (
        if_then_else(
            grey_ng_nm_cost_difference() > 1,
            lambda: (grey_ng_nm() / gas_lockin_period() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (grey_ng_nm_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="Grey NG NM Economic Decommissioning delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_grey_ng_nm_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_grey_ng_nm_economic_decommissioning_delayed": {
            "initial": {},
            "step": {"grey_ng_nm_economic_decommissioning": 1},
        }
    },
)
def grey_ng_nm_economic_decommissioning_delayed():
    return _delayn_grey_ng_nm_economic_decommissioning_delayed()


_delayn_grey_ng_nm_economic_decommissioning_delayed = DelayN(
    lambda: grey_ng_nm_economic_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_grey_ng_nm_economic_decommissioning_delayed",
)


@component.add(
    name="Grey NG NM EF",
    units="tCO2/GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"gas_emission_factor": 1},
)
def grey_ng_nm_ef():
    return gas_emission_factor() * 3600


@component.add(
    name="Grey NG NM emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_ng_nm": 1, "grey_ng_nm_ef": 1},
)
def grey_ng_nm_emissions():
    return grey_ng_nm() * grey_ng_nm_ef()


@component.add(
    name="Grey NG NM Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_investment_pipeline": 1,
        "grey_ng_nm_investment_share": 1,
    },
)
def grey_ng_nm_investment():
    return high_temperature_investment_pipeline() * grey_ng_nm_investment_share()


@component.add(
    name="Grey NG NM investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nm_equalizer": 1, "grey_ng_nm_level": 1},
)
def grey_ng_nm_investment_share():
    return nm_equalizer() * grey_ng_nm_level()


@component.add(
    name="Grey NG NM level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "grey_ng_nm_competitiveness": 2,
        "grey_nm_sector_share": 1,
        "high_temperature_excess_activity": 1,
    },
)
def grey_ng_nm_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - grey_ng_nm_competitiveness()))))
        * float(np.maximum(0.1, grey_nm_sector_share()))
        * if_then_else(high_temperature_excess_activity() > 0, lambda: 0, lambda: 1)
        + grey_ng_nm_competitiveness() * 0.001
    )


@component.add(
    name="Grey NM sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_ng_nm": 1, "sum_high_temperature_activity": 1},
)
def grey_nm_sector_share():
    return grey_ng_nm() / sum_high_temperature_activity()


@component.add(
    name="H2 NM",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_h2_nm": 1},
    other_deps={
        "_integ_h2_nm": {
            "initial": {},
            "step": {"h2_nm_commissioning": 1, "h2_nm_decommissioning": 1},
        }
    },
)
def h2_nm():
    return _integ_h2_nm()


_integ_h2_nm = Integ(
    lambda: h2_nm_commissioning() - h2_nm_decommissioning(), lambda: 0, "_integ_h2_nm"
)


@component.add(
    name="H2 NM bid share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_nm_desired_investment": 1},
)
def h2_nm_bid_share():
    return h2_nm_desired_investment()


@component.add(
    name="H2 NM Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_nm_construction": 1, "high_temperature_construction_time": 1},
)
def h2_nm_commissioning():
    return h2_nm_construction() / high_temperature_construction_time()


@component.add(
    name="H2 NM Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_h2_nm_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_h2_nm_commissioning_subsidy_level": {
            "initial": {"high_temperature_construction_time": 1},
            "step": {"nm_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def h2_nm_commissioning_subsidy_level():
    return _delayfixed_h2_nm_commissioning_subsidy_level()


_delayfixed_h2_nm_commissioning_subsidy_level = DelayFixed(
    lambda: nm_h2_subsidy() + green_h2_subsidy(),
    lambda: high_temperature_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_h2_nm_commissioning_subsidy_level",
)


@component.add(
    name="H2 NM competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_ng_cost": 1,
        "nm_h2_gj_cost": 3,
        "grey_ng_cost": 1,
        "biogas_cost": 1,
    },
)
def h2_nm_competitiveness():
    return float(
        np.minimum(
            float(
                np.minimum(
                    blue_ng_cost() / nm_h2_gj_cost(), grey_ng_cost() / nm_h2_gj_cost()
                )
            ),
            biogas_cost() / nm_h2_gj_cost(),
        )
    )


@component.add(
    name="H2 NM Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_h2_nm_construction": 1},
    other_deps={
        "_integ_h2_nm_construction": {
            "initial": {},
            "step": {
                "h2_nm_innovators": 1,
                "h2_nm_investment": 1,
                "h2_nm_commissioning": 1,
            },
        }
    },
)
def h2_nm_construction():
    return _integ_h2_nm_construction()


_integ_h2_nm_construction = Integ(
    lambda: h2_nm_innovators() + h2_nm_investment() - h2_nm_commissioning(),
    lambda: 0,
    "_integ_h2_nm_construction",
)


@component.add(
    name="H2 NM Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_nm": 1, "gas_lockin_period": 1},
)
def h2_nm_decommissioning():
    return h2_nm() / gas_lockin_period()


@component.add(
    name="H2 NM Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_h2_nm_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_h2_nm_decommissioning_subsidy_level": {
            "initial": {"gas_lockin_period": 1},
            "step": {"h2_nm_commissioning_subsidy_level": 1},
        }
    },
)
def h2_nm_decommissioning_subsidy_level():
    return _delayfixed_h2_nm_decommissioning_subsidy_level()


_delayfixed_h2_nm_decommissioning_subsidy_level = DelayFixed(
    lambda: h2_nm_commissioning_subsidy_level(),
    lambda: gas_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_h2_nm_decommissioning_subsidy_level",
)


@component.add(
    name="H2 NM desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_h2_nm_desired_investment": 1},
    other_deps={
        "_smooth_h2_nm_desired_investment": {
            "initial": {
                "h2_nm_level": 2,
                "biogas_nm_level": 1,
                "grey_ng_nm_level": 1,
                "blue_ng_nm_level": 1,
            },
            "step": {
                "h2_nm_level": 2,
                "biogas_nm_level": 1,
                "grey_ng_nm_level": 1,
                "blue_ng_nm_level": 1,
                "hba_stabilizer": 1,
            },
        }
    },
)
def h2_nm_desired_investment():
    return _smooth_h2_nm_desired_investment()


_smooth_h2_nm_desired_investment = Smooth(
    lambda: h2_nm_level()
    / (biogas_nm_level() + blue_ng_nm_level() + grey_ng_nm_level() + h2_nm_level()),
    lambda: hba_stabilizer(),
    lambda: h2_nm_level()
    / (biogas_nm_level() + blue_ng_nm_level() + grey_ng_nm_level() + h2_nm_level()),
    lambda: 1,
    "_smooth_h2_nm_desired_investment",
)


@component.add(
    name="H2 NM HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_continuous_investment": 1,
        "h2_lhv": 1,
        "h2_nm_bid_share": 1,
    },
)
def h2_nm_hba_volume():
    return (
        high_temperature_continuous_investment() * 1000 / h2_lhv() * h2_nm_bid_share()
    )


@component.add(
    name="H2 NM inno switch",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_nm_competitiveness": 1, "inno_switch_level": 1},
)
def h2_nm_inno_switch():
    return if_then_else(
        h2_nm_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="H2 NM innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_nm_inno_switch": 1, "high_temperature_innovators": 1},
)
def h2_nm_innovator_share():
    return h2_nm_inno_switch() / high_temperature_innovators()


@component.add(
    name="H2 NM Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"high_temperature_innovator_pipeline": 1, "h2_nm_innovator_share": 1},
)
def h2_nm_innovators():
    return high_temperature_innovator_pipeline() * h2_nm_innovator_share()


@component.add(
    name="H2 NM Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"high_temperature_investment_pipeline": 1, "h2_nm_investment_share": 1},
)
def h2_nm_investment():
    return high_temperature_investment_pipeline() * h2_nm_investment_share()


@component.add(
    name="H2 NM investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nm_h2_subsidy": 1,
        "h2_nm_bid_share": 1,
        "nm_equalizer": 1,
        "h2_nm_level": 1,
    },
)
def h2_nm_investment_share():
    return if_then_else(
        nm_h2_subsidy() > 0.01,
        lambda: h2_nm_bid_share(),
        lambda: nm_equalizer() * h2_nm_level(),
    )


@component.add(
    name="H2 NM level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "h2_nm_competitiveness": 2, "h2_nm_sector_share": 1},
)
def h2_nm_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - h2_nm_competitiveness()))))
        * float(np.maximum(0.1, h2_nm_sector_share()))
        + h2_nm_competitiveness() * 0.001
    )


@component.add(
    name="H2 NM sector share",
    units="fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_nm": 1, "sum_high_temperature_activity": 1},
)
def h2_nm_sector_share():
    return h2_nm() / sum_high_temperature_activity()


@component.add(
    name="H2 NM subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_h2_nm_subsidy_cost": 1},
    other_deps={
        "_integ_h2_nm_subsidy_cost": {
            "initial": {},
            "step": {
                "h2_nm_commissioning_subsidy_level": 1,
                "subsidized_h2_nm_commissioning": 1,
                "h2_nm_decommissioning_subsidy_level": 1,
                "subsidized_h2_nm_decommissioning": 1,
            },
        }
    },
)
def h2_nm_subsidy_cost():
    return _integ_h2_nm_subsidy_cost()


_integ_h2_nm_subsidy_cost = Integ(
    lambda: h2_nm_commissioning_subsidy_level() * subsidized_h2_nm_commissioning()
    - h2_nm_decommissioning_subsidy_level() * subsidized_h2_nm_decommissioning(),
    lambda: 0,
    "_integ_h2_nm_subsidy_cost",
)


@component.add(
    name="high temperature allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "initial_high_temperature_emissions": 1,
        "time": 1,
        "emissions_cap_lookup": 1,
    },
)
def high_temperature_allocated_emissions():
    return initial_high_temperature_emissions() * emissions_cap_lookup(time())


@component.add(
    name="high temperature average cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biogas_cost": 1,
        "biogas_nm_sector_share": 1,
        "blue_nm_sector_share": 1,
        "blue_ng_cost": 1,
        "grey_nm_sector_share": 1,
        "grey_ng_cost": 1,
        "nm_h2_gj_cost": 1,
        "h2_nm_sector_share": 1,
    },
)
def high_temperature_average_cost():
    return (
        biogas_cost() * biogas_nm_sector_share()
        + blue_ng_cost() * blue_nm_sector_share()
        + grey_ng_cost() * grey_nm_sector_share()
        + nm_h2_gj_cost() * h2_nm_sector_share()
    )


@component.add(
    name="high temperature backlog",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_high_temperature_backlog": 1},
    other_deps={
        "_integ_high_temperature_backlog": {
            "initial": {},
            "step": {
                "high_temperature_current_demand": 1,
                "sum_high_temperature_activity": 1,
            },
        }
    },
)
def high_temperature_backlog():
    return _integ_high_temperature_backlog()


_integ_high_temperature_backlog = Integ(
    lambda: high_temperature_current_demand() - sum_high_temperature_activity(),
    lambda: 0,
    "_integ_high_temperature_backlog",
)


@component.add(
    name="high temperature biomass demand",
    units="GWh Biomass",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biogas_nm": 1, "biogas_biomass_usage": 1},
)
def high_temperature_biomass_demand():
    return biogas_nm() * biogas_biomass_usage()


@component.add(
    name="high temperature construction time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def high_temperature_construction_time():
    return 1


@component.add(
    name="high temperature continuous investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_forecast_demand": 1,
        "high_temperature_construction_time": 2,
        "sum_high_temperature_decommissioning": 1,
        "high_temperature_backlog": 1,
        "sum_high_temperature_activity": 1,
        "innovators": 1,
    },
)
def high_temperature_continuous_investment():
    return float(
        np.maximum(
            (
                high_temperature_forecast_demand()
                + sum_high_temperature_decommissioning()
                * high_temperature_construction_time()
                + high_temperature_backlog() / high_temperature_construction_time() / 3
                - sum_high_temperature_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="high temperature current demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "high_temperature_projected_demand": 1},
)
def high_temperature_current_demand():
    """
    19.1 MT/year - assumed constant moving forward. EHB European Backbone Report: 19.1 Mt/year CEPS Report: 21 Mt/year (capacity)
    """
    return high_temperature_projected_demand(time())


@component.add(
    name="high temperature emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_ng_nm_emissions": 1, "grey_ng_nm_emissions": 1},
)
def high_temperature_emissions():
    return blue_ng_nm_emissions() + grey_ng_nm_emissions()


@component.add(
    name="high temperature excess activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_excess_emissions": 1,
        "grey_ng_nm_ef": 1,
        "hard_regulation": 1,
    },
)
def high_temperature_excess_activity():
    return (
        float(np.maximum(high_temperature_excess_emissions() / grey_ng_nm_ef(), 0))
        * hard_regulation()
    )


@component.add(
    name="high temperature excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_emissions": 1,
        "high_temperature_allocated_emissions": 1,
    },
)
def high_temperature_excess_emissions():
    return high_temperature_emissions() - high_temperature_allocated_emissions()


@component.add(
    name="high temperature forecast demand",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_high_temperature_forecast_demand": 1},
    other_deps={
        "_forecast_high_temperature_forecast_demand": {
            "initial": {"high_temperature_current_demand": 1},
            "step": {
                "high_temperature_current_demand": 1,
                "high_temperature_construction_time": 2,
            },
        }
    },
)
def high_temperature_forecast_demand():
    return _forecast_high_temperature_forecast_demand()


_forecast_high_temperature_forecast_demand = Forecast(
    lambda: high_temperature_current_demand(),
    lambda: 3 * high_temperature_construction_time(),
    lambda: high_temperature_construction_time(),
    lambda: 0,
    "_forecast_high_temperature_forecast_demand",
)


@component.add(
    name="high temperature H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_ng_cost": 1},
)
def high_temperature_h2_wtp():
    return grey_ng_cost() * 120 / 1000


@component.add(
    name="high temperature hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_nm": 1, "h2_lhv": 1},
)
def high_temperature_hydrogen_demand():
    """
    Convert from GWh to tons.
    """
    return h2_nm() * 1000 / h2_lhv()


@component.add(
    name="high temperature initial sector activity",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_high_temperature_initial_sector_activity": 1},
    other_deps={
        "_initial_high_temperature_initial_sector_activity": {
            "initial": {"high_temperature_current_demand": 1},
            "step": {},
        }
    },
)
def high_temperature_initial_sector_activity():
    return _initial_high_temperature_initial_sector_activity()


_initial_high_temperature_initial_sector_activity = Initial(
    lambda: high_temperature_current_demand(),
    "_initial_high_temperature_initial_sector_activity",
)


@component.add(
    name="high temperature innovator pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"high_temperature_continuous_investment": 1, "innovators": 2},
)
def high_temperature_innovator_pipeline():
    return high_temperature_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="high temperature innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_ng_nm_inno_switch": 1,
        "biogas_nm_inno_switch": 1,
        "h2_nm_inno_switch": 1,
    },
)
def high_temperature_innovators():
    return float(
        np.maximum(
            blue_ng_nm_inno_switch() + biogas_nm_inno_switch() + h2_nm_inno_switch(), 1
        )
    )


@component.add(
    name="high temperature investment pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"high_temperature_continuous_investment": 1},
)
def high_temperature_investment_pipeline():
    return high_temperature_continuous_investment()


@component.add(
    name="high temperature projected demand",
    units="GWh",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_high_temperature_projected_demand"},
)
def high_temperature_projected_demand(x, final_subs=None):
    """
    207 TWh/year - assumed constant moving forward.
    """
    return _hardcodedlookup_high_temperature_projected_demand(x, final_subs)


_hardcodedlookup_high_temperature_projected_demand = HardcodedLookups(
    [2022, 2050],
    [207000, 207000],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_high_temperature_projected_demand",
)


@component.add(
    name="HT effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_average_cost": 1,
        "high_temperature_current_demand": 1,
    },
)
def ht_effective_cost():
    """
    €/GJ to €/GWh to B€/GWh * activity (GWh)
    """
    return (
        (high_temperature_average_cost() * 3600)
        / 1000000000.0
        * high_temperature_current_demand()
    )


@component.add(
    name="Initial high temperature emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_high_temperature_emissions": 1},
    other_deps={
        "_initial_initial_high_temperature_emissions": {
            "initial": {"high_temperature_emissions": 1},
            "step": {},
        }
    },
)
def initial_high_temperature_emissions():
    return _initial_initial_high_temperature_emissions()


_initial_initial_high_temperature_emissions = Initial(
    lambda: high_temperature_emissions(), "_initial_initial_high_temperature_emissions"
)


@component.add(
    name="NM equalizer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nm_h2_subsidy": 1,
        "biogas_nm_level": 2,
        "h2_nm_bid_share": 1,
        "grey_ng_nm_level": 2,
        "blue_ng_nm_level": 2,
        "h2_nm_level": 1,
    },
)
def nm_equalizer():
    return if_then_else(
        nm_h2_subsidy() > 0.01,
        lambda: (1 - h2_nm_bid_share())
        / (grey_ng_nm_level() + blue_ng_nm_level() + biogas_nm_level()),
        lambda: 1
        / (grey_ng_nm_level() + h2_nm_level() + blue_ng_nm_level() + biogas_nm_level()),
    )


@component.add(
    name="Subsidized H2 NM Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_h2_nm_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_h2_nm_commissioning": {
            "initial": {"high_temperature_construction_time": 1},
            "step": {"subsidized_h2_nm_investment": 1},
        }
    },
)
def subsidized_h2_nm_commissioning():
    return _delayfixed_subsidized_h2_nm_commissioning()


_delayfixed_subsidized_h2_nm_commissioning = DelayFixed(
    lambda: subsidized_h2_nm_investment(),
    lambda: high_temperature_construction_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_h2_nm_commissioning",
)


@component.add(
    name="Subsidized H2 NM Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_h2_nm_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_h2_nm_decommissioning": {
            "initial": {"gas_lockin_period": 1},
            "step": {"subsidized_h2_nm_commissioning": 1},
        }
    },
)
def subsidized_h2_nm_decommissioning():
    return _delayfixed_subsidized_h2_nm_decommissioning()


_delayfixed_subsidized_h2_nm_decommissioning = DelayFixed(
    lambda: subsidized_h2_nm_commissioning(),
    lambda: gas_lockin_period(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_h2_nm_decommissioning",
)


@component.add(
    name="Subsidized H2 NM Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nm_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "h2_nm_investment": 1,
        "h2_lhv": 1,
    },
)
def subsidized_h2_nm_investment():
    return (
        if_then_else(
            nm_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: h2_nm_investment(),
            lambda: 0,
        )
        / h2_lhv()
        / 1000
    )


@component.add(
    name="sum high temperature activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_ng_nm": 1, "h2_nm": 1, "blue_ng_nm": 1, "biogas_nm": 1},
)
def sum_high_temperature_activity():
    return grey_ng_nm() + h2_nm() + blue_ng_nm() + biogas_nm()


@component.add(
    name="sum high temperature construction",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biogas_nm_construction": 1,
        "blue_ng_nm_construction": 1,
        "grey_ng_nm_construction": 1,
        "h2_nm_construction": 1,
    },
)
def sum_high_temperature_construction():
    return (
        biogas_nm_construction()
        + blue_ng_nm_construction()
        + grey_ng_nm_construction()
        + h2_nm_construction()
    )


@component.add(
    name="sum high temperature decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biogas_decommissioning": 1,
        "blue_ng_nm_decommissioning": 1,
        "grey_ng_nm_decommissioning": 1,
        "h2_nm_decommissioning": 1,
        "grey_ng_nm_economic_decommissioning": 1,
    },
)
def sum_high_temperature_decommissioning():
    return (
        biogas_decommissioning()
        + blue_ng_nm_decommissioning()
        + grey_ng_nm_decommissioning()
        + h2_nm_decommissioning()
        + grey_ng_nm_economic_decommissioning()
    )


@component.add(
    name="Support H2 NM",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_h2_nm_investment": 1,
        "green_h2_subsidy": 1,
        "nm_h2_subsidy": 1,
        "gas_lockin_period": 1,
    },
)
def support_h2_nm():
    return (
        subsidized_h2_nm_investment()
        * (green_h2_subsidy() + nm_h2_subsidy())
        * gas_lockin_period()
    )
