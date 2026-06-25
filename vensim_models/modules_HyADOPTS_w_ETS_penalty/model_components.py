"""
Module model_components
Translated using PySD version 3.14.3
"""

@component.add(
    name="Activity Change",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"activity_projection": 1},
)
def activity_change():
    return 0 * activity_projection()


@component.add(name="Activity Projection", comp_type="Constant", comp_subtype="Normal")
def activity_projection():
    return 0


@component.add(name="Alternative costs", comp_type="Constant", comp_subtype="Normal")
def alternative_costs():
    return 1


@component.add(name="Alternative levels", comp_type="Constant", comp_subtype="Normal")
def alternative_levels():
    return 0


@component.add(
    name="biomass demand",
    units="GWh Biomass",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technology_activity_levels": 1},
)
def biomass_demand():
    """
    Convert from GWh MeOH to GWh biomass
    """
    return technology_activity_levels()


@component.add(name='"Decom- missioning"', comp_type="Constant", comp_subtype="Normal")
def decom_missioning():
    return 0


@component.add(
    name="Green Hydrogen Cost",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_green_hydrogen_cost": 1},
    other_deps={
        "_delay_green_hydrogen_cost": {
            "initial": {"installed_electrolysis": 1},
            "step": {"installed_electrolysis": 1},
        },
        "_integ_green_hydrogen_cost": {
            "initial": {},
            "step": {"_delay_green_hydrogen_cost": 1},
        },
    },
)
def green_hydrogen_cost():
    return _integ_green_hydrogen_cost()


_delay_green_hydrogen_cost = Delay(
    lambda: installed_electrolysis(),
    lambda: 1,
    lambda: installed_electrolysis(),
    lambda: 1,
    time_step,
    "_delay_green_hydrogen_cost",
)

_integ_green_hydrogen_cost = Integ(
    lambda: _delay_green_hydrogen_cost(), lambda: 0, "_integ_green_hydrogen_cost"
)


@component.add(
    name="Installed Electrolysis",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sectoral_green_h2_demands": 1},
)
def installed_electrolysis():
    return sectoral_green_h2_demands()


@component.add(
    name='"Invest- ments"',
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "technology_cost_1": 1,
        "technology_1_cost": 1,
        "technology_n_cost": 1,
        "technology_activity_levels": 1,
    },
)
def invest_ments():
    return (
        technology_cost_1()
        * technology_1_cost()
        * 0
        * technology_n_cost()
        * technology_activity_levels()
    )


@component.add(
    name="Investment Pipeline",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_investment_pipeline": 1},
    other_deps={
        "_integ_investment_pipeline": {
            "initial": {},
            "step": {"activity_change": 1, "decom_missioning": 1, "invest_ments": 1},
        }
    },
)
def investment_pipeline():
    return _integ_investment_pipeline()


_integ_investment_pipeline = Integ(
    lambda: activity_change() + decom_missioning() - invest_ments(),
    lambda: 0,
    "_integ_investment_pipeline",
)


@component.add(
    name="Learning Curves",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sectoral_hydrogen_demand": 1},
)
def learning_curves():
    return sectoral_hydrogen_demand() * 0


@component.add(
    name="sector emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technology_activity_levels": 1},
)
def sector_emissions():
    return technology_activity_levels()


@component.add(
    name="Sector Investment Pipeline", comp_type="Constant", comp_subtype="Normal"
)
def sector_investment_pipeline():
    return 1


@component.add(
    name="Sectoral Green H2 Demands",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sectoral_h2_investments": 1},
)
def sectoral_green_h2_demands():
    return sectoral_h2_investments()


@component.add(
    name="Sectoral H2 Competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_hydrogen_cost": 1},
)
def sectoral_h2_competitiveness():
    return green_hydrogen_cost()


@component.add(
    name="Sectoral H2 Investments",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sectoral_h2_competitiveness": 1},
)
def sectoral_h2_investments():
    return sectoral_h2_competitiveness()


@component.add(
    name="Sectoral Hydrogen Demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technology_activity_levels": 1},
)
def sectoral_hydrogen_demand():
    """
    Get this from Balmorel or have a range of possible scenarios?
    """
    return technology_activity_levels()


@component.add(
    name="Sum of sector levels",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"alternative_levels": 1, "technology_level": 1},
)
def sum_of_sector_levels():
    return alternative_levels() + technology_level()


@component.add(name='"Techno-economics"', comp_type="Constant", comp_subtype="Normal")
def technoeconomics():
    return 1


@component.add(
    name="Technology 1 cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technoeconomics": 1},
)
def technology_1_cost():
    return technoeconomics()


@component.add(
    name="Technology Activity Levels",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_technology_activity_levels": 1},
    other_deps={
        "_integ_technology_activity_levels": {
            "initial": {},
            "step": {"invest_ments": 1, "decom_missioning": 1},
        }
    },
)
def technology_activity_levels():
    return _integ_technology_activity_levels()


_integ_technology_activity_levels = Integ(
    lambda: invest_ments() + decom_missioning(),
    lambda: 0,
    "_integ_technology_activity_levels",
)


@component.add(
    name="Technology Commissioning",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technology_construction": 1, "tehnology_construction_time": 1},
)
def technology_commissioning():
    return technology_construction() / tehnology_construction_time()


@component.add(
    name="Technology Competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"alternative_costs": 1, "technology_cost": 1},
)
def technology_competitiveness():
    """
    MIN( Blue H2 cost / refinery H2 cost , Grey H2 cost / refinery H2 cost )
    """
    return alternative_costs() / technology_cost()


@component.add(
    name="Technology Construction",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_technology_construction": 1},
    other_deps={
        "_integ_technology_construction": {
            "initial": {},
            "step": {
                "technology_innovators": 1,
                "technology_investment": 1,
                "technology_commissioning": 1,
            },
        }
    },
)
def technology_construction():
    return _integ_technology_construction()


_integ_technology_construction = Integ(
    lambda: technology_innovators()
    + technology_investment()
    - technology_commissioning(),
    lambda: 0,
    "_integ_technology_construction",
)


@component.add(name="Technology cost", comp_type="Constant", comp_subtype="Normal")
def technology_cost():
    return 1


@component.add(
    name='"Technology .. cost"',
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technoeconomics": 1},
)
def technology_cost_1():
    return technoeconomics()


@component.add(
    name="Technology Decommissioning",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technology_stock": 1, "technology_lifetime": 1},
)
def technology_decommissioning():
    return technology_stock() / technology_lifetime()


@component.add(
    name="Technology Early Decommissioning",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technology_competitiveness": 1, "technology_stock": 1},
)
def technology_early_decommissioning():
    return if_then_else(
        technology_competitiveness() < 0.5, lambda: technology_stock() * 0.1, lambda: 0
    )


@component.add(
    name="Technology innovator share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technology_competitiveness": 1},
)
def technology_innovator_share():
    return if_then_else(technology_competitiveness() > 0.5, lambda: 1, lambda: 0)


@component.add(
    name="Technology Innovators",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sector_investment_pipeline": 1, "technology_innovator_share": 1},
)
def technology_innovators():
    return sector_investment_pipeline() * technology_innovator_share() * 0.05


@component.add(
    name="Technology Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"sector_investment_pipeline": 1, "technology_investment_share": 1},
)
def technology_investment():
    return sector_investment_pipeline() * technology_investment_share() * 0.95


@component.add(
    name="Technology investment share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technology_level": 1, "sum_of_sector_levels": 1},
)
def technology_investment_share():
    return technology_level() / sum_of_sector_levels()


@component.add(
    name="Technology level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technology_competitiveness": 2, "technology_sector_share": 1},
)
def technology_level():
    return (
        1
        / (1 + float(np.exp(10 * (1 - technology_competitiveness()))))
        * float(np.maximum(0.1, technology_sector_share()))
        + technology_competitiveness() * 0.001
    )


@component.add(name="Technology Lifetime", comp_type="Constant", comp_subtype="Normal")
def technology_lifetime():
    return 1


@component.add(
    name="Technology N cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"technoeconomics": 1},
)
def technology_n_cost():
    return technoeconomics()


@component.add(
    name="Technology sector share", comp_type="Constant", comp_subtype="Normal"
)
def technology_sector_share():
    return 1


@component.add(
    name="Technology Stock",
    units="MT H2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_technology_stock": 1},
    other_deps={
        "_integ_technology_stock": {
            "initial": {},
            "step": {
                "technology_commissioning": 1,
                "technology_decommissioning": 1,
                "technology_early_decommissioning": 1,
            },
        }
    },
)
def technology_stock():
    return _integ_technology_stock()


_integ_technology_stock = Integ(
    lambda: technology_commissioning()
    - technology_decommissioning()
    - technology_early_decommissioning(),
    lambda: 0,
    "_integ_technology_stock",
)


@component.add(
    name="Tehnology Construction Time", comp_type="Constant", comp_subtype="Normal"
)
def tehnology_construction_time():
    return 1
