import numpy as np
np.random.seed(42)

class result_loading_class:

    h2_summary = ["H2 DEMAND in TWh", "industry TWh", "trans TWh", "power TWh"]
    subsidy_summary = ["TOTAL GREEN HYDROGEN DEMAND", "Green H2 cost", "TOTAL SUBSIDIES"]

    # Overall activity projections
    activity_projections = {"steel": "primary sector",
                            "naphtha": "naphtha production",
                            "MeOH": "methanol production",
                            "fertilizer": "NH3 fertilizer consumption",
                            "high temperature": "NM gas consumption",
                            "refinery": "Refinery hydrogen consumption",
                            "international aviation": "international aviation consumption",
                            "domestic aviation": "domestic aviation consumption",
                            "international shipping": "international shipping consumption",
                            "domestic shipping": "domestic shipping consumption",
                            "light duty": "LD RT consumption",
                            "heavy duty": "HD RT consumption",
                            }

    # Define the sectors of the model
    steel_sector = ["BF BOF", "BF BOF CCS", "NGDRI EAF", "H2DRI EAF"]
    hvc_sector = ["Fossil naphtha", "SynNaphtha", "BioNaphtha"]
    meoh_sector = ["Grey MeOH", "Blue MeOH", "BioMeOH", "eMeOH"]
    fertilizer_sector = ["Grey NH3", "Blue NH3", "Green NH3"]
    temp_sector = ["Grey NG NM", "Blue NG NM", "Biogas NM", "H2 NM"]
    refining_sector = ["Grey Refinery", "Blue Refinery", "Green Refinery"]
    industry_sectors = steel_sector + hvc_sector + fertilizer_sector + temp_sector + refining_sector + meoh_sector

    int_aviation_sector = ["Jetfuel IA", "SynKero IA", "BioKero IA"]
    dom_aviation_sector = ["Jetfuel DA", "SynKero DA", "BioKero DA"]
    int_shipping_sector = ["HFO IS", "NH3 IS", "MeOH IS"]
    dom_shipping_sector = ["HFO DS", "Electric DS", "MeOH DS", "H2FC DS"]
    ld_road_transport_sector = ["LD Fossil", "LD BEV", "LD FCEV"]
    hd_road_transport_sector = ["HD Fossil", "HD BEV", "HD FCEV"]
    transport_sectors = int_aviation_sector + dom_aviation_sector + int_shipping_sector + dom_shipping_sector + ld_road_transport_sector + hd_road_transport_sector

    technologies = industry_sectors + transport_sectors

    # Define the costs for each sector
    steel_costs = ["BF BOF cost", "BF BOF CCS cost", "NGDRI cost", "H2DRI cost"]
    hvc_costs = ["Naphtha cost", "BioNaphtha cost", "SynNaphtha cost",]
    meoh_costs = ["convMeOH cost", "Blue MeOH cost", "Green bioMeOH cost", "Green eMeOH cost"]
    fertilizer_costs = ["Grey NH3 cost", "Blue NH3 cost", "fertilizer NH3 cost"]
    temp_costs = ["Grey NG cost", "Blue NG cost", "NM H2 GJ cost", "biogas cost"]
    refining_costs = ["Grey H2 cost", "Blue H2 cost", "refinery H2 cost"]

    int_aviation_costs = ["Jetfuel cost", "SynKero cost", "BioKero cost"]
    dom_aviation_costs = ["Jetfuel cost", "SynKero cost", "BioKero cost"]
    int_shipping_costs = ["HFO containership cost", "NH3 containership cost", "MeOH containership cost"]
    dom_shipping_costs = ["HFO ship cost", "BE ship cost", "MeOH ship cost", "FC ship cost"]
    ld_road_transport_costs = ["LD ICE LCO", "LD BE LCO", "LD FC LCO"]
    hd_road_transport_costs = ["HD ICE LCO", "HD BE LCO", "HD FC LCO"]

    sectors = industry_sectors + transport_sectors

    price_break_list = ["steel H2 WTP",
                    "SynNaphtha H2 WTP", 
                    "BioNaphtha H2 WTP", 
                    "eMeOH H2 WTP",
                    "bioMeOH H2 WTP",
                    "BioKero H2 WTP",
                    "SynKero H2 WTP", 
                    "fertilizer H2 WTP", 
                    "refinery H2 WTP", 
                    "high temperature H2 WTP",
                    "LD H2 WTP", 
                    "HD H2 WTP", 
                    "NH3 containership H2 WTP", 
                    "MeOH containership H2 WTP",
                    "MeOH ship H2 WTP", 
                    "FC ship H2 WTP",
                    ]
    
    fuel_to_activity_conversions = {
                            "steel": {"conversion": 0.0563e6, "units": "MT Steel to t H2"},
                            "SynNaphtha": {"conversion": 5.85/33.33*1e6, "units": "MT Naphtha to t H2"},
                            "BioNaphtha": {"conversion": 0.78/33.33*1e6, "units": "MT Naphtha to t H2"},
                            "eMeOH": {"conversion": 1e6/5.26, "units": "MT MeOH to t H2"},
                            "bioMeOH": {"conversion": 1e6/15.7, "units": "MT MeOH to t H2"},
                            "BioKero": {"conversion": 0.099e3/33.33, "units": "GWh Kerosene to t H2"},
                            "SynKero": {"conversion": 0.995e3/33.33, "units": "MT Kerosene to t H2"},
                            "fertilizer": {"conversion": 1e6/5.56, "units": "MT NH3 to t H2"},
                            "refinery": {"conversion": 1e6, "units": "MT H2 to t H2"},
                            "high temperature": {"conversion": 1e3/33.33, "units": "GWh to t H2"},
                            "LD": {"conversion": 0.32/0.57*1e3/33.33, "units": "GWh to t H2"},
                            "HD": {"conversion": 0.343/0.57*1e3/33.33, "units": "GWh to t H2"},
                            "NH3 containership": {"conversion": 3600/18.6/5.56, "units": "GWh to t H2"},
                            "MeOH containership": {"conversion": 3600/19.9/15.7, "units": "GWh to t H2"},
                            "MeOH ship": {"conversion": 3600/19.9/15.7, "units": "GWh to t H2"},
                            "FC ship": {"conversion": 0.4/0.55*3600/33.33, "units": "GWh to t H2"},
    }
    
    co2_wtp_list = ["steel CO2 WTP",
                    "Naphtha CO2 WTP", 
                    "convMeOH CO2 WTP",
                    "Jetfuel CO2 WTP",
                    "Grey NH3 CO2 WTP",
                    "Blue NH3 CO2 WTP",
                    "Grey NG NM CO2 WTP",
                    "Blue NG NM CO2 WTP",
                    "Grey refinery CO2 WTP",
                    "Blue refinery CO2 WTP",
                    "LD CO2 WTP",
                    "HD CO2 WTP",
                    "HFO containership CO2 WTP", 
                    "HFO ship CO2 WTP", 
                    ]
    
    sector_average_costs = ["refinery average cost"
                            "high temperature average cost",
                            "fertilizer average cost",
                            "steel average cost",
                            "naphtha average cost",
                            "MeOH average cost",
                            "international aviation average cost",
                            "domestic aviation average cost",
                            "international shipping average cost",
                            "domestic shipping average cost",
                            "LD average cost",
                            "HD average cost",
                            ]
    
    pretty_names = {"steel": "Steel",
                    "naphtha": "High Value Chemicals",
                    "MeOH": "Methanol",
                    "fertilizer": "Fertilizer",
                    "high temperature": "High Temperature Heat",
                    "refinery": "Refining",
                    "international aviation": "International Aviation",
                    "domestic aviation": "Domestic Aviation",
                    "international shipping": "International Shipping",
                    "domestic shipping": "Domestic Shipping",
                    "light duty": "Light Duty Road Transport",
                    "heavy duty": "Heavy Duty Road Transport",
                    "power": "Power",
                    "TOTAL TWh": "Total",
                    }
    
    pretty_names_technologies = {
                                "Grey NH3": "Grey Ammonia",
                                "Blue NH3": "Blue Ammonia",
                                "Green NH3": "Green Ammonia",
                                "Grey Refinery": "Grey Hydrogen",
                                "Blue Refinery": "Blue Hydrogen",
                                "Green Refinery": "Green Hydrogen",
                                "Grey NG NM": "Grey Natural Gas",
                                "Blue NG NM": "Blue Natural Gas",
                                "Biogas NM": "Biogas",
                                "H2 NM": "Hydrogen",
                                "Grey MeOH": "Grey Methanol",
                                "Blue MeOH": "Blue Methanol",
                                "BioMeOH": "Biogenic Methanol",
                                "eMeOH": "eMethanol",
                                "BF BOF": "Coal BF BOF",
                                "BF BOF CCS": "Coal BF BOF CCS",
                                "NGDRI EAF": "NG DRI-EAF",
                                "H2DRI EAF": "H$_2$ DRI-EAF",
                                "Fossil naphtha": "Fossil Naphtha",
                                "BioNaphtha": "Biogenic Naphtha",
                                "SynNaphtha": "Synthetic Naphtha",
                                "Jetfuel IA": "Fossil Kerosene",
                                "SynKero IA": "Synthetic Kerosene",
                                "BioKero IA": "Biogenic Kerosene",
                                "Jetfuel DA": "Fossil Kerosene",
                                "SynKero DA": "Synthetic Kerosene",
                                "BioKero DA": "Biogenic Kerosene",
                                "HFO IS": "HFO",
                                "NH3 IS": "NH$_3$",
                                "MeOH IS": "Bio-MeOH",
                                "HFO DS": "HFO",
                                "Electric DS": "Battery-Electric",
                                "MeOH DS": "Bio-MeOH",
                                "H2FC DS": "H$_2$ FC",
                                "LD Fossil": "Diesel ICE",
                                "LD BEV": "Battery EV",
                                "LD FCEV": "H$_2$ FC EV",
                                "HD Fossil": "Diesel ICE",
                                "HD BEV": "Battery EV",
                                "HD FCEV": "H$_2$ FC EV",
                                }
    
    pretty_names_costs = {
                        "BF BOF cost": "Coal BF BOF",
                        "BF BOF CCS cost": "Coal BF BOF CCS",
                        "NGDRI cost": "NG DRI-EAF",
                        "H2DRI cost": "H$_2$ DRI-EAF",
                        "Naphtha cost": "Fossil Naphtha",
                        "BioNaphtha cost": "Biogenic Naphtha",
                        "SynNaphtha cost": "Synthetic Naphtha",
                        "convMeOH cost": "Grey Methanol",
                        "Blue MeOH cost": "Blue Methanol",
                        "Green bioMeOH cost": "Biogenic Methanol",
                        "Green eMeOH cost": "eMethanol",
                        "Grey NH3 cost": "Grey Ammonia",
                        "Blue NH3 cost": "Blue Ammonia",
                        "fertilizer NH3 cost": "Green Ammonia",
                        "Grey NG cost": "Grey Natural Gas",
                        "Blue NG cost": "Blue Natural Gas",
                        "NM H2 GJ cost": "Hydrogen",
                        "biogas cost": "Biogas",
                        "Grey H2 cost": "Grey Hydrogen",
                        "Blue H2 cost": "Blue Hydrogen",
                        "refinery H2 cost": "Green Hydrogen",
                        "Jetfuel cost": "Fossil Kerosene",
                        "SynKero cost": "Synthetic Kerosene",
                        "BioKero cost": "Biogenic Kerosene",
                        "HFO containership cost": "HFO",
                        "NH3 containership cost": "NH$_3$",
                        "MeOH containership cost": "Bio-MeOH",
                        "HFO ship cost": "HFO",
                        "BE ship cost": "Battery-Electric",
                        "MeOH ship cost": "Bio-MeOH",
                        "FC ship cost": "H$_2$ FC",
                        "LD ICE LCO": "Diesel ICE",
                        "LD BE LCO": "Battery EV",
                        "LD FC LCO": "H$_2$ FC EV",
                        "HD ICE LCO": "Diesel ICE",
                        "HD BE LCO": "Battery EV",
                        "HD FC LCO": "H$_2$ FC EV",
                        }

    # Define the dictionary of sectors, include a key for each sector which defines the unit used in the sector
    industry_sector_dict = {
                            "refinery": {"unit": "MT H2", "stocks" : refining_sector, "h2 demand" : "refinery hydrogen demand", "emissions" : "refinery emissions", "subsidy": "refinery subsidy", "WTP": "refinery H2 WTP", "CT revenue": "refinery CT revenue", "costs": refining_costs, "CO2 WTP": "Grey refinery CO2 WTP", "cost index": "refinery cost index"},
                            "high temperature": {"unit": "GWh", "stocks" : temp_sector, "h2 demand" : "high temperature hydrogen demand", "emissions" : "high temperature emissions", "biomass": "high temperature biomass demand", "subsidy": "high temperature subsidy", "WTP": "high temperature H2 WTP", "CT revenue": "high temperature CT revenue", "costs": temp_costs, "CO2 WTP": "Grey NG NM CO2 WTP", "cost index": "high temperature cost index"},
                            "fertilizer": {"unit": "MT NH3", "stocks" : fertilizer_sector, "h2 demand" : "fertilizer hydrogen demand", "emissions" : "fertilizer emissions", "subsidy": "fertilizer subsidy", "WTP": "fertilizer H2 WTP", "CT revenue": "fertilizer CT revenue", "costs": fertilizer_costs, "CO2 WTP": "Grey NH3 CO2 WTP", "cost index": "fertilizer cost index"},
                            "steel": {"unit": "MT Steel", "stocks" : steel_sector, "h2 demand" : "steel hydrogen demand", "emissions" : "steel emissions", "subsidy": "steel subsidy", "WTP": "steel H2 WTP", "CT revenue": "steel CT revenue", "costs": steel_costs, "CO2 WTP": "steel CO2 WTP", "cost index": "steel cost index"},
                            "naphtha": {"unit": "MT Naphtha", "stocks" : hvc_sector, "h2 demand" : "naphtha hydrogen demand", "emissions" : "naphtha emissions", "biomass": "naphtha biomass demand", "subsidy": "naphtha subsidy", "WTP": "SynNaphtha H2 WTP", "WTP 2": "BioNaphtha H2 WTP", "h2 demands": ["SynNaphtha hydrogen demand", "BioNaphtha hydrogen demand"], "CT revenue": "naphtha CT revenue", "costs": hvc_costs, "CO2 WTP": "Naphtha CO2 WTP", "cost index": "naphtha cost index"},
                            "MeOH": {"unit": "MT MeOH", "stocks" : meoh_sector, "h2 demand" : "MeOH hydrogen demand", "emissions" : "MeOH emissions", "biomass": "MeOH biomass demand", "subsidy": "MeOH subsidy", "WTP": "eMeOH H2 WTP", "WTP 2": "bioMeOH H2 WTP", "h2 demands": ["eMeOH hydrogen demand", "bioMeOH hydrogen demand"], "CT revenue": "MeOH CT revenue", "costs": meoh_costs, "CO2 WTP": "convMeOH CO2 WTP", "cost index": "MeOH cost index"},
                            }

    transport_sector_dict = {"international aviation": {"unit": "GWh", "stocks" : int_aviation_sector, "h2 demand" : "international aviation hydrogen demand", "emissions" : "international aviation emissions", "biomass": "international aviation biomass demand", "subsidy": "international aviation subsidy", "WTP": "SynKero H2 WTP", "WTP 2": "BioKero H2 WTP", "h2 demands": ["international aviation SynKero hydrogen demand", "international aviation BioKero hydrogen demand"], "CT revenue": "international aviation CT revenue", "costs": int_aviation_costs, "CO2 WTP": "Jetfuel CO2 WTP", "cost index": "international aviation cost index"},
                            "domestic aviation": {"unit": "GWh", "stocks" : dom_aviation_sector, "h2 demand" : "domestic aviation hydrogen demand", "emissions" : "domestic aviation emissions", "biomass": "domestic aviation biomass demand", "subsidy": "domestic aviation subsidy", "WTP": "SynKero H2 WTP", "WTP 2": "BioKero H2 WTP", "h2 demands": ["domestic aviation SynKero hydrogen demand", "domestic aviation BioKero hydrogen demand"], "CT revenue": "domestic aviation CT revenue", "costs": dom_aviation_costs, "CO2 WTP": "Jetfuel CO2 WTP", "cost index": "domestic aviation cost index"},
                            "light duty": {"unit": "GWh", "stocks" : ld_road_transport_sector, "h2 demand" : "light duty hydrogen demand", "emissions" : "light duty emissions", "subsidy": "light duty subsidy", "WTP": "LD H2 WTP", "CT revenue": "light duty CT revenue", "costs": ld_road_transport_costs, "CO2 WTP": "LD CO2 WTP", "cost index": "LD cost index"},
                            "heavy duty": {"unit": "GWh", "stocks" : hd_road_transport_sector, "h2 demand" : "heavy duty hydrogen demand", "emissions" : "heavy duty emissions", "subsidy": "heavy duty subsidy", "WTP": "HD H2 WTP", "CT revenue": "heavy duty CT revenue", "costs": hd_road_transport_costs, "CO2 WTP": "HD CO2 WTP", "cost index": "HD cost index"},
                            "international shipping": {"unit": "GWh", "stocks" : int_shipping_sector, "h2 demand" : "international shipping hydrogen demand", "emissions" : "international shipping emissions", "biomass": "international shipping biomass demand", "subsidy": "international shipping subsidy", "WTP": "NH3 containership H2 WTP", "WTP 2": "MeOH containership H2 WTP", "h2 demands": ["international shipping NH3 hydrogen demand", "international shipping MeOH hydrogen demand"], "CT revenue": "international shipping CT revenue", "costs": int_shipping_costs, "CO2 WTP": "HFO containership CO2 WTP", "cost index": "international shipping cost index"},
                            "domestic shipping": {"unit": "GWh", "stocks" : dom_shipping_sector, "h2 demand" : "domestic shipping hydrogen demand", "emissions" : "domestic shipping emissions", "biomass": "domestic shipping biomass demand", "subsidy": "domestic shipping subsidy", "WTP": "MeOH ship H2 WTP", "WTP 2": "FC ship H2 WTP", "h2 demands": ["domestic shipping MeOH hydrogen demand", "domestic shipping FC hydrogen demand"], "CT revenue": "domestic shipping CT revenue",  "costs": dom_shipping_costs, "CO2 WTP": "HFO ship CO2 WTP", "cost index": "domestic shipping cost index"},
                            }

    sector_dict = {"industry": industry_sector_dict, "transport": transport_sector_dict}

    h2_tech_to_sector_dict = {'Green Refinery': 'refinery', 'H2 NM': 'high temperature', 'Green NH3': 'fertilizer', 'H2DRI EAF': 'steel', 'BioNaphtha': 'naphtha',
                                                     'SynNaphtha': 'naphtha', 'BioMeOH': 'MeOH', 'eMeOH': 'MeOH', 'SynKero IA': 'international aviation', 
                                                     'BioKero IA': 'international aviation', 'SynKero DA': 'domestic aviation', 'BioKero DA': 'domestic aviation', 'LD FCEV': 'light duty',
                                                     'HD FCEV': 'heavy duty', 'NH3 IS': 'international shipping', 'MeOH IS': 'international shipping',
                                                     'MeOH DS': 'domestic shipping', 'H2FC DS': 'domestic shipping'}
    
    sector_to_lifetime = {'high temperature': 5, 'international aviation': 5, 'domestic aviation': 5}

    h2_tech_color_dict = {tech : np.random.uniform(0,1,size=3) for tech in h2_tech_to_sector_dict.keys()}

    hydrogen_demands = {"power" : "power hydrogen demand"}
    subsidies = {"power" : "power subsidy"}
    biomass_demands = {}
    emissions = {}
    price_breaks = {}
    hydrogen_demands_technologies = {}

    for main_sector in sector_dict.keys():
        for i, (sub_sector, sub_dict) in enumerate(sector_dict[main_sector].items()):
            hydrogen_demands[sub_sector] = sub_dict["h2 demand"]
            subsidies[sub_sector] = sub_dict["subsidy"]
            emissions[sub_sector] = sub_dict["emissions"]
            price_breaks[sub_sector] = sub_dict["WTP"]
            if "WTP 2" in sub_dict.keys():
                price_breaks[sub_sector + " 2"] = sub_dict["WTP 2"]
                for i, demand in enumerate(sub_dict["h2 demands"]):
                    hydrogen_demands_technologies[str(sub_sector + (" 2" if i > 0 else ""))] = demand
            else:
                hydrogen_demands_technologies[sub_sector] = sub_dict["h2 demand"]
            if "biomass" in sub_dict.keys():
                biomass_demands[sub_sector] = sub_dict["biomass"]

    sector_colors = {'power': 'lightgrey',
                    'MeOH': (0.8705882352941177, 0.5607843137254902, 0.0196078431372549),
                    'refinery': (0.00784313725490196, 0.6196078431372549, 0.45098039215686275),
                    'fertilizer': (0.8352941176470589, 0.3686274509803922, 0.0),
                    'steel': (0.8, 0.47058823529411764, 0.7372549019607844),
                    'domestic shipping': (0.792156862745098, 0.5686274509803921, 0.3803921568627451),
                    'high temperature': (0.984313725490196, 0.6862745098039216, 0.8941176470588236),
                    'naphtha': 'turquoise',
                    'international shipping': (0.9254901960784314, 0.8823529411764706, 0.2),
                    'international aviation': (0.33725490196078434, 0.7058823529411765, 0.9137254901960784),
                    'domestic aviation': (0.00392156862745098, 0.45098039215686275, 0.6980392156862745),
                    'heavy duty': 'grey',
                    'light duty': 'black'}
    
    tech_colors = sector_colors.copy()
    tech_colors.update({
                    'SynNaphtha': (0.00784313725490196, 0.6196078431372549, 0.45098039215686275),
                    'BioNaphtha': (0.8352941176470589, 0.3686274509803922, 0.0),
                    'eMeOH': (0.8705882352941177, 0.5607843137254902, 0.0196078431372549),
                    'bioMeOH': (0.984313725490196, 0.6862745098039216, 0.8941176470588236),
                    'international aviation SynKero': (0.33725490196078434, 0.7058823529411765, 0.9137254901960784),
                    'international aviation BioKero': (0.00392156862745098, 0.45098039215686275, 0.6980392156862745),
                    'domestic aviation SynKero': (0.33725490196078434, 0.7058823529411765, 0.9137254901960784),
                    'domestic aviation BioKero': (0.00392156862745098, 0.45098039215686275, 0.6980392156862745),
                    'international shipping NH3': (0.9254901960784314, 0.8823529411764706, 0.2),
                    'international shipping MeOH': (0.792156862745098, 0.5686274509803921, 0.3803921568627451),
                    'domestic shipping MeOH': (0.792156862745098, 0.5686274509803921, 0.3803921568627451),
                    'domestic shipping FC': (0.8, 0.47058823529411764, 0.7372549019607844),})

    
if __name__ == "__main__":
    r = result_loading_class()
    print(r.hydrogen_demands_technologies)