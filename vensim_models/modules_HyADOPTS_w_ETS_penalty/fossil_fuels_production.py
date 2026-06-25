"""
Module fossil_fuels_production
Translated using PySD version 3.14.3
"""

@component.add(
    name="Blue NG cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "blue_ng_cost_wo_co2": 1,
        "cc_capture_rate": 1,
        "gas_emission_factor": 1,
        "carbon_tax": 1,
    },
)
def blue_ng_cost():
    return (
        blue_ng_cost_wo_co2()
        + gas_emission_factor() * (1 - cc_capture_rate()) * carbon_tax()
    )


@component.add(
    name="Blue NG cost wo CO2",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"gas_price": 1, "gas_emission_factor": 1, "ccs_cost": 1},
)
def blue_ng_cost_wo_co2():
    return gas_price() + gas_emission_factor() * ccs_cost()


@component.add(
    name="Diesel cost wo CO2",
    units="€/l",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"oil_price": 1, "oil_price_init": 1},
)
def diesel_cost_wo_co2():
    """
    Scale the diesel price with the oil price by assuming that the 2019 oil price corresponds to a diesel price of 1.2€/l. Assumed diesel price is from: https://doi.org/10.1016/j.apenergy.2021.118079
    """
    return oil_price() / oil_price_init() * 1.2


@component.add(
    name="Diesel emission factor",
    units="tCO2/kWh",
    comp_type="Constant",
    comp_subtype="Normal",
)
def diesel_emission_factor():
    """
    Source: DOI 10.1007/s40095-015-0160-6 EF: 74.14 kgCO2/GJ / (1000 kg/t) / (1000/3.6 kWh/GJ) = 0.0003 t/CO2/kWh
    """
    return 74.14 / 1000 / 1.0551 / (1000 / 3.6)


@component.add(
    name="Diesel LHV", units="kWh/l", comp_type="Constant", comp_subtype="Unchangeable"
)
def diesel_lhv():
    """
    https://www.engineeringtoolbox.com/fuels-higher-calorific-values-d_169.html
    """
    return 10


@component.add(
    name="Diesel price",
    units="€/l",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "diesel_cost_wo_co2": 1,
        "diesel_emission_factor": 1,
        "carbon_tax": 1,
        "diesel_lhv": 1,
    },
)
def diesel_price():
    """
    Scale the diesel price with the oil price by assuming that the 2019 oil price corresponds to a diesel price of 1.2€/l. Assumed diesel price is from: https://doi.org/10.1016/j.apenergy.2021.118079
    """
    return diesel_cost_wo_co2() + carbon_tax() * (
        diesel_emission_factor() * diesel_lhv()
    )


@component.add(
    name="diesel price scaler",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_diesel_price_scaler": 1},
    other_deps={
        "_initial_diesel_price_scaler": {
            "initial": {"diesel_price_per_gj": 1, "oil_price": 1},
            "step": {},
        }
    },
)
def diesel_price_scaler():
    return _initial_diesel_price_scaler()


_initial_diesel_price_scaler = Initial(
    lambda: diesel_price_per_gj() / oil_price(), "_initial_diesel_price_scaler"
)


@component.add(
    name="GAS EMISSION FACTOR",
    units="tCO2/GJ",
    comp_type="Constant",
    comp_subtype="Normal",
)
def gas_emission_factor():
    """
    https://www.eia.gov/environment/emissions/co2_vol_mass.php
    """
    return 52.91 / 1000 / 1.0551


@component.add(
    name="Grey NG cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_excess_activity": 1,
        "carbon_tax_w_penalty": 1,
        "gas_emission_factor": 2,
        "carbon_tax": 1,
        "gas_price": 1,
    },
)
def grey_ng_cost():
    return (
        if_then_else(
            high_temperature_excess_activity() > 0,
            lambda: carbon_tax_w_penalty() * gas_emission_factor(),
            lambda: carbon_tax() * gas_emission_factor(),
        )
        + gas_price()
    )


@component.add(
    name="HFO cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "is_excess_activity": 1,
        "ds_excess_activity": 1,
        "carbon_tax_w_penalty": 1,
        "hfo_emission_factor": 2,
        "carbon_tax": 1,
        "oil_price": 1,
    },
)
def hfo_cost():
    """
    €/GJ Oil
    """
    return (
        if_then_else(
            float(np.maximum(is_excess_activity(), ds_excess_activity())) > 0,
            lambda: carbon_tax_w_penalty() * hfo_emission_factor(),
            lambda: carbon_tax() * hfo_emission_factor(),
        )
        + oil_price()
    )


@component.add(
    name="HFO emission factor",
    units="tCO2/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_lhv": 1},
)
def hfo_emission_factor():
    """
    Emission factor: 0.075 t per GJ
    """
    return 3.15 / hfo_lhv()


@component.add(
    name="HFO LHV", units="MJ/kg", comp_type="Constant", comp_subtype="Unchangeable"
)
def hfo_lhv():
    return 39


@component.add(
    name="Jetfuel cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ia_excess_emissions": 1,
        "da_excess_emissions": 1,
        "hard_regulation": 1,
        "carbon_tax_w_penalty": 1,
        "jetfuel_emission_factor": 2,
        "carbon_tax": 1,
        "jetfuel_cost_wo_co2": 1,
    },
)
def jetfuel_cost():
    return (
        if_then_else(
            float(np.maximum(ia_excess_emissions(), da_excess_emissions()))
            * hard_regulation()
            > 0,
            lambda: carbon_tax_w_penalty() * jetfuel_emission_factor(),
            lambda: carbon_tax() * jetfuel_emission_factor(),
        )
        + jetfuel_cost_wo_co2()
    )


@component.add(
    name="Jetfuel cost wo CO2",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jetfuel_crack_spread": 1, "oil_price": 1},
)
def jetfuel_cost_wo_co2():
    return (1 + jetfuel_crack_spread()) * oil_price()


@component.add(
    name="Jetfuel crack spread",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def jetfuel_crack_spread():
    """
    30 % of crude oil price
    """
    return 0.3


@component.add(
    name="Jetfuel emission factor",
    units="tCO2/GJ",
    comp_type="Constant",
    comp_subtype="Normal",
)
def jetfuel_emission_factor():
    """
    https://www.eia.gov/environment/emissions/co2_vol_mass.php
    """
    return 73.19 / 1000 / 1.0551


@component.add(
    name="Methane LHV", units="GJ/t", comp_type="Constant", comp_subtype="Normal"
)
def methane_lhv():
    """
    https://www.engineeringtoolbox.com/fuels-higher-calorific-values-d_169.html
    """
    return 55.5


@component.add(
    name="Naphtha cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "naphtha_excess_activity": 1,
        "carbon_tax_w_penalty": 1,
        "naphtha_emission_factor": 2,
        "carbon_tax": 1,
        "naphtha_cost_wo_co2": 1,
    },
)
def naphtha_cost():
    """
    Per energy content it is assumed that the cost of naphtha is 10% higher than the crude oil cost. Based on average market price difference observed the last 12 months (anno May 2024). Source: https://tradingeconomics.com/commodity/naphtha
    """
    return (
        if_then_else(
            naphtha_excess_activity() > 0,
            lambda: carbon_tax_w_penalty() * naphtha_emission_factor(),
            lambda: carbon_tax() * naphtha_emission_factor(),
        )
        + naphtha_cost_wo_co2()
    )


@component.add(
    name="Naphtha cost wo CO2",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_crack_spread": 1, "oil_price": 1},
)
def naphtha_cost_wo_co2():
    return (1 + naphtha_crack_spread()) * oil_price()


@component.add(
    name="Naphtha crack spread",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def naphtha_crack_spread():
    """
    10 % of crude oil price
    """
    return 0.1


@component.add(
    name="Naphtha emission factor",
    units="tCO2/GJ",
    comp_type="Constant",
    comp_subtype="Normal",
)
def naphtha_emission_factor():
    """
    https://www.eia.gov/environment/emissions/co2_vol_mass.php Source of carbon emission factor is in kgCO2/MMBtu. Converted to usable unit.
    """
    return 68.02 / 1000 / 1.0551
