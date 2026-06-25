"""
Module road_transport_costs
Translated using PySD version 3.14.3
"""

@component.add(
    name="battery weight penalty",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_be_weight_penalty_switch": 1, "hd_battery_weight": 1},
)
def battery_weight_penalty():
    """
    The levelized cost of trasnporting cargo with BE trucks is higher since the battery weight of 8 tons removes potential cargo from the assumed 14 tons of storage space. Following previously sourced material 75% of the 14 tons space is utilized on average. Motivates the discussion on whether trucks and buses should be evaluated on the same metrics.
    """
    return (
        hd_be_weight_penalty_switch()
        * ((0.75 * 14) / (14 - hd_battery_weight() / 1000) - 1)
        + 1
    )


@component.add(
    name="BioDiesel consumer price",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biodiesel_cost": 1, "diesel_price_scaler": 1},
)
def biodiesel_consumer_price():
    return biodiesel_cost() * diesel_price_scaler()


@component.add(
    name="diesel price per gj",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"diesel_price": 1, "diesel_lhv": 1},
)
def diesel_price_per_gj():
    return diesel_price() / 3600 * 10**6 / diesel_lhv()


@component.add(
    name="Diesel tank cost",
    units="€/l Diesel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"diesel_lhv": 1},
)
def diesel_tank_cost():
    return 0.21 * diesel_lhv()


@component.add(
    name="Electricity Taxes",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def electricity_taxes():
    """
    Assumption on cost of grid tariffs and electricity taxes. Normal place to subsidize the OPEX of EVs.
    """
    return 1


@component.add(
    name="H2 tank cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_lhv": 1},
)
def h2_tank_cost():
    return 24.75 * h2_lhv()


@component.add(
    name="HD AF",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "hd_lifetime": 1},
)
def hd_af():
    return 1 / ((1 - (1 + discount_rate()) ** -hd_lifetime()) / discount_rate())


@component.add(
    name="HD annual km",
    units="km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_daily_range": 1},
)
def hd_annual_km():
    """
    Assumes that the truck is driven daily all weekdays of the year
    """
    return hd_daily_range() * 5 * 52


@component.add(
    name="HD battery weight", units="kg", comp_type="Constant", comp_subtype="Normal"
)
def hd_battery_weight():
    return 8000


@component.add(
    name="HD BE CAPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_be_powertrain_capex": 1,
        "hd_be_storage_capex": 1,
        "hd_rest_of_vehicle_capex": 1,
        "hd_scrappage_value": 1,
        "vehicle_insurance": 1,
        "hd_af": 1,
        "hd_annual_km": 1,
    },
)
def hd_be_capex():
    return (
        (hd_be_powertrain_capex() + hd_be_storage_capex() + hd_rest_of_vehicle_capex())
        * (hd_af() * (1 - hd_scrappage_value()) + vehicle_insurance())
        / hd_annual_km()
    )


@component.add(
    name="HD BE energy usage",
    units="kWh/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_weight": 1, "hd_battery_weight": 1},
)
def hd_be_energy_usage():
    return 0.3814 * float(np.log(hd_weight() + hd_battery_weight())) - 2.6735


@component.add(
    name="HD BE LCO",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_be_capex": 1, "hd_be_opex": 1, "battery_weight_penalty": 1},
)
def hd_be_lco():
    return (hd_be_capex() + hd_be_opex()) * battery_weight_penalty()


@component.add(
    name="HD BE OM", units="€/km", comp_type="Constant", comp_subtype="Normal"
)
def hd_be_om():
    """
    Sourced from results graph in source.
    """
    return 0.074


@component.add(
    name="HD BE OPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_be_om": 1,
        "charging_efficiency": 1,
        "grid_electricity_price": 1,
        "hd_be_energy_usage": 1,
    },
)
def hd_be_opex():
    return (
        hd_be_om()
        + (hd_be_energy_usage() / charging_efficiency())
        * grid_electricity_price()
        / 1000
    )


@component.add(
    name="HD BE powertrain CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_electric_motor_cost": 1, "hd_power_capacity": 1},
)
def hd_be_powertrain_capex():
    return hd_electric_motor_cost() * hd_power_capacity()


@component.add(
    name="HD BE storage capacity",
    units="kWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_be_energy_usage": 1, "hd_daily_range": 1},
)
def hd_be_storage_capacity():
    """
    Storage capacity of battery electric truck assuming 50 % safety margin.
    """
    return hd_be_energy_usage() * hd_daily_range() * 1.5


@component.add(
    name="HD BE storage CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rt_battery_cost": 1, "hd_be_storage_capacity": 1},
)
def hd_be_storage_capex():
    return rt_battery_cost() * hd_be_storage_capacity()


@component.add(
    name="HD BE weight penalty switch", comp_type="Constant", comp_subtype="Normal"
)
def hd_be_weight_penalty_switch():
    """
    1 if fully activated, 0 if not
    """
    return 0.5


@component.add(
    name="HD BEV EF",
    units="gCO2/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_be_energy_usage": 1, "electricity_emission_factor": 1},
)
def hd_bev_ef():
    return hd_be_energy_usage() * electricity_emission_factor() * 1000


@component.add(
    name="HD CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fc_lco": 1,
        "hd_be_lco": 1,
        "diesel_emission_factor": 2,
        "hd_ice_lco": 1,
        "hd_ice_energy_usage": 2,
        "carbon_tax": 1,
        "diesel_lhv": 2,
    },
)
def hd_co2_wtp():
    """
    €/km / (tCO2/km)
    """
    return (
        float(np.minimum(hd_fc_lco(), hd_be_lco()))
        - (
            hd_ice_lco()
            - diesel_emission_factor()
            * diesel_lhv()
            * carbon_tax()
            * hd_ice_energy_usage()
        )
    ) / (diesel_emission_factor() * diesel_lhv() * hd_ice_energy_usage())


@component.add(
    name="HD current emissions cap",
    units="gCO2/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fossil_ef": 1,
        "time": 1,
        "hd_relative_emissions_reduction_lookup": 1,
        "hard_regulation": 1,
    },
)
def hd_current_emissions_cap():
    return hd_fossil_ef() * (
        1 - hd_relative_emissions_reduction_lookup(time()) * hard_regulation()
    )


@component.add(
    name="HD daily range", units="km", comp_type="Constant", comp_subtype="Normal"
)
def hd_daily_range():
    return 600


@component.add(
    name="HD electric motor cost",
    units="€/kW",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hd_electric_motor_cost():
    return 32.5


@component.add(
    name="HD EV efficiency",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hd_ev_efficiency():
    """
    Assumed on the higher range as opposed to light duty, which are assumed to do more urban driving.
    """
    return 0.85


@component.add(
    name="HD FC CAPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fc_powertrain_capex": 1,
        "hd_fc_storage_capex": 1,
        "hd_rest_of_vehicle_capex": 1,
        "hd_scrappage_value": 1,
        "vehicle_insurance": 1,
        "hd_af": 1,
        "hd_annual_km": 1,
    },
)
def hd_fc_capex():
    return (
        (hd_fc_powertrain_capex() + hd_fc_storage_capex() + hd_rest_of_vehicle_capex())
        * (hd_af() * (1 - hd_scrappage_value()) + vehicle_insurance())
        / hd_annual_km()
    )


@component.add(
    name="HD FC energy usage",
    units="kgH2/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_be_energy_usage": 1,
        "hd_ev_efficiency": 1,
        "hd_fcev_efficiency": 1,
        "h2_lhv": 1,
    },
)
def hd_fc_energy_usage():
    return hd_be_energy_usage() * hd_ev_efficiency() / hd_fcev_efficiency() / h2_lhv()


@component.add(
    name="HD FC LCO",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fc_lco_without_h2": 1,
        "hd_fcev_h2_cost": 1,
        "hd_fc_energy_usage": 1,
    },
)
def hd_fc_lco():
    return hd_fc_lco_without_h2() + hd_fc_energy_usage() * hd_fcev_h2_cost()


@component.add(
    name="HD FC LCO without H2",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fc_capex": 1, "hd_fc_om": 1},
)
def hd_fc_lco_without_h2():
    return hd_fc_capex() + hd_fc_om()


@component.add(
    name="HD FC OM", units="€/km", comp_type="Constant", comp_subtype="Normal"
)
def hd_fc_om():
    """
    Sourced from results graph in source - assumed similar to BE OPEX.
    """
    return 0.074


@component.add(
    name="HD FC powertrain CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_electric_motor_cost": 1, "fc_cost": 1, "hd_power_capacity": 1},
)
def hd_fc_powertrain_capex():
    return (hd_electric_motor_cost() + fc_cost()) * hd_power_capacity()


@component.add(
    name="HD FC storage capacity",
    units="kg H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fc_energy_usage": 1, "hd_daily_range": 1},
)
def hd_fc_storage_capacity():
    """
    Storage capacity of fuel cell truck assuming 50 % safety margin.
    """
    return hd_fc_energy_usage() * hd_daily_range() * 1.5


@component.add(
    name="HD FC storage CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rt_battery_cost": 1, "hd_fc_storage_capacity": 1, "h2_lhv": 1},
)
def hd_fc_storage_capex():
    """
    A constant cost of the 700 bar hydrogen tank is assumed of 42000 € in line with the used source for all cost numbers. Furthermore an additional (small) battery storage is included 1/17th the capacity of the hydrogen fuel tank
    """
    return 42000 + rt_battery_cost() * (hd_fc_storage_capacity() * h2_lhv()) / 17


@component.add(
    name="HD FCEV efficiency",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hd_fcev_efficiency():
    """
    New assumption: Efficiency of FCEV truck is 57% like the FCEV car Builds on the assumption that the EV truck has an efficiency of 85% and the fuel economy is determined by the fits found by Noll et al. (https://doi.org/10.1016/j.apenergy.2021.118079) - old assumption.
    """
    return 0.57


@component.add(
    name="HD fossil biodiesel share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_current_emissions_cap": 1, "hd_fossil_ef": 1},
)
def hd_fossil_biodiesel_share():
    return 1 - hd_current_emissions_cap() / hd_fossil_ef()


@component.add(
    name="HD Fossil EF",
    units="gCO2/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_ice_energy_usage": 1, "diesel_emission_factor": 1, "diesel_lhv": 1},
)
def hd_fossil_ef():
    return hd_ice_energy_usage() * diesel_emission_factor() * diesel_lhv() * 10**6


@component.add(
    name="HD fossil fuel cost",
    units="€/l",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "diesel_price": 1,
        "hd_fossil_biodiesel_share": 2,
        "diesel_lhv": 1,
        "biodiesel_consumer_price": 1,
    },
)
def hd_fossil_fuel_cost():
    return (
        diesel_price() * (1 - hd_fossil_biodiesel_share())
        + biodiesel_consumer_price()
        * 3600
        / 10**6
        * diesel_lhv()
        * hd_fossil_biodiesel_share()
    )


@component.add(
    name="HD ICE CAPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_ice_powertrain_capex": 1,
        "hd_ice_storage_capex": 1,
        "hd_rest_of_vehicle_capex": 1,
        "hd_scrappage_value": 1,
        "vehicle_insurance": 1,
        "hd_af": 1,
        "hd_annual_km": 1,
    },
)
def hd_ice_capex():
    return (
        (
            hd_ice_powertrain_capex()
            + hd_ice_storage_capex()
            + hd_rest_of_vehicle_capex()
        )
        * (hd_af() * (1 - hd_scrappage_value()) + vehicle_insurance())
        / hd_annual_km()
    )


@component.add(
    name="HD ICE energy usage",
    units="l Diesel/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_weight": 1},
)
def hd_ice_energy_usage():
    return 0.0903 * float(np.log(hd_weight())) - 0.6404


@component.add(
    name="HD ICE engine cost", units="€/kW", comp_type="Constant", comp_subtype="Normal"
)
def hd_ice_engine_cost():
    return 40.77


@component.add(
    name="HD ICE LCO",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_ice_capex": 1, "hd_ice_opex": 1},
)
def hd_ice_lco():
    return hd_ice_capex() + hd_ice_opex()


@component.add(
    name="HD ICE OM", units="€/km", comp_type="Constant", comp_subtype="Normal"
)
def hd_ice_om():
    """
    Sourced from results graph in source.
    """
    return 0.11


@component.add(
    name="HD ICE OPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_ice_om": 1, "hd_ice_energy_usage": 1, "hd_fossil_fuel_cost": 1},
)
def hd_ice_opex():
    return hd_ice_om() + hd_ice_energy_usage() * hd_fossil_fuel_cost()


@component.add(
    name="HD ICE powertrain CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_ice_engine_cost": 1, "hd_power_capacity": 1},
)
def hd_ice_powertrain_capex():
    return hd_ice_engine_cost() * hd_power_capacity()


@component.add(
    name="HD ICE storage capacity",
    units="l Diesel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_ice_energy_usage": 1, "hd_daily_range": 1},
)
def hd_ice_storage_capacity():
    """
    Storage capacity of diesel ICE truck assuming 50 % safety margin.
    """
    return hd_ice_energy_usage() * hd_daily_range() * 1.5


@component.add(
    name="HD ICE storage CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"diesel_tank_cost": 1, "hd_ice_storage_capacity": 1},
)
def hd_ice_storage_capex():
    return diesel_tank_cost() * hd_ice_storage_capacity()


@component.add(
    name="HD lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def hd_lifetime():
    """
    Financial investment horizon
    """
    return 8


@component.add(
    name="HD power capacity", units="kW", comp_type="Constant", comp_subtype="Normal"
)
def hd_power_capacity():
    return 343


@component.add(
    name="HD RELATIVE EMISSIONS REDUCTION LOOKUP",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_hd_relative_emissions_reduction_lookup"
    },
)
def hd_relative_emissions_reduction_lookup(x, final_subs=None):
    """
    percent reduction
    """
    return _hardcodedlookup_hd_relative_emissions_reduction_lookup(x, final_subs)


_hardcodedlookup_hd_relative_emissions_reduction_lookup = HardcodedLookups(
    [2020.0, 2025.0, 2030.0, 2035.0, 2040.0, 2050.0],
    [0.0, 0.15, 0.45, 0.65, 0.9, 0.9],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_hd_relative_emissions_reduction_lookup",
)


@component.add(
    name="HD rest of vehicle CAPEX",
    units="€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hd_rest_of_vehicle_capex():
    """
    €2019 for a vehicle
    """
    return 57560


@component.add(
    name="HD scrappage value",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hd_scrappage_value():
    """
    https://doi.org/10.1016/j.apenergy.2021.118079
    """
    return 0.18


@component.add(
    name="HD weight", units="kg", comp_type="Constant", comp_subtype="Normal"
)
def hd_weight():
    """
    Loaded weight of heavy duty truck assuming 75% utilization of payload.
    """
    return 14000 * 0.75 + 32000


@component.add(
    name="LD AF",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "ld_lifetime": 1},
)
def ld_af():
    return 1 / ((1 - (1 + discount_rate()) ** -ld_lifetime()) / discount_rate())


@component.add(
    name="LD annual km",
    units="km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_daily_drive": 1},
)
def ld_annual_km():
    """
    Assumes that the car is driven daily all weekdays of the year
    """
    return ld_daily_drive() * 5 * 52


@component.add(
    name="LD BE CAPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_be_engine_capex": 1,
        "ld_be_storage_capex": 1,
        "ld_rest_of_vehicle_capex": 1,
        "ld_af": 1,
        "vehicle_insurance": 1,
        "ld_scrappage_value": 1,
        "ld_annual_km": 1,
    },
)
def ld_be_capex():
    return (
        (ld_be_engine_capex() + ld_be_storage_capex() + ld_rest_of_vehicle_capex())
        * (ld_af() * (1 - ld_scrappage_value()) + vehicle_insurance())
        / ld_annual_km()
    )


@component.add(
    name="LD BE energy usage",
    units="kWh/km",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ld_be_energy_usage():
    return 0.2


@component.add(
    name="LD BE engine CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_electric_motor_cost": 1, "ld_power_capacity": 1},
)
def ld_be_engine_capex():
    return ld_electric_motor_cost() * ld_power_capacity()


@component.add(
    name="LD BE LCO",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_be_capex": 1, "ld_be_opex": 1},
)
def ld_be_lco():
    return ld_be_capex() + ld_be_opex()


@component.add(
    name="LD BE OM", units="€/km", comp_type="Constant", comp_subtype="Normal"
)
def ld_be_om():
    """
    Sourced from results graph in source. Assumed to be 1/10th of the O&M associated with a heavy duty truck.
    """
    return 0.074 / 10


@component.add(
    name="LD BE OPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_be_om": 1,
        "charging_efficiency": 1,
        "ld_be_energy_usage": 1,
        "electricity_taxes": 1,
        "grid_electricity_price": 1,
    },
)
def ld_be_opex():
    return (
        ld_be_om()
        + (ld_be_energy_usage() / charging_efficiency())
        * (grid_electricity_price() * electricity_taxes())
        / 1000
    )


@component.add(
    name="LD BE storage capacity",
    units="kWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_be_energy_usage": 1, "ld_range": 1},
)
def ld_be_storage_capacity():
    """
    Storage capacity of battery electric car assuming 25 % safety margin.
    """
    return ld_be_energy_usage() * ld_range() * 1.25


@component.add(
    name="LD BE storage CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rt_battery_cost": 1, "ld_be_storage_capacity": 1},
)
def ld_be_storage_capex():
    return rt_battery_cost() * ld_be_storage_capacity()


@component.add(
    name="LD BEV EF",
    units="gCO2/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_be_energy_usage": 1, "electricity_emission_factor": 1},
)
def ld_bev_ef():
    return ld_be_energy_usage() * electricity_emission_factor() * 1000


@component.add(
    name="LD CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fc_lco": 1,
        "ld_be_lco": 1,
        "diesel_emission_factor": 2,
        "ld_ice_lco": 1,
        "ld_ice_energy_usage": 2,
        "carbon_tax": 1,
        "diesel_lhv": 2,
    },
)
def ld_co2_wtp():
    return (
        float(np.minimum(ld_fc_lco(), ld_be_lco()))
        - (
            ld_ice_lco()
            - diesel_emission_factor()
            * diesel_lhv()
            * carbon_tax()
            * ld_ice_energy_usage()
        )
    ) / (diesel_emission_factor() * diesel_lhv() * ld_ice_energy_usage())


@component.add(
    name="LD current emissions cap",
    units="gCO2/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "ld_emissions_cap_lookup": 1},
)
def ld_current_emissions_cap():
    return ld_emissions_cap_lookup(time())


@component.add(
    name="LD daily drive", units="km", comp_type="Constant", comp_subtype="Normal"
)
def ld_daily_drive():
    """
    Source: https://doi.org/10.1016/j.trd.2021.103126
    """
    return 60


@component.add(
    name="LD electric motor cost",
    units="€/kW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_electric_motor_cost": 1,
        "ld_ice_engine_cost": 1,
        "hd_ice_engine_cost": 1,
    },
)
def ld_electric_motor_cost():
    """
    Assumes same cost relation as for heavy duty vehicles
    """
    return hd_electric_motor_cost() * ld_ice_engine_cost() / hd_ice_engine_cost()


@component.add(
    name="LD EMISSIONS CAP LOOKUP",
    units="gCO2/km",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_ld_emissions_cap_lookup"},
)
def ld_emissions_cap_lookup(x, final_subs=None):
    return _hardcodedlookup_ld_emissions_cap_lookup(x, final_subs)


_hardcodedlookup_ld_emissions_cap_lookup = HardcodedLookups(
    [2020.0, 2025.0, 2030.0, 2035.0, 2050.0],
    [120.0, 93.6, 49.5, 0.0, 0.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_ld_emissions_cap_lookup",
)


@component.add(
    name="LD EV efficiency",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ld_ev_efficiency():
    return 0.85


@component.add(
    name="LD FC CAPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fc_engine_capex": 1,
        "ld_fc_storage_capex": 1,
        "ld_rest_of_vehicle_capex": 1,
        "ld_af": 1,
        "vehicle_insurance": 1,
        "ld_scrappage_value": 1,
        "ld_annual_km": 1,
    },
)
def ld_fc_capex():
    return (
        (ld_fc_engine_capex() + ld_fc_storage_capex() + ld_rest_of_vehicle_capex())
        * (ld_af() * (1 - ld_scrappage_value()) + vehicle_insurance())
        / ld_annual_km()
    )


@component.add(
    name="LD FC energy usage",
    units="kgH2/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_be_energy_usage": 1,
        "ld_ev_efficiency": 1,
        "ld_fcev_efficiency": 1,
        "h2_lhv": 1,
    },
)
def ld_fc_energy_usage():
    """
    Assumes 57% efficiency of FC car with 85% efficiency of EV car.
    """
    return ld_be_energy_usage() * ld_ev_efficiency() / ld_fcev_efficiency() / h2_lhv()


@component.add(
    name="LD FC engine CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_electric_motor_cost": 1, "fc_cost": 1, "ld_power_capacity": 1},
)
def ld_fc_engine_capex():
    return (ld_electric_motor_cost() + fc_cost()) * ld_power_capacity()


@component.add(
    name="LD FC LCO",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fc_lco_without_h2": 1,
        "ld_fcev_h2_cost": 1,
        "ld_fc_energy_usage": 1,
    },
)
def ld_fc_lco():
    return ld_fc_lco_without_h2() + ld_fc_energy_usage() * ld_fcev_h2_cost()


@component.add(
    name="LD FC LCO without H2",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fc_capex": 1, "ld_fc_om": 1},
)
def ld_fc_lco_without_h2():
    return ld_fc_capex() + ld_fc_om()


@component.add(
    name="LD FC OM", units="€/km", comp_type="Constant", comp_subtype="Normal"
)
def ld_fc_om():
    """
    Sourced from results graph in source - assumed similar to BE OPEX. Assumed to be 1/10th of the O&M associated with a heavy duty truck.
    """
    return 0.074 / 10


@component.add(
    name="LD FC storage capacity",
    units="kg H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fc_energy_usage": 1, "ld_range": 1},
)
def ld_fc_storage_capacity():
    """
    Storage capacity of fuel cell car assuming 25 % safety margin.
    """
    return ld_fc_energy_usage() * ld_range() * 1.25


@component.add(
    name="LD FC storage CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fc_storage_capacity": 2,
        "h2_tank_cost": 1,
        "rt_battery_cost": 1,
        "h2_lhv": 1,
    },
)
def ld_fc_storage_capex():
    """
    A cost per capacity for hydrogen storage is assumed for LD cars. Furthermore an additional (small) battery storage is included 1/11.5th the capacity of the hydrogen fuel tank in line with assumptions made in (https://doi.org/10.1016/j.apenergy.2021.118079).
    """
    return (
        ld_fc_storage_capacity() * h2_tank_cost()
        + rt_battery_cost() * (ld_fc_storage_capacity() * h2_lhv()) / 11.5
    )


@component.add(
    name="LD FCEV efficiency",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ld_fcev_efficiency():
    """
    60% efficiency from energy content of H2 to energy delivered to the electric motor. 95% efficient electric motor.
    """
    return 0.57


@component.add(
    name="LD fossil biodiesel share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_current_emissions_cap": 1, "ld_fossil_ef": 1, "hard_regulation": 1},
)
def ld_fossil_biodiesel_share():
    return (1 - ld_current_emissions_cap() / ld_fossil_ef()) * hard_regulation()


@component.add(
    name="LD Fossil EF",
    units="gCO2/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_ice_energy_usage": 1, "diesel_emission_factor": 1, "diesel_lhv": 1},
)
def ld_fossil_ef():
    return ld_ice_energy_usage() * diesel_emission_factor() * diesel_lhv() * 10**6


@component.add(
    name="LD fossil fuel cost",
    units="€/l",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "diesel_price": 1,
        "ld_fossil_biodiesel_share": 2,
        "diesel_lhv": 1,
        "biodiesel_consumer_price": 1,
    },
)
def ld_fossil_fuel_cost():
    return (
        diesel_price() * (1 - ld_fossil_biodiesel_share())
        + biodiesel_consumer_price()
        * 3600
        / 10**6
        * diesel_lhv()
        * ld_fossil_biodiesel_share()
    )


@component.add(
    name="LD ICE CAPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_ice_engine_capex": 1,
        "ld_ice_storage_capex": 1,
        "ld_rest_of_vehicle_capex": 1,
        "ld_af": 1,
        "vehicle_insurance": 1,
        "ld_scrappage_value": 1,
        "ld_annual_km": 1,
    },
)
def ld_ice_capex():
    return (
        (ld_ice_engine_capex() + ld_ice_storage_capex() + ld_rest_of_vehicle_capex())
        * (ld_af() * (1 - ld_scrappage_value()) + vehicle_insurance())
        / ld_annual_km()
    )


@component.add(
    name="LD ICE energy usage",
    units="l Diesel/km",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ld_ice_energy_usage():
    return 1 / 20


@component.add(
    name="LD ICE engine CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_ice_engine_cost": 1, "ld_power_capacity": 1},
)
def ld_ice_engine_capex():
    return ld_ice_engine_cost() * ld_power_capacity()


@component.add(
    name="LD ICE engine cost", units="€/kW", comp_type="Constant", comp_subtype="Normal"
)
def ld_ice_engine_cost():
    return 59.89


@component.add(
    name="LD ICE LCO",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_ice_capex": 1, "ld_ice_opex": 1},
)
def ld_ice_lco():
    return ld_ice_capex() + ld_ice_opex()


@component.add(
    name="LD ICE OM", units="€/km", comp_type="Constant", comp_subtype="Normal"
)
def ld_ice_om():
    """
    Sourced from results graph in source. Assumed to be 1/10th of the O&M associated with a heavy duty truck.
    """
    return 0.11 / 10


@component.add(
    name="LD ICE OPEX",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_ice_om": 1, "ld_ice_energy_usage": 1, "ld_fossil_fuel_cost": 1},
)
def ld_ice_opex():
    return ld_ice_om() + ld_ice_energy_usage() * ld_fossil_fuel_cost()


@component.add(
    name="LD ICE storage capacity",
    units="l Diesel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_ice_energy_usage": 1, "ld_range": 1},
)
def ld_ice_storage_capacity():
    """
    Storage capacity of diesel ICE car assuming 25 % safety margin.
    """
    return ld_ice_energy_usage() * ld_range() * 1.25


@component.add(
    name="LD ICE storage CAPEX",
    units="€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"diesel_tank_cost": 1, "ld_ice_storage_capacity": 1},
)
def ld_ice_storage_capex():
    return diesel_tank_cost() * ld_ice_storage_capacity()


@component.add(
    name="LD lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def ld_lifetime():
    """
    Financial investment horizon.
    """
    return 7


@component.add(
    name="LD power capacity", units="kW", comp_type="Constant", comp_subtype="Normal"
)
def ld_power_capacity():
    """
    Equal to a 100 hp car - own assumption. This value is critical for FCEVs as the FC is expensive. Would likely be prioritized differently in the different car types.
    """
    return 75


@component.add(name="LD range", units="km", comp_type="Constant", comp_subtype="Normal")
def ld_range():
    """
    Own assumption of consumer desires
    """
    return 250


@component.add(
    name="LD rest of vehicle CAPEX",
    units="€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ld_rest_of_vehicle_capex():
    """
    Own assumption - small truck rest of vehicle cost is 17k in the referenced study, which regards commercial light duty vehicles.
    """
    return 5000


@component.add(
    name="LD scrappage value",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ld_scrappage_value():
    """
    https://doi.org/10.1016/j.apenergy.2021.118079
    """
    return 0.25


@component.add(
    name="RT battery cost", units="€/kWh", comp_type="Constant", comp_subtype="Normal"
)
def rt_battery_cost():
    return 139.34


@component.add(
    name="Vehicle insurance",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def vehicle_insurance():
    """
    Assunmption: insurance cost is 2% of CAPEX
    """
    return 0.02
