"""
Module steel_production
Translated using PySD version 3.14.3
"""

@component.add(
    name="BF BOF CCS cost",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_bof_cost": 1,
        "bf_coal_emission_factor": 1,
        "cc_capture_rate": 1,
        "carbon_tax": 1,
        "ccs_cost": 1,
    },
)
def bf_bof_ccs_cost():
    return bf_bof_cost() + bf_coal_emission_factor() * cc_capture_rate() * (
        ccs_cost() - carbon_tax()
    )


@component.add(
    name="BF BOF cost",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "steel_excess_emissions": 1,
        "bf_coal_emission_factor": 2,
        "carbon_tax_w_penalty": 1,
        "carbon_tax": 1,
        "coal_price": 1,
        "coal_lhv": 1,
        "coal_to_steel": 1,
        "grid_electricity_price": 1,
        "el_to_steel_bf_coal": 1,
        "foundry_operating_hours": 1,
        "bf_coal_capex": 1,
        "foundry_af": 1,
        "inflation_lookup": 1,
    },
)
def bf_bof_cost():
    """
    OPEX as well as iron ore/steel raw material costs are assumed identical across technologies.
    """
    return (
        if_then_else(
            steel_excess_emissions() > 0,
            lambda: carbon_tax_w_penalty() * bf_coal_emission_factor(),
            lambda: carbon_tax() * bf_coal_emission_factor(),
        )
        + coal_price() * (coal_to_steel() * coal_lhv())
        + grid_electricity_price() * el_to_steel_bf_coal()
        + bf_coal_capex()
        / (foundry_operating_hours() / 8760)
        * foundry_af()
        * inflation_lookup(2022)
    )


@component.add(
    name="BF BOF cost marginal",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_bof_cost": 1,
        "foundry_operating_hours": 1,
        "bf_coal_capex": 1,
        "foundry_af": 1,
        "inflation_lookup": 1,
    },
)
def bf_bof_cost_marginal():
    return bf_bof_cost() - bf_coal_capex() / (
        foundry_operating_hours() / 8760
    ) * foundry_af() * inflation_lookup(2022)


@component.add(
    name="BF Coal CAPEX", units="€/tsteel", comp_type="Constant", comp_subtype="Normal"
)
def bf_coal_capex():
    """
    https://doi.org/10.1016/j.jclepro.2023.136391 Table 2 average
    """
    return 456


@component.add(
    name="BF Coal cost without CO2",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_bof_cost": 1,
        "el_to_steel_bf_coal": 1,
        "bf_coal_emission_factor": 1,
        "electricity_emission_factor": 1,
        "carbon_tax": 1,
    },
)
def bf_coal_cost_without_co2():
    return bf_bof_cost() - carbon_tax() * (
        bf_coal_emission_factor()
        + electricity_emission_factor() * el_to_steel_bf_coal()
    )


@component.add(
    name="BF Coal emission factor",
    units="tCO2/tsteel",
    comp_type="Constant",
    comp_subtype="Normal",
)
def bf_coal_emission_factor():
    """
    https://doi.org/10.1016/j.jclepro.2023.136391
    """
    return 1.815


@component.add(
    name="Coal LHV", units="GJ/t", comp_type="Constant", comp_subtype="Unchangeable"
)
def coal_lhv():
    """
    https://www.engineeringtoolbox.com/fuels-higher-calorific-values-d_169.html
    """
    return 29


@component.add(
    name="Coal to Steel",
    units="tCoal/tsteel",
    comp_type="Constant",
    comp_subtype="Normal",
)
def coal_to_steel():
    """
    ton Coal per ton steel https://doi.org/10.1016/j.jclepro.2023.136391
    """
    return 0.8


@component.add(
    name="EL to Steel BF Coal",
    units="MWh/tsteel",
    comp_type="Constant",
    comp_subtype="Normal",
)
def el_to_steel_bf_coal():
    """
    https://www.globalccsinstitute.com/archive/hub/publications/15671/global-te chnology-roadmap-ccs-industry-steel-sectoral-report.pdf
    """
    return 0.25


@component.add(
    name="EL to Steel H2DRI",
    units="GJ/tsteel",
    comp_type="Constant",
    comp_subtype="Normal",
)
def el_to_steel_h2dri():
    """
    https://doi.org/10.1016/j.jclepro.2023.136391 Table 2 - energy consumption minus an assumed H2 consumption of 6.7 GJ H2 per ton Steel.
    """
    return 5.8


@component.add(
    name="EL to Steel NGDRI",
    units="MWh/tsteel",
    comp_type="Constant",
    comp_subtype="Normal",
)
def el_to_steel_ngdri():
    """
    https://www.europarl.europa.eu/RegData/etudes/STUD/2021/690008/EPRS_STU(202 1)690008_EN.pdf
    """
    return 0.88


@component.add(
    name="foundry AF",
    units="scalar",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "foundry_lifetime": 1},
)
def foundry_af():
    """
    The assumption that the original source uses 8% discount rate for its capex calculations is made. With this the CAPEX of steel production is sensitive to discount rate variations.
    """
    return 1 / ((1 - (1 + discount_rate()) ** -foundry_lifetime()) / discount_rate())


@component.add(
    name="foundry operating hours",
    units="hours",
    comp_type="Constant",
    comp_subtype="Normal",
)
def foundry_operating_hours():
    """
    Own assumption
    """
    return 8000


@component.add(
    name="Gas to Steel",
    units="MWhNG/tsteel",
    comp_type="Constant",
    comp_subtype="Normal",
)
def gas_to_steel():
    """
    MWh gas per ton steel https://www.europarl.europa.eu/RegData/etudes/STUD/2021/690008/EPRS_STU(202 1)690008_EN.pdf
    """
    return 3.73


@component.add(
    name="H2DRI CAPEX",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2dri_learning_curve": 1,
        "h2dri_capex_base": 1,
        "foundry_af": 1,
        "inflation_lookup": 1,
    },
)
def h2dri_capex():
    return (
        h2dri_learning_curve()
        * h2dri_capex_base()
        * foundry_af()
        * inflation_lookup(2022)
    )


@component.add(
    name="H2DRI CAPEX BASE",
    units="€/tsteel",
    comp_type="Constant",
    comp_subtype="Normal",
)
def h2dri_capex_base():
    """
    https://doi.org/10.1016/j.jclepro.2023.136391 Table 2 average
    """
    return 750


@component.add(
    name="H2DRI CAPEX subsidy",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2dri_capex_subsidy_length": 1,
        "time": 1,
        "h2dri_capex_subsidy_size": 1,
        "h2dri_capex": 1,
    },
)
def h2dri_capex_subsidy():
    return (
        pulse(__data["time"], 2025, width=h2dri_capex_subsidy_length())
        * h2dri_capex_subsidy_size()
        * h2dri_capex()
    )


@component.add(
    name="H2DRI CAPEX subsidy length",
    units="years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def h2dri_capex_subsidy_length():
    return 10


@component.add(
    name="H2DRI CAPEX subsidy size",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def h2dri_capex_subsidy_size():
    return 0


@component.add(
    name="H2DRI cost",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_h2_cost": 1, "h2_to_steel": 1, "h2dri_cost_without_h2": 1},
)
def h2dri_cost():
    return (steel_h2_cost() * 1000) * h2_to_steel() + h2dri_cost_without_h2()


@component.add(
    name="H2DRI cost without H2",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "grid_electricity_price": 1,
        "el_to_steel_h2dri": 1,
        "h2dri_capex_subsidy": 1,
        "h2dri_capex": 1,
        "foundry_operating_hours": 1,
    },
)
def h2dri_cost_without_h2():
    return grid_electricity_price() * el_to_steel_h2dri() / 3.6 + (
        h2dri_capex() - h2dri_capex_subsidy()
    ) / (foundry_operating_hours() / 8760)


@component.add(
    name="H2DRI learning curve",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_plant_size": 2, "h2dri_eaf": 1, "h2dri_learning_rate": 1},
)
def h2dri_learning_curve():
    """
    Needs to have built the equivalent to 2 MT/steel/year of capacity before further learning is obtained.
    """
    return (
        float(np.maximum(h2dri_plant_size(), h2dri_eaf())) / h2dri_plant_size()
    ) ** (float(np.log(1 - h2dri_learning_rate())) / float(np.log(2)))


@component.add(
    name="H2DRI learning rate",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def h2dri_learning_rate():
    return 0.01


@component.add(
    name="H2DRI plant size", units="MT", comp_type="Constant", comp_subtype="Normal"
)
def h2dri_plant_size():
    """
    Common capacity found in https://globalenergymonitor.org/projects/global-steel-plant-tracker/tracker -map/
    """
    return 2


@component.add(
    name="new H2DRI capacity",
    units="Mtsteel/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2dri_eaf_commissioning": 1},
)
def new_h2dri_capacity():
    return h2dri_eaf_commissioning()


@component.add(
    name="NGDRI CAPEX", units="€/tsteel", comp_type="Constant", comp_subtype="Normal"
)
def ngdri_capex():
    """
    https://doi.org/10.1016/j.jclepro.2023.136391 Table 2 average
    """
    return 428


@component.add(
    name="NGDRI cost",
    units="€/tsteel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "carbon_tax": 1,
        "ngdri_emission_factor": 1,
        "gas_to_steel": 1,
        "gas_price": 1,
        "grid_electricity_price": 1,
        "el_to_steel_ngdri": 1,
        "ngdri_capex": 1,
        "foundry_operating_hours": 1,
        "foundry_af": 1,
        "inflation_lookup": 1,
    },
)
def ngdri_cost():
    """
    OPEX as well as iron ore/steel raw material costs are assumed identical across technologies.
    """
    return (
        carbon_tax() * ngdri_emission_factor()
        + gas_price() * (gas_to_steel() * 3.6)
        + grid_electricity_price() * el_to_steel_ngdri()
        + ngdri_capex()
        / (foundry_operating_hours() / 8760)
        * foundry_af()
        * inflation_lookup(2022)
    )


@component.add(
    name="NGDRI emission factor",
    units="tCO2/tsteel",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ngdri_emission_factor():
    """
    https://doi.org/10.1016/j.jclepro.2023.136391
    """
    return 1.105


@component.add(
    name="steel CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2dri_cost": 1,
        "bf_coal_cost_without_co2": 1,
        "bf_coal_emission_factor": 1,
        "electricity_emission_factor": 1,
        "el_to_steel_bf_coal": 1,
    },
)
def steel_co2_wtp():
    """
    €/tSteel / (tCO2/tSteel)
    """
    return (h2dri_cost() - bf_coal_cost_without_co2()) / (
        bf_coal_emission_factor()
        + electricity_emission_factor() * el_to_steel_bf_coal()
    )


@component.add(
    name="steel H2 marginal WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_bof_cost": 1,
        "el_to_steel_h2dri": 1,
        "renewable_electricity_price": 1,
        "h2_to_steel": 1,
    },
)
def steel_h2_marginal_wtp():
    return (
        (bf_bof_cost() - renewable_electricity_price() * (el_to_steel_h2dri() / 3.6))
        / 1000
        / h2_to_steel()
    )


@component.add(
    name="steel H2 WTP",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_bof_cost": 1, "h2dri_cost_without_h2": 1, "h2_to_steel": 1},
)
def steel_h2_wtp():
    return (bf_bof_cost() - h2dri_cost_without_h2()) / 1000 / h2_to_steel()


@component.add(
    name="total H2DRI CAPEX subsidy",
    units="M€",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_total_h2dri_capex_subsidy": 1},
    other_deps={
        "_integ_total_h2dri_capex_subsidy": {
            "initial": {},
            "step": {
                "h2dri_capex_subsidy": 1,
                "foundry_lifetime": 1,
                "new_h2dri_capacity": 1,
            },
        }
    },
)
def total_h2dri_capex_subsidy():
    return _integ_total_h2dri_capex_subsidy()


_integ_total_h2dri_capex_subsidy = Integ(
    lambda: h2dri_capex_subsidy() * foundry_lifetime() * new_h2dri_capacity(),
    lambda: 0,
    "_integ_total_h2dri_capex_subsidy",
)
