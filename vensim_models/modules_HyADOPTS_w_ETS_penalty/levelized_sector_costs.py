"""
Module levelized_sector_costs
Translated using PySD version 3.14.3
"""

@component.add(
    name="domestic aviation cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_aviation_average_cost": 1,
        "domestic_aviation_cost_indexer": 1,
    },
)
def domestic_aviation_cost_index():
    return domestic_aviation_average_cost() / domestic_aviation_cost_indexer()


@component.add(
    name="domestic aviation cost indexer",
    units="€/GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_domestic_aviation_cost_indexer": 1},
    other_deps={
        "_initial_domestic_aviation_cost_indexer": {
            "initial": {"domestic_aviation_average_cost": 1},
            "step": {},
        }
    },
)
def domestic_aviation_cost_indexer():
    return _initial_domestic_aviation_cost_indexer()


_initial_domestic_aviation_cost_indexer = Initial(
    lambda: domestic_aviation_average_cost(), "_initial_domestic_aviation_cost_indexer"
)


@component.add(
    name="domestic shipping cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_shipping_average_cost": 1,
        "domestic_shipping_cost_indexer": 1,
    },
)
def domestic_shipping_cost_index():
    return domestic_shipping_average_cost() / domestic_shipping_cost_indexer()


@component.add(
    name="domestic shipping cost indexer",
    units="€/GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_domestic_shipping_cost_indexer": 1},
    other_deps={
        "_initial_domestic_shipping_cost_indexer": {
            "initial": {"domestic_shipping_average_cost": 1},
            "step": {},
        }
    },
)
def domestic_shipping_cost_indexer():
    return _initial_domestic_shipping_cost_indexer()


_initial_domestic_shipping_cost_indexer = Initial(
    lambda: domestic_shipping_average_cost(), "_initial_domestic_shipping_cost_indexer"
)


@component.add(
    name="fertilizer cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fertilizer_average_cost": 1, "fertilizer_cost_indexer": 1},
)
def fertilizer_cost_index():
    return fertilizer_average_cost() / fertilizer_cost_indexer()


@component.add(
    name="fertilizer cost indexer",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_fertilizer_cost_indexer": 1},
    other_deps={
        "_initial_fertilizer_cost_indexer": {
            "initial": {"fertilizer_average_cost": 1},
            "step": {},
        }
    },
)
def fertilizer_cost_indexer():
    return _initial_fertilizer_cost_indexer()


_initial_fertilizer_cost_indexer = Initial(
    lambda: fertilizer_average_cost(), "_initial_fertilizer_cost_indexer"
)


@component.add(
    name="HD cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_average_cost": 1, "hd_cost_indexer": 1},
)
def hd_cost_index():
    return hd_average_cost() / hd_cost_indexer()


@component.add(
    name="HD cost indexer",
    units="€/GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_hd_cost_indexer": 1},
    other_deps={
        "_initial_hd_cost_indexer": {"initial": {"hd_average_cost": 1}, "step": {}}
    },
)
def hd_cost_indexer():
    return _initial_hd_cost_indexer()


_initial_hd_cost_indexer = Initial(
    lambda: hd_average_cost(), "_initial_hd_cost_indexer"
)


@component.add(
    name="high temperature cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"high_temperature_average_cost": 1, "high_temperature_cost_indexer": 1},
)
def high_temperature_cost_index():
    return high_temperature_average_cost() / high_temperature_cost_indexer()


@component.add(
    name="high temperature cost indexer",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_high_temperature_cost_indexer": 1},
    other_deps={
        "_initial_high_temperature_cost_indexer": {
            "initial": {"high_temperature_average_cost": 1},
            "step": {},
        }
    },
)
def high_temperature_cost_indexer():
    return _initial_high_temperature_cost_indexer()


_initial_high_temperature_cost_indexer = Initial(
    lambda: high_temperature_average_cost(), "_initial_high_temperature_cost_indexer"
)


@component.add(
    name="international aviation cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "international_aviation_average_cost": 1,
        "international_aviation_cost_indexer": 1,
    },
)
def international_aviation_cost_index():
    return international_aviation_average_cost() / international_aviation_cost_indexer()


@component.add(
    name="international aviation cost indexer",
    units="€/GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_international_aviation_cost_indexer": 1},
    other_deps={
        "_initial_international_aviation_cost_indexer": {
            "initial": {"international_aviation_average_cost": 1},
            "step": {},
        }
    },
)
def international_aviation_cost_indexer():
    return _initial_international_aviation_cost_indexer()


_initial_international_aviation_cost_indexer = Initial(
    lambda: international_aviation_average_cost(),
    "_initial_international_aviation_cost_indexer",
)


@component.add(
    name="international shipping cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "international_shipping_average_cost": 1,
        "international_shipping_cost_indexer": 1,
    },
)
def international_shipping_cost_index():
    return international_shipping_average_cost() / international_shipping_cost_indexer()


@component.add(
    name="international shipping cost indexer",
    units="€/GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_international_shipping_cost_indexer": 1},
    other_deps={
        "_initial_international_shipping_cost_indexer": {
            "initial": {"international_shipping_average_cost": 1},
            "step": {},
        }
    },
)
def international_shipping_cost_indexer():
    return _initial_international_shipping_cost_indexer()


_initial_international_shipping_cost_indexer = Initial(
    lambda: international_shipping_average_cost(),
    "_initial_international_shipping_cost_indexer",
)


@component.add(
    name="LD cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_average_cost": 1, "ld_cost_indexer": 1},
)
def ld_cost_index():
    return ld_average_cost() / ld_cost_indexer()


@component.add(
    name="LD cost indexer",
    units="€/GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_ld_cost_indexer": 1},
    other_deps={
        "_initial_ld_cost_indexer": {"initial": {"ld_average_cost": 1}, "step": {}}
    },
)
def ld_cost_indexer():
    return _initial_ld_cost_indexer()


_initial_ld_cost_indexer = Initial(
    lambda: ld_average_cost(), "_initial_ld_cost_indexer"
)


@component.add(
    name="MeOH cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"meoh_average_cost": 1, "meoh_cost_indexer": 1},
)
def meoh_cost_index():
    return meoh_average_cost() / meoh_cost_indexer()


@component.add(
    name="MeOH cost indexer",
    units="€/GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_meoh_cost_indexer": 1},
    other_deps={
        "_initial_meoh_cost_indexer": {"initial": {"meoh_average_cost": 1}, "step": {}}
    },
)
def meoh_cost_indexer():
    return _initial_meoh_cost_indexer()


_initial_meoh_cost_indexer = Initial(
    lambda: meoh_average_cost(), "_initial_meoh_cost_indexer"
)


@component.add(
    name="naphtha cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"naphtha_average_cost": 1, "naphtha_cost_indexer": 1},
)
def naphtha_cost_index():
    return naphtha_average_cost() / naphtha_cost_indexer()


@component.add(
    name="naphtha cost indexer",
    units="€/GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_naphtha_cost_indexer": 1},
    other_deps={
        "_initial_naphtha_cost_indexer": {
            "initial": {"naphtha_average_cost": 1},
            "step": {},
        }
    },
)
def naphtha_cost_indexer():
    return _initial_naphtha_cost_indexer()


_initial_naphtha_cost_indexer = Initial(
    lambda: naphtha_average_cost(), "_initial_naphtha_cost_indexer"
)


@component.add(
    name="refinery cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"refinery_average_cost": 1, "refinery_cost_indexer": 1},
)
def refinery_cost_index():
    return refinery_average_cost() / refinery_cost_indexer()


@component.add(
    name="refinery cost indexer",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_refinery_cost_indexer": 1},
    other_deps={
        "_initial_refinery_cost_indexer": {
            "initial": {"refinery_average_cost": 1},
            "step": {},
        }
    },
)
def refinery_cost_indexer():
    return _initial_refinery_cost_indexer()


_initial_refinery_cost_indexer = Initial(
    lambda: refinery_average_cost(), "_initial_refinery_cost_indexer"
)


@component.add(
    name="steel cost index",
    units="index",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_average_cost": 1, "steel_cost_indexer": 1},
)
def steel_cost_index():
    return steel_average_cost() / steel_cost_indexer()


@component.add(
    name="steel cost indexer",
    units="€/tsteel",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_steel_cost_indexer": 1},
    other_deps={
        "_initial_steel_cost_indexer": {
            "initial": {"steel_average_cost": 1},
            "step": {},
        }
    },
)
def steel_cost_indexer():
    return _initial_steel_cost_indexer()


_initial_steel_cost_indexer = Initial(
    lambda: steel_average_cost(), "_initial_steel_cost_indexer"
)
