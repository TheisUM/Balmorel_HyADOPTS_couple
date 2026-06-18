import pysd
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class expando:
    pass

class Finance:
    investment_rate = 0.08
    discount_rate = 0.08
    _years = np.arange(2020, 2100)
    _carbon_taxes = np.linspace(0, 1, 2100-2020)  # Example list of carbon taxes €/kg CO2
    df_carbon = pd.DataFrame({'Carbon tax': _carbon_taxes}, index=_years)
    annualization_factor = 0.1  # Example value of the annualization factor

class Resource:
    energy_content = None
    name = ""
    historical_prices: list
    forecasted_prices: list
    resource_type = None
    h2_mwh_per_kg = 0.0333  # MWh/kg H2
    h2_kg_per_mwh = 1/h2_mwh_per_kg  # kg H2/MWh
    
    
    def load_historical_prices(self):
        pass

    def forecast_prices(self):
        pass

    def set_energy_content(self, energy_content):
        self.energy_content = energy_content
    
class Electricity(Resource):
    def __init__(self):
        self.resource_type = "Electricity"
        self.historical_years = [year for year in np.arange(2000,2023)]
        self.historical_prices = [x*50 for x in np.ones(len(self.historical_years))] # Example list of historical prices €/MWh
        self.df_hist = pd.DataFrame({'Price': self.historical_prices}, index=self.historical_years)
        self.forecasted_years = [year for year in np.arange(2023,2100)]
        self.forecasted_prices = [self.historical_prices[-1]*(1.01)**ix for ix, x in enumerate(np.ones(len(self.forecasted_years)))] # Example list of forecasted prices
        self.df_forecast = pd.DataFrame({'Price': self.forecasted_prices}, index=self.forecasted_years)

    def load_historical_prices(self, filename):
        with open(filename, 'r') as file:
            self.historical_prices = [float(price) for price in file.readlines()]
        
    def forecast_prices(self, forecasted_prices):
        self.forecasted_prices = forecasted_prices

class Gas(Resource):
    def __init__(self):
        self.resource_type = "Gas"
        self.historical_years = [year for year in np.arange(2000,2023)]
        self.historical_prices = [x*7 for x in np.ones(len(self.historical_years))] # Example list of historical prices €/MWh
        self.df_hist = pd.DataFrame({'Price': self.historical_prices}, index=self.historical_years)
        self.forecasted_years = [year for year in np.arange(2023,2100)]
        self.forecasted_prices = [self.historical_prices[-1]*(1.02)**ix for ix, x in enumerate(np.ones(len(self.forecasted_years)))] # Example list of forecasted prices
        self.df_forecast = pd.DataFrame({'Price': self.forecasted_prices}, index=self.forecasted_years)
    
    def load_historical_prices(self, filename):
        with open(filename, 'r') as file:
            self.historical_prices = [float(price) for price in file.readlines()]

    def forecast_prices(self, forecasted_prices):
        self.forecasted_prices = forecasted_prices

class Technology(Finance):
    def __init__(self, name, capital_cost, fixed_cost, resource_type, efficiency, carbon_footprint, lifetime, init_capacity, hours=8760):
        """
        Initializes an instance of the class.

        Parameters:
        name (str): The name of the technology.
        capital_cost (float): The capital cost of the resource - CAPEX.
        fixed_cost (float): The fixed cost of the resource as percentage of CAPEX.
        resource_type (str): The type of the resource.
        efficiency (float): The efficiency of the usage of the resource (energy to energy).
        carbon_footprint (float): The carbon footprint of the resource.
        lifetime (int): The lifetime of the resource.
        init_capacity (float): The initial capacity of the resource.
        """
        self.name = name
        self.capital_cost = capital_cost * 1000 # Capital cost in €/MW
        self.fixed_cost = fixed_cost # Fixed cost as percentage of CAPEX
        self.resource = Gas() if resource_type == 'Gas' else Electricity() # Resource type
        self.efficiency = efficiency # Efficiency of the usage of the resource
        self.carbon_footprint = carbon_footprint*self.resource.h2_kg_per_mwh # Carbon footprint in kg CO2/MWh of H2 production
        self.lifetime = lifetime # Lifetime of the production facility
        # self.capacity = init_capacity
        self.lcoH = []
        self.get_production(hours)
        
        for year in np.arange(2023, 2070):
            self.lcoH.append(self._calc_lcoH(year))

    def _learning_curve(self, year):
        return self.capital_cost * (1 - 0.2 * np.log(year - 2022))

    def get_production(self, hours):
        self.production = hours # Production in MWh/year

    def calc_npv(self, cashflows):
        npv = 0
        for ix, cashflow in enumerate(cashflows):
            npv += cashflow / (1 + Finance.discount_rate)**ix
        return npv

    def _calc_lcoH(self, year):
        capex = self.capital_cost/self.lifetime # Capital cost per year
        fixed_annual_cost = self.fixed_cost * self.capital_cost

        cashflows = []
        production_per_year = []
        for current_year in np.arange(year, year+self.lifetime):
            carbon_tax = Finance.df_carbon.loc[current_year, 'Carbon tax'] # Carbon tax in €/kg CO2 in the given year
            resource_cost = self.resource.df_forecast.loc[current_year, 'Price'] # resource cost in €/MWh in the given year
            variable_cost = resource_cost / self.efficiency # Variable cost in €/MWh
            
            cost = capex + fixed_annual_cost + (variable_cost + carbon_tax * self.carbon_footprint) * self.production
            production_per_year.append(self.production)
            cashflows.append(cost)
        print(capex, fixed_annual_cost, variable_cost, carbon_tax, self.carbon_footprint, self.production)
        lcoh = self.calc_npv(cashflows) / self.calc_npv(production_per_year)
        return lcoh

class AdoptionSimulation:
    uncertainty = 1  # Term multiplied by the timestep size to determine the standard deviation of the random noise added to the derivative calculations

    def __init__(self, demand, I_0, R_0, C_0, L_R, L_C, lcoC, lcoR, dt, start_time=0, stop_time=100, logic='sigmoid'):
        self.technologies = expando()
        self.runs = {}
        self.cache = None
        
        # Forecasted demand
        self.demand = demand

        # Initial values
        self.I_0 = I_0
        self.R_0 = R_0
        self.C_0 = C_0

        # Technology Parameters
        self.L_R = L_R
        self.L_C = L_C
        self.lcoC = lcoC
        self.lcoR = lcoR

        # Economic parameters
        self.investment_rate = 0.1  # Investment rate
        self.carbon_tax = 0.1  # Carbon tax
        self.carbon_footprint = 0.1  # Carbon footprint

        # Forecasted resource prices

        # Simulation parameters
        self.dt = dt
        self.start_time = start_time
        self.stop_time = stop_time
        self.current_time = start_time
        self.logic = logic
        self.update_timesteps()
    
    def update_timesteps(self):
        self.timesteps = np.arange(self.start_time, self.stop_time, self.dt) # Create a list of timesteps

    def _dR_dt(self, B, t):
        return (- 1/self.L_R * self.R[t-1] + B * self.I[t-1]) * self.dt #* (1 - self.C[t-1]/self.demand[t-1])

    def _dC_dt(self, B, t):
        return (- 1/self.L_C * self.C[t-1] + (1-B) * self.I[t-1]) * self.dt #* (1 - self.R[t-1]/self.demand[t-1])

    def run_simulation(self, name=''):
        self.I = [self.I_0] # Initial value of I. I is the amount of production currently being invested in
        self.R = [self.R_0] # Initial value of R. R is the amount of production from renewable sources
        self.C = [self.C_0] # Initial value of C. C is the amount of production from non-renewable sources
        self.K = [sum([self.I_0, self.R_0, self.C_0])] # Initial value of K. K is the total amount of production capacity built + planned

        price_diff = [self.lcoC[i] - self.lcoR[i] for i in range(len(self.lcoC))] # Difference in price between the two sources of production

        for t in range(1, len(self.timesteps)):
            eps = np.random.normal(0, self.dt*self.uncertainty, 1)[0] # Random noise added to the derivatives
            if self.logic == 'sigmoid':
                B = 1/(1 + np.exp(-price_diff[t])) # Sigmoid function
            elif self.logic == 'sign':
                B = price_diff[t] > 0 # Sign function
            elif self.logic == 'linear':
                B = price_diff[t] # Third type of logic (placeholder)
            else:
                raise ValueError('Invalid logic type')
            B = max(min(B, 1), 0)  # Limit B's value between 0 and 1

            dR = self._dR_dt(B, t) # Calculate the derivative of R
            dR = max(dR + eps, -self.R[t-1]) # Limit the derivative to be at least -R[t]
            self.R.append(self.R[t-1] + dR) # Add the derivative to the previous value of R

            dC = self._dC_dt(B, t) # Calculate the derivative of C
            dC = max(dC - eps, -self.C[t-1]) # Limit the derivative to be at least -C[t]
            self.C.append(self.C[t-1] + dC) # Add the derivative to the previous value of C

            dI = -(dR + dC) + (self.demand[t-1] - self.R[t-1] - self.C[t-1]) * 0.05 # Calculate the derivative of I (the negative of the sum of the derivatives of R and C added to the forecasted demand minus the total capacity built + planned)
            self.I.append(self.I[t-1] + dI) # Add the derivative to the previous value of I
            self.K.append(sum([self.I[t], self.R[t], self.C[t]])) # Calculate the total value of K

            self.current_time += self.dt
        
        if len(name) > 1:
            self._save_simulation(name)
        else:
            self._cache_simulation()
    
    def _save_simulation(self, name):
        self.runs[name] = {
            'timesteps' : self.timesteps,
            'I' : self.I,
            'R' : self.R,
            'C' : self.C,
            'K' : self.K,
            'logic' : self.logic}

    def _cache_simulation(self):
        self.cache = {
            'timesteps' : self.timesteps,
            'I' : self.I,
            'R' : self.R,
            'C' : self.C,
            'K' : self.K,
            'logic' : self.logic}

    def plot_simulation(self, name = None):
        cost_shift = np.where(self.lcoR < self.lcoC)[0][0]

        if name not in self.runs:
            if self.cache is None:
                raise ValueError('No simulation has been cached yet - run a simulation first or specify a saved simulation to plot.')
            # print('Plotting cached simulation')
            timesteps = self.cache['timesteps']
            I = self.cache['I']
            R = self.cache['R']
            C = self.cache['C']
            K = self.cache['K']
            logic = self.cache['logic']
        else:
            print('Plotting specified saved simulation')
            timesteps = self.runs[name]['timesteps']
            I = self.runs[name]['I']
            R = self.runs[name]['R']
            C = self.runs[name]['C']
            K = self.runs[name]['K']
            logic = self.runs[name]['logic']

        demand = self.demand[:len(timesteps)]

        fig = plt.figure(figsize=(10, 6))

        plt.plot(timesteps, I, label='Pipeline for extra production')
        plt.plot(timesteps, R, label='Renewable production')
        plt.plot(timesteps, C, label='Conventional production')
        plt.plot(timesteps, [r + c for r, c in zip(R, C)], label='Total online production', linestyle='--')

        plt.plot(timesteps, K, label='Total planned production', linestyle='--')
        plt.plot(timesteps, demand, label='Demand', linestyle='-.')
        plt.axvline(x=timesteps[cost_shift], color='black', linestyle='--', label='Cost shift', alpha=0.5)

        # Adding labels and legend
        plt.xlabel('Year')
        plt.ylabel('Value')
        plt.title(f'Production and investment over time - adoption logic: {logic}')
        plt.legend()

        # Setting xticks
        ticks = np.arange(timesteps[0], timesteps[-1]+10, 10)
        plt.xticks(ticks)

        plt.grid(alpha=0.3)
        fig.tight_layout()

        # Displaying the plot
        plt.show()




if __name__ == '__main__':
    start_time = 2020  # Start time of the simulation
    stop_time = 2050  # Stop time of the simulation
    dt = 0.01  # Timestep size (also used as the standard deviation for the random noise added to the derivative calculations)
    steps = int((stop_time - start_time)/dt)  # Number of timesteps
    
    ## Demand forecast of hydrogen
    demand = np.linspace(80, 100, steps+1)  # Example list of demand
    if False:
        for i in range(1,len(demand)):
            demand[i] = demand[i-1]*(1+0.01*dt)  # Exponential growth of demand
        for i in range(1,len(demand)):
            demand[i] = demand[i-1]*(1-0.01*dt)  # Exponential growth of demand
    demand = np.insert(demand, 0, np.ones(int(1/dt)) * demand[0]) # Insert the initial value of demand at the beginning of the list

    ## Production of hydrogen from renewable and non-renewable sources

    lcoC = np.linspace(2,50,steps)  # Example list of prices
    L_C = 20 # Lifetime of non-renewable production
    
    lcoR = np.linspace(10,35,steps)  # Example list of prices of a competing product
    L_R = 12 # Lifetime of renewable production
    
    R_0 = 5 # Initial production in renewable production
    C_0 = 75 # Initial production in non-renewable production
    I_0 = demand[0] - R_0 - C_0 # Initial investment in production
    logic = 'sigmoid'  # Logic used to determine the investment in renewable vs non-renewable production
    stop_time = 2050  # Stop time of the simulation

    ### Example usage of the AdoptionSimulation class ###
    techs = expando()
    techs.renewable = Technology('Electrolysis', 1014.5, 0.015, 'Electricity', 0.69, 0, L_R, R_0)
    techs.conventional = Technology('SMR', 910, 0.047, 'Gas', 0.76, 8.9, L_C, C_0)

    plt.plot(techs.renewable.lcoH, label='Renewable production LCoH')
    plt.plot(techs.conventional.lcoH, label='Non-renewable production LCoH')
    plt.xlabel('Year')
    plt.ylabel('LCoH [€/MWh]')
    plt.legend()
    plt.show()
    # techs.blue = Technology(100, 10, 'SMR with CCS', 0.1, 0.1, 20, 100)

    sim = AdoptionSimulation(demand, I_0, R_0, C_0, L_R, L_C, lcoC, lcoR, dt, start_time, stop_time, logic)
    
    sim.run_simulation(name='run1')
    sim.plot_simulation('run1')

    
    sim.logic = 'sign'
    sim.run_simulation(name='run2')

    sim.stop_time = 2040
    sim.update_timesteps()
    sim.run_simulation(name='run3')

    sim.stop_time = 2050
    sim.update_timesteps()
    sim.uncertainty = 3 # Increase the uncertainty
    sim.logic = 'sigmoid'
    sim.run_simulation(name='run4')

    sim.plot_simulation('run2')
    sim.plot_simulation('run3')
    sim.plot_simulation('run4')
    

    plt.plot(sim.lcoC, label='Non-renewable production')
    plt.plot(sim.lcoR, label='Renewable production')
    plt.xlabel('Year')
    plt.ylabel('Price')
    plt.title('Production prices over time')
    plt.legend()
    plt.show()


    
