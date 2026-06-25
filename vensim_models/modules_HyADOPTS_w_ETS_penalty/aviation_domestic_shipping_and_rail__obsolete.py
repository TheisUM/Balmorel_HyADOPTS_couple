"""
Module aviation_domestic_shipping_and_rail__obsolete
Translated using PySD version 3.14.3
"""

@component.add(
    name="aviation",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def aviation():
    """
    That is 1.9% average annual growth per year over the 2017-2040 period. The traffic growth will be faster in the early years (2018-2030) than in the late years (2030-2040). Estimated 2.1% (2019-2030), 1.7% (2030-2040), 1.5% (2040-2050).
    !year
    !GWh
    """
    return np.interp(
        time(), [2019.0, 2030.0, 2040.0, 2050.0], [75721.7, 95170.8, 112645.0, 130729.0]
    )


@component.add(
    name="BEV implementation curve",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def bev_implementation_curve():
    return np.interp(
        time(),
        [
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
            0.0,
            0.0,
            0.01,
            0.01,
            0.02,
            0.03,
            0.04,
            0.05,
            0.07,
            0.09,
            0.12,
            0.16,
            0.2,
            0.27,
            0.33,
            0.41,
            0.49,
            0.57,
            0.65,
            0.72,
            0.79,
            0.84,
            0.89,
            0.91,
            0.94,
            0.96,
            0.97,
            0.98,
            0.99,
            0.99,
            0.996294,
            0.998147,
        ],
    )


@component.add(
    name='"bio kerosene - hydrogen rate"',
    units="MWh H2 / MWh kero",
    comp_type="Constant",
    comp_subtype="Normal",
)
def bio_kerosene_hydrogen_rate():
    return 0.15


@component.add(
    name="biofuel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"biofuel_curve": 1, "medium_long_range": 1},
)
def biofuel():
    return biofuel_curve() * medium_long_range()


@component.add(
    name="biofuel curve",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def biofuel_curve():
    return np.interp(
        time(),
        [2019.0, 2025.32, 2028.22, 2031.21, 2033.31, 2035.6, 2038.85, 2043.85, 2050.0],
        [
            0.0,
            0.00151515,
            0.0287879,
            0.0909091,
            0.143939,
            0.215152,
            0.290909,
            0.356061,
            0.4,
        ],
    )


@component.add(
    name="biofuels share",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rail_electricity_share": 1, "time": 1},
)
def biofuels_share():
    return if_then_else(
        rail_electricity_share() < 1,
        lambda: (0.1857 * (time() - 2019) + 0.012) / 100,
        lambda: 0,
    )


@component.add(
    name='"bio-kerosene energy consumption dom. aviation"',
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "decarbonization_curve_dom_aviation": 1,
        "dom_aviation_energy_consumption": 1,
        "hydrogen_energy_consumption_dom_aviation": 1,
    },
)
def biokerosene_energy_consumption_dom_aviation():
    return (
        decarbonization_curve_dom_aviation() * dom_aviation_energy_consumption()
        - hydrogen_energy_consumption_dom_aviation()
    ) * 1


@component.add(
    name='"bio-kerosene energy consumption int. aviation"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "decarbonization_curve_int_aviation": 1,
        "int_aviation_energy_consumption": 1,
    },
)
def biokerosene_energy_consumption_int_aviation():
    return decarbonization_curve_int_aviation() * int_aviation_energy_consumption() * 1


@component.add(
    name='"commuter/regional"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"aviation": 1},
)
def commuterregional():
    return 0.03 * aviation()


@component.add(
    name='"decarbonization curve dom. aviation"',
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def decarbonization_curve_dom_aviation():
    return np.interp(
        time(),
        [
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
            0.0,
            0.0,
            0.01,
            0.01,
            0.02,
            0.03,
            0.04,
            0.05,
            0.07,
            0.09,
            0.12,
            0.16,
            0.2,
            0.27,
            0.33,
            0.41,
            0.49,
            0.57,
            0.65,
            0.72,
            0.79,
            0.84,
            0.89,
            0.91,
            0.94,
            0.96,
            0.97,
            0.98,
            0.99,
            0.99,
            0.996294,
            0.998147,
        ],
    )


@component.add(
    name='"decarbonization curve int. aviation"',
    units="{%}",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def decarbonization_curve_int_aviation():
    return np.interp(
        time(),
        [
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
            0.0,
            0.0,
            0.01,
            0.01,
            0.02,
            0.03,
            0.04,
            0.05,
            0.07,
            0.09,
            0.12,
            0.16,
            0.2,
            0.27,
            0.33,
            0.41,
            0.49,
            0.57,
            0.65,
            0.72,
            0.79,
            0.84,
            0.89,
            0.91,
            0.94,
            0.96,
            0.97,
            0.98,
            0.99,
            0.99,
            0.996294,
            0.998147,
        ],
    )


@component.add(
    name="diesel locomotive efficiency", comp_type="Constant", comp_subtype="Normal"
)
def diesel_locomotive_efficiency():
    return 0.3


@component.add(
    name='"dom. aviation energy consumption"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def dom_aviation_energy_consumption():
    return np.interp(time(), [2019, 2050], [75722, 109601])


@component.add(
    name='"dom. navigation energy consumption"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def dom_navigation_energy_consumption():
    """
    Considering an annual growth rate of 2.64%
    """
    return np.interp(time(), [2019, 2050], [49177, 97795])


@component.add(
    name='"dom. navigation energy demand"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"dom_navigation_energy_consumption": 1, "ice_efficiency_0": 1},
)
def dom_navigation_energy_demand():
    return dom_navigation_energy_consumption() * ice_efficiency_0()


@component.add(
    name='"dom. navigation fossil energy consumption"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"dom_navigation_fossil_fuel_demand": 1, "ice_efficiency_0": 1},
)
def dom_navigation_fossil_energy_consumption():
    return dom_navigation_fossil_fuel_demand() / ice_efficiency_0()


@component.add(
    name='"dom. navigation fossil fuel demand"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"dom_navigation_energy_demand": 1, "bev_implementation_curve": 1},
)
def dom_navigation_fossil_fuel_demand():
    return dom_navigation_energy_demand() * (1 - bev_implementation_curve())


@component.add(
    name="electric aircraft",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"commuterregional": 1, "electric_aircraft_curve": 1},
)
def electric_aircraft():
    return commuterregional() * electric_aircraft_curve()


@component.add(
    name="electric aircraft curve",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def electric_aircraft_curve():
    """

    !Year
    !share (%)
    """
    return np.interp(
        time(),
        [
            2019.0,
            2025.15,
            2029.98,
            2032.52,
            2034.02,
            2035.16,
            2037.18,
            2039.29,
            2041.13,
            2043.85,
            2046.66,
            2050.0,
        ],
        [
            0.0,
            0.00378788,
            0.0530303,
            0.155303,
            0.265152,
            0.344697,
            0.518939,
            0.715909,
            0.840909,
            0.931818,
            0.977273,
            1.0,
        ],
    )


@component.add(
    name="fossil energy consumption from rail",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fossil_energy_demand": 1, "diesel_locomotive_efficiency": 1},
)
def fossil_energy_consumption_from_rail():
    return fossil_energy_demand() / diesel_locomotive_efficiency()


@component.add(
    name="fossil energy demand",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "rail_energy_demand": 1,
        "rail_electricity_share": 1,
        "biofuels_share": 1,
    },
)
def fossil_energy_demand():
    return (
        rail_energy_demand() * (1 - rail_electricity_share()) * (1 - biofuels_share())
    )


@component.add(
    name="fossil substitution aviation",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "electric_aircraft": 1,
        "hydrogen_aircraft": 1,
        "biofuel": 1,
        "synfuel": 1,
    },
)
def fossil_substitution_aviation():
    return electric_aircraft() + hydrogen_aircraft() + biofuel() + synfuel()


@component.add(
    name="hydrogen aircraft",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"short_hydrogen_aircraft_curve": 1, "short_range": 1},
)
def hydrogen_aircraft():
    return short_hydrogen_aircraft_curve() * short_range()


@component.add(
    name='"hydrogen energy consumption dom. aviation"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "dom_aviation_energy_consumption": 1,
        "hydrogen_penetration_in_dom_aviation": 1,
    },
)
def hydrogen_energy_consumption_dom_aviation():
    return dom_aviation_energy_consumption() * hydrogen_penetration_in_dom_aviation()


@component.add(
    name='"HYDROGEN F. AVIATON"',
    units="t H2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "biokerosene_energy_consumption_dom_aviation": 1,
        "biokerosene_energy_consumption_int_aviation": 1,
        "bio_kerosene_hydrogen_rate": 1,
        "syn_kerosene_hydrogen_rate": 1,
        "synthetic_kerosene_energy_consumption_dom_aviation": 1,
        "synthetic_kerosene_energy_consumption_int_aviation": 1,
        "hydrogen_energy_consumption_dom_aviation": 1,
    },
)
def hydrogen_f_aviaton():
    """
    33.33 MWh/t = calorific power H2
    """
    return (
        (
            (
                biokerosene_energy_consumption_dom_aviation()
                + biokerosene_energy_consumption_int_aviation()
            )
            * bio_kerosene_hydrogen_rate()
            + (
                synthetic_kerosene_energy_consumption_dom_aviation()
                + synthetic_kerosene_energy_consumption_int_aviation()
            )
            * syn_kerosene_hydrogen_rate()
            + hydrogen_energy_consumption_dom_aviation()
        )
        * 10**3
        / 33.33
    )


@component.add(
    name='"hydrogen penetration in dom. aviation"',
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def hydrogen_penetration_in_dom_aviation():
    return np.interp(
        time(),
        [
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
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.01,
            0.01,
            0.02,
            0.03,
            0.04,
            0.05,
            0.07,
            0.09,
            0.12,
            0.16,
            0.2,
            0.27,
            0.33,
            0.41,
            0.49,
            0.57,
            0.65,
            0.72,
            0.79,
        ],
    )


@component.add(name="ICE efficiency 0", comp_type="Constant", comp_subtype="Normal")
def ice_efficiency_0():
    """
    Considering the same efficiency for all the fossil fuel engines
    """
    return 0.45


@component.add(
    name='"int. aviation energy consumption"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def int_aviation_energy_consumption():
    return np.interp(time(), [2019, 2050], [486033, 703496])


@component.add(
    name="kerosene",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"aviation": 1, "fossil_substitution_aviation": 1},
)
def kerosene():
    return aviation() - fossil_substitution_aviation()


@component.add(
    name="medium long range",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"aviation": 1},
)
def medium_long_range():
    return 0.73 * aviation()


@component.add(
    name="rail electricity share",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def rail_electricity_share():
    return np.interp(time(), [2019.0, 2038.0, 2050.0], [0.7615, 1.0, 1.0])


@component.add(
    name="rail energy demand",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def rail_energy_demand():
    return np.interp(time(), [2019, 2050], [47212, 39177])


@component.add(
    name="short hydrogen aircraft curve",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def short_hydrogen_aircraft_curve():
    return np.interp(
        time(),
        [2019.0, 2029.98, 2033.58, 2037.97, 2040.78, 2044.91, 2050.0],
        [0.0, 0.0568182, 0.166667, 0.583333, 0.80303, 0.912879, 1.0],
    )


@component.add(
    name="short range",
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"aviation": 1},
)
def short_range():
    return 0.24 * aviation()


@component.add(
    name='"syn kerosene - hydrogen rate"',
    units="MWh H2 / MWh kero",
    comp_type="Constant",
    comp_subtype="Normal",
)
def syn_kerosene_hydrogen_rate():
    return 1.2


@component.add(
    name="synfuel",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"synfuel_curve": 1, "medium_long_range": 1},
)
def synfuel():
    return synfuel_curve() * medium_long_range()


@component.add(
    name="synfuel curve",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def synfuel_curve():
    return np.interp(
        time(),
        [2019.0, 2025.0, 2028.48, 2033.4, 2036.83, 2039.81, 2043.59, 2047.54, 2050.0],
        [0.0, 0.0, 0.0212121, 0.129545, 0.231818, 0.354545, 0.438636, 0.484091, 0.5],
    )


@component.add(
    name='"synthetic kerosene energy consumption dom. aviation"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "dom_aviation_energy_consumption": 1,
        "decarbonization_curve_dom_aviation": 1,
        "hydrogen_energy_consumption_dom_aviation": 1,
    },
)
def synthetic_kerosene_energy_consumption_dom_aviation():
    return (
        dom_aviation_energy_consumption() * decarbonization_curve_dom_aviation()
        - hydrogen_energy_consumption_dom_aviation()
    ) * 0


@component.add(
    name='"synthetic kerosene energy consumption int. aviation"',
    units="GWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "decarbonization_curve_int_aviation": 1,
        "int_aviation_energy_consumption": 1,
    },
)
def synthetic_kerosene_energy_consumption_int_aviation():
    return decarbonization_curve_int_aviation() * int_aviation_energy_consumption() * 0
