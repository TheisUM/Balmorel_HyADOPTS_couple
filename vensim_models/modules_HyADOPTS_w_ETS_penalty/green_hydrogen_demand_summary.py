"""
Module green_hydrogen_demand_summary
Translated using PySD version 3.14.3
"""

@component.add(
    name="all hydrogen",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grey_hydrogen_twh": 1, "total_twh": 1, "blue_hydrogen_twh": 1},
)
def all_hydrogen():
    return grey_hydrogen_twh() + total_twh() + blue_hydrogen_twh()


@component.add(
    name="BioKero DA H2 WTP gap",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_h2_wtp_gap": 1},
)
def biokero_da_h2_wtp_gap():
    return biokero_h2_wtp_gap()


@component.add(
    name="BioKero H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "biokero_h2_wtp": 1},
)
def biokero_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - biokero_h2_wtp()


@component.add(
    name="BioKero hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_aviation_biokero_hydrogen_demand": 1,
        "international_aviation_biokero_hydrogen_demand": 1,
    },
)
def biokero_hydrogen_demand():
    return (
        domestic_aviation_biokero_hydrogen_demand()
        + international_aviation_biokero_hydrogen_demand()
    )


@component.add(
    name="BioKero IA H2 WTP gap",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biokero_h2_wtp_gap": 1},
)
def biokero_ia_h2_wtp_gap():
    return biokero_h2_wtp_gap()


@component.add(
    name="BioMeOH H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "biomeoh_h2_wtp": 1},
)
def biomeoh_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - biomeoh_h2_wtp()


@component.add(
    name="BioNaphtha H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "bionaphtha_h2_wtp": 1},
)
def bionaphtha_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - bionaphtha_h2_wtp()


@component.add(
    name="blue hydrogen TWH",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2_lhv": 1,
        "fertilizer_blue_hydrogen_demand": 1,
        "refinery_blue_hydrogen_demand": 1,
    },
)
def blue_hydrogen_twh():
    return (
        h2_lhv()
        * (fertilizer_blue_hydrogen_demand() + refinery_blue_hydrogen_demand())
        / 10**6
    )


@component.add(
    name="BUILDINGS TWH",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_lhv": 1, "buildings_hydrogen_demand": 1},
)
def buildings_twh():
    return h2_lhv() * buildings_hydrogen_demand() / 10**6


@component.add(
    name="eMeOH H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "emeoh_h2_wtp": 1},
)
def emeoh_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - emeoh_h2_wtp()


@component.add(
    name="Green NH3 H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "fertilizer_h2_wtp": 1},
)
def green_nh3_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - fertilizer_h2_wtp()


@component.add(
    name="Green Refinery H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "refinery_h2_wtp": 1},
)
def green_refinery_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - refinery_h2_wtp()


@component.add(
    name="grey hydrogen TWH",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2_lhv": 1,
        "fertilizer_grey_hydrogen_demand": 1,
        "refinery_grey_hydrogen_demand": 1,
    },
)
def grey_hydrogen_twh():
    return (
        h2_lhv()
        * (fertilizer_grey_hydrogen_demand() + refinery_grey_hydrogen_demand())
        / 10**6
    )


@component.add(
    name="H2 NM H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "high_temperature_h2_wtp": 1},
)
def h2_nm_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - high_temperature_h2_wtp()


@component.add(
    name="H2DRI EAF H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "steel_h2_wtp": 1},
)
def h2dri_eaf_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - steel_h2_wtp()


@component.add(
    name="H2FC DS H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "fc_ship_h2_wtp": 1},
)
def h2fc_ds_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - fc_ship_h2_wtp()


@component.add(
    name="HD FCEV H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "hd_h2_wtp": 1},
)
def hd_fcev_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - hd_h2_wtp()


@component.add(
    name="industry hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_hydrogen_demand": 1,
        "naphtha_hydrogen_demand": 1,
        "high_temperature_hydrogen_demand": 1,
        "refinery_hydrogen_demand": 1,
        "steel_hydrogen_demand": 1,
        "meoh_hydrogen_demand": 1,
    },
)
def industry_hydrogen_demand():
    return (
        fertilizer_hydrogen_demand()
        + naphtha_hydrogen_demand()
        + high_temperature_hydrogen_demand()
        + refinery_hydrogen_demand()
        + steel_hydrogen_demand()
        + meoh_hydrogen_demand()
    )


@component.add(
    name="INDUSTRY TWH",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_lhv": 1, "industry_hydrogen_demand": 1},
)
def industry_twh():
    return h2_lhv() * industry_hydrogen_demand() / 10**6


@component.add(
    name="LD FCEV H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "ld_h2_wtp": 1},
)
def ld_fcev_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - ld_h2_wtp()


@component.add(
    name="MeOH DS H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "meoh_ship_h2_wtp": 1},
)
def meoh_ds_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - meoh_ship_h2_wtp()


@component.add(
    name="MeOH IS H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "meoh_containership_h2_wtp": 1},
)
def meoh_is_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - meoh_containership_h2_wtp()


@component.add(
    name="NH3 IS H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "nh3_containership_h2_wtp": 1},
)
def nh3_is_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - nh3_containership_h2_wtp()


@component.add(
    name="POWER TWH",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_lhv": 1, "power_hydrogen_demand": 1},
)
def power_twh():
    return h2_lhv() * power_hydrogen_demand() / 10**6


@component.add(
    name="SCOPE TWH",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"industry_twh": 1, "transportation_twh": 1},
)
def scope_twh():
    return industry_twh() + transportation_twh()


@component.add(
    name="shipping MeOH hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_shipping_meoh_hydrogen_demand": 1,
        "international_shipping_meoh_hydrogen_demand": 1,
    },
)
def shipping_meoh_hydrogen_demand():
    return (
        domestic_shipping_meoh_hydrogen_demand()
        + international_shipping_meoh_hydrogen_demand()
    )


@component.add(
    name="SynKero DA H2 WTP gap",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_h2_wtp_gap": 1},
)
def synkero_da_h2_wtp_gap():
    return synkero_h2_wtp_gap()


@component.add(
    name="SynKero H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "synkero_h2_wtp": 1},
)
def synkero_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - synkero_h2_wtp()


@component.add(
    name="SynKero hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_aviation_synkero_hydrogen_demand": 1,
        "international_aviation_synkero_hydrogen_demand": 1,
    },
)
def synkero_hydrogen_demand():
    return (
        domestic_aviation_synkero_hydrogen_demand()
        + international_aviation_synkero_hydrogen_demand()
    )


@component.add(
    name="SynKero IA H2 WTP gap",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synkero_h2_wtp_gap": 1},
)
def synkero_ia_h2_wtp_gap():
    return synkero_h2_wtp_gap()


@component.add(
    name="SynNaphtha H2 WTP gap",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "synnaphtha_h2_wtp": 1},
)
def synnaphtha_h2_wtp_gap():
    return unsubsidized_green_h2_cost() - synnaphtha_h2_wtp()


@component.add(
    name="TOTAL GREEN HYDROGEN DEMAND",
    units="t H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industry_hydrogen_demand": 1,
        "power_hydrogen_demand": 1,
        "transportation_hydrogen_demand": 1,
        "buildings_hydrogen_demand": 1,
    },
)
def total_green_hydrogen_demand():
    return float(
        np.maximum(
            5000,
            industry_hydrogen_demand()
            + power_hydrogen_demand()
            + transportation_hydrogen_demand()
            + buildings_hydrogen_demand(),
        )
    )


@component.add(
    name="TOTAL TWH",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_lhv": 1, "total_green_hydrogen_demand": 1},
)
def total_twh():
    return h2_lhv() * total_green_hydrogen_demand() / 10**6


@component.add(
    name="transportation hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_aviation_hydrogen_demand": 1,
        "domestic_shipping_hydrogen_demand": 1,
        "heavy_duty_hydrogen_demand": 1,
        "international_aviation_hydrogen_demand": 1,
        "international_shipping_hydrogen_demand": 1,
        "light_duty_hydrogen_demand": 1,
    },
)
def transportation_hydrogen_demand():
    return (
        domestic_aviation_hydrogen_demand()
        + domestic_shipping_hydrogen_demand()
        + heavy_duty_hydrogen_demand()
        + international_aviation_hydrogen_demand()
        + international_shipping_hydrogen_demand()
        + light_duty_hydrogen_demand()
    )


@component.add(
    name="TRANSPORTATION TWH",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_lhv": 1, "transportation_hydrogen_demand": 1},
)
def transportation_twh():
    return h2_lhv() * transportation_hydrogen_demand() / 10**6
