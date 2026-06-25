"""
Module biomass_usage_summary
Translated using PySD version 3.14.3
"""

@component.add(
    name="biomass availability",
    units="GWh Biomass",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biomass_availability():
    """
    18350 PJ of biomass available in 2030. Hazardous wood waste not included. Source: S2Biom SEAMAPS also has numbers on this. 18.35 EJ is not a high availability limit compared to their estimates (LB: 30 EJ, UB: 90 EJ). Remaining question is, how much of this is currently utilized elsewhere? Probably most.
    """
    return 18350 / 3600 * 10**6


@component.add(
    name="biomass demand saturation",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biomass_used": 1, "biomass_availability": 1},
)
def biomass_demand_saturation():
    return biomass_used() / biomass_availability()


@component.add(
    name="biomass price scaler",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"biomass_demand_saturation": 1},
)
def biomass_price_scaler():
    return np.interp(
        biomass_demand_saturation(),
        [0.0, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 2.0],
        [1.0, 1.0, 1.1, 1.3, 1.6, 2.2, 3.0, 10.0, 20.0, 100.0],
    )


@component.add(
    name="biomass used",
    units="GWh Biomass",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_shipping_biomass_demand": 1,
        "international_shipping_biomass_demand": 1,
        "domestic_aviation_biomass_demand": 1,
        "international_aviation_biomass_demand": 1,
        "high_temperature_biomass_demand": 1,
        "naphtha_biomass_demand": 1,
        "meoh_biomass_demand": 1,
    },
)
def biomass_used():
    return (
        domestic_shipping_biomass_demand()
        + international_shipping_biomass_demand()
        + domestic_aviation_biomass_demand()
        + international_aviation_biomass_demand()
        + high_temperature_biomass_demand()
        + naphtha_biomass_demand()
        + meoh_biomass_demand()
    )
