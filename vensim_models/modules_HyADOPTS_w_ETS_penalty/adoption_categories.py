"""
Module adoption_categories
Translated using PySD version 3.14.3
"""

@component.add(
    name="early adopters", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def early_adopters():
    return 0.1


@component.add(
    name="early majority", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def early_majority():
    return 0.34


@component.add(
    name="inno switch level", units="Dmnl", comp_type="Constant", comp_subtype="Normal"
)
def inno_switch_level():
    return 0.5


@component.add(
    name="innovators", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def innovators():
    return 0.05


@component.add(
    name="laggards", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def laggards():
    return 0.16


@component.add(
    name="late majority", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def late_majority():
    return 0.34
