"""
Module financial_resources_and_hyperparameters
Translated using PySD version 3.14.3
"""

@component.add(
    name="BIOMASS PRICE",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "biomass_price_lookup": 1, "biomass_price_scaler": 1},
)
def biomass_price():
    """
    €/GJ
    """
    return biomass_price_lookup(time()) * biomass_price_scaler()


@component.add(
    name="BIOMASS PRICE INIT",
    units="€/GJ",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_biomass_price_init": 1},
    other_deps={
        "_initial_biomass_price_init": {"initial": {"biomass_price": 1}, "step": {}}
    },
)
def biomass_price_init():
    return _initial_biomass_price_init()


_initial_biomass_price_init = Initial(
    lambda: biomass_price(), "_initial_biomass_price_init"
)


@component.add(
    name="BIOMASS PRICE LOOKUP",
    units="€/GJ",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_biomass_price_lookup"},
)
def biomass_price_lookup(x, final_subs=None):
    """
    €/GJ
    """
    return _hardcodedlookup_biomass_price_lookup(x, final_subs)


_hardcodedlookup_biomass_price_lookup = HardcodedLookups(
    [2020.0, 2030.0, 2040.0, 2050.0],
    [12.0, 11.0, 10.5, 8.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_biomass_price_lookup",
)


@component.add(
    name="CARBON TAX",
    units="€/tCO2",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={
        "ets": 1,
        "_smooth_carbon_tax": 1,
        "carbon_tax_lookup": 1,
        "carbon_tax_sensitivity": 1,
        "time": 1,
    },
    other_deps={
        "_smooth_carbon_tax": {
            "initial": {"ets_clearing": 1},
            "step": {"ets_clearing": 1, "time_step": 1},
        }
    },
)
def carbon_tax():
    """
    €/tCO2
    !Time
    """
    return if_then_else(
        ets(),
        lambda: _smooth_carbon_tax(),
        lambda: carbon_tax_lookup(time()) * carbon_tax_sensitivity(),
    )


_smooth_carbon_tax = Smooth(
    lambda: ets_clearing(),
    lambda: 3 * time_step(),
    lambda: ets_clearing(),
    lambda: 1,
    "_smooth_carbon_tax",
)


@component.add(
    name="CARBON TAX LOOKUP",
    units="€/tCO2",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_carbon_tax_lookup"},
)
def carbon_tax_lookup(x, final_subs=None):
    return _hardcodedlookup_carbon_tax_lookup(x, final_subs)


_hardcodedlookup_carbon_tax_lookup = HardcodedLookups(
    [2022, 2030, 2040, 2050],
    [55, 110, 200, 300],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_carbon_tax_lookup",
)


@component.add(
    name="CARBON TAX SENSITIVITY",
    units="scalar",
    comp_type="Constant",
    comp_subtype="Normal",
)
def carbon_tax_sensitivity():
    return 1


@component.add(
    name="CARBON TAX W PENALTY",
    units="€/tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"carbon_tax": 1},
)
def carbon_tax_w_penalty():
    """
    source for penalty: https://climate.ec.europa.eu/eu-action/carbon-markets/eu-emissions-trading- system-eu-ets/monitoring-reporting-and-verification_en
    """
    return carbon_tax() + 100


@component.add(
    name="COAL PRICE",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "coal_price_lookup": 1},
)
def coal_price():
    """
    €/t. To be updated
    """
    return coal_price_lookup(time())


@component.add(
    name="COAL PRICE LOOKUP",
    units="€/GJ",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_coal_price_lookup"},
)
def coal_price_lookup(x, final_subs=None):
    return _hardcodedlookup_coal_price_lookup(x, final_subs)


_hardcodedlookup_coal_price_lookup = HardcodedLookups(
    [2015.0, 2030.0, 2050.0],
    [2.85, 3.5, 3.5],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_coal_price_lookup",
)


@component.add(
    name="DISCOUNT RATE", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def discount_rate():
    """
    General discount rate if nothing special is assumed.
    """
    return 0.081


@component.add(
    name="ECONOMIC DECOMMISSIONING",
    units="boolean",
    comp_type="Constant",
    comp_subtype="Normal",
)
def economic_decommissioning():
    return 1


@component.add(
    name="ELECTRICITY EMISSION FACTOR",
    units="tCO2/MWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "electricity_emission_lookup": 1},
)
def electricity_emission_factor():
    """
    https://ens.dk/en/our-services/statistics-data-key-figures-and-energy-maps/key-figure s 207 gCO2/kWh
    """
    return electricity_emission_lookup(time())


@component.add(
    name="ELECTRICITY EMISSION LOOKUP",
    units="tCO2/MWh",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_electricity_emission_lookup"},
)
def electricity_emission_lookup(x, final_subs=None):
    """
    https://www.eea.europa.eu/en/analysis/indicators/greenhouse-gas-emission-in tensity-of-1
    """
    return _hardcodedlookup_electricity_emission_lookup(x, final_subs)


_hardcodedlookup_electricity_emission_lookup = HardcodedLookups(
    [2019.0, 2022.0, 2030.0, 2050.0],
    [0.22, 0.207, 0.12, 0.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_electricity_emission_lookup",
)


@component.add(
    name="ELECTRICITY PRICE LOOKUP",
    units="€/MWh",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_electricity_price_lookup"},
)
def electricity_price_lookup(x, final_subs=None):
    """
    Alternative: ([(0,0)-(10,10)],(2019,38),(2030,38),(2040,43),(2050,43) ) Output from net zero Balmorel run.
    """
    return _hardcodedlookup_electricity_price_lookup(x, final_subs)


_hardcodedlookup_electricity_price_lookup = HardcodedLookups(
    [2019, 2030, 2050],
    [40, 40, 40],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_electricity_price_lookup",
)


@component.add(
    name="ELECTRICITY SENSITIVITY",
    units="scalar",
    comp_type="Constant",
    comp_subtype="Normal",
)
def electricity_sensitivity():
    return 1


@component.add(name="ETS", comp_type="Constant", comp_subtype="Normal")
def ets():
    """
    1 if scenario of regulation, 0 if not
    """
    return 0


@component.add(
    name="ETS Clearing", units="€/tCO2", comp_type="Constant", comp_subtype="Normal"
)
def ets_clearing():
    return 0


@component.add(
    name="GAS PRICE",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "gas_price_lookup": 1},
)
def gas_price():
    """
    €/GJ
    """
    return gas_price_lookup(time())


@component.add(
    name="GAS PRICE LOOKUP",
    units="€/GJ",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_gas_price_lookup"},
)
def gas_price_lookup(x, final_subs=None):
    return _hardcodedlookup_gas_price_lookup(x, final_subs)


_hardcodedlookup_gas_price_lookup = HardcodedLookups(
    [2015.0, 2030.0, 2040.0, 2050.0],
    [6.3, 8.5, 9.3, 10.2],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_gas_price_lookup",
)


@component.add(
    name="GRID ELECTRICITY PRICE",
    units="€/MWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "electricity_price_lookup": 1, "electricity_sensitivity": 1},
)
def grid_electricity_price():
    """
    €/MWh
    """
    return electricity_price_lookup(time()) * electricity_sensitivity()


@component.add(
    name="Hard Regulation",
    units="boolean",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def hard_regulation():
    """
    1 if mandates and hard EU regulation is enforced, 0 if not.
    """
    return step(__data["time"], 0, 2022)


@component.add(name="HBA", units="boolean", comp_type="Constant", comp_subtype="Normal")
def hba():
    """
    If 1, then sector subsidies are based on WTP gap, else on stated level.
    """
    return 0


@component.add(
    name="INFLATION LOOKUP",
    units="scalar",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_inflation_lookup"},
)
def inflation_lookup(x, final_subs=None):
    """
    Base year 2020
    """
    return _hardcodedlookup_inflation_lookup(x, final_subs)


_hardcodedlookup_inflation_lookup = HardcodedLookups(
    [
        2000.0,
        2001.0,
        2002.0,
        2003.0,
        2004.0,
        2005.0,
        2006.0,
        2007.0,
        2008.0,
        2009.0,
        2010.0,
        2011.0,
        2012.0,
        2013.0,
        2014.0,
        2015.0,
        2016.0,
        2017.0,
        2018.0,
        2019.0,
        2020.0,
        2021.0,
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
        2051.0,
        2052.0,
        2053.0,
        2054.0,
        2055.0,
        2056.0,
        2057.0,
        2058.0,
        2059.0,
        2060.0,
        2061.0,
        2062.0,
        2063.0,
        2064.0,
        2065.0,
        2066.0,
        2067.0,
        2068.0,
        2069.0,
        2070.0,
    ],
    [
        1.41,
        1.38,
        1.35,
        1.32,
        1.29,
        1.27,
        1.24,
        1.21,
        1.18,
        1.15,
        1.14,
        1.13,
        1.1,
        1.07,
        1.06,
        1.05,
        1.05,
        1.05,
        1.03,
        1.01,
        1.0,
        1.0,
        0.97,
        0.89,
        0.85,
        0.81,
        0.8,
        0.78,
        0.77,
        0.75,
        0.74,
        0.72,
        0.71,
        0.69,
        0.68,
        0.67,
        0.65,
        0.64,
        0.63,
        0.62,
        0.6,
        0.59,
        0.58,
        0.57,
        0.56,
        0.55,
        0.54,
        0.53,
        0.51,
        0.5,
        0.49,
        0.49,
        0.48,
        0.47,
        0.46,
        0.45,
        0.44,
        0.43,
        0.42,
        0.41,
        0.41,
        0.4,
        0.39,
        0.38,
        0.38,
        0.37,
        0.36,
        0.35,
        0.35,
        0.34,
        0.33,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_inflation_lookup",
)


@component.add(
    name="INTEREST RATE", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def interest_rate():
    """
    Derisked discount rate.
    """
    return 0.0548


@component.add(
    name="INTERSEC DECOM", units="unitless", comp_type="Constant", comp_subtype="Normal"
)
def intersec_decom():
    return 1.5


@component.add(name="k i", comp_type="Constant", comp_subtype="Normal")
def k_i():
    return 0.2 / 3


@component.add(name="k p", comp_type="Constant", comp_subtype="Normal")
def k_p():
    return 2


@component.add(
    name="MODEL SEED",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "seed": 1},
)
def model_seed():
    return time() * seed()


@component.add(
    name="OIL PRICE",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "oil_price_lookup": 1},
)
def oil_price():
    """
    €/GJ
    """
    return oil_price_lookup(time())


@component.add(
    name="OIL PRICE INIT",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_oil_price_init": 1},
    other_deps={"_initial_oil_price_init": {"initial": {"oil_price": 1}, "step": {}}},
)
def oil_price_init():
    return _initial_oil_price_init()


_initial_oil_price_init = Initial(lambda: oil_price(), "_initial_oil_price_init")


@component.add(
    name="OIL PRICE LOOKUP",
    units="€/GJ",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_oil_price_lookup"},
)
def oil_price_lookup(x, final_subs=None):
    return _hardcodedlookup_oil_price_lookup(x, final_subs)


_hardcodedlookup_oil_price_lookup = HardcodedLookups(
    [2019.0, 2030.0, 2040.0, 2050.0],
    [11.3, 14.3, 16.2, 20.2],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_oil_price_lookup",
)


@component.add(
    name="RENEWABLE ELECTRICITY PRICE",
    units="€/MWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "electricity_price_lookup": 1, "electricity_sensitivity": 1},
)
def renewable_electricity_price():
    return electricity_price_lookup(time()) * electricity_sensitivity()


@component.add(name="SEED", comp_type="Constant", comp_subtype="Normal")
def seed():
    return 40


@component.add(name="SLOPE", units="Dmnl", comp_type="Constant", comp_subtype="Normal")
def slope():
    """
    Tuned hyperparameter through model validation/calibration.
    """
    return 10


@component.add(
    name="SLOPE DECOM", units="unitless", comp_type="Constant", comp_subtype="Normal"
)
def slope_decom():
    return 10


@component.add(
    name="SYSTEM NOISE", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def system_noise():
    """
    Standard deviation in percent of flow rate with which each state is changing.
    """
    return 0.03


@component.add(name="USD to EUR", comp_type="Constant", comp_subtype="Unchangeable")
def usd_to_eur():
    """
    https://www.google.com/finance/quote/USD-EUR?sa=X&sqi=2&ved=2ahUKEwjLjIbOkrCGAxUz3wIH HdJaCOAQmY0JegQIJBAw Exchange rate 28/05-2024
    """
    return 0.92
