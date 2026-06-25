"""
Module shipping_costs
Translated using PySD version 3.14.3
"""

@component.add(
    name="Auxilliary battery capacity",
    units="kWh",
    comp_type="Constant",
    comp_subtype="Normal",
)
def auxilliary_battery_capacity():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 2.5 * 1000


@component.add(
    name="Battery capacity", units="kWh", comp_type="Constant", comp_subtype="Normal"
)
def battery_capacity():
    """
    Expected battery capacity of regionally sailing cargo ships. Based on Chinese example, which sails on a route with 150-600 nautical miles. https://maritime-executive.com/article/largest-electric-battery-powered-con tainerships-commissioned-in-china
    """
    return 50000


@component.add(
    name="Battery cost",
    units="€/kWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"usd_to_eur": 1},
)
def battery_cost():
    """
    https://about.bnef.com/blog/lithium-ion-battery-pack-prices-hit-record-low- of-139-kwh/
    """
    return 140 * usd_to_eur()


@component.add(
    name="Battery pack lifetime",
    units="years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def battery_pack_lifetime():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023) Weighted average of battery system components - system and cells which have an assumed lifetime of 25 and 12.5 years respectively
    """
    return 20


@component.add(
    name="BE ship cost",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "opex_electric_ship": 2,
        "ship_battery_af": 1,
        "battery_capacity": 1,
        "auxilliary_battery_capacity": 1,
        "battery_cost": 1,
        "electric_motor_cost": 1,
        "ship_motor_capacity": 1,
        "ship_engine_af": 1,
        "rest_of_ship_cost": 1,
        "charging_infrastructure_cost": 1,
        "usd_to_eur": 1,
        "yearly_electricity_bought": 1,
        "grid_electricity_price": 1,
    },
)
def be_ship_cost():
    return (
        (opex_electric_ship() + ship_battery_af())
        * (battery_capacity() + auxilliary_battery_capacity())
        * battery_cost()
        + (opex_electric_ship() + ship_engine_af())
        * (ship_motor_capacity() * electric_motor_cost() + rest_of_ship_cost())
        + yearly_electricity_bought()
        * (grid_electricity_price() + charging_infrastructure_cost() * usd_to_eur())
    ) / 10**6


@component.add(
    name="Charging efficiency",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def charging_efficiency():
    return 0.9


@component.add(
    name="Charging infrastructure cost",
    units="$/MWh",
    comp_type="Constant",
    comp_subtype="Normal",
)
def charging_infrastructure_cost():
    """
    https://doi.org/10.1038/s41560-022-01065-y
    """
    return 0.029 * 1000


@component.add(
    name="Containership OPEX",
    units="M€/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def containership_opex():
    return 3.3


@component.add(
    name="Electric motor cost",
    units="€/kW",
    comp_type="Constant",
    comp_subtype="Normal",
)
def electric_motor_cost():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 150


@component.add(
    name="Electric ship efficiency",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def electric_ship_efficiency():
    """
    Assumption from: https://static-content.springer.com/esm/art%3A10.1038%2Fs41560-022-01065-y/ MediaObjects/41560_2022_1065_MOESM1_ESM.pdf
    """
    return 0.95 * 0.95


@component.add(
    name="FC AF",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "fc_lifetime": 1},
)
def fc_af():
    return 1 / ((1 - (1 + discount_rate()) ** -fc_lifetime()) / discount_rate())


@component.add(
    name="FC CAPEX", units="€/kW", comp_type="Constant", comp_subtype="Normal"
)
def fc_capex():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023) capital cost in 2022
    """
    return 1300


@component.add(
    name="FC cost",
    units="€/kW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fc_capex": 1, "fc_ec_induced_learning_curve": 1},
)
def fc_cost():
    """
    Assumed identical to electrolyzer costs. Assumption "from": Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return fc_capex() * fc_ec_induced_learning_curve()


@component.add(
    name="FC efficiency", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def fc_efficiency():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 0.55


@component.add(
    name="FC lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def fc_lifetime():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 10


@component.add(
    name="FC ship cost",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fc_ship_cost_without_h2": 1,
        "yearly_h2_consumption": 1,
        "h2fc_ds_h2_cost": 1,
        "h2_lhv": 1,
    },
)
def fc_ship_cost():
    return (
        fc_ship_cost_without_h2()
        + (yearly_h2_consumption() * h2fc_ds_h2_cost() / h2_lhv() * 1000) / 10**6
    )


@component.add(
    name="FC ship cost without H2",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "auxilliary_battery_capacity": 1,
        "battery_cost": 1,
        "opex_electric_ship": 4,
        "ship_battery_af": 1,
        "ship_motor_capacity": 1,
        "fc_cost": 1,
        "electric_motor_cost": 1,
        "fc_af": 1,
        "ship_engine_af": 2,
        "h2_capacity": 1,
        "h2_storage_cost": 1,
        "rest_of_ship_cost": 1,
    },
)
def fc_ship_cost_without_h2():
    return (
        auxilliary_battery_capacity()
        * battery_cost()
        * (opex_electric_ship() + ship_battery_af())
        + ship_motor_capacity()
        * (
            electric_motor_cost() * (ship_engine_af() + opex_electric_ship())
            + fc_cost() * (fc_af() + opex_electric_ship())
        )
        + (rest_of_ship_cost() + h2_capacity() * h2_storage_cost())
        * (opex_electric_ship() + ship_engine_af())
    ) / 10**6


@component.add(
    name="Fuel Use Index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def fuel_use_index():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023) Efficiency improvements in ship operation (lower overall fuel use)
    """
    return np.interp(time(), [2019.0, 2030.0, 2050.0], [1.0, 1.0, 0.8])


@component.add(
    name="H2 capacity",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"output_energy_capacity": 1, "fc_efficiency": 1},
)
def h2_capacity():
    return output_energy_capacity() / fc_efficiency() / 33.33 / 1000


@component.add(
    name="H2 storage cost", units="€/t", comp_type="Constant", comp_subtype="Normal"
)
def h2_storage_cost():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 50000


@component.add(
    name="HFO capacity",
    units="t HFO",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"output_energy_capacity": 1, "ice_efficiency": 1, "hfo_lhv": 1},
)
def hfo_capacity():
    return output_energy_capacity() / ice_efficiency() / (hfo_lhv() / 3.6) / 1000


@component.add(
    name="HFO containership CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "min_green_containership_cost": 1,
        "yearly_containership_consumption": 2,
        "hfo_emission_factor": 2,
        "hfo_containership_cost": 1,
        "carbon_tax": 1,
    },
)
def hfo_containership_co2_wtp():
    """
    €/year / (tCO2/year)
    """
    return (
        min_green_containership_cost() * 10**6
        - (
            hfo_containership_cost() * 10**6
            - carbon_tax()
            * yearly_containership_consumption()
            * 3600
            * hfo_emission_factor()
        )
    ) / (hfo_emission_factor() * yearly_containership_consumption() * 3600)


@component.add(
    name="HFO containership cost",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "containership_opex": 1,
        "ship_engine_af": 1,
        "hfo_ship_capex": 1,
        "hfo_cost": 1,
        "yearly_containership_consumption": 1,
        "scrubber_cost": 1,
    },
)
def hfo_containership_cost():
    return (
        containership_opex()
        + hfo_ship_capex() * ship_engine_af()
        + (hfo_cost() * 3600 + scrubber_cost() * 1000)
        * yearly_containership_consumption()
        / 10**6
    )


@component.add(
    name="HFO containership cost marginal",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_containership_cost": 1, "ship_engine_af": 1, "hfo_ship_capex": 1},
)
def hfo_containership_cost_marginal():
    return hfo_containership_cost() - hfo_ship_capex() * ship_engine_af()


@component.add(
    name="HFO Ship CAPEX", units="M€", comp_type="Constant", comp_subtype="Normal"
)
def hfo_ship_capex():
    return 70.3


@component.add(
    name="HFO ship CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "min_green_ship_cost": 1,
        "yearly_hfo_consumption": 2,
        "hfo_emission_factor": 2,
        "hfo_ship_cost": 1,
        "carbon_tax": 1,
    },
)
def hfo_ship_co2_wtp():
    return (
        min_green_ship_cost() * 10**6
        - (
            hfo_ship_cost() * 10**6
            - carbon_tax() * yearly_hfo_consumption() * 3.6 * hfo_emission_factor()
        )
    ) / (hfo_emission_factor() * yearly_hfo_consumption() * 3.6)


@component.add(
    name="HFO ship cost",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "opex_ice_ship": 2,
        "ship_engine_af": 1,
        "ship_ice_cost": 1,
        "oil_tank_cost": 1,
        "ship_motor_capacity": 1,
        "rest_of_ship_cost": 1,
        "hfo_capacity": 1,
        "ship_battery_af": 1,
        "auxilliary_battery_capacity": 1,
        "battery_cost": 1,
        "scrubber_cost": 1,
        "yearly_hfo_consumption": 1,
        "hfo_cost": 1,
    },
)
def hfo_ship_cost():
    return (
        (opex_ice_ship() + ship_engine_af())
        * (
            rest_of_ship_cost()
            + hfo_capacity() * oil_tank_cost()
            + ship_motor_capacity() * ship_ice_cost()
        )
        + (opex_ice_ship() + ship_battery_af())
        * auxilliary_battery_capacity()
        * battery_cost()
        + yearly_hfo_consumption() * (scrubber_cost() + hfo_cost() * 3.6)
    ) / 10**6


@component.add(
    name="HFO vs MeOH CAPEX",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hfo_vs_meoh_capex():
    """
    According to the study, Seamaps, MeOH ships are on average 17% more expensive than HFO fueled ships in capital costs.
    """
    return 1.17


@component.add(
    name="ICE efficiency", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def ice_efficiency():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 0.4


@component.add(
    name="MeOH containership cost",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "containership_opex": 1,
        "meoh_ship_capex": 1,
        "ship_engine_af": 1,
        "yearly_containership_consumption": 1,
        "is_biomeoh_cost": 1,
    },
)
def meoh_containership_cost():
    return (
        containership_opex()
        + meoh_ship_capex() * ship_engine_af()
        + (is_biomeoh_cost() * 3.6) * yearly_containership_consumption() / 1000
    )


@component.add(
    name="MeOH Ship CAPEX", units="M€", comp_type="Constant", comp_subtype="Normal"
)
def meoh_ship_capex():
    return 75.8


@component.add(
    name="MeOH ship cost",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_ship_cost_without_meoh": 1,
        "yearly_hfo_consumption": 1,
        "ds_biomeoh_cost": 1,
    },
)
def meoh_ship_cost():
    return (
        meoh_ship_cost_without_meoh()
        + ds_biomeoh_cost() * yearly_hfo_consumption() * 3.6 / 10**6
    )


@component.add(
    name="MeOH ship cost without MeOH",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "opex_ice_ship": 2,
        "ship_engine_af": 1,
        "ship_ice_cost": 1,
        "oil_tank_cost": 1,
        "ship_motor_capacity": 1,
        "rest_of_ship_cost": 1,
        "hfo_capacity": 1,
        "ship_battery_af": 1,
        "auxilliary_battery_capacity": 1,
        "battery_cost": 1,
        "hfo_vs_meoh_capex": 1,
    },
)
def meoh_ship_cost_without_meoh():
    return (
        (
            (opex_ice_ship() + ship_engine_af())
            * (
                rest_of_ship_cost()
                + hfo_capacity() * oil_tank_cost()
                + ship_motor_capacity() * ship_ice_cost()
            )
            + (opex_ice_ship() + ship_battery_af())
            * auxilliary_battery_capacity()
            * battery_cost()
        )
        * hfo_vs_meoh_capex()
    ) / 10**6


@component.add(
    name="NH3 containership cost",
    units="M€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "containership_opex": 1,
        "ship_engine_af": 1,
        "nh3_ship_capex": 1,
        "shipping_nh3_cost": 1,
        "yearly_containership_consumption": 1,
    },
)
def nh3_containership_cost():
    return (
        containership_opex()
        + nh3_ship_capex() * ship_engine_af()
        + shipping_nh3_cost() * 3600 * yearly_containership_consumption() / 10**6
    )


@component.add(
    name="NH3 Ship CAPEX", units="M€", comp_type="Constant", comp_subtype="Normal"
)
def nh3_ship_capex():
    return 77.4


@component.add(
    name="Oil tank cost", units="€/t", comp_type="Constant", comp_subtype="Normal"
)
def oil_tank_cost():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 1000


@component.add(
    name="OPEX electric ship",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def opex_electric_ship():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 0.01


@component.add(
    name="OPEX ICE ship", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def opex_ice_ship():
    """
    2.5% of CAPEX Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 0.025


@component.add(
    name="Output energy capacity",
    units="kWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"battery_capacity": 1, "electric_ship_efficiency": 1},
)
def output_energy_capacity():
    return battery_capacity() * electric_ship_efficiency()


@component.add(
    name="Rest of ship cost", units="€", comp_type="Constant", comp_subtype="Normal"
)
def rest_of_ship_cost():
    """
    Own assumption
    """
    return 5 * 10**6


@component.add(
    name="Scrubber cost",
    units="€/MWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"usd_to_eur": 1},
)
def scrubber_cost():
    """
    https://doi.org/10.1038/s41560-022-01065-y Cost of removing sulphur from HFO
    """
    return 5 * usd_to_eur()


@component.add(
    name="Ship battery AF",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "battery_pack_lifetime": 1},
)
def ship_battery_af():
    return 1 / (
        (1 - (1 + discount_rate()) ** -battery_pack_lifetime()) / discount_rate()
    )


@component.add(
    name="Ship engine AF",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "ship_engine_lifetime": 1},
)
def ship_engine_af():
    return 1 / (
        (1 - (1 + discount_rate()) ** -ship_engine_lifetime()) / discount_rate()
    )


@component.add(
    name="Ship engine lifetime",
    units="years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ship_engine_lifetime():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 25


@component.add(
    name="Ship ICE cost", units="€/kW", comp_type="Constant", comp_subtype="Normal"
)
def ship_ice_cost():
    """
    Source: Potential of Hydrogen as fuel for shipping (report, 2023)
    """
    return 200


@component.add(
    name="Ship motor capacity",
    units="kW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"output_energy_capacity": 1},
)
def ship_motor_capacity():
    """
    General assumption/research. Made so the ship can sail for 10 hours at max power. Currently it is sized to sail 7.5 hours at 20 knots.
    """
    return output_energy_capacity() / 10


@component.add(
    name="Yearly Containership Consumption",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_lhv": 1, "fuel_use_index": 1},
)
def yearly_containership_consumption():
    """
    Consuming 130 tons/day (Source: https://transportgeography.org/contents/chapter4/transportation-and-energy/ fuel-consumption-containerships/). Assumes sailing 300 days of the year. Converted to GWh.
    """
    return 130 * hfo_lhv() / 3600 * 300 * fuel_use_index()


@component.add(
    name="Yearly Electricity Bought",
    units="MWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "yearly_ship_consumption": 1,
        "electric_ship_efficiency": 1,
        "charging_efficiency": 1,
    },
)
def yearly_electricity_bought():
    return (
        yearly_ship_consumption() / electric_ship_efficiency() / charging_efficiency()
    )


@component.add(
    name="Yearly H2 Consumption",
    units="MWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"yearly_ship_consumption": 1, "fc_efficiency": 1},
)
def yearly_h2_consumption():
    return yearly_ship_consumption() / fc_efficiency()


@component.add(
    name="Yearly HFO Consumption",
    units="MWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"yearly_ship_consumption": 1, "ice_efficiency": 1},
)
def yearly_hfo_consumption():
    return yearly_ship_consumption() / ice_efficiency()


@component.add(
    name="Yearly Ship Consumption",
    units="MWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hfo_lhv": 1, "ice_efficiency": 1, "fuel_use_index": 1},
)
def yearly_ship_consumption():
    """
    A year of operation sailing 150 nautical miles per day. Converted to MWh and then converted to actual energy consumed by ship post conversion losses. Assumptions explained in comment box.
    """
    return (
        (150 * 3900 / 100 * hfo_lhv())
        / 3600
        * 365
        * ice_efficiency()
        * fuel_use_index()
    )
