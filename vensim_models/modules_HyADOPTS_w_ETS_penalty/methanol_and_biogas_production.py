"""
Module methanol_and_biogas_production
Translated using PySD version 3.14.3
"""

@component.add(
    name="biogas AF",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "biogas_lifetime": 1},
)
def biogas_af():
    return 1 / ((1 - (1 + discount_rate()) ** -biogas_lifetime()) / discount_rate())


@component.add(
    name="biogas biomass usage",
    units="GJ Biomass / GJ biogas",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biogas_biomass_usage():
    """
    1.67 GJ biogas is produced per ton of biomass. Each ton of biomass contains 2.81 GJ of energy.
    """
    return 2.81 / 1.67


@component.add(
    name="biogas CAPEX",
    units="M€/MW",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def biogas_capex():
    return np.interp(
        time(), [2015.0, 2025.0, 2030.0, 2040.0, 2050.0], [1.04, 1.04, 0.9, 0.87, 0.82]
    )


@component.add(
    name="biogas cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biogas_af": 1,
        "biogas_capex": 1,
        "biogas_opex": 1,
        "biogas_operating_hours": 1,
        "biogas_electricity_usage": 1,
        "grid_electricity_price": 1,
        "heat_cost": 1,
        "biogas_heat_usage": 1,
        "biogas_biomass_usage": 1,
        "biomass_price": 1,
    },
)
def biogas_cost():
    """
    Assumes 8500 full load hours - no mention of downtime in the tech. catalogue. OPEX multiplied by 2.28/3.42 to not double-count electricity and heat costs.
    """
    return (
        (biogas_af() * biogas_capex() * 1000 + biogas_opex() * 2.28 / 3.42)
        * 1000
        / biogas_operating_hours()
        / 3.6
        + biogas_electricity_usage() * grid_electricity_price() / 3.6
        + biogas_heat_usage() * heat_cost() / 3.6
        + biogas_biomass_usage() * biomass_price()
    )


@component.add(
    name="biogas electricity usage",
    units="GJ el / GJ biogas",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def biogas_electricity_usage():
    return np.interp(
        time(),
        [2015.0, 2025.0, 2030.0, 2040.0, 2050.0],
        [0.0216, 0.0216, 0.0188, 0.0182, 0.0171],
    )


@component.add(
    name="biogas heat usage",
    units="GJ heat / GJ biogas",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def biogas_heat_usage():
    return np.interp(
        time(),
        [2015.0, 2025.0, 2030.0, 2040.0, 2050.0],
        [0.0505, 0.0505, 0.044, 0.0425, 0.0425],
    )


@component.add(
    name="biogas lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def biogas_lifetime():
    return 20


@component.add(
    name="biogas operating hours",
    units="hours",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biogas_operating_hours():
    return 8000


@component.add(
    name="biogas OPEX",
    units="k€/MW/yr",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def biogas_opex():
    return np.interp(
        time(),
        [2015.0, 2025.0, 2030.0, 2040.0, 2050.0],
        [63.98, 63.98, 55.66, 53.74, 50.54],
    )


@component.add(
    name="bioMeOH AF",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "biomeoh_lifetime": 1},
)
def biomeoh_af():
    return 1 / ((1 - (1 + discount_rate()) ** -biomeoh_lifetime()) / discount_rate())


@component.add(
    name="bioMeOH biomass usage",
    units="kWh biomass/kWh MeOH",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biomeoh_biomass_usage():
    """
    kWh biomass/kWh MeOH Source:https://doi.org/10.1016/j.energy.2020.118432
    """
    return 0.73


@component.add(
    name="bioMeOH CAPEX",
    units="€/kgMeOH/h",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomeoh_learning": 1},
)
def biomeoh_capex():
    return 11900 * 1.3 * 1.3 * biomeoh_learning()


@component.add(
    name="bioMeOH cost without H2",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_capex": 1,
        "biomeoh_opex": 1,
        "biomeoh_af": 1,
        "meoh_lhv": 2,
        "biomeoh_operating_hours": 1,
        "heat_cost": 1,
        "grid_electricity_price": 1,
        "biomeoh_electricity_usage": 1,
        "biomeoh_excess_heat": 1,
        "biomeoh_biomass_usage": 1,
        "biomass_price": 1,
    },
)
def biomeoh_cost_without_h2():
    """
    €/GJ MeOH [ [kgBM/kgMeOH] * [€/GJ] * [MJ/kgBM ] / [MJ/GJ] + [€/kgH2] / [kgMeOH/kgH2] + [€/kWh * kWh/kgMeOH] ] / [MJ/kgMeOH]
    """
    return (
        biomeoh_capex()
        * (biomeoh_af() + biomeoh_opex())
        / (biomeoh_operating_hours() * meoh_lhv())
        * 1000
        + (
            grid_electricity_price() * biomeoh_electricity_usage()
            - heat_cost() * biomeoh_excess_heat()
        )
        / meoh_lhv()
        + biomeoh_biomass_usage() * biomass_price()
    )


@component.add(
    name="bioMeOH electricity usage",
    units="kWh/kgMeOH",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biomeoh_electricity_usage():
    """
    kWhe/kgMeOH
    """
    return 0.64


@component.add(
    name="bioMeOH excess heat",
    units="kWh/kgMeOH",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biomeoh_excess_heat():
    return 0.428


@component.add(
    name="bioMeOH H2 usage",
    units="kgMeOH/kgH2",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biomeoh_h2_usage():
    """
    kg MeOH per kg H2
    """
    return 15.7


@component.add(
    name="bioMeOH H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "min_alternative_meoh_cost": 1,
        "biomeoh_cost_without_h2": 1,
        "meoh_lhv": 1,
        "biomeoh_h2_usage": 1,
    },
)
def biomeoh_h2_wtp():
    return (
        (min_alternative_meoh_cost() - biomeoh_cost_without_h2())
        * meoh_lhv()
        * biomeoh_h2_usage()
        / 1000
    )


@component.add(
    name="bioMeOH learning",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_plant_size": 2,
        "meoh_lhv": 1,
        "green_biomeoh_weight": 1,
        "meoh_is": 1,
        "meoh_ds": 1,
        "biomeoh": 1,
        "biomeoh_learning_rate": 1,
    },
)
def biomeoh_learning():
    return (
        float(
            np.maximum(
                biomeoh_plant_size(),
                (meoh_ds() + meoh_is()) * green_biomeoh_weight()
                + biomeoh() * meoh_lhv() / 3.6 * 10**3,
            )
        )
        / biomeoh_plant_size()
    ) ** (float(np.log(1 - biomeoh_learning_rate())) / float(np.log(2)))


@component.add(
    name="bioMeOH learning rate", comp_type="Constant", comp_subtype="Normal"
)
def biomeoh_learning_rate():
    return 0.03


@component.add(
    name="bioMeOH lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def biomeoh_lifetime():
    return 25


@component.add(
    name="bioMeOH operating hours",
    units="h",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biomeoh_operating_hours():
    return 8000


@component.add(
    name="bioMeOH OPEX", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def biomeoh_opex():
    """
    Percentage of CAPEX
    """
    return 0.04


@component.add(
    name="bioMeOH plant size",
    units="GWh/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biomeoh_plant_size():
    """
    400 kt MeOH per year
    """
    return 400 * 19.9 / 3.6


@component.add(
    name="Blue bioMeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_cost_without_h2": 1,
        "blue_h2_cost": 1,
        "biomeoh_h2_usage": 1,
        "meoh_lhv": 1,
    },
)
def blue_biomeoh_cost():
    return (
        biomeoh_cost_without_h2()
        + blue_h2_cost() / biomeoh_h2_usage() / meoh_lhv() * 1000
    )


@component.add(
    name="Blue eMeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "emeoh_cost_without_hydrogen": 1,
        "blue_h2_cost": 1,
        "emeoh_h2_usage": 1,
        "meoh_lhv": 1,
    },
)
def blue_emeoh_cost():
    return (
        emeoh_cost_without_hydrogen()
        + blue_h2_cost() / emeoh_h2_usage() / meoh_lhv() * 1000
    )


@component.add(
    name="Blue MeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "convmeoh_cost": 1,
        "meoh_lhv": 1,
        "cc_capture_rate": 1,
        "carbon_tax": 1,
        "convmeoh_emission_factor": 1,
        "ccs_cost": 1,
    },
)
def blue_meoh_cost():
    return (
        convmeoh_cost()
        + convmeoh_emission_factor()
        / meoh_lhv()
        * cc_capture_rate()
        * (ccs_cost() - carbon_tax())
    )


@component.add(
    name="convMeOH AF",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "convmeoh_lifetime": 1},
)
def convmeoh_af():
    return 1 / ((1 - (1 + discount_rate()) ** -convmeoh_lifetime()) / discount_rate())


@component.add(
    name="convMeOH CAPEX", units="€/(t/yr)", comp_type="Constant", comp_subtype="Normal"
)
def convmeoh_capex():
    return 846.73


@component.add(
    name="convMeOH CO2 WTP",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "min_green_meoh_cost": 1,
        "convmeoh_cost_without_co2": 1,
        "meoh_lhv": 1,
        "convmeoh_emission_factor": 1,
        "convmeoh_electricity_usage": 1,
        "electricity_emission_factor": 1,
    },
)
def convmeoh_co2_wtp():
    """
    €/tMeOH / (tCO2/tMeOH)
    """
    return (
        (min_green_meoh_cost() - convmeoh_cost_without_co2())
        * meoh_lhv()
        / (
            convmeoh_emission_factor()
            + convmeoh_electricity_usage() * electricity_emission_factor()
        )
    )


@component.add(
    name="convMeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_excess_activity": 1,
        "convmeoh_emission_factor": 2,
        "carbon_tax": 1,
        "carbon_tax_w_penalty": 1,
        "grid_electricity_price": 1,
        "convmeoh_electricity_usage": 1,
        "gas_price": 1,
        "convmeoh_gas_usage": 1,
        "convmeoh_opex": 1,
        "convmeoh_af": 1,
        "convmeoh_capex": 1,
        "meoh_lhv": 1,
    },
)
def convmeoh_cost():
    return (
        if_then_else(
            meoh_excess_activity() > 0,
            lambda: convmeoh_emission_factor() * carbon_tax(),
            lambda: convmeoh_emission_factor() * carbon_tax_w_penalty(),
        )
        + convmeoh_electricity_usage() * grid_electricity_price()
        + convmeoh_gas_usage() * gas_price()
        + convmeoh_opex()
        + convmeoh_capex() * convmeoh_af()
    ) / meoh_lhv()


@component.add(
    name="convMeOH cost marginal",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "convmeoh_cost": 1,
        "convmeoh_af": 1,
        "convmeoh_capex": 1,
        "meoh_lhv": 1,
    },
)
def convmeoh_cost_marginal():
    return convmeoh_cost() - convmeoh_capex() * convmeoh_af() / meoh_lhv()


@component.add(
    name="convMeOH cost without CO2",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "convmeoh_cost": 1,
        "convmeoh_electricity_usage": 1,
        "meoh_lhv": 1,
        "electricity_emission_factor": 1,
        "carbon_tax": 1,
        "convmeoh_emission_factor": 1,
    },
)
def convmeoh_cost_without_co2():
    return (
        convmeoh_cost()
        - carbon_tax()
        * (
            convmeoh_emission_factor()
            + electricity_emission_factor() * convmeoh_electricity_usage()
        )
        / meoh_lhv()
    )


@component.add(
    name="convMeOH electricity usage",
    units="MWh/tMeOH",
    comp_type="Constant",
    comp_subtype="Normal",
)
def convmeoh_electricity_usage():
    return 0.147


@component.add(
    name="convMeOH emission factor",
    units="tCO2/tMeOH",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"convmeoh_gas_usage": 1, "gas_emission_factor": 1},
)
def convmeoh_emission_factor():
    """
    Direct synthesis emissions + combustion emissions
    """
    return convmeoh_gas_usage() * gas_emission_factor()


@component.add(
    name="convMeOH gas usage", units="GJ/t", comp_type="Constant", comp_subtype="Normal"
)
def convmeoh_gas_usage():
    return 33.4


@component.add(
    name="convMeOH lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def convmeoh_lifetime():
    return 25


@component.add(
    name="convMeOH OPEX", units="€/t", comp_type="Constant", comp_subtype="Normal"
)
def convmeoh_opex():
    """
    Variable costs + fixed costs
    """
    return 42.84


@component.add(
    name="DS bioMeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_cost_without_h2": 1,
        "biomeoh_h2_usage": 1,
        "meoh_lhv": 1,
        "meoh_ds_h2_cost": 1,
    },
)
def ds_biomeoh_cost():
    return (
        biomeoh_cost_without_h2()
        + meoh_ds_h2_cost() / biomeoh_h2_usage() / meoh_lhv() * 1000
    )


@component.add(
    name="eMeOH AF",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"discount_rate": 2, "emeoh_lifetime": 1},
)
def emeoh_af():
    return 1 / ((1 - (1 + discount_rate()) ** -emeoh_lifetime()) / discount_rate())


@component.add(
    name="eMeOH CAPEX",
    units="€/kgMeOH/h",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh_learning": 1},
)
def emeoh_capex():
    return 11900 * emeoh_learning()


@component.add(
    name="eMeOH CO2 usage",
    units="kgCO2/kgMeOH",
    comp_type="Constant",
    comp_subtype="Normal",
)
def emeoh_co2_usage():
    """
    kg CO2 per kg MeOH
    """
    return 1.374


@component.add(
    name="eMeOH cost without hydrogen",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "emeoh_capex": 1,
        "emeoh_opex": 1,
        "emeoh_af": 1,
        "emeoh_operating_hours": 1,
        "meoh_lhv": 2,
        "heat_cost": 1,
        "grid_electricity_price": 1,
        "emeoh_excess_heat": 1,
        "ps_cc_cost": 1,
        "cc_capture_rate": 1,
        "emeoh_co2_usage": 1,
        "emeoh_electricity_usage": 1,
    },
)
def emeoh_cost_without_hydrogen():
    """
    €/GJ MeOH [ [kgBM/kgMeOH] * [€/GJ] * [MJ/kgBM ] / [MJ/GJ] + [€/kgH2] / [kgMeOH/kgH2] + [€/kWh * kWh/kgMeOH] ] / [MJ/kgMeOH]
    """
    return (
        emeoh_capex()
        * (emeoh_af() + emeoh_opex())
        / (emeoh_operating_hours() * meoh_lhv())
        * 1000
        + (
            emeoh_co2_usage() * (ps_cc_cost() / cc_capture_rate())
            + grid_electricity_price() * emeoh_electricity_usage()
            - heat_cost() * emeoh_excess_heat()
        )
        / meoh_lhv()
    )


@component.add(
    name="eMeOH electricity usage",
    units="kWh/kgMeOH",
    comp_type="Constant",
    comp_subtype="Normal",
)
def emeoh_electricity_usage():
    """
    kWhe/kgMeOH
    """
    return 0.316


@component.add(
    name="eMeOH excess heat",
    units="kWh/kg MeOH",
    comp_type="Constant",
    comp_subtype="Normal",
)
def emeoh_excess_heat():
    return 0.68


@component.add(
    name="eMeOH H2 usage",
    units="kgMeOH/kgH2",
    comp_type="Constant",
    comp_subtype="Normal",
)
def emeoh_h2_usage():
    """
    kg MeOH per kg H2
    """
    return 5.26


@component.add(
    name="eMeOH H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "min_alternative_meoh_cost": 1,
        "emeoh_cost_without_hydrogen": 1,
        "emeoh_h2_usage": 1,
        "meoh_lhv": 1,
    },
)
def emeoh_h2_wtp():
    return (
        (min_alternative_meoh_cost() - emeoh_cost_without_hydrogen())
        * emeoh_h2_usage()
        * meoh_lhv()
        / 1000
    )


@component.add(
    name="eMeOH learning",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "emeoh_plant_size": 2,
        "meoh_lhv": 1,
        "emeoh": 1,
        "green_biomeoh_weight": 1,
        "meoh_is": 1,
        "meoh_ds": 1,
        "emeoh_learning_rate": 1,
    },
)
def emeoh_learning():
    return (
        float(
            np.maximum(
                emeoh_plant_size(),
                (meoh_ds() + meoh_is()) * (1 - green_biomeoh_weight())
                + emeoh() * meoh_lhv() / 3.6 * 10**3,
            )
        )
        / emeoh_plant_size()
    ) ** (float(np.log(1 - emeoh_learning_rate())) / float(np.log(2)))


@component.add(name="eMeOH learning rate", comp_type="Constant", comp_subtype="Normal")
def emeoh_learning_rate():
    return 0.03


@component.add(
    name="eMeOH lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def emeoh_lifetime():
    return 25


@component.add(
    name="eMeOH operating hours", units="h", comp_type="Constant", comp_subtype="Normal"
)
def emeoh_operating_hours():
    return 8000


@component.add(
    name="eMeOH OPEX", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def emeoh_opex():
    """
    Percentage of CAPEX
    """
    return 0.04


@component.add(
    name="eMeOH plant size",
    units="GWh/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def emeoh_plant_size():
    """
    400 kt MeOH per year
    """
    return 400 * 19.9 / 3.6


@component.add(
    name="Green bioMeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_cost_without_h2": 1,
        "biomeoh_h2_usage": 1,
        "meoh_lhv": 1,
        "biomeoh_h2_cost": 1,
    },
)
def green_biomeoh_cost():
    return (
        biomeoh_cost_without_h2()
        + biomeoh_h2_cost() / biomeoh_h2_usage() / meoh_lhv() * 1000
    )


@component.add(
    name="Green eMeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "emeoh_cost_without_hydrogen": 1,
        "emeoh_h2_cost": 1,
        "meoh_lhv": 1,
        "emeoh_h2_usage": 1,
    },
)
def green_emeoh_cost():
    return (
        emeoh_cost_without_hydrogen()
        + emeoh_h2_cost() / emeoh_h2_usage() / meoh_lhv() * 1000
    )


@component.add(
    name="Grey bioMeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_cost_without_h2": 1,
        "biomeoh_h2_usage": 1,
        "meoh_lhv": 1,
        "grey_h2_cost": 1,
    },
)
def grey_biomeoh_cost():
    return (
        biomeoh_cost_without_h2()
        + grey_h2_cost() / biomeoh_h2_usage() / meoh_lhv() * 1000
    )


@component.add(
    name="Grey eMeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "emeoh_cost_without_hydrogen": 1,
        "grey_h2_cost": 1,
        "meoh_lhv": 1,
        "emeoh_h2_usage": 1,
    },
)
def grey_emeoh_cost():
    return (
        emeoh_cost_without_hydrogen()
        + grey_h2_cost() / emeoh_h2_usage() / meoh_lhv() * 1000
    )


@component.add(
    name="IS bioMeOH cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_cost_without_h2": 1,
        "biomeoh_h2_usage": 1,
        "meoh_lhv": 1,
        "meoh_is_h2_cost": 1,
    },
)
def is_biomeoh_cost():
    return (
        biomeoh_cost_without_h2()
        + meoh_is_h2_cost() / biomeoh_h2_usage() / meoh_lhv() * 1000
    )


@component.add(
    name="MeOH LHV", units="GJ/t", comp_type="Constant", comp_subtype="Unchangeable"
)
def meoh_lhv():
    return 19.9


@component.add(
    name="min alternative MeOH cost",
    units="€/MJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"convmeoh_cost": 1},
)
def min_alternative_meoh_cost():
    return convmeoh_cost()
