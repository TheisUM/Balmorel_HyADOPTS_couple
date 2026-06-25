"""
Module hydrogen_production
Translated using PySD version 3.14.3
"""

@component.add(
    name="AEC AF",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "aec_lifetime": 1},
)
def aec_af():
    return 1 / ((1 - (1 + discount_rate()) ** -aec_lifetime()) / discount_rate())


@component.add(
    name="AEC CAPEX",
    units="€/kWe",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "electrolysis_experience": 3,
        "one_gw_aec_capex": 2,
        "learning_rate": 1,
        "initial_gw_aec_capex": 2,
    },
)
def aec_capex():
    """
    If it is desired to use the Irena learning curve from Carmen's work: - Initial GW AEC CAPEX should be set to 650 €/kW. - One GW AEC CAPEX should be set to 600 €/kW. IF statement used to ensure reasonable costs at very low levels of installed electrolysis.
    """
    return if_then_else(
        electrolysis_experience() > 1,
        lambda: one_gw_aec_capex()
        * electrolysis_experience()
        ** (float(np.log(1 - learning_rate())) / float(np.log(2))),
        lambda: initial_gw_aec_capex()
        - (initial_gw_aec_capex() - one_gw_aec_capex()) * electrolysis_experience(),
    )


@component.add(
    name="AEC CAPEX BASE", units="€/kW", comp_type="Constant", comp_subtype="Normal"
)
def aec_capex_base():
    return 1400


@component.add(
    name="AEC efficiency",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"aec_efficiency_improvement": 1, "aec_max_efficiency": 1},
)
def aec_efficiency():
    return aec_efficiency_improvement() * aec_max_efficiency()


@component.add(
    name="AEC efficiency improvement",
    units="scalar",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def aec_efficiency_improvement():
    return np.interp(time(), [2022.0, 2050.0], [0.8, 1.0])


@component.add(
    name="AEC lifetime",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"aec_lifetime_hours": 1, "electrolyser_operating_hours": 1},
)
def aec_lifetime():
    """
    electrolyzer lifetime in years
    """
    return aec_lifetime_hours() / electrolyser_operating_hours()


@component.add(
    name="AEC lifetime hours", units="h", comp_type="Constant", comp_subtype="Normal"
)
def aec_lifetime_hours():
    """
    electrolyzer lifetime in hours
    """
    return 70000


@component.add(
    name="AEC max efficiency",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def aec_max_efficiency():
    return 0.65


@component.add(
    name="AEC OPEX", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def aec_opex():
    """
    Percentage of CAPEX - ren. fuels tech. catalogue
    """
    return 0.04


@component.add(
    name="Blue H2 CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "green_h2_cost": 1,
        "grey_h2_cost": 1,
        "grey_h2_cost_wo_co2": 1,
        "ccs_cost": 1,
        "smr_emission_factor": 2,
        "cc_capture_rate": 2,
    },
)
def blue_h2_co2_wtp():
    """
    Blue_cost = Grey H2 cost wo CO2 + SMR emission factor/1000 * (CCS cost + (1-CC Capture Rate) * CARBON TAX) + SMR emission factor/1000 * (CCS OPEX - CC Capture Rate * CARBON TAX) + SMR emission factor/1000 * CCS CAPEX
    """
    return (
        float(np.minimum(green_h2_cost(), grey_h2_cost()))
        - grey_h2_cost_wo_co2()
        - smr_emission_factor() / 1000 * ccs_cost() * cc_capture_rate()
    ) / (smr_emission_factor() / 1000 * (1 - cc_capture_rate()))


@component.add(
    name="Blue H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_h2_cost_wo_co2": 1, "blue_h2_ef": 1, "carbon_tax": 1},
)
def blue_h2_cost():
    return blue_h2_cost_wo_co2() + blue_h2_ef() * carbon_tax() / 1000


@component.add(
    name="Blue H2 cost wo CO2",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"blue_h2_fixed_costs": 1, "blue_h2_variable_costs": 1},
)
def blue_h2_cost_wo_co2():
    return blue_h2_fixed_costs() + blue_h2_variable_costs()


@component.add(
    name="Blue H2 EF",
    units="tCO2/tH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "smr_el_usage": 1,
        "electricity_emission_factor": 1,
        "smr_emission_factor": 1,
        "cc_capture_rate": 1,
    },
)
def blue_h2_ef():
    return smr_el_usage() * electricity_emission_factor() + smr_emission_factor() * (
        1 - cc_capture_rate()
    )


@component.add(
    name="Blue H2 fixed costs",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"smr_h2_fixed_costs": 1, "smr_emission_factor": 1, "ccs_capex": 1},
)
def blue_h2_fixed_costs():
    return smr_h2_fixed_costs() + smr_emission_factor() / 1000 * ccs_capex()


@component.add(
    name="Blue H2 variable costs",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"smr_h2_variable_costs": 1, "smr_emission_factor": 1, "ccs_opex": 1},
)
def blue_h2_variable_costs():
    return smr_h2_variable_costs() + smr_emission_factor() / 1000 * ccs_opex()


@component.add(
    name="construction",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_construction": 1},
    other_deps={
        "_integ_construction": {"initial": {}, "step": {"electrolyzer_investments": 1}}
    },
)
def construction():
    return _integ_construction()


_integ_construction = Integ(
    lambda: electrolyzer_investments(), lambda: 0, "_integ_construction"
)


@component.add(
    name="electrolyser capacity",
    units="GW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_electrolyser_capacity": 1},
    other_deps={
        "_integ_electrolyser_capacity": {
            "initial": {"pilot_plant_capacity": 1},
            "step": {"electrolyzer_investments": 1, "electrolyzer_decommissioning": 1},
        }
    },
)
def electrolyser_capacity():
    """
    Hydrogen demand (tH2) * 1000 (kgH2/tH2) * 33.33 (kWhH2/kgH2) / efficiency / working hours (h) *10^-6 (GW/kW)= GW of electroliser capacity
    """
    return _integ_electrolyser_capacity()


_integ_electrolyser_capacity = Integ(
    lambda: electrolyzer_investments() - electrolyzer_decommissioning(),
    lambda: pilot_plant_capacity(),
    "_integ_electrolyser_capacity",
)


@component.add(
    name="electrolyser operating hours",
    units="h/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def electrolyser_operating_hours():
    return 4000


@component.add(
    name="electrolysis experience",
    units="GW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_electrolysis_experience": 1},
    other_deps={
        "_integ_electrolysis_experience": {
            "initial": {"pilot_plant_capacity": 1},
            "step": {"electrolyzer_investments": 1},
        }
    },
)
def electrolysis_experience():
    return _integ_electrolysis_experience()


_integ_electrolysis_experience = Integ(
    lambda: electrolyzer_investments(),
    lambda: pilot_plant_capacity(),
    "_integ_electrolysis_experience",
)


@component.add(
    name="electrolyzer decommissioning",
    units="GW/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"electrolyzer_investments_delayed": 2, "electrolyser_capacity": 2},
)
def electrolyzer_decommissioning():
    return if_then_else(
        electrolyzer_investments_delayed() > electrolyser_capacity(),
        lambda: electrolyser_capacity(),
        lambda: electrolyzer_investments_delayed(),
    )


@component.add(
    name="electrolyzer investments",
    units="GW/yr",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"missing_production_capacity": 1},
)
def electrolyzer_investments():
    return float(np.maximum(0, missing_production_capacity()))


@component.add(
    name="electrolyzer investments delayed",
    units="GW/yr",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_electrolyzer_investments_delayed": 1},
    other_deps={
        "_delayfixed_electrolyzer_investments_delayed": {
            "initial": {"aec_lifetime": 1},
            "step": {"electrolyzer_investments": 1},
        }
    },
)
def electrolyzer_investments_delayed():
    return _delayfixed_electrolyzer_investments_delayed()


_delayfixed_electrolyzer_investments_delayed = DelayFixed(
    lambda: electrolyzer_investments(),
    lambda: aec_lifetime(),
    lambda: 0,
    time_step,
    "_delayfixed_electrolyzer_investments_delayed",
)


@component.add(
    name="FC EC induced learning curve",
    units="scalar",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"electrolysis_experience": 1, "learning_rate": 1},
)
def fc_ec_induced_learning_curve():
    return float(
        np.minimum(
            1,
            electrolysis_experience()
            ** (float(np.log(1 - learning_rate() / 2)) / float(np.log(2))),
        )
    )


@component.add(
    name="Green H2 CAPEX",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "aec_capex": 1,
        "aec_af": 1,
        "electrolyser_operating_hours": 1,
        "aec_efficiency": 1,
        "h2_lhv": 1,
    },
)
def green_h2_capex():
    return (
        aec_capex()
        * aec_af()
        / electrolyser_operating_hours()
        / aec_efficiency()
        * h2_lhv()
    )


@component.add(
    name="Green H2 derisked CAPEX",
    units="€/kW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "aec_capex": 1,
        "interest_rate": 2,
        "aec_lifetime": 1,
        "electrolyser_operating_hours": 1,
        "aec_efficiency": 1,
        "h2_lhv": 1,
    },
)
def green_h2_derisked_capex():
    return (
        aec_capex()
        * 1
        / ((1 - (1 + interest_rate()) ** -aec_lifetime()) / interest_rate())
        / electrolyser_operating_hours()
        / aec_efficiency()
        * h2_lhv()
    )


@component.add(
    name="Green H2 H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_h2_cost": 1},
)
def green_h2_h2_wtp():
    return grey_h2_cost()


@component.add(
    name="Green H2 OPEX",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "aec_capex": 1,
        "aec_opex": 1,
        "electrolyser_operating_hours": 1,
        "renewable_electricity_price": 1,
        "aec_efficiency": 1,
        "h2_lhv": 1,
    },
)
def green_h2_opex():
    return (
        (
            aec_capex() * aec_opex() / electrolyser_operating_hours()
            + renewable_electricity_price() / 1000
        )
        / aec_efficiency()
        * h2_lhv()
    )


@component.add(
    name="Grey H2 CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_h2_cost": 1,
        "green_h2_cost": 1,
        "grey_h2_cost_wo_co2": 1,
        "smr_emission_factor": 1,
    },
)
def grey_h2_co2_wtp():
    return (
        (float(np.minimum(blue_h2_cost(), green_h2_cost())) - grey_h2_cost_wo_co2())
        / smr_emission_factor()
        * 1000
    )


@component.add(
    name="Grey H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "refinery_excess_activity": 1,
        "grey_h2_ef": 2,
        "carbon_tax_w_penalty": 1,
        "carbon_tax": 1,
        "grey_h2_cost_wo_co2": 1,
    },
)
def grey_h2_cost():
    """
    €/kg grey H2
    """
    return (
        if_then_else(
            refinery_excess_activity() > 0,
            lambda: carbon_tax_w_penalty() * grey_h2_ef() / 1000,
            lambda: carbon_tax() * grey_h2_ef() / 1000,
        )
        + grey_h2_cost_wo_co2()
    )


@component.add(
    name="Grey H2 cost marginal",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "grey_h2_cost": 1,
        "smr_capacity_factor": 1,
        "smr_af": 1,
        "smr_capex": 1,
    },
)
def grey_h2_cost_marginal():
    return grey_h2_cost() - (smr_capex() * smr_af() / smr_capacity_factor()) / 1000


@component.add(
    name="Grey H2 cost wo CO2",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"smr_h2_fixed_costs": 1, "smr_h2_variable_costs": 1},
)
def grey_h2_cost_wo_co2():
    """
    Cost_grey = SMR CAPEX * (SMR AF + SMR OPEX) / SMR operating hours * H2 LHV + (GAS PRICE/1000 * 3.6) / SMR efficiency * H2 LHV + (CARBON TAX/1000) * SMR emission factor CT** = (Alt_cost - (SMR CAPEX * (SMR AF + SMR OPEX) / SMR operating hours * H2 LHV + (GAS PRICE/1000 * 3.6) / SMR efficiency * H2 LHV)) / SMR emission factor * 1000
    """
    return smr_h2_fixed_costs() + smr_h2_variable_costs()


@component.add(
    name="Grey H2 EF",
    units="tCO2/tH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "smr_el_usage": 1,
        "electricity_emission_factor": 1,
        "smr_emission_factor": 1,
    },
)
def grey_h2_ef():
    return smr_el_usage() * electricity_emission_factor() + smr_emission_factor()


@component.add(
    name="H2 LHV", units="kWh/kg", comp_type="Constant", comp_subtype="Unchangeable"
)
def h2_lhv():
    """
    33.33 kWh/kg as LHV H2
    """
    return 33.33


@component.add(
    name="Initial GW AEC CAPEX",
    units="€/kW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"aec_capex_base": 1},
)
def initial_gw_aec_capex():
    return 1.3 * aec_capex_base()


@component.add(
    name="learning rate", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def learning_rate():
    return 0.15


@component.add(
    name="missing production capacity",
    units="GW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"required_electrolysis_capacity": 1, "electrolyser_capacity": 1},
)
def missing_production_capacity():
    return required_electrolysis_capacity() - electrolyser_capacity()


@component.add(
    name="One GW AEC CAPEX",
    units="€/kW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"aec_capex_base": 1},
)
def one_gw_aec_capex():
    return aec_capex_base()


@component.add(
    name="pilot plant capacity", units="GW", comp_type="Constant", comp_subtype="Normal"
)
def pilot_plant_capacity():
    """
    Can be used to include already installed capacity, which is not present in any of the sectors (pilot plants and demonstrations)
    """
    return 0.08


@component.add(
    name="required electrolysis capacity",
    units="GW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "total_green_hydrogen_demand": 1,
        "aec_efficiency": 1,
        "electrolyser_operating_hours": 1,
    },
)
def required_electrolysis_capacity():
    return (
        total_green_hydrogen_demand()
        * 33.33
        / 1000
        / aec_efficiency()
        / electrolyser_operating_hours()
    )


@component.add(
    name="SMR AF",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "smr_lifetime": 1},
)
def smr_af():
    return 1 / ((1 - (1 + discount_rate()) ** -smr_lifetime()) / discount_rate())


@component.add(
    name="SMR Capacity Factor",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def smr_capacity_factor():
    return 0.95


@component.add(
    name="SMR CAPEX", units="€/(tH2/yr)", comp_type="Constant", comp_subtype="Normal"
)
def smr_capex():
    """
    €/(tH2/yr)
    """
    return 5306


@component.add(
    name="SMR El usage", units="MWh/tH2", comp_type="Constant", comp_subtype="Normal"
)
def smr_el_usage():
    return 0.549


@component.add(
    name="SMR emission factor",
    units="tCO2/tH2",
    comp_type="Constant",
    comp_subtype="Normal",
)
def smr_emission_factor():
    return 8.545


@component.add(
    name="SMR fixed OPEX", units="€/tH2", comp_type="Constant", comp_subtype="Normal"
)
def smr_fixed_opex():
    return 311


@component.add(
    name="SMR H2 fixed costs",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "smr_capex": 1,
        "smr_af": 1,
        "smr_capacity_factor": 1,
        "smr_fixed_opex": 1,
    },
)
def smr_h2_fixed_costs():
    return (smr_capex() * smr_af() / smr_capacity_factor() + smr_fixed_opex()) / 1000


@component.add(
    name="SMR H2 variable costs",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "gas_price": 1,
        "smr_ng_usage": 1,
        "grid_electricity_price": 1,
        "smr_el_usage": 1,
    },
)
def smr_h2_variable_costs():
    return (
        gas_price() * smr_ng_usage() + grid_electricity_price() * smr_el_usage()
    ) / 1000


@component.add(
    name="SMR lifetime", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def smr_lifetime():
    return 20


@component.add(
    name="SMR NG usage", units="GJ/tH2", comp_type="Constant", comp_subtype="Normal"
)
def smr_ng_usage():
    """
    GJ ng/t H2
    """
    return 170.9


@component.add(
    name="Unsubsidized green H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_capex": 1, "green_h2_opex": 1},
)
def unsubsidized_green_h2_cost():
    return green_h2_capex() + green_h2_opex()
