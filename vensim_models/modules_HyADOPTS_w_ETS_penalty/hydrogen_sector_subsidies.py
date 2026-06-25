"""
Module hydrogen_sector_subsidies
Translated using PySD version 3.14.3
"""

@component.add(
    name="BioKero H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "biokero_h2_cost": 1},
)
def biokero_h2_actual_subsidy():
    return green_h2_cost() - biokero_h2_cost()


@component.add(
    name="BioKero H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def biokero_h2_cost():
    return float(
        np.maximum(
            if_then_else(
                biokero_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - biokero_h2_subsidy(),
            0.1,
        )
    )


@component.add(
    name="BioKero H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_aviation_subsidy_ytd": 1,
        "international_aviation_subsidy_ytd": 1,
        "biokero_h2_subsidy_limit": 1,
        "biokero_h2_subsidy_size": 1,
        "biokero_h2_subsidy_length": 1,
        "time": 1,
    },
)
def biokero_h2_subsidy():
    return if_then_else(
        domestic_aviation_subsidy_ytd() + international_aviation_subsidy_ytd()
        < biokero_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=biokero_h2_subsidy_length())
        * biokero_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="BioKero H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def biokero_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="BioKero H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biokero_h2_subsidy_limit():
    return 10**9


@component.add(
    name="BioKero H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokero_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def biokero_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(biokero_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                biokero_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), biokero_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="BioMeOH H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "biomeoh_h2_cost": 1},
)
def biomeoh_h2_actual_subsidy():
    return green_h2_cost() - biomeoh_h2_cost()


@component.add(
    name="BioMeOH H2 cost",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def biomeoh_h2_cost():
    return float(
        np.maximum(
            0.1,
            if_then_else(
                biomeoh_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - biomeoh_h2_subsidy(),
        )
    )


@component.add(
    name="BioMeOH H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_subsidy_ytd": 1,
        "biomeoh_h2_subsidy_limit": 1,
        "biomeoh_h2_subsidy_size": 1,
        "time": 1,
        "biomeoh_h2_subsidy_length": 1,
    },
)
def biomeoh_h2_subsidy():
    return if_then_else(
        meoh_subsidy_ytd() < biomeoh_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=biomeoh_h2_subsidy_length())
        * biomeoh_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="BioMeOH H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def biomeoh_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="BioMeOH H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biomeoh_h2_subsidy_limit():
    return 10**9


@component.add(
    name="BioMeOH H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biomeoh_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def biomeoh_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(biomeoh_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                biomeoh_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), biomeoh_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="BioNaphtha H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "bionaphtha_h2_cost": 1},
)
def bionaphtha_h2_actual_subsidy():
    return green_h2_cost() - bionaphtha_h2_cost()


@component.add(
    name="BioNaphtha H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bionaphtha_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def bionaphtha_h2_cost():
    return float(
        np.maximum(
            if_then_else(
                bionaphtha_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - bionaphtha_h2_subsidy(),
            0.1,
        )
    )


@component.add(
    name="BioNaphtha H2 subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "naphtha_subsidy_ytd": 1,
        "bionaphtha_h2_subsidy_limit": 1,
        "bionaphtha_h2_subsidy_length": 1,
        "bionaphtha_h2_subsidy_size": 1,
        "time": 1,
    },
)
def bionaphtha_h2_subsidy():
    return if_then_else(
        naphtha_subsidy_ytd() < bionaphtha_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=bionaphtha_h2_subsidy_length())
        * bionaphtha_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="BioNaphtha H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def bionaphtha_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="BioNaphtha H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def bionaphtha_h2_subsidy_limit():
    return 10**9


@component.add(
    name="BioNaphtha H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bionaphtha_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def bionaphtha_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(
                        bionaphtha_h2_wtp_gap() + bid_increase(), hba_max_subsidy()
                    )
                ),
                bionaphtha_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(
                        hba_max_subsidy(), bionaphtha_h2_wtp_gap() + bid_increase()
                    )
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="delay green h2 cost",
    units="€/kg H2",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_delay_green_h2_cost": 1},
    other_deps={
        "_delayfixed_delay_green_h2_cost": {
            "initial": {"green_h2_cost": 1},
            "step": {"green_h2_cost": 1},
        }
    },
)
def delay_green_h2_cost():
    return _delayfixed_delay_green_h2_cost()


_delayfixed_delay_green_h2_cost = DelayFixed(
    lambda: green_h2_cost(),
    lambda: 10,
    lambda: green_h2_cost(),
    time_step,
    "_delayfixed_delay_green_h2_cost",
)


@component.add(
    name="Derisked green H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "green_h2_derisked_capex": 1,
        "green_h2_opex": 1,
        "green_h2_subsidy": 1,
    },
)
def derisked_green_h2_cost():
    return float(
        np.maximum(
            green_h2_derisked_capex() + green_h2_opex() - green_h2_subsidy(), 0.1
        )
    )


@component.add(
    name="DS subsidy ban",
    units="boolean",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def ds_subsidy_ban():
    return step(__data["time"], 0, 2025)


@component.add(
    name="eMeOH H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "emeoh_h2_cost": 1},
)
def emeoh_h2_actual_subsidy():
    return green_h2_cost() - emeoh_h2_cost()


@component.add(
    name="eMeOH H2 cost",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"emeoh_h2_subsidy": 2, "derisked_green_h2_cost": 1, "green_h2_cost": 1},
)
def emeoh_h2_cost():
    return float(
        np.maximum(
            0.1,
            if_then_else(
                emeoh_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - emeoh_h2_subsidy(),
        )
    )


@component.add(
    name="eMeOH H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_subsidy_ytd": 1,
        "emeoh_h2_subsidy_limit": 1,
        "emeoh_h2_subsidy_size": 1,
        "emeoh_h2_subsidy_length": 1,
        "time": 1,
    },
)
def emeoh_h2_subsidy():
    return if_then_else(
        meoh_subsidy_ytd() < emeoh_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=emeoh_h2_subsidy_length())
        * emeoh_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="eMeOH H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def emeoh_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="eMeOH H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def emeoh_h2_subsidy_limit():
    return 10**9


@component.add(
    name="eMeOH H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "emeoh_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def emeoh_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(emeoh_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                emeoh_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), emeoh_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="fertilizer H2 actual subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "fertilizer_h2_cost": 1},
)
def fertilizer_h2_actual_subsidy():
    return green_h2_cost() - fertilizer_h2_cost()


@component.add(
    name="fertilizer H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def fertilizer_h2_cost():
    return float(
        np.maximum(
            0.1,
            if_then_else(
                fertilizer_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - fertilizer_h2_subsidy(),
        )
    )


@component.add(
    name="fertilizer H2 subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertilizer_subsidy_ytd": 1,
        "fertilizer_h2_subsidy_limit": 1,
        "fertilizer_h2_subsidy_length": 1,
        "fertilizer_h2_subsidy_size": 1,
        "time": 1,
    },
)
def fertilizer_h2_subsidy():
    return if_then_else(
        fertilizer_subsidy_ytd() < fertilizer_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=fertilizer_h2_subsidy_length())
        * fertilizer_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="fertilizer H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def fertilizer_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="fertilizer H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def fertilizer_h2_subsidy_limit():
    return 10**9


@component.add(
    name="fertilizer H2 subsidy size",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "green_nh3_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def fertilizer_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(
                        green_nh3_h2_wtp_gap() + bid_increase(), hba_max_subsidy()
                    )
                ),
                green_nh3_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(
                        hba_max_subsidy(), green_nh3_h2_wtp_gap() + bid_increase()
                    )
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="Green H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"unsubsidized_green_h2_cost": 1, "green_h2_cost": 1},
)
def green_h2_actual_subsidy():
    return unsubsidized_green_h2_cost() - green_h2_cost()


@component.add(
    name="Green H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "unsubsidized_green_h2_cost": 1,
        "green_h2_tariff": 1,
        "green_h2_subsidy": 1,
    },
)
def green_h2_cost():
    """
    First CAPEX and OPEX is calculated as €/kWh input energy, then as €/kWh output H2. Electricity costs are added on top, also as €/kWh output H2. Multiplied by LHV of H2 to change the value to €/kg
    """
    return float(
        np.maximum(
            unsubsidized_green_h2_cost() + green_h2_tariff() - green_h2_subsidy(), 0.1
        )
    )


@component.add(
    name="Green H2 subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "yearly_total_subsidies_limit": 1,
        "total_subsidies_ytd": 1,
        "green_h2_subsidy_size": 1,
        "pulse_h2_subsidy": 1,
    },
)
def green_h2_subsidy():
    return if_then_else(
        yearly_total_subsidies_limit() >= total_subsidies_ytd(),
        lambda: green_h2_subsidy_size() * pulse_h2_subsidy(),
        lambda: 0,
    )


@component.add(
    name="Green H2 subsidy size",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba": 1},
)
def green_h2_subsidy_size():
    return 1.5 * (1 - hba())


@component.add(
    name="Green H2 tariff", units="€/kg", comp_type="Constant", comp_subtype="Normal"
)
def green_h2_tariff():
    return 0


@component.add(
    name="H2 subsidy length", units="years", comp_type="Constant", comp_subtype="Normal"
)
def h2_subsidy_length():
    return 10


@component.add(
    name="H2FC DS H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "h2fc_ds_h2_cost": 1},
)
def h2fc_ds_h2_actual_subsidy():
    return green_h2_cost() - h2fc_ds_h2_cost()


@component.add(
    name="H2FC DS H2 cost",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2fc_ds_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
        "ds_subsidy_ban": 1,
    },
)
def h2fc_ds_h2_cost():
    return (
        float(
            np.maximum(
                0.1,
                if_then_else(
                    h2fc_ds_h2_subsidy() > 0,
                    lambda: derisked_green_h2_cost(),
                    lambda: green_h2_cost(),
                )
                - h2fc_ds_h2_subsidy(),
            )
        )
        + ds_subsidy_ban() * 1000
    )


@component.add(
    name="H2FC DS H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "shipping_nh3_subsidy_ytd": 1,
        "h2fc_ds_h2_subsidy_limit": 1,
        "h2fc_ds_h2_subsidy_length": 1,
        "h2fc_ds_h2_subsidy_size": 1,
        "time": 1,
    },
)
def h2fc_ds_h2_subsidy():
    return if_then_else(
        shipping_nh3_subsidy_ytd() < h2fc_ds_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=h2fc_ds_h2_subsidy_length())
        * h2fc_ds_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="H2FC DS H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def h2fc_ds_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="H2FC DS H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def h2fc_ds_h2_subsidy_limit():
    return 10**9


@component.add(
    name="H2FC DS H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2fc_ds_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def h2fc_ds_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(h2fc_ds_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                h2fc_ds_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), h2fc_ds_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="HBA active",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1, "time": 1},
)
def hba_active():
    return pulse(__data["time"], 2025, width=hba_duration())


@component.add(
    name="HBA duration", units="years", comp_type="Constant", comp_subtype="Normal"
)
def hba_duration():
    return 10


@component.add(
    name="HD FCEV H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "hd_fcev_h2_cost": 1},
)
def hd_fcev_h2_actual_subsidy():
    return green_h2_cost() - hd_fcev_h2_cost()


@component.add(
    name="HD FCEV H2 cost",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fcev_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
        "hd_subsidy_ban": 1,
    },
)
def hd_fcev_h2_cost():
    return (
        float(
            np.maximum(
                0.1,
                if_then_else(
                    hd_fcev_h2_subsidy() > 0,
                    lambda: derisked_green_h2_cost(),
                    lambda: green_h2_cost(),
                )
                - hd_fcev_h2_subsidy(),
            )
        )
        + hd_subsidy_ban() * 1000
    )


@component.add(
    name="HD FCEV H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heavy_duty_subsidy_ytd": 1,
        "hd_fcev_h2_subsidy_limit": 1,
        "hd_fcev_h2_subsidy_length": 1,
        "hd_fcev_h2_subsidy_size": 1,
        "time": 1,
    },
)
def hd_fcev_h2_subsidy():
    return if_then_else(
        heavy_duty_subsidy_ytd() < hd_fcev_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=hd_fcev_h2_subsidy_length())
        * hd_fcev_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="HD FCEV H2 subsidy length",
    units="Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def hd_fcev_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="HD FCEV H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hd_fcev_h2_subsidy_limit():
    return 10**9


@component.add(
    name="HD FCEV H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "hd_fcev_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def hd_fcev_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(hd_fcev_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                hd_fcev_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), hd_fcev_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="HD subsidy ban",
    units="boolean",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def hd_subsidy_ban():
    return step(__data["time"], 0, 2025)


@component.add(
    name="HT subsidy ban",
    units="boolean",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def ht_subsidy_ban():
    return step(__data["time"], 0, 2025)


@component.add(
    name="LD FCEV H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "ld_fcev_h2_cost": 1},
)
def ld_fcev_h2_actual_subsidy():
    return green_h2_cost() - ld_fcev_h2_cost()


@component.add(
    name="LD FCEV H2 cost",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fcev_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def ld_fcev_h2_cost():
    return float(
        np.maximum(
            0.1,
            if_then_else(
                ld_fcev_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - ld_fcev_h2_subsidy(),
        )
    )


@component.add(
    name="LD FCEV H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "light_duty_subsidy_ytd": 1,
        "ld_fcev_h2_subsidy_limit": 1,
        "ld_fcev_h2_subsidy_length": 1,
        "ld_fcev_h2_subsidy_size": 1,
        "time": 1,
    },
)
def ld_fcev_h2_subsidy():
    return if_then_else(
        light_duty_subsidy_ytd() < ld_fcev_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=ld_fcev_h2_subsidy_length())
        * ld_fcev_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="LD FCEV H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def ld_fcev_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="LD FCEV H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ld_fcev_h2_subsidy_limit():
    return 10**9


@component.add(
    name="LD FCEV H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ld_fcev_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def ld_fcev_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(ld_fcev_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                ld_fcev_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), ld_fcev_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="MeOH DS H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "meoh_ds_h2_cost": 1},
)
def meoh_ds_h2_actual_subsidy():
    return green_h2_cost() - meoh_ds_h2_cost()


@component.add(
    name="MeOH DS H2 cost",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_ds_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def meoh_ds_h2_cost():
    return float(
        np.maximum(
            0.1,
            if_then_else(
                meoh_ds_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - meoh_ds_h2_subsidy(),
        )
    )


@component.add(
    name="MeOH DS H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "shipping_meoh_subsidy_ytd": 1,
        "meoh_ds_h2_subsidy_limit": 1,
        "meoh_ds_h2_subsidy_size": 1,
        "meoh_ds_h2_subsidy_length": 1,
        "time": 1,
    },
)
def meoh_ds_h2_subsidy():
    return if_then_else(
        shipping_meoh_subsidy_ytd() < meoh_ds_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=meoh_ds_h2_subsidy_length())
        * meoh_ds_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="MeOH DS H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def meoh_ds_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="MeOH DS H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def meoh_ds_h2_subsidy_limit():
    return 10**9


@component.add(
    name="MeOH DS H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_ds_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def meoh_ds_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(meoh_ds_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                meoh_ds_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), meoh_ds_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="MeOH IS H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "meoh_is_h2_cost": 1},
)
def meoh_is_h2_actual_subsidy():
    return green_h2_cost() - meoh_is_h2_cost()


@component.add(
    name="MeOH IS H2 cost",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_is_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def meoh_is_h2_cost():
    return float(
        np.maximum(
            0.1,
            if_then_else(
                meoh_is_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - meoh_is_h2_subsidy(),
        )
    )


@component.add(
    name="MeOH IS H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "shipping_meoh_subsidy_ytd": 1,
        "meoh_is_h2_subsidy_limit": 1,
        "meoh_is_h2_subsidy_size": 1,
        "meoh_is_h2_subsidy_length": 1,
        "time": 1,
    },
)
def meoh_is_h2_subsidy():
    return if_then_else(
        shipping_meoh_subsidy_ytd() < meoh_is_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=meoh_is_h2_subsidy_length())
        * meoh_is_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="MeOH IS H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def meoh_is_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="MeOH IS H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def meoh_is_h2_subsidy_limit():
    return 10**9


@component.add(
    name="MeOH IS H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "meoh_is_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def meoh_is_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(meoh_is_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                meoh_is_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), meoh_is_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="NH3 IS H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "nh3_is_h2_cost": 1},
)
def nh3_is_h2_actual_subsidy():
    return green_h2_cost() - nh3_is_h2_cost()


@component.add(
    name="NH3 IS H2 cost",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nh3_is_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def nh3_is_h2_cost():
    return float(
        np.maximum(
            0.1,
            if_then_else(
                nh3_is_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - nh3_is_h2_subsidy(),
        )
    )


@component.add(
    name="NH3 IS H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "shipping_nh3_subsidy_ytd": 1,
        "nh3_is_h2_subsidy_limit": 1,
        "nh3_is_h2_subsidy_size": 1,
        "nh3_is_h2_subsidy_length": 1,
        "time": 1,
    },
)
def nh3_is_h2_subsidy():
    return if_then_else(
        shipping_nh3_subsidy_ytd() < nh3_is_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=nh3_is_h2_subsidy_length())
        * nh3_is_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="NH3 IS H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def nh3_is_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="NH3 IS H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def nh3_is_h2_subsidy_limit():
    return 10**9


@component.add(
    name="NH3 IS H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nh3_is_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def nh3_is_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(nh3_is_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                nh3_is_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), nh3_is_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="NM H2 actual subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "nm_h2_cost": 1},
)
def nm_h2_actual_subsidy():
    return green_h2_cost() - nm_h2_cost()


@component.add(
    name="NM H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "nm_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
        "ht_subsidy_ban": 1,
    },
)
def nm_h2_cost():
    return (
        float(
            np.maximum(
                0.1,
                if_then_else(
                    nm_h2_subsidy() > 0,
                    lambda: derisked_green_h2_cost(),
                    lambda: green_h2_cost(),
                )
                - nm_h2_subsidy(),
            )
        )
        + ht_subsidy_ban() * 1000
    )


@component.add(
    name="NM H2 GJ cost",
    units="€/GJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nm_h2_cost": 1},
)
def nm_h2_gj_cost():
    return nm_h2_cost() / 120 * 1000


@component.add(
    name="NM H2 subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "high_temperature_subsidy_ytd": 1,
        "nm_h2_subsidy_limit": 1,
        "nm_h2_subsidy_length": 1,
        "nm_h2_subsidy_size": 1,
        "time": 1,
    },
)
def nm_h2_subsidy():
    return if_then_else(
        high_temperature_subsidy_ytd() < nm_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=nm_h2_subsidy_length())
        * nm_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="NM H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def nm_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="NM H2 subsidy limit", units="M€", comp_type="Constant", comp_subtype="Normal"
)
def nm_h2_subsidy_limit():
    return 10**9


@component.add(
    name="NM H2 subsidy size",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2_nm_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def nm_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(h2_nm_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                h2_nm_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), h2_nm_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="pulse H2 subsidy",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"h2_subsidy_length": 1, "time": 1},
)
def pulse_h2_subsidy():
    return pulse(__data["time"], 2025, width=h2_subsidy_length())


@component.add(
    name="refinery H2 actual subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "refinery_h2_cost": 1},
)
def refinery_h2_actual_subsidy():
    return green_h2_cost() - refinery_h2_cost()


@component.add(
    name="refinery H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "refinery_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def refinery_h2_cost():
    return float(
        np.maximum(
            0.1,
            if_then_else(
                refinery_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - refinery_h2_subsidy(),
        )
    )


@component.add(
    name="refinery H2 subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "refinery_subsidy_ytd": 1,
        "refinery_h2_subsidy_limit": 1,
        "refinery_h2_subsidy_length": 1,
        "refinery_h2_subsidy_size": 1,
        "time": 1,
    },
)
def refinery_h2_subsidy():
    return if_then_else(
        refinery_subsidy_ytd() < refinery_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=refinery_h2_subsidy_length())
        * refinery_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="refinery H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def refinery_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="refinery H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def refinery_h2_subsidy_limit():
    return 10**9


@component.add(
    name="refinery H2 subsidy size",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "green_refinery_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def refinery_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(
                        green_refinery_h2_wtp_gap() + bid_increase(), hba_max_subsidy()
                    )
                ),
                green_refinery_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(
                        hba_max_subsidy(), green_refinery_h2_wtp_gap() + bid_increase()
                    )
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="steel H2 actual subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "steel_h2_cost": 1},
)
def steel_h2_actual_subsidy():
    return green_h2_cost() - steel_h2_cost()


@component.add(
    name="steel H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_h2_subsidy": 2, "derisked_green_h2_cost": 1, "green_h2_cost": 1},
)
def steel_h2_cost():
    return float(
        np.maximum(
            0.1,
            if_then_else(
                steel_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - steel_h2_subsidy(),
        )
    )


@component.add(
    name="steel H2 subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "steel_subsidy_ytd": 1,
        "steel_h2_subsidy_limit": 1,
        "steel_h2_subsidy_size": 1,
        "steel_h2_subsidy_length": 1,
        "time": 1,
    },
)
def steel_h2_subsidy():
    return if_then_else(
        steel_subsidy_ytd() < steel_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=steel_h2_subsidy_length())
        * steel_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="steel H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def steel_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="steel H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def steel_h2_subsidy_limit():
    return 10**9


@component.add(
    name="steel H2 subsidy size",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "h2dri_eaf_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def steel_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(
                        h2dri_eaf_h2_wtp_gap() + bid_increase(), hba_max_subsidy()
                    )
                ),
                h2dri_eaf_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(
                        hba_max_subsidy(), h2dri_eaf_h2_wtp_gap() + bid_increase()
                    )
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="subsidized electrolysis capacity",
    units="GW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_subsidized_electrolysis_capacity": 1},
    other_deps={
        "_integ_subsidized_electrolysis_capacity": {
            "initial": {},
            "step": {
                "electrolyzer_investments": 1,
                "pulse_h2_subsidy": 1,
                "support_terminations": 1,
            },
        }
    },
)
def subsidized_electrolysis_capacity():
    return _integ_subsidized_electrolysis_capacity()


_integ_subsidized_electrolysis_capacity = Integ(
    lambda: electrolyzer_investments() * pulse_h2_subsidy() - support_terminations(),
    lambda: 0,
    "_integ_subsidized_electrolysis_capacity",
)


@component.add(
    name="subsidized green H2 production",
    units="t H2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "subsidized_electrolysis_capacity": 1,
        "electrolyser_operating_hours": 1,
        "aec_efficiency": 1,
    },
)
def subsidized_green_h2_production():
    return (
        subsidized_electrolysis_capacity()
        * electrolyser_operating_hours()
        * aec_efficiency()
        * 1000
        / 33.33
    )


@component.add(
    name="subsidy payout",
    units="B€/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"subsidized_green_h2_production": 1, "green_h2_subsidy_size": 1},
)
def subsidy_payout():
    return subsidized_green_h2_production() * green_h2_subsidy_size() / 10**6


@component.add(
    name="support terminations",
    units="GW",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_support_terminations": 1},
    other_deps={
        "_delayfixed_support_terminations": {
            "initial": {},
            "step": {"electrolyzer_investments": 1, "pulse_h2_subsidy": 1},
        }
    },
)
def support_terminations():
    return _delayfixed_support_terminations()


_delayfixed_support_terminations = DelayFixed(
    lambda: electrolyzer_investments() * pulse_h2_subsidy(),
    lambda: 10,
    lambda: 0,
    time_step,
    "_delayfixed_support_terminations",
)


@component.add(
    name="SynKero H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "synkero_h2_cost": 1},
)
def synkero_h2_actual_subsidy():
    return green_h2_cost() - synkero_h2_cost()


@component.add(
    name="SynKero H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synkero_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def synkero_h2_cost():
    return float(
        np.maximum(
            if_then_else(
                synkero_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - synkero_h2_subsidy(),
            0.1,
        )
    )


@component.add(
    name="SynKero H2 subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "domestic_aviation_subsidy_ytd": 1,
        "international_aviation_subsidy_ytd": 1,
        "synkero_h2_subsidy_limit": 1,
        "synkero_h2_subsidy_length": 1,
        "synkero_h2_subsidy_size": 1,
        "time": 1,
    },
)
def synkero_h2_subsidy():
    return if_then_else(
        domestic_aviation_subsidy_ytd() + international_aviation_subsidy_ytd()
        < synkero_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=synkero_h2_subsidy_length())
        * synkero_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="SynKero H2 subsidy length",
    units="years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def synkero_h2_subsidy_length():
    return 10


@component.add(
    name="SynKero H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def synkero_h2_subsidy_limit():
    return 10**9


@component.add(
    name="SynKero H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synkero_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def synkero_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(synkero_h2_wtp_gap() + bid_increase(), hba_max_subsidy())
                ),
                synkero_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(hba_max_subsidy(), synkero_h2_wtp_gap() + bid_increase())
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="SynNaphtha H2 actual subsidy",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"green_h2_cost": 1, "synnaphtha_h2_cost": 1},
)
def synnaphtha_h2_actual_subsidy():
    return green_h2_cost() - synnaphtha_h2_cost()


@component.add(
    name="SynNaphtha H2 cost",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synnaphtha_h2_subsidy": 2,
        "derisked_green_h2_cost": 1,
        "green_h2_cost": 1,
    },
)
def synnaphtha_h2_cost():
    return float(
        np.maximum(
            if_then_else(
                synnaphtha_h2_subsidy() > 0,
                lambda: derisked_green_h2_cost(),
                lambda: green_h2_cost(),
            )
            - synnaphtha_h2_subsidy(),
            0.1,
        )
    )


@component.add(
    name="SynNaphtha H2 subsidy",
    units="€/kgH2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "naphtha_subsidy_ytd": 1,
        "synnaphtha_h2_subsidy_limit": 1,
        "synnaphtha_h2_subsidy_length": 1,
        "synnaphtha_h2_subsidy_size": 1,
        "time": 1,
    },
)
def synnaphtha_h2_subsidy():
    return if_then_else(
        naphtha_subsidy_ytd() < synnaphtha_h2_subsidy_limit(),
        lambda: pulse(__data["time"], 2025, width=synnaphtha_h2_subsidy_length())
        * synnaphtha_h2_subsidy_size(),
        lambda: 0,
    )


@component.add(
    name="SynNaphtha H2 subsidy length",
    units="years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hba_duration": 1},
)
def synnaphtha_h2_subsidy_length():
    return hba_duration()


@component.add(
    name="SynNaphtha H2 subsidy limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def synnaphtha_h2_subsidy_limit():
    return 10**9


@component.add(
    name="SynNaphtha H2 subsidy size",
    units="€/kg",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "synnaphtha_h2_wtp_gap": 3,
        "bid_increase": 2,
        "hba_max_subsidy": 2,
        "hba_auction_cleared": 1,
    },
)
def synnaphtha_h2_subsidy_size():
    return if_then_else(
        float(
            np.maximum(
                float(
                    np.minimum(
                        synnaphtha_h2_wtp_gap() + bid_increase(), hba_max_subsidy()
                    )
                ),
                synnaphtha_h2_wtp_gap(),
            )
        )
        <= hba_auction_cleared(),
        lambda: float(
            np.maximum(
                0.001,
                float(
                    np.minimum(
                        hba_max_subsidy(), synnaphtha_h2_wtp_gap() + bid_increase()
                    )
                ),
            )
        ),
        lambda: 0,
    )


@component.add(
    name="total subsidy cost",
    units="B€",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_total_subsidy_cost": 1},
    other_deps={
        "_integ_total_subsidy_cost": {"initial": {}, "step": {"subsidy_payout": 1}}
    },
)
def total_subsidy_cost():
    return _integ_total_subsidy_cost()


_integ_total_subsidy_cost = Integ(
    lambda: subsidy_payout(), lambda: 0, "_integ_total_subsidy_cost"
)


@component.add(
    name="WAC green H2",
    units="€/kgH2",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_wac_green_h2": 1},
    other_deps={
        "_integ_wac_green_h2": {
            "initial": {
                "green_h2_cost": 1,
                "pilot_plant_capacity": 1,
                "electrolyser_capacity": 1,
            },
            "step": {
                "electrolyzer_investments": 1,
                "electrolyser_capacity": 2,
                "wac_green_h2": 2,
                "green_h2_cost": 1,
                "delay_green_h2_cost": 1,
                "support_terminations": 1,
            },
        }
    },
)
def wac_green_h2():
    return _integ_wac_green_h2()


_integ_wac_green_h2 = Integ(
    lambda: electrolyzer_investments()
    / electrolyser_capacity()
    * (green_h2_cost() - wac_green_h2())
    - support_terminations()
    / electrolyser_capacity()
    * (delay_green_h2_cost() - wac_green_h2()),
    lambda: green_h2_cost() * pilot_plant_capacity() / electrolyser_capacity(),
    "_integ_wac_green_h2",
)


@component.add(
    name="yearly total subsidies limit",
    units="M€",
    comp_type="Constant",
    comp_subtype="Normal",
)
def yearly_total_subsidies_limit():
    return 10000 * 100
