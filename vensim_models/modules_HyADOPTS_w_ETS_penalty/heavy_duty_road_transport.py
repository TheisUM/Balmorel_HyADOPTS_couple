"""
Module heavy_duty_road_transport
Translated using PySD version 3.14.3
"""

@component.add(
    name="alternative HD cost",
    units="€/km",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_be_lco": 1, "hd_fc_lco": 1},
)
def alternative_hd_cost():
    return float(np.minimum(hd_be_lco(), hd_fc_lco()))


@component.add(
    name="HD allocated emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"initial_hd_emissions": 1, "emissions_cap_lookup": 1, "time": 1},
)
def hd_allocated_emissions():
    return initial_hd_emissions() * emissions_cap_lookup(time())


@component.add(
    name="HD average cost",
    units="€/GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_bev_sector_share": 1,
        "hd_be_lco": 1,
        "hd_fc_lco": 1,
        "hd_fcev_sector_share": 1,
        "hd_fossil_sector_share": 1,
        "hd_ice_lco": 1,
        "diesel_lhv": 1,
        "hd_ice_energy_usage": 1,
    },
)
def hd_average_cost():
    """
    €/GWh of diesel equivalent. (Total truck ownership costs). Unit check: GWh * €/km * km/kWh * 10^6 kWh/GWh = € -> €/GWh
    """
    return (
        (
            hd_bev_sector_share() * hd_be_lco()
            + hd_fcev_sector_share() * hd_fc_lco()
            + hd_fossil_sector_share() * hd_ice_lco()
        )
        / (hd_ice_energy_usage() * diesel_lhv())
        * 10**6
    )


@component.add(
    name="HD backlog",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hd_backlog": 1},
    other_deps={
        "_integ_hd_backlog": {
            "initial": {"sum_hd_activity": 1},
            "step": {"hd_current_demand": 1, "sum_hd_activity": 1},
        }
    },
)
def hd_backlog():
    return _integ_hd_backlog()


_integ_hd_backlog = Integ(
    lambda: hd_current_demand() - sum_hd_activity(),
    lambda: sum_hd_activity() * 0.015,
    "_integ_hd_backlog",
)


@component.add(
    name="HD BEV",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hd_bev": 1},
    other_deps={
        "_integ_hd_bev": {
            "initial": {"hd_initial_sector_activity": 1},
            "step": {"hd_bev_commissioning": 1, "hd_bev_decommissioning": 1},
        }
    },
)
def hd_bev():
    return _integ_hd_bev()


_integ_hd_bev = Integ(
    lambda: hd_bev_commissioning() - hd_bev_decommissioning(),
    lambda: hd_initial_sector_activity() * 0.014,
    "_integ_hd_bev",
)


@component.add(
    name="HD BEV Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_bev_construction": 1, "truck_procurement_time": 1},
)
def hd_bev_commissioning():
    return hd_bev_construction() / truck_procurement_time()


@component.add(
    name="HD BEV competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_ice_lco": 1, "hd_be_lco": 2, "hd_fc_lco": 1},
)
def hd_bev_competitiveness():
    return float(np.minimum(hd_ice_lco() / hd_be_lco(), hd_fc_lco() / hd_be_lco()))


@component.add(
    name="HD BEV Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hd_bev_construction": 1},
    other_deps={
        "_integ_hd_bev_construction": {
            "initial": {},
            "step": {
                "hd_bev_innovators": 1,
                "hd_bev_investment": 1,
                "hd_bev_commissioning": 1,
            },
        }
    },
)
def hd_bev_construction():
    return _integ_hd_bev_construction()


_integ_hd_bev_construction = Integ(
    lambda: hd_bev_innovators() + hd_bev_investment() - hd_bev_commissioning(),
    lambda: 0,
    "_integ_hd_bev_construction",
)


@component.add(
    name="HD BEV Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_bev": 1, "truck_lifetime": 1},
)
def hd_bev_decommissioning():
    return hd_bev() / truck_lifetime()


@component.add(
    name="HD BEV emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_bev": 1,
        "hd_ice_efficiency": 1,
        "charging_efficiency": 1,
        "hd_ev_efficiency": 1,
        "electricity_emission_factor": 1,
    },
)
def hd_bev_emissions():
    return (
        hd_bev()
        * hd_ice_efficiency()
        / (charging_efficiency() * hd_ev_efficiency())
        * electricity_emission_factor()
        * 1000
    )


@component.add(
    name="HD BEV inno switch",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_bev_competitiveness": 1, "inno_switch_level": 1},
)
def hd_bev_inno_switch():
    return if_then_else(
        hd_bev_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="HD BEV innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_bev_inno_switch": 1, "hd_innovators": 1},
)
def hd_bev_innovator_share():
    return hd_bev_inno_switch() / hd_innovators()


@component.add(
    name="HD BEV Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_innovator_pipeline": 1, "hd_bev_innovator_share": 1},
)
def hd_bev_innovators():
    return hd_innovator_pipeline() * hd_bev_innovator_share()


@component.add(
    name="HD BEV Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_investment_pipeline": 1, "hd_bev_investment_share": 1},
)
def hd_bev_investment():
    return hd_investment_pipeline() * hd_bev_investment_share()


@component.add(
    name="HD BEV investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_equalizer": 1, "hd_bev_level": 1},
)
def hd_bev_investment_share():
    return hd_equalizer() * hd_bev_level()


@component.add(
    name="HD BEV level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "hd_bev_competitiveness": 1, "hd_bev_sector_share": 1},
)
def hd_bev_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - hd_bev_competitiveness()))))
        * float(np.maximum(0.1, hd_bev_sector_share()))
    )


@component.add(
    name="HD BEV sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_bev": 1, "sum_hd_activity": 1},
)
def hd_bev_sector_share():
    return hd_bev() / sum_hd_activity()


@component.add(
    name="HD continuous investment",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_forecast_demand": 1,
        "sum_hd_decommissioning": 1,
        "truck_procurement_time": 1,
        "hd_backlog": 1,
        "sum_hd_activity": 1,
        "innovators": 1,
    },
)
def hd_continuous_investment():
    return float(
        np.maximum(
            (
                hd_forecast_demand()
                + sum_hd_decommissioning()
                + hd_backlog() / truck_procurement_time() / 3
                - sum_hd_activity()
            )
            * (1 - innovators()),
            0,
        )
    )


@component.add(
    name="HD current demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_projected_demand": 1},
)
def hd_current_demand():
    return hd_projected_demand()


@component.add(
    name="HD effective cost",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_average_cost": 1, "hd_current_demand": 1},
)
def hd_effective_cost():
    return hd_average_cost() * hd_current_demand() / 1000000000.0


@component.add(
    name="HD Emissions cap lookup",
    units="percent",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_hd_emissions_cap_lookup"},
)
def hd_emissions_cap_lookup(x, final_subs=None):
    """
    Maximum investment share of fossil trucks.
    """
    return _hardcodedlookup_hd_emissions_cap_lookup(x, final_subs)


_hardcodedlookup_hd_emissions_cap_lookup = HardcodedLookups(
    [2010.0, 2025.0, 2030.0, 2035.0, 2040.0, 2050.0],
    [1.0, 0.85, 0.55, 0.35, 0.1, 0.1],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_hd_emissions_cap_lookup",
)


@component.add(
    name="HD equalizer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fcev_h2_subsidy": 1,
        "hd_fossil_level": 2,
        "hd_bev_level": 2,
        "hd_fcev_bid_share": 1,
        "hd_fcev_level": 1,
    },
)
def hd_equalizer():
    return if_then_else(
        hd_fcev_h2_subsidy() > 0.01,
        lambda: (1 - hd_fcev_bid_share()) / (hd_bev_level() + hd_fossil_level()),
        lambda: 1 / (hd_fossil_level() + hd_fcev_level() + hd_bev_level()),
    )


@component.add(
    name="HD excess emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"heavy_duty_emissions": 1, "hd_allocated_emissions": 1},
)
def hd_excess_emissions():
    return heavy_duty_emissions() - hd_allocated_emissions()


@component.add(
    name="HD FCEV",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hd_fcev": 1},
    other_deps={
        "_integ_hd_fcev": {
            "initial": {},
            "step": {"hd_fcev_commissioning": 1, "hd_fcev_decommissioning": 1},
        }
    },
)
def hd_fcev():
    return _integ_hd_fcev()


_integ_hd_fcev = Integ(
    lambda: hd_fcev_commissioning() - hd_fcev_decommissioning(),
    lambda: 0,
    "_integ_hd_fcev",
)


@component.add(
    name="HD FCEV bid share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fcev_desired_investment": 1},
)
def hd_fcev_bid_share():
    return hd_fcev_desired_investment()


@component.add(
    name="HD FCEV Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fcev_construction": 1, "truck_procurement_time": 1},
)
def hd_fcev_commissioning():
    return hd_fcev_construction() / truck_procurement_time()


@component.add(
    name="HD FCEV Commissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_hd_fcev_commissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_hd_fcev_commissioning_subsidy_level": {
            "initial": {"truck_procurement_time": 1},
            "step": {"hd_fcev_h2_subsidy": 1, "green_h2_subsidy": 1},
        }
    },
)
def hd_fcev_commissioning_subsidy_level():
    return _delayfixed_hd_fcev_commissioning_subsidy_level()


_delayfixed_hd_fcev_commissioning_subsidy_level = DelayFixed(
    lambda: hd_fcev_h2_subsidy() + green_h2_subsidy(),
    lambda: truck_procurement_time(),
    lambda: 0,
    time_step,
    "_delayfixed_hd_fcev_commissioning_subsidy_level",
)


@component.add(
    name="HD FCEV competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_be_lco": 1, "hd_fc_lco": 2, "hd_ice_lco": 1},
)
def hd_fcev_competitiveness():
    return float(np.minimum(hd_be_lco() / hd_fc_lco(), hd_ice_lco() / hd_fc_lco()))


@component.add(
    name="HD FCEV Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hd_fcev_construction": 1},
    other_deps={
        "_integ_hd_fcev_construction": {
            "initial": {},
            "step": {
                "hd_fcev_innovators": 1,
                "hd_fcev_investment": 1,
                "hd_fcev_commissioning": 1,
            },
        }
    },
)
def hd_fcev_construction():
    return _integ_hd_fcev_construction()


_integ_hd_fcev_construction = Integ(
    lambda: hd_fcev_innovators() + hd_fcev_investment() - hd_fcev_commissioning(),
    lambda: 0,
    "_integ_hd_fcev_construction",
)


@component.add(
    name="HD FCEV Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fcev": 1, "truck_lifetime": 1},
)
def hd_fcev_decommissioning():
    return hd_fcev() / truck_lifetime()


@component.add(
    name="HD FCEV Decommissioning subsidy level",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_hd_fcev_decommissioning_subsidy_level": 1},
    other_deps={
        "_delayfixed_hd_fcev_decommissioning_subsidy_level": {
            "initial": {},
            "step": {"hd_fcev_commissioning_subsidy_level": 1},
        }
    },
)
def hd_fcev_decommissioning_subsidy_level():
    return _delayfixed_hd_fcev_decommissioning_subsidy_level()


_delayfixed_hd_fcev_decommissioning_subsidy_level = DelayFixed(
    lambda: hd_fcev_commissioning_subsidy_level(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_hd_fcev_decommissioning_subsidy_level",
)


@component.add(
    name="HD FCEV desired investment",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_hd_fcev_desired_investment": 1},
    other_deps={
        "_smooth_hd_fcev_desired_investment": {
            "initial": {"hd_fcev_level": 2, "hd_fossil_level": 1, "hd_bev_level": 1},
            "step": {"hd_fcev_level": 2, "hd_fossil_level": 1, "hd_bev_level": 1},
        }
    },
)
def hd_fcev_desired_investment():
    return _smooth_hd_fcev_desired_investment()


_smooth_hd_fcev_desired_investment = Smooth(
    lambda: hd_fcev_level() / (hd_bev_level() + hd_fcev_level() + hd_fossil_level()),
    lambda: 2,
    lambda: hd_fcev_level() / (hd_bev_level() + hd_fcev_level() + hd_fossil_level()),
    lambda: 1,
    "_smooth_hd_fcev_desired_investment",
)


@component.add(
    name="HD FCEV HBA volume",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_continuous_investment": 1,
        "hd_ice_efficiency": 1,
        "hd_fcev_efficiency": 1,
        "h2_lhv": 1,
        "hd_fcev_bid_share": 1,
    },
)
def hd_fcev_hba_volume():
    return (
        hd_continuous_investment()
        * hd_ice_efficiency()
        / hd_fcev_efficiency()
        * 1000
        / h2_lhv()
        * hd_fcev_bid_share()
    )


@component.add(
    name="HD FCEV inno switch",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fcev_competitiveness": 1, "inno_switch_level": 1},
)
def hd_fcev_inno_switch():
    return if_then_else(
        hd_fcev_competitiveness() > inno_switch_level(), lambda: 1, lambda: 0
    )


@component.add(
    name="HD FCEV innovator share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fcev_inno_switch": 1, "hd_innovators": 1},
)
def hd_fcev_innovator_share():
    return hd_fcev_inno_switch() / hd_innovators()


@component.add(
    name="HD FCEV Innovators",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_innovator_pipeline": 1, "hd_fcev_innovator_share": 1},
)
def hd_fcev_innovators():
    return hd_innovator_pipeline() * hd_fcev_innovator_share()


@component.add(
    name="HD FCEV Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_investment_pipeline": 1, "hd_fcev_investment_share": 1},
)
def hd_fcev_investment():
    return hd_investment_pipeline() * hd_fcev_investment_share()


@component.add(
    name="HD FCEV investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fcev_h2_subsidy": 1,
        "hd_fcev_bid_share": 1,
        "hd_equalizer": 1,
        "hd_fcev_level": 1,
    },
)
def hd_fcev_investment_share():
    return if_then_else(
        hd_fcev_h2_subsidy() > 0.01,
        lambda: hd_fcev_bid_share(),
        lambda: hd_equalizer() * hd_fcev_level(),
    )


@component.add(
    name="HD FCEV level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"slope": 1, "hd_fcev_competitiveness": 1, "hd_fcev_sector_share": 1},
)
def hd_fcev_level():
    return (
        1
        / (1 + float(np.exp(slope() * (1 - hd_fcev_competitiveness()))))
        * float(np.maximum(0.1, hd_fcev_sector_share()))
    )


@component.add(
    name="HD FCEV sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fcev": 1, "sum_hd_activity": 1},
)
def hd_fcev_sector_share():
    return hd_fcev() / sum_hd_activity()


@component.add(
    name="HD FCEV subsidy cost",
    units="B€/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hd_fcev_subsidy_cost": 1},
    other_deps={
        "_integ_hd_fcev_subsidy_cost": {
            "initial": {},
            "step": {
                "hd_fcev_commissioning_subsidy_level": 1,
                "subsidized_hd_fcev_commissioning": 1,
                "hd_fcev_decommissioning_subsidy_level": 1,
                "subsidized_hd_fcev_decommissioning": 1,
            },
        }
    },
)
def hd_fcev_subsidy_cost():
    return _integ_hd_fcev_subsidy_cost()


_integ_hd_fcev_subsidy_cost = Integ(
    lambda: hd_fcev_commissioning_subsidy_level() * subsidized_hd_fcev_commissioning()
    - hd_fcev_decommissioning_subsidy_level() * subsidized_hd_fcev_decommissioning(),
    lambda: 0,
    "_integ_hd_fcev_subsidy_cost",
)


@component.add(
    name="HD forecast demand",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Forecast",
    depends_on={"_forecast_hd_forecast_demand": 1},
    other_deps={
        "_forecast_hd_forecast_demand": {
            "initial": {"hd_current_demand": 1},
            "step": {"hd_current_demand": 1, "truck_procurement_time": 2},
        }
    },
)
def hd_forecast_demand():
    return _forecast_hd_forecast_demand()


_forecast_hd_forecast_demand = Forecast(
    lambda: hd_current_demand(),
    lambda: 3 * truck_procurement_time(),
    lambda: truck_procurement_time(),
    lambda: 0,
    "_forecast_hd_forecast_demand",
)


@component.add(
    name="HD Fossil",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hd_fossil": 1},
    other_deps={
        "_integ_hd_fossil": {
            "initial": {"hd_initial_sector_activity": 1},
            "step": {
                "hd_fossil_commissioning": 1,
                "hd_fossil_decommissioning": 1,
                "hd_fossil_early_decommissioning": 1,
                "hd_fossil_economic_decommissioning": 1,
            },
        }
    },
)
def hd_fossil():
    return _integ_hd_fossil()


_integ_hd_fossil = Integ(
    lambda: hd_fossil_commissioning()
    - hd_fossil_decommissioning()
    - hd_fossil_early_decommissioning()
    - hd_fossil_economic_decommissioning(),
    lambda: hd_initial_sector_activity() * 0.986,
    "_integ_hd_fossil",
)


@component.add(
    name="HD Fossil Commissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fossil_construction": 1, "truck_procurement_time": 1},
)
def hd_fossil_commissioning():
    return hd_fossil_construction() / truck_procurement_time()


@component.add(
    name="HD Fossil competitiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_be_lco": 1, "hd_ice_lco": 2, "hd_fc_lco": 1},
)
def hd_fossil_competitiveness():
    return float(np.minimum(hd_be_lco() / hd_ice_lco(), hd_fc_lco() / hd_ice_lco()))


@component.add(
    name="HD Fossil Construction",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_hd_fossil_construction": 1},
    other_deps={
        "_integ_hd_fossil_construction": {
            "initial": {
                "hd_initial_sector_activity": 1,
                "truck_lifetime": 1,
                "truck_procurement_time": 1,
            },
            "step": {"hd_fossil_investment": 1, "hd_fossil_commissioning": 1},
        }
    },
)
def hd_fossil_construction():
    return _integ_hd_fossil_construction()


_integ_hd_fossil_construction = Integ(
    lambda: hd_fossil_investment() - hd_fossil_commissioning(),
    lambda: hd_initial_sector_activity()
    / truck_lifetime()
    * truck_procurement_time()
    * 1.15,
    "_integ_hd_fossil_construction",
)


@component.add(
    name="HD fossil cost difference",
    units="factor",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_ice_opex": 1, "alternative_hd_cost": 1},
)
def hd_fossil_cost_difference():
    return hd_ice_opex() / alternative_hd_cost()


@component.add(
    name="HD Fossil Decommissioning",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_hd_fossil_decommissioning": 1, "hd_fossil": 1},
    other_deps={
        "_smooth_hd_fossil_decommissioning": {
            "initial": {
                "hd_fossil_delayed": 1,
                "hd_fossil_economic_decommissioning_delayed": 1,
            },
            "step": {
                "hd_fossil_delayed": 1,
                "hd_fossil_economic_decommissioning_delayed": 1,
            },
        }
    },
)
def hd_fossil_decommissioning():
    return float(
        np.maximum(
            0, float(np.minimum(_smooth_hd_fossil_decommissioning(), hd_fossil()))
        )
    )


_smooth_hd_fossil_decommissioning = Smooth(
    lambda: hd_fossil_delayed() - hd_fossil_economic_decommissioning_delayed(),
    lambda: 1,
    lambda: hd_fossil_delayed() - hd_fossil_economic_decommissioning_delayed(),
    lambda: 1,
    "_smooth_hd_fossil_decommissioning",
)


@component.add(
    name="HD Fossil delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_hd_fossil_delayed": 1},
    other_deps={
        "_delayfixed_hd_fossil_delayed": {
            "initial": {"hd_initial_sector_activity": 1, "truck_lifetime": 2},
            "step": {"hd_fossil_commissioning": 1},
        }
    },
)
def hd_fossil_delayed():
    return _delayfixed_hd_fossil_delayed()


_delayfixed_hd_fossil_delayed = DelayFixed(
    lambda: hd_fossil_commissioning(),
    lambda: truck_lifetime(),
    lambda: hd_initial_sector_activity() / truck_lifetime(),
    time_step,
    "_delayfixed_hd_fossil_delayed",
)


@component.add(
    name="HD Fossil Early Decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fossil": 1},
)
def hd_fossil_early_decommissioning():
    return 0 * hd_fossil()


@component.add(
    name="HD fossil economic decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fossil_cost_difference": 2,
        "hd_fossil": 1,
        "truck_lifetime": 1,
        "slope_decom": 1,
        "intersec_decom": 1,
        "economic_decommissioning": 1,
    },
)
def hd_fossil_economic_decommissioning():
    return (
        if_then_else(
            hd_fossil_cost_difference() > 1,
            lambda: (hd_fossil() / truck_lifetime() * 3)
            * (
                1
                / (
                    1
                    + float(
                        np.exp(
                            -slope_decom()
                            * (hd_fossil_cost_difference() - intersec_decom())
                        )
                    )
                )
            ),
            lambda: 0,
        )
        * economic_decommissioning()
    )


@component.add(
    name="HD Fossil economic decommissioning delayed",
    units="GWh/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delayn_hd_fossil_economic_decommissioning_delayed": 1},
    other_deps={
        "_delayn_hd_fossil_economic_decommissioning_delayed": {
            "initial": {},
            "step": {
                "hd_fossil_economic_decommissioning": 1,
                "hd_fossil_early_decommissioning": 1,
            },
        }
    },
)
def hd_fossil_economic_decommissioning_delayed():
    return _delayn_hd_fossil_economic_decommissioning_delayed()


_delayn_hd_fossil_economic_decommissioning_delayed = DelayN(
    lambda: hd_fossil_economic_decommissioning() + hd_fossil_early_decommissioning(),
    lambda: 3,
    lambda: 0,
    lambda: 10,
    time_step,
    "_delayn_hd_fossil_economic_decommissioning_delayed",
)


@component.add(
    name="HD Fossil emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fossil": 1, "diesel_emission_factor": 1},
)
def hd_fossil_emissions():
    return hd_fossil() * diesel_emission_factor() * 10**6


@component.add(
    name="HD Fossil Investment",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_investment_pipeline": 1, "hd_fossil_investment_share": 1},
)
def hd_fossil_investment():
    return hd_investment_pipeline() * hd_fossil_investment_share()


@component.add(
    name="HD Fossil investment share",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_equalizer": 1, "hd_fossil_level": 1},
)
def hd_fossil_investment_share():
    return hd_equalizer() * hd_fossil_level()


@component.add(
    name="HD Fossil level",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hard_regulation": 1,
        "hd_fossil_competitiveness": 2,
        "slope": 2,
        "hd_fossil_sector_share": 2,
        "hd_emissions_cap_lookup": 2,
        "time": 2,
        "hd_zero_emission_level": 1,
    },
)
def hd_fossil_level():
    """
    fossil_level / (fossil_level+zero_emissions_level) <= cap fossil_level <= cap * (fossil_level+zero_emissions_level) (1-cap) * fossil_level <= cap * zero_emissions_level fossil_level <= cap / (1-cap) * zero_emissions_level fossil_level = min(fossil_level, cap / (1-cap) * zero_emissions_level)
    """
    return if_then_else(
        hard_regulation() < 0.5,
        lambda: 1
        / (1 + float(np.exp(slope() * (1 - hd_fossil_competitiveness()))))
        * float(np.maximum(0.1, hd_fossil_sector_share())),
        lambda: float(
            np.minimum(
                1
                / (1 + float(np.exp(slope() * (1 - hd_fossil_competitiveness()))))
                * float(np.maximum(0.1, hd_fossil_sector_share())),
                hd_emissions_cap_lookup(time())
                / (1 - hd_emissions_cap_lookup(time()))
                * hd_zero_emission_level(),
            )
        ),
    )


@component.add(
    name="HD Fossil sector share",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fossil": 1, "sum_hd_activity": 1},
)
def hd_fossil_sector_share():
    return hd_fossil() / sum_hd_activity()


@component.add(
    name="HD H2 WTP",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_ice_lco": 1, "hd_fc_lco_without_h2": 1, "hd_fc_energy_usage": 1},
)
def hd_h2_wtp():
    return (hd_ice_lco() - hd_fc_lco_without_h2()) / hd_fc_energy_usage()


@component.add(
    name="HD ICE efficiency",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hd_ice_efficiency():
    """
    Builds on the assumption that the EV truck has an efficiency of 85% and the fuel economy is determined by the fits found by Noll et al. (https://doi.org/10.1016/j.apenergy.2021.118079)
    """
    return 0.343


@component.add(
    name="HD initial sector activity",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_hd_initial_sector_activity": 1},
    other_deps={
        "_initial_hd_initial_sector_activity": {
            "initial": {"hd_current_demand": 1},
            "step": {},
        }
    },
)
def hd_initial_sector_activity():
    return _initial_hd_initial_sector_activity()


_initial_hd_initial_sector_activity = Initial(
    lambda: hd_current_demand(), "_initial_hd_initial_sector_activity"
)


@component.add(
    name="HD innovator pipeline",
    units="MT NH3",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_continuous_investment": 1, "innovators": 2},
)
def hd_innovator_pipeline():
    return hd_continuous_investment() / (1 - innovators()) * innovators()


@component.add(
    name="HD innovators",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_bev_inno_switch": 1, "hd_fcev_inno_switch": 1},
)
def hd_innovators():
    return float(np.maximum(hd_bev_inno_switch() + hd_fcev_inno_switch(), 1))


@component.add(
    name="HD investment pipeline",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_continuous_investment": 1},
)
def hd_investment_pipeline():
    return hd_continuous_investment()


@component.add(
    name="HD projected demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rt_energy_demand": 1, "heavy_duty_fraction": 1},
)
def hd_projected_demand():
    return rt_energy_demand() * heavy_duty_fraction()


@component.add(
    name="HD Zero Emission level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_bev_level": 1, "hd_fcev_level": 1},
)
def hd_zero_emission_level():
    return hd_bev_level() + hd_fcev_level()


@component.add(
    name="heavy duty emissions",
    units="tCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_bev_emissions": 1, "hd_fossil_emissions": 1},
)
def heavy_duty_emissions():
    return hd_bev_emissions() + hd_fossil_emissions()


@component.add(
    name="Heavy duty fraction",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"light_duty_fraction": 1},
)
def heavy_duty_fraction():
    """
    Fraction of road transport energy consumption which is heavy duty.
    """
    return 1 - light_duty_fraction()


@component.add(
    name="heavy duty hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fcev": 1,
        "hd_ice_efficiency": 1,
        "hd_fcev_efficiency": 1,
        "h2_lhv": 1,
    },
)
def heavy_duty_hydrogen_demand():
    """
    GWh * MWh/GWh / MWh/t
    """
    return hd_fcev() * hd_ice_efficiency() / hd_fcev_efficiency() * 1000 / h2_lhv()


@component.add(
    name="Initial HD emissions",
    units="tCO2",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_initial_hd_emissions": 1},
    other_deps={
        "_initial_initial_hd_emissions": {
            "initial": {"heavy_duty_emissions": 1},
            "step": {},
        }
    },
)
def initial_hd_emissions():
    return _initial_initial_hd_emissions()


_initial_initial_hd_emissions = Initial(
    lambda: heavy_duty_emissions(), "_initial_initial_hd_emissions"
)


@component.add(
    name="Subsidized HD FCEV Commissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_hd_fcev_commissioning": 1},
    other_deps={
        "_delayfixed_subsidized_hd_fcev_commissioning": {
            "initial": {"truck_procurement_time": 1},
            "step": {"subsidized_hd_fcev_investment": 1},
        }
    },
)
def subsidized_hd_fcev_commissioning():
    return _delayfixed_subsidized_hd_fcev_commissioning()


_delayfixed_subsidized_hd_fcev_commissioning = DelayFixed(
    lambda: subsidized_hd_fcev_investment(),
    lambda: truck_procurement_time(),
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_hd_fcev_commissioning",
)


@component.add(
    name="Subsidized HD FCEV Decommissioning",
    units="MT H2/Year",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_subsidized_hd_fcev_decommissioning": 1},
    other_deps={
        "_delayfixed_subsidized_hd_fcev_decommissioning": {
            "initial": {},
            "step": {"subsidized_hd_fcev_commissioning": 1},
        }
    },
)
def subsidized_hd_fcev_decommissioning():
    return _delayfixed_subsidized_hd_fcev_decommissioning()


_delayfixed_subsidized_hd_fcev_decommissioning = DelayFixed(
    lambda: subsidized_hd_fcev_commissioning(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_subsidized_hd_fcev_decommissioning",
)


@component.add(
    name="Subsidized HD FCEV Investment",
    units="MT H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fcev_h2_subsidy": 1,
        "green_h2_subsidy": 1,
        "hd_fcev_investment": 1,
        "hd_ice_efficiency": 1,
        "hd_fcev_efficiency": 1,
        "h2_lhv": 1,
    },
)
def subsidized_hd_fcev_investment():
    return (
        if_then_else(
            hd_fcev_h2_subsidy() + green_h2_subsidy() > 0,
            lambda: hd_fcev_investment(),
            lambda: 0,
        )
        * hd_ice_efficiency()
        / hd_fcev_efficiency()
        / h2_lhv()
        / 1000
    )


@component.add(
    name="sum HD activity",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hd_fossil": 1, "hd_fcev": 1, "hd_bev": 1},
)
def sum_hd_activity():
    return hd_fossil() + hd_fcev() + hd_bev()


@component.add(
    name="sum HD decommissioning",
    units="GWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fcev_decommissioning": 1,
        "hd_fossil_decommissioning": 1,
        "hd_fossil_early_decommissioning": 1,
        "hd_bev_decommissioning": 1,
        "hd_fossil_economic_decommissioning": 1,
    },
)
def sum_hd_decommissioning():
    return (
        hd_fcev_decommissioning()
        + hd_fossil_decommissioning()
        + hd_fossil_early_decommissioning()
        + hd_bev_decommissioning()
        + hd_fossil_economic_decommissioning()
    )


@component.add(
    name="Support HD FCEV",
    units="B€",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_hd_fcev_investment": 1,
        "hd_fcev_h2_subsidy": 1,
        "green_h2_subsidy": 1,
    },
)
def support_hd_fcev():
    return (
        subsidized_hd_fcev_investment()
        * (green_h2_subsidy() + hd_fcev_h2_subsidy())
        * 10
    )


@component.add(
    name="truck lifetime", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def truck_lifetime():
    """
    inverse scrappage rate based on Eurostat numbers.
    """
    return 12


@component.add(
    name="truck procurement time",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def truck_procurement_time():
    return 0.5
