"""
Module hvo_production__to_be_compared_to_uco_price
Translated using PySD version 3.14.3
"""

@component.add(
    name="BioDiesel Cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hvo_electricity_usage": 1,
        "grid_electricity_price": 1,
        "blue_ng_cost": 1,
        "hvo_gas_usage": 1,
        "lpg_fraction_hvo": 1,
        "uco_price": 1,
        "hvo_biomass_usage": 1,
        "h2_lhv": 1,
        "hvo_h2_usage": 1,
        "green_h2_cost": 1,
        "hvo_excess_heat": 1,
        "heat_cost": 1,
        "hvo_fraction": 1,
        "hvo_af": 1,
        "hvo_capex": 1,
        "hvo_variable": 1,
        "hvo_operating_hours": 1,
        "hvo_opex": 1,
    },
)
def biodiesel_cost():
    """
    Used cooking oil is assumed 3 times more expensive than wood per unit of energy. This equals a price of UCO of around 30 €/GJ equalling market prices of slightlly above 1000 €/t UCO. 5% of the cost is removed through coproduct selling of naphtha.
    """
    return (
        (
            hvo_electricity_usage() * grid_electricity_price() / 3.6
            + (hvo_gas_usage() - lpg_fraction_hvo()) * blue_ng_cost()
            + hvo_biomass_usage() * uco_price()
            + hvo_h2_usage() * green_h2_cost() / h2_lhv() * 1000 / 3.6
            - hvo_excess_heat() * heat_cost() / 3.6
        )
        / hvo_fraction()
        + (
            (hvo_af() * hvo_capex() + hvo_opex()) / hvo_operating_hours()
            + hvo_variable()
        )
        / 3.6
    ) * 0.95


@component.add(
    name="BioNaphtha Cost as HVO byproduct",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biodiesel_cost": 1, "hvo_jet_naphtha_fraction": 1},
)
def bionaphtha_cost_as_hvo_byproduct():
    return biodiesel_cost() / 0.95 * 0.05 / hvo_jet_naphtha_fraction()


@component.add(
    name="HVO AF",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "hvo_lifetime": 1},
)
def hvo_af():
    return 1 / ((1 - (1 + discount_rate()) ** -hvo_lifetime()) / discount_rate())


@component.add(
    name="HVO biomass usage",
    units="MWh/MWh inputs",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hvo_biomass_usage():
    return 0.881


@component.add(
    name="HVO CAPEX",
    units="€/MWfuel",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def hvo_capex():
    return np.interp(time(), [2019, 2030, 2040, 2050], [760000, 640000, 600000, 580000])


@component.add(
    name="HVO Electricity Usage",
    units="MWh/MWh inputs",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hvo_electricity_usage():
    """
    MWh electricity per MWh input energy
    """
    return 0.008


@component.add(
    name="HVO Excess Heat",
    units="MWh/MWh input",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hvo_excess_heat():
    """
    MWh heat per MWh of energy input
    """
    return 0.004


@component.add(name="HVO fraction", comp_type="Constant", comp_subtype="Normal")
def hvo_fraction():
    return 0.85


@component.add(
    name="HVO Gas Usage", units="MWh/MWh", comp_type="Constant", comp_subtype="Normal"
)
def hvo_gas_usage():
    """
    MWh natural gas per MWh energy input
    """
    return 0.007


@component.add(
    name="HVO H2 Usage", units="MWh/MWh", comp_type="Constant", comp_subtype="Normal"
)
def hvo_h2_usage():
    """
    MWh H2 per MWh energy input
    """
    return 0.105


@component.add(
    name="HVO Lifetime", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def hvo_lifetime():
    return 25


@component.add(
    name="HVO operating hours",
    units="hours",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hvo_operating_hours():
    """
    2 weeks of planned downtime per year
    """
    return 8760 * 50 / 52


@component.add(
    name="HVO OPEX", units="€/MW", comp_type="Constant", comp_subtype="Normal"
)
def hvo_opex():
    """
    €/MW/year of installed output HVO capacity.
    """
    return 36000


@component.add(
    name="HVO variable", units="€/MWh", comp_type="Constant", comp_subtype="Normal"
)
def hvo_variable():
    """
    €/MWh of output
    """
    return 8.48


@component.add(
    name="LPG fraction HVO",
    units="MWh/MWh input",
    comp_type="Constant",
    comp_subtype="Normal",
)
def lpg_fraction_hvo():
    """
    LPG and fuel gas 50/50 mix.
    """
    return 0.061
