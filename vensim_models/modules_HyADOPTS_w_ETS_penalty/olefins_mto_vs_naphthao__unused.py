"""
Module olefins_mto_vs_naphthao__unused
Translated using PySD version 3.14.3
"""

@component.add(
    name="BF cracking competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_cracking_cost": 3,
        "fossil_cracking_cost": 1,
        "mto_cost": 1,
        "e_cracking_cost": 1,
    },
)
def bf_cracking_competitiveness():
    return float(
        np.maximum(
            bf_cracking_cost() / fossil_cracking_cost(),
            float(
                np.maximum(
                    bf_cracking_cost() / e_cracking_cost(),
                    bf_cracking_cost() / mto_cost(),
                )
            ),
        )
    )


@component.add(
    name="BF cracking cost", units="€/t", comp_type="Constant", comp_subtype="Normal"
)
def bf_cracking_cost():
    return 300


@component.add(
    name="BF cracking decay",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bio_fueled_cracking": 1, "cracker_lifetime": 1},
)
def bf_cracking_decay():
    return bio_fueled_cracking() / cracker_lifetime()


@component.add(
    name="BF cracking imitators",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_cracking_investment_level": 1, "cracking_reinvestment": 1},
)
def bf_cracking_imitators():
    return bf_cracking_investment_level() * cracking_reinvestment()


@component.add(
    name="BF cracking inno switch",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_cracking_competitiveness": 1},
)
def bf_cracking_inno_switch():
    return if_then_else(bf_cracking_competitiveness() < 2, lambda: 1, lambda: 0)


@component.add(
    name="BF cracking innovators",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_cracking_inno_switch": 1,
        "cracking_reinvestment": 1,
        "innovators": 1,
    },
)
def bf_cracking_innovators():
    return bf_cracking_inno_switch() * cracking_reinvestment() * innovators()


@component.add(
    name="BF cracking investment",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"bf_cracking_imitators": 1, "bf_cracking_innovators": 1},
)
def bf_cracking_investment():
    return bf_cracking_imitators() + bf_cracking_innovators()


@component.add(
    name="BF cracking investment level",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"olefin_equalizer": 1, "bf_cracking_level": 1},
)
def bf_cracking_investment_level():
    return olefin_equalizer() * bf_cracking_level()


@component.add(
    name="BF cracking level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_cracking_competitiveness": 1,
        "bio_fueled_cracking": 1,
        "olefin_capacity": 1,
    },
)
def bf_cracking_level():
    return (
        1
        / (1 + float(np.exp(10 * (bf_cracking_competitiveness() - 1.1))))
        * bio_fueled_cracking()
        / olefin_capacity()
    )


@component.add(
    name="Bio fueled cracking",
    units="tOlefins",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_bio_fueled_cracking": 1},
    other_deps={
        "_integ_bio_fueled_cracking": {
            "initial": {},
            "step": {"bf_cracking_investment": 1, "bf_cracking_decay": 1},
        }
    },
)
def bio_fueled_cracking():
    return _integ_bio_fueled_cracking()


_integ_bio_fueled_cracking = Integ(
    lambda: bf_cracking_investment() - bf_cracking_decay(),
    lambda: 0,
    "_integ_bio_fueled_cracking",
)


@component.add(
    name="check olefin",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bio_fueled_cracking": 1,
        "mto": 1,
        "electrical_cracking": 1,
        "fossil_cracking": 1,
    },
)
def check_olefin():
    return bio_fueled_cracking() + mto() + electrical_cracking() + fossil_cracking()


@component.add(name="cracker lifetime", comp_type="Constant", comp_subtype="Normal")
def cracker_lifetime():
    return 20


@component.add(
    name="cracking reinvestment",
    units="GWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cracking_reinvestment": 1},
    other_deps={
        "_integ_cracking_reinvestment": {
            "initial": {"olefin_production": 1, "cracker_lifetime": 1},
            "step": {
                "bf_cracking_decay": 1,
                "demand_change_olefin": 1,
                "e_cracking_decay": 1,
                "f_cracking_decay": 1,
                "mto_decay": 1,
                "bf_cracking_investment": 1,
                "e_cracking_investment": 1,
                "f_cracking_investment": 1,
                "mto_investment": 1,
            },
        }
    },
)
def cracking_reinvestment():
    return _integ_cracking_reinvestment()


_integ_cracking_reinvestment = Integ(
    lambda: bf_cracking_decay()
    + demand_change_olefin()
    + e_cracking_decay()
    + f_cracking_decay()
    + mto_decay()
    - bf_cracking_investment()
    - e_cracking_investment()
    - f_cracking_investment()
    - mto_investment(),
    lambda: olefin_production() / cracker_lifetime(),
    "_integ_cracking_reinvestment",
)


@component.add(
    name="ctrl olefin",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"k_p": 1, "error_olefin": 1, "error_int_olefin": 1},
)
def ctrl_olefin():
    return k_p() * error_olefin() + error_int_olefin()


@component.add(
    name="demand change olefin",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ctrl_olefin": 1},
)
def demand_change_olefin():
    return ctrl_olefin()


@component.add(
    name="E cracking competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "e_cracking_cost": 3,
        "fossil_cracking_cost": 1,
        "mto_cost": 1,
        "bf_cracking_cost": 1,
    },
)
def e_cracking_competitiveness():
    return float(
        np.maximum(
            e_cracking_cost() / fossil_cracking_cost(),
            float(
                np.maximum(
                    e_cracking_cost() / bf_cracking_cost(),
                    e_cracking_cost() / mto_cost(),
                )
            ),
        )
    )


@component.add(
    name="E cracking cost", units="€/t", comp_type="Constant", comp_subtype="Normal"
)
def e_cracking_cost():
    return 300


@component.add(
    name="E cracking decay",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"electrical_cracking": 1, "cracker_lifetime": 1},
)
def e_cracking_decay():
    return electrical_cracking() / cracker_lifetime()


@component.add(
    name="E cracking imitators",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cracking_reinvestment": 1, "e_cracking_investment_level": 1},
)
def e_cracking_imitators():
    return cracking_reinvestment() * e_cracking_investment_level()


@component.add(
    name="E cracking inno switch",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"e_cracking_competitiveness": 1},
)
def e_cracking_inno_switch():
    return if_then_else(e_cracking_competitiveness() < 2, lambda: 1, lambda: 0)


@component.add(
    name="E cracking innovators",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "cracking_reinvestment": 1,
        "innovators": 1,
        "e_cracking_inno_switch": 1,
    },
)
def e_cracking_innovators():
    return cracking_reinvestment() * innovators() * e_cracking_inno_switch()


@component.add(
    name="E cracking investment",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"e_cracking_innovators": 1, "e_cracking_imitators": 1},
)
def e_cracking_investment():
    return e_cracking_innovators() + e_cracking_imitators()


@component.add(
    name="E cracking investment level",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"olefin_equalizer": 1, "e_cracking_level": 1},
)
def e_cracking_investment_level():
    return olefin_equalizer() * e_cracking_level()


@component.add(
    name="E cracking level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "e_cracking_competitiveness": 1,
        "electrical_cracking": 1,
        "olefin_capacity": 1,
    },
)
def e_cracking_level():
    return (
        1
        / (1 + float(np.exp(10 * (e_cracking_competitiveness() - 1.1))))
        * electrical_cracking()
        / olefin_capacity()
    )


@component.add(
    name="Electrical cracking",
    units="tOlefins",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_electrical_cracking": 1},
    other_deps={
        "_integ_electrical_cracking": {
            "initial": {},
            "step": {"e_cracking_investment": 1, "e_cracking_decay": 1},
        }
    },
)
def electrical_cracking():
    return _integ_electrical_cracking()


_integ_electrical_cracking = Integ(
    lambda: e_cracking_investment() - e_cracking_decay(),
    lambda: 0,
    "_integ_electrical_cracking",
)


@component.add(
    name="error int olefin",
    units="e",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_error_int_olefin": 1},
    other_deps={
        "_integ_error_int_olefin": {
            "initial": {},
            "step": {"k_i": 1, "error_olefin": 1},
        }
    },
)
def error_int_olefin():
    return _integ_error_int_olefin()


_integ_error_int_olefin = Integ(
    lambda: k_i() * error_olefin(), lambda: 0, "_integ_error_int_olefin"
)


@component.add(
    name="error olefin",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"olefin_production": 1, "check_olefin": 1},
)
def error_olefin():
    return olefin_production() - check_olefin()


@component.add(
    name="F cracking competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fossil_cracking_cost": 3,
        "bf_cracking_cost": 1,
        "mto_cost": 1,
        "e_cracking_cost": 1,
    },
)
def f_cracking_competitiveness():
    return float(
        np.maximum(
            fossil_cracking_cost() / bf_cracking_cost(),
            float(
                np.maximum(
                    fossil_cracking_cost() / e_cracking_cost(),
                    fossil_cracking_cost() / mto_cost(),
                )
            ),
        )
    )


@component.add(
    name="F cracking decay",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fossil_cracking": 1, "cracker_lifetime": 1},
)
def f_cracking_decay():
    return fossil_cracking() / cracker_lifetime()


@component.add(
    name="F cracking investment",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cracking_reinvestment": 1, "f_cracking_investment_level": 1},
)
def f_cracking_investment():
    return cracking_reinvestment() * f_cracking_investment_level()


@component.add(
    name="F cracking investment level",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"olefin_equalizer": 1, "f_cracking_level": 1},
)
def f_cracking_investment_level():
    return olefin_equalizer() * f_cracking_level()


@component.add(
    name="F cracking level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "f_cracking_competitiveness": 1,
        "fossil_cracking": 1,
        "olefin_capacity": 1,
    },
)
def f_cracking_level():
    return (
        1
        / (1 + float(np.exp(10 * (f_cracking_competitiveness() - 0.9))))
        * fossil_cracking()
        / olefin_capacity()
    )


@component.add(
    name="Fossil cracking",
    units="tOlefins",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_fossil_cracking": 1},
    other_deps={
        "_integ_fossil_cracking": {
            "initial": {"olefin_production": 1},
            "step": {"f_cracking_investment": 1, "f_cracking_decay": 1},
        }
    },
)
def fossil_cracking():
    return _integ_fossil_cracking()


_integ_fossil_cracking = Integ(
    lambda: f_cracking_investment() - f_cracking_decay(),
    lambda: olefin_production(),
    "_integ_fossil_cracking",
)


@component.add(
    name="Fossil cracking cost",
    units="€/t",
    comp_type="Constant",
    comp_subtype="Normal",
)
def fossil_cracking_cost():
    return 100


@component.add(
    name="MeOH to olefin",
    units="MWh H2/t HVC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def meoh_to_olefin():
    return 5


@component.add(
    name="MtO",
    units="tOlefins",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_mto": 1},
    other_deps={
        "_integ_mto": {"initial": {}, "step": {"mto_investment": 1, "mto_decay": 1}}
    },
)
def mto():
    return _integ_mto()


_integ_mto = Integ(lambda: mto_investment() - mto_decay(), lambda: 0, "_integ_mto")


@component.add(
    name="MtO competitiveness",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "mto_cost": 3,
        "fossil_cracking_cost": 1,
        "e_cracking_cost": 1,
        "bf_cracking_cost": 1,
    },
)
def mto_competitiveness():
    return float(
        np.maximum(
            mto_cost() / fossil_cracking_cost(),
            float(
                np.maximum(
                    mto_cost() / e_cracking_cost(), mto_cost() / bf_cracking_cost()
                )
            ),
        )
    )


@component.add(
    name="MtO cost", units="€/t", comp_type="Constant", comp_subtype="Normal"
)
def mto_cost():
    return 400


@component.add(
    name="MtO decay",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"mto": 1, "cracker_lifetime": 1},
)
def mto_decay():
    return mto() / cracker_lifetime()


@component.add(
    name="MtO hydrogen demand",
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"mto": 1, "meoh_to_olefin": 1},
)
def mto_hydrogen_demand():
    return mto() * meoh_to_olefin() / 33.33


@component.add(
    name="MtO imitators",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cracking_reinvestment": 1, "mto_investment_level": 1},
)
def mto_imitators():
    return cracking_reinvestment() * mto_investment_level()


@component.add(
    name="MtO inno switch",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"mto_competitiveness": 1},
)
def mto_inno_switch():
    return if_then_else(mto_competitiveness() < 2, lambda: 1, lambda: 0)


@component.add(
    name="MtO innovators",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cracking_reinvestment": 1, "innovators": 1, "mto_inno_switch": 1},
)
def mto_innovators():
    return cracking_reinvestment() * innovators() * mto_inno_switch()


@component.add(
    name="MtO investment",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"mto_imitators": 1, "mto_innovators": 1},
)
def mto_investment():
    return mto_imitators() + mto_innovators()


@component.add(
    name="MtO investment level",
    units="percent",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"olefin_equalizer": 1, "mto_level": 1},
)
def mto_investment_level():
    return olefin_equalizer() * mto_level()


@component.add(
    name="MtO level",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"mto_competitiveness": 1, "mto": 1, "olefin_capacity": 1},
)
def mto_level():
    return (
        1
        / (1 + float(np.exp(10 * (mto_competitiveness() - 1.1))))
        * mto()
        / olefin_capacity()
    )


@component.add(
    name="olefin capacity",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bio_fueled_cracking": 1,
        "fossil_cracking": 1,
        "electrical_cracking": 1,
        "mto": 1,
    },
)
def olefin_capacity():
    return bio_fueled_cracking() + fossil_cracking() + electrical_cracking() + mto()


@component.add(
    name="olefin equalizer",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "bf_cracking_level": 1,
        "mto_level": 1,
        "e_cracking_level": 1,
        "f_cracking_level": 1,
    },
)
def olefin_equalizer():
    return 1 / (
        bf_cracking_level() + mto_level() + e_cracking_level() + f_cracking_level()
    )


@component.add(
    name="olefin production",
    units="tOlefins",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def olefin_production():
    """
    20% decrease in connection to plastic production forecasts
    """
    return np.interp(time(), [2019.0, 2050.0], [41495000.0, 33196000.0])
