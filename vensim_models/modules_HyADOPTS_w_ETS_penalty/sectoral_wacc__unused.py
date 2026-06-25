"""
Module sectoral_wacc__unused
Translated using PySD version 3.14.3
"""

@component.add(
    name="aviation wacc", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def aviation_wacc():
    """
    Air Transport WACC from source.
    """
    return 0.0606


@component.add(
    name="chemical wacc", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def chemical_wacc():
    """
    Chemical (basic) WACC from source
    """
    return 0.0732


@component.add(
    name="shipping wacc", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def shipping_wacc():
    """
    Shipbuilding and marine WACC from source
    """
    return 0.0674


@component.add(
    name="steel wacc", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def steel_wacc():
    """
    Steel WACC from source
    """
    return 0.0818


@component.add(
    name="transportation wacc",
    units="percent",
    comp_type="Constant",
    comp_subtype="Normal",
)
def transportation_wacc():
    """
    Transportation WACC from source
    """
    return 0.0825


@component.add(
    name="trucking wacc", units="percent", comp_type="Constant", comp_subtype="Normal"
)
def trucking_wacc():
    """
    Trucking WACC from source
    """
    return 0.0827
