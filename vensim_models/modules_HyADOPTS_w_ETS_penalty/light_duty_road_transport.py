"""
Module light_duty_road_transport
Translated using PySD version 3.14.3
"""

@component.add(
    name="car lifetime", units="years", comp_type="Constant", comp_subtype="Normal"
)
def car_lifetime():
    """
    inverse scrappage rate based on Eurostat numbers.
    """
    return 14


@component.add(
    name="car procurement time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def car_procurement_time():
    return 0.5


@component.add(
    name="ICE car ban",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hard_regulation": 1, "time": 1},
)
def ice_car_ban():
    return step(__data["time"], hard_regulation(), 2035)


@component.add(
    name="Initial LD emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_ld_emissions": 1},
    other_deps={
        "_initial_initial_ld_emissions": {
            "initial": {"light_duty_emissions": 1},
            "step": {},
        }
    },
)
def initial_ld_emissions():
    return _initial_initial_ld_emissions()


_initial_initial_ld_emissions = Initial(
    lambda: light_duty_emissions(), "_initial_initial_ld_emissions"
)


@component.add(
    name="LD allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_ld_emissions": 1, "emissions_cap_lookup": 1, "time": 1},
)
def ld_allocated_emissions():
    return initial_ld_emissions() * emissions_cap_lookup(time())


@component.add(
    name="LD average cost",
    units="€/GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_bev_sector_share": 1,
        "ld_be_lco": 1,
        "ld_fc_lco": 1,
        "ld_fcev_sector_share": 1,
        "ld_ice_lco": 1,
        "ld_fossil_sector_share": 1,
        "diesel_lhv": 1,
        "ld_ice_energy_usage": 1,
    },
)
def ld_average_cost():
    """
    €/GWh of diesel equivalent. (Total car ownership costs). Unit check: GWh * €/km * km/kWh * 10^6 kWh/GWh = € -> €/GWh
    """
    return (
        (
            ld_bev_sector_share() * ld_be_lco()
            + ld_fcev_sector_share() * ld_fc_lco()
            + ld_fossil_sector_share() * ld_ice_lco()
        )
        / (ld_ice_energy_usage() * diesel_lhv())
        * 10**6
    )


@component.add(
    name="LD backlog",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ld_backlog": 1},
    other_deps={
        "_integ_ld_backlog": {
            "initial": {"sum_ld_activity": 1},
            "step": {"ld_current_demand": 1, "sum_ld_activity": 1},
        }
    },
)
def ld_backlog():
    return _integ_ld_backlog()


_integ_ld_backlog = Integ(
    lambda: ld_current_demand() - sum_ld_activity(),
    lambda: sum_ld_activity() * 0.015 * 0.5,
    "_integ_ld_backlog",
)


@component.add(
    name="LD BEV",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ld_bev": 1},
    other_deps={
        "_integ_ld_bev": {
            "initial": {"ld_initial_sector_activity": 1},
            "step": {"ld_bev_commissioning": 1, "ld_bev_decommissioning": 1},
        }
    },
)
def ld_bev():
    return _integ_ld_bev()


_integ_ld_bev = Integ(
    lambda: ld_bev_commissioning() - ld_bev_decommissioning(),
    lambda: ld_initial_sector_activity() * 0.014,
    "_integ_ld_bev",
)


@component.add(
    name="LD BEV Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_bev_construction": 1, "car_procurement_time": 1},
)
def ld_bev_commissioning():
    return ld_bev_construction() / car_procurement_time()


@component.add(
    name="LD BEV competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_ice_lco": 1, "ld_be_lco": 2, "ld_fc_lco": 1},
)
def ld_bev_competitiveness():
    return float(np.minimum(ld_ice_lco() / ld_be_lco(), ld_fc_lco() / ld_be_lco()))


@component.add(
    name="LD BEV Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ld_bev_construction": 1},
    other_deps={
        "_integ_ld_bev_construction": {
            "initial": {},
            "step": {
                "ld_bev_innovators": 1,
                "ld_bev_investment": 1,
                "ld_bev_commissioning": 1,
            },
        }
    },
)
def ld_bev_construction():
    return _integ_ld_bev_construction()


_integ_ld_bev_construction = Integ(
    lambda: ld_bev_innovators() + ld_bev_investment() - ld_bev_commissioning(),
    lambda: 0,
    "_integ_ld_bev_construction",
)


@component.add(
    name="LD BEV Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_bev": 1, "car_lifetime": 1},
)
def ld_bev_decommissioning():
    return ld_bev() / car_lifetime()


@component.add(
    name="LD BEV emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_bev": 1,
        "ld_ice_efficiency": 1,
        "charging_efficiency": 1,
        "ld_ev_efficiency": 1,
        "electricity_emission_factor": 1,
    },
)
def ld_bev_emissions():
    return (
        ld_bev()
        * ld_ice_efficiency()
        / (charging_efficiency() * ld_ev_efficiency())
        * electricity_emission_factor()
        * 1000
    )


@component.add(
    name="LD BEV inno switch",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_bev_competitiveness": 1, "inno_switch_level": 1},
)
def ld_bev_inno_switch():
    return if_then_else(
        ld_bev_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="LD BEV innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_bev_inno_switch": 1, "ld_innovators": 1},
)
def ld_bev_innovator_share():
    return ld_bev_inno_switch() / ld_innovators()


@component.add(
    name="LD BEV Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_innovator_pipeline": 1, "ld_bev_innovator_share": 1},
)
def ld_bev_innovators():
    return ld_innovator_pipeline() * ld_bev_innovator_share()


@component.add(
    name="LD BEV Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_investment_pipeline": 1, "ld_bev_investment_share": 1},
)
def ld_bev_investment():
    return ld_investment_pipeline() * ld_bev_investment_share()


@component.add(
    name="LD BEV investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_equalizer": 1, "ld_bev_level": 1},
)
def ld_bev_investment_share():
    return ld_equalizer() * ld_bev_level()


@component.add(
    name="LD BEV level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "ld_bev_competitiveness": 1, "ld_bev_sector_share": 1},
)
def ld_bev_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - ld_bev_competitiveness()))))
        * float(np.maximum(0.1, ld_bev_sector_share()))
    )


@component.add(
    name="LD BEV sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_bev": 1, "sum_ld_activity": 1},
)
def ld_bev_sector_share():
    return ld_bev() / sum_ld_activity()


@component.add(
    name="LD continuous investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_forecast_demand": 1,
        "sum_ld_decommissioning": 1,
        "ld_backlog": 1,
        "car_procurement_time": 1,
        "sum_ld_activity": 1,
        "innovators": 1,
    },
)
def ld_continuous_investment():
    return float(
        np.maximum(
            (
                ld_forecast_demand()
                + sum_ld_decommissioning()
                + ld_backlog() / car_procurement_time() / 3
                - sum_ld_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="LD current demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_projected_demand": 1},
)
def ld_current_demand():
    return ld_projected_demand()


@component.add(
    name="LD effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_average_cost": 1, "ld_current_demand": 1},
)
def ld_effective_cost():
    return ld_average_cost() * ld_current_demand() / 1000000000.0


@component.add(
    name="LD equalizer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fcev_h2_subsidy": 1,
        "ld_bev_level": 2,
        "ld_fcev_bid_share": 1,
        "ld_fossil_level": 2,
        "ld_fcev_level": 1,
    },
)
def ld_equalizer():
    return if_then_else(
        ld_fcev_h2_subsidy() > 0.01,
        lambda: (1 - ld_fcev_bid_share()) / (ld_bev_level() + ld_fossil_level()),
        lambda: 1 / (ld_fossil_level() + ld_fcev_level() + ld_bev_level()),
    )


@component.add(
    name="LD excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"light_duty_emissions": 1, "ld_allocated_emissions": 1},
)
def ld_excess_emissions():
    return light_duty_emissions() - ld_allocated_emissions()


@component.add(
    name="LD FCEV",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ld_fcev": 1},
    other_deps={
        "_integ_ld_fcev": {
            "initial": {},
            "step": {"ld_fcev_commissioning": 1, "ld_fcev_decommissioning": 1},
        }
    },
)
def ld_fcev():
    return _integ_ld_fcev()


_integ_ld_fcev = Integ(
    lambda: ld_fcev_commissioning() - ld_fcev_decommissioning(),
    lambda: 0,
    "_integ_ld_fcev",
)


@component.add(
    name="LD FCEV bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fcev_desired_investment": 1},
)
def ld_fcev_bid_share():
    return ld_fcev_desired_investment()


@component.add(
    name="LD FCEV Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fcev_construction": 1, "car_procurement_time": 1},
)
def ld_fcev_commissioning():
    return ld_fcev_construction() / car_procurement_time()


@component.add(
    name="LD FCEV Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_ld_fcev_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_ld_fcev_commissioning_subsidy_level": {
            "initial": {"car_procurement_time": 1},
            "step": {"ld_fcev_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def ld_fcev_commissioning_subsidy_level():
    return _delayfixed_ld_fcev_commissioning_subsidy_level()


_delayfixed_ld_fcev_commissioning_subsidy_level = DelayFixed(
    lambda: ld_fcev_h2_subsidy() + green_h2_subsidy(),
    lambda: car_procurement_time(),
    lambda: 0,
    time_step,
    "_delayfixed_ld_fcev_commissioning_subsidy_level",
)


@component.add(
    name="LD FCEV competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_be_lco": 1, "ld_fc_lco": 2, "ld_ice_lco": 1},
)
def ld_fcev_competitiveness():
    return float(np.minimum(ld_be_lco() / ld_fc_lco(), ld_ice_lco() / ld_fc_lco()))


@component.add(
    name="LD FCEV Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ld_fcev_construction": 1},
    other_deps={
        "_integ_ld_fcev_construction": {
            "initial": {},
            "step": {
                "ld_fcev_innovators": 1,
                "ld_fcev_investment": 1,
                "ld_fcev_commissioning": 1,
            },
        }
    },
)
def ld_fcev_construction():
    return _integ_ld_fcev_construction()


_integ_ld_fcev_construction = Integ(
    lambda: ld_fcev_innovators() + ld_fcev_investment() - ld_fcev_commissioning(),
    lambda: 0,
    "_integ_ld_fcev_construction",
)


@component.add(
    name="LD FCEV Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fcev": 1, "car_lifetime": 1},
)
def ld_fcev_decommissioning():
    return ld_fcev() / car_lifetime()


@component.add(
    name="LD FCEV Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_ld_fcev_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_ld_fcev_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"ld_fcev_commissioning_subsidy_level": 1},
        }
    },
)
def ld_fcev_decommissioning_subsidy_level():
    return _delayfixed_ld_fcev_decommissioning_subsidy_level()


_delayfixed_ld_fcev_decommissioning_subsidy_level = DelayFixed(
    lambda: ld_fcev_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_ld_fcev_decommissioning_subsidy_level",
)


@component.add(
    name="LD FCEV desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_ld_fcev_desired_investment": 1},
    other_deps={
        "_smooth_ld_fcev_desired_investment": {
            "initial": {"ld_fcev_level": 2, "ld_bev_level": 1, "ld_fossil_level": 1},
            "step": {"ld_fcev_level": 2, "ld_bev_level": 1, "ld_fossil_level": 1},
        }
    },
)
def ld_fcev_desired_investment():
    return _smooth_ld_fcev_desired_investment()


_smooth_ld_fcev_desired_investment = Smooth(
    lambda: ld_fcev_level() / (ld_bev_level() + ld_fcev_level() + ld_fossil_level()),
    lambda: 2,
    lambda: ld_fcev_level() / (ld_bev_level() + ld_fcev_level() + ld_fossil_level()),
    lambda: 1,
    "_smooth_ld_fcev_desired_investment",
)


@component.add(
    name="LD FCEV HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_continuous_investment": 1,
        "ld_ice_efficiency": 1,
        "ld_fcev_efficiency": 1,
        "h2_lhv": 1,
        "ld_fcev_bid_share": 1,
    },
)
def ld_fcev_hba_volume():
    return (
        ld_continuous_investment()
        * ld_ice_efficiency()
        / ld_fcev_efficiency()
        * 1000
        / h2_lhv()
        * ld_fcev_bid_share()
    )


@component.add(
    name="LD FCEV inno switch",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fcev_competitiveness": 1, "inno_switch_level": 1},
)
def ld_fcev_inno_switch():
    return if_then_else(
        ld_fcev_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="LD FCEV innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fcev_inno_switch": 1, "ld_innovators": 1},
)
def ld_fcev_innovator_share():
    return ld_fcev_inno_switch() / ld_innovators()


@component.add(
    name="LD FCEV Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_innovator_pipeline": 1, "ld_fcev_innovator_share": 1},
)
def ld_fcev_innovators():
    return ld_innovator_pipeline() * ld_fcev_innovator_share()


@component.add(
    name="LD FCEV Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_investment_pipeline": 1, "ld_fcev_investment_share": 1},
)
def ld_fcev_investment():
    return ld_investment_pipeline() * ld_fcev_investment_share()


@component.add(
    name="LD FCEV investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fcev_h2_subsidy": 1,
        "ld_fcev_bid_share": 1,
        "ld_fcev_level": 1,
        "ld_equalizer": 1,
    },
)
def ld_fcev_investment_share():
    return if_then_else(
        ld_fcev_h2_subsidy() > 0.01,
        lambda: ld_fcev_bid_share(),
        lambda: ld_equalizer() * ld_fcev_level(),
    )


@component.add(
    name="LD FCEV level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "ld_fcev_competitiveness": 1, "ld_fcev_sector_share": 1},
)
def ld_fcev_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - ld_fcev_competitiveness()))))
        * float(np.maximum(0.1, ld_fcev_sector_share()))
    )


@component.add(
    name="LD FCEV sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fcev": 1, "sum_ld_activity": 1},
)
def ld_fcev_sector_share():
    return ld_fcev() / sum_ld_activity()


@component.add(
    name="LD FCEV subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ld_fcev_subsidy_cost": 1},
    other_deps={
        "_integ_ld_fcev_subsidy_cost": {
            "initial": {},
            "step": {
                "ld_fcev_commissioning_subsidy_level": 1,
                "subsidized_ld_fcev_commissioning": 1,
                "subsidized_ld_fcev_decommissioning": 1,
                "ld_fcev_decommissioning_subsidy_level": 1,
            },
        }
    },
)
def ld_fcev_subsidy_cost():
    return _integ_ld_fcev_subsidy_cost()


_integ_ld_fcev_subsidy_cost = Integ(
    lambda: ld_fcev_commissioning_subsidy_level() * subsidized_ld_fcev_commissioning()
    - ld_fcev_decommissioning_subsidy_level() * subsidized_ld_fcev_decommissioning(),
    lambda: 0,
    "_integ_ld_fcev_subsidy_cost",
)


@component.add(
    name="LD forecast demand",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_ld_forecast_demand": 1},
    other_deps={
        "_forecast_ld_forecast_demand": {
            "initial": {"ld_current_demand": 1},
            "step": {"ld_current_demand": 1, "car_procurement_time": 2},
        }
    },
)
def ld_forecast_demand():
    return _forecast_ld_forecast_demand()


_forecast_ld_forecast_demand = Forecast(
    lambda: ld_current_demand(),
    lambda: 3 * car_procurement_time(),
    lambda: car_procurement_time(),
    lambda: 0,
    "_forecast_ld_forecast_demand",
)


@component.add(
    name="LD Fossil",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ld_fossil": 1},
    other_deps={
        "_integ_ld_fossil": {
            "initial": {"ld_initial_sector_activity": 1},
            "step": {
                "ld_fossil_commissioning": 1,
                "ld_fossil_decommissioning": 1,
                "ld_fossil_early_decommissioning": 1,
                "ld_fossil_economic_decommissioning": 1,
            },
        }
    },
)
def ld_fossil():
    return _integ_ld_fossil()


_integ_ld_fossil = Integ(
    lambda: ld_fossil_commissioning()
    - ld_fossil_decommissioning()
    - ld_fossil_early_decommissioning()
    - ld_fossil_economic_decommissioning(),
    lambda: ld_initial_sector_activity() * 0.986,
    "_integ_ld_fossil",
)


@component.add(
    name="LD Fossil Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fossil_construction": 1, "car_procurement_time": 1},
)
def ld_fossil_commissioning():
    return ld_fossil_construction() / car_procurement_time()


@component.add(
    name="LD Fossil competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_be_lco": 1, "ld_ice_lco": 2, "ld_fc_lco": 1},
)
def ld_fossil_competitiveness():
    return float(np.minimum(ld_be_lco() / ld_ice_lco(), ld_fc_lco() / ld_ice_lco()))


@component.add(
    name="LD Fossil Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ld_fossil_construction": 1},
    other_deps={
        "_integ_ld_fossil_construction": {
            "initial": {
                "ld_initial_sector_activity": 1,
                "car_lifetime": 1,
                "car_procurement_time": 1,
            },
            "step": {"ld_fossil_investment": 1, "ld_fossil_commissioning": 1},
        }
    },
)
def ld_fossil_construction():
    return _integ_ld_fossil_construction()


_integ_ld_fossil_construction = Integ(
    lambda: ld_fossil_investment() - ld_fossil_commissioning(),
    lambda: ld_initial_sector_activity()
    / car_lifetime()
    * car_procurement_time()
    * 1.2,
    "_integ_ld_fossil_construction",
)


@component.add(
    name="LD fossil cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_ice_opex": 1, "ld_be_lco": 1},
)
def ld_fossil_cost_difference():
    return ld_ice_opex() / ld_be_lco()


@component.add(
    name="LD Fossil Decommissioning",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_ld_fossil_decommissioning": 1, "ld_fossil": 1},
    other_deps={
        "_smooth_ld_fossil_decommissioning": {
            "initial": {
                "ld_fossil_delayed": 1,
                "ld_fossil_economic_decommissioning_delayed": 1,
            },
            "step": {
                "ld_fossil_delayed": 1,
                "ld_fossil_economic_decommissioning_delayed": 1,
            },
        }
    },
)
def ld_fossil_decommissioning():
    return float(
        np.maximum(
            0, float(np.minimum(_smooth_ld_fossil_decommissioning(), ld_fossil()))
        )
    )


_smooth_ld_fossil_decommissioning = Smooth(
    lambda: ld_fossil_delayed() - ld_fossil_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: ld_fossil_delayed() - ld_fossil_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_ld_fossil_decommissioning",
)


@component.add(
    name="LD Fossil delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_ld_fossil_delayed": 1},
    other_deps={
        "_delayfixed_ld_fossil_delayed": {
            "initial": {"ld_initial_sector_activity": 1, "car_lifetime": 2},
            "step": {"ld_fossil_commissioning": 1},
        }
    },
)
def ld_fossil_delayed():
    return _delayfixed_ld_fossil_delayed()


_delayfixed_ld_fossil_delayed = DelayFixed(
    lambda: ld_fossil_commissioning(),
    lambda: car_lifetime(),
    lambda: ld_initial_sector_activity() / car_lifetime(),
    time_step,
    "_delayfixed_ld_fossil_delayed",
)


@component.add(
    name="LD Fossil Early Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fossil": 1},
)
def ld_fossil_early_decommissioning():
    return 0 * ld_fossil()


@component.add(
    name="LD fossil economic decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fossil_cost_difference": 2,
        "car_lifetime": 1,
        "ld_fossil": 1,
        "slope_decom": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def ld_fossil_economic_decommissioning():
    return (
        if_then_else(
            ld_fossil_cost_difference() > 1,
            lambda: (ld_fossil() / car_lifetime() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (ld_fossil_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="LD Fossil Economic Decommissioning delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_ld_fossil_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_ld_fossil_economic_decommissioning_delayed": {
            "initial": {},
            "step": {
                "ld_fossil_economic_decommissioning": 1,
                "ld_fossil_early_decommissioning": 1,
            },
        }
    },
)
def ld_fossil_economic_decommissioning_delayed():
    return _delayn_ld_fossil_economic_decommissioning_delayed()


_delayn_ld_fossil_economic_decommissioning_delayed = DelayN(
    lambda: ld_fossil_economic_decommissioning() + ld_fossil_early_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_ld_fossil_economic_decommissioning_delayed",
)


@component.add(
    name="LD Fossil emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fossil": 1, "diesel_emission_factor": 1},
)
def ld_fossil_emissions():
    return ld_fossil() * diesel_emission_factor() * 10**6


@component.add(
    name="LD Fossil Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_investment_pipeline": 1, "ld_fossil_investment_share": 1},
)
def ld_fossil_investment():
    return ld_investment_pipeline() * ld_fossil_investment_share()


@component.add(
    name="LD Fossil investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_equalizer": 1, "ld_fossil_level": 1},
)
def ld_fossil_investment_share():
    return ld_equalizer() * ld_fossil_level()


@component.add(
    name="LD Fossil level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "slope": 1,
        "ld_fossil_competitiveness": 1,
        "ld_fossil_sector_share": 1,
        "ice_car_ban": 1,
    },
)
def ld_fossil_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - ld_fossil_competitiveness()))))
        * float(np.maximum(0.1, ld_fossil_sector_share()))
        * (1 - ice_car_ban())
    )


@component.add(
    name="LD Fossil sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fossil": 1, "sum_ld_activity": 1},
)
def ld_fossil_sector_share():
    return ld_fossil() / sum_ld_activity()


@component.add(
    name="LD H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_ice_lco": 1, "ld_fc_lco_without_h2": 1, "ld_fc_energy_usage": 1},
)
def ld_h2_wtp():
    return (ld_ice_lco() - ld_fc_lco_without_h2()) / ld_fc_energy_usage()


@component.add(
    name="LD ICE efficiency",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ld_ice_efficiency():
    """
    Builds on assumption that the ICE car can drive 20 km/l, while the EV car can drive 5 km/kWh and has an assumed efficiency of 85%
    """
    return 0.32


@component.add(
    name="LD initial sector activity",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_ld_initial_sector_activity": 1},
    other_deps={
        "_initial_ld_initial_sector_activity": {
            "initial": {"ld_current_demand": 1},
            "step": {},
        }
    },
)
def ld_initial_sector_activity():
    return _initial_ld_initial_sector_activity()


_initial_ld_initial_sector_activity = Initial(
    lambda: ld_current_demand(), "_initial_ld_initial_sector_activity"
)


@component.add(
    name="LD innovator pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_continuous_investment": 1, "innovators": 2},
)
def ld_innovator_pipeline():
    return ld_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="LD innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_bev_inno_switch": 1, "ld_fcev_inno_switch": 1},
)
def ld_innovators():
    return float(np.maximum(ld_bev_inno_switch() + ld_fcev_inno_switch(), 1))


@component.add(
    name="LD investment pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_continuous_investment": 1},
)
def ld_investment_pipeline():
    return ld_continuous_investment()


@component.add(
    name="LD projected demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rt_energy_demand": 1, "light_duty_fraction": 1},
)
def ld_projected_demand():
    return rt_energy_demand() * light_duty_fraction()


@component.add(
    name="light duty emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_bev_emissions": 1, "ld_fossil_emissions": 1},
)
def light_duty_emissions():
    return ld_bev_emissions() + ld_fossil_emissions()


@component.add(name="Light duty fraction", comp_type="Constant", comp_subtype="Normal")
def light_duty_fraction():
    """
    Fraction of road transport energy consumption which is light duty.
    """
    return 0.73


@component.add(
    name="light duty hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fcev": 1,
        "ld_ice_efficiency": 1,
        "ld_fcev_efficiency": 1,
        "h2_lhv": 1,
    },
)
def light_duty_hydrogen_demand():
    """
    GWh * MWh/GWh / MWh/t
    """
    return ld_fcev() * ld_ice_efficiency() / ld_fcev_efficiency() * 1000 / h2_lhv()


@component.add(
    name="RT energy demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def rt_energy_demand():
    """
    1.56% increase per year compared to the base year (2019). Energy is denoted as total energy supplied to the wheels after ICE efficiency losses.
    """
    return np.interp(
        time(),
        [
            1990.0,
            1991.0,
            1992.0,
            1993.0,
            1994.0,
            1995.0,
            1996.0,
            1997.0,
            1998.0,
            1999.0,
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
        ],
        [
            2826790.0,
            2855560.0,
            2925860.0,
            2963340.0,
            2986900.0,
            3019350.0,
            3126610.0,
            3178780.0,
            3276960.0,
            3346050.0,
            3340730.0,
            3398480.0,
            3446660.0,
            3479300.0,
            3566350.0,
            3575440.0,
            3649610.0,
            3704130.0,
            3653790.0,
            3573480.0,
            3566740.0,
            3543890.0,
            3425970.0,
            3413450.0,
            3484900.0,
            3534240.0,
            3616960.0,
            3678130.0,
            3689730.0,
            3718680.0,
            3776690.0,
            3835610.0,
            3895440.0,
            3956210.0,
            4017930.0,
            4080610.0,
            4144270.0,
            4208920.0,
            4274580.0,
            4341260.0,
            4408980.0,
            4477760.0,
            4547620.0,
            4618560.0,
            4690610.0,
            4763780.0,
            4838100.0,
            4913570.0,
            4990220.0,
            5068070.0,
            5147130.0,
            5227430.0,
            5308980.0,
            5391800.0,
            5475910.0,
            5561330.0,
            5648090.0,
            5736200.0,
            5825680.0,
            5916560.0,
            6008860.0,
        ],
    )


@component.add(
    name="Subsidized LD FCEV Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_ld_fcev_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_ld_fcev_commissioning": {
            "initial": {"car_procurement_time": 1},
            "step": {"subsidized_ld_fcev_investment": 1},
        }
    },
)
def subsidized_ld_fcev_commissioning():
    return _delayfixed_subsidized_ld_fcev_commissioning()


_delayfixed_subsidized_ld_fcev_commissioning = DelayFixed(
    lambda: subsidized_ld_fcev_investment(),
    lambda: car_procurement_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_ld_fcev_commissioning",
)


@component.add(
    name="Subsidized LD FCEV Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_ld_fcev_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_ld_fcev_decommissioning": {
            "initial": {},
            "step": {"subsidized_ld_fcev_commissioning": 1},
        }
    },
)
def subsidized_ld_fcev_decommissioning():
    return _delayfixed_subsidized_ld_fcev_decommissioning()


_delayfixed_subsidized_ld_fcev_decommissioning = DelayFixed(
    lambda: subsidized_ld_fcev_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_ld_fcev_decommissioning",
)


@component.add(
    name="Subsidized LD FCEV Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fcev_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "ld_fcev_investment": 1,
        "ld_ice_efficiency": 1,
        "ld_fcev_efficiency": 1,
        "h2_lhv": 1,
    },
)
def subsidized_ld_fcev_investment():
    return (
        if_then_else(
            ld_fcev_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: ld_fcev_investment(),
            lambda: 0,
        )
        * ld_ice_efficiency()
        / ld_fcev_efficiency()
        / h2_lhv()
        / 1000
    )


@component.add(
    name="sum LD activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ld_fossil": 1, "ld_fcev": 1, "ld_bev": 1},
)
def sum_ld_activity():
    return ld_fossil() + ld_fcev() + ld_bev()


@component.add(
    name="sum LD decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fcev_decommissioning": 1,
        "ld_fossil_decommissioning": 1,
        "ld_fossil_early_decommissioning": 1,
        "ld_bev_decommissioning": 1,
        "ld_fossil_economic_decommissioning": 1,
    },
)
def sum_ld_decommissioning():
    return (
        ld_fcev_decommissioning()
        + ld_fossil_decommissioning()
        + ld_fossil_early_decommissioning()
        + ld_bev_decommissioning()
        + ld_fossil_economic_decommissioning()
    )


@component.add(
    name="Support LD FCEV",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_ld_fcev_investment": 1,
        "ld_fcev_h2_subsidy": 1,
        "green_h2_subsidy": 1,
    },
)
def support_ld_fcev():
    return (
        subsidized_ld_fcev_investment()
        * (green_h2_subsidy() + ld_fcev_h2_subsidy())
        * 10
    )
