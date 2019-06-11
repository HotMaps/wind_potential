#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 10:01:38 2018

@author: ggaregnani
"""
import numpy as np

# TODO: the idea is to set also a class for the planning rules in order to
# have the possibility to analyze potential territorial conflicts. this
# is a first tentative


class Planning_rules:
    def __init__(self, area_target, energy_target,
                 area_available, energy_available):
        """
        The class defines the rule in the use of the energy reosurce

        :param area_target: max availavble area to be exploited
        :param energy_target: target of the administrative unit
        of energy production
        :param area_available: total exploitable area
        :param energy_available: total energy available
        """
        self.area_target = area_target
        self.energy_target = energy_target
        self.area_available = area_available
        self.energy_available = energy_available

    def n_plants(self, plant):
        """
        Compute the number of plants in a region accounting for the minimum
        bewteen energy and area targets

        :param plant: plant object
        """
        n_plants_area = self.area_target / plant.area
        n_plants_energy = self.energy_target / plant.energy_production
        return min(int(n_plants_area), int(n_plants_energy))

    def validity(self):
        """
        Verify the consistency between constraints
        """
        consistency = ((self.area_target < self.area_available) *
                       (self.energy_target < self.energy_available))
        return consistency


class Financial:
    def __init__(self, investement_cost, yearly_cost, plant_life, **kwargs):
        """

        The class describes the financial feasibility of a plant providing
        methods to compute different indicators

        :param investement_cost: Total investment [positive real number]
        :param yearly_cost: (Outflow) variable cost [positive real number]
        :param plant_life: number of year of plant life [integer]
        """
        self.investement_cost = investement_cost
        self.yearly_cost = yearly_cost
        self.plant_life = plant_life
        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def lcoe(self, energy_production, i_r=0.03):
        """
        Computes th Levelized cost of Energy

        :param i_r: discount rate [0.0< positive real number<1.0]
        :param energy_production: total energy generated during a year
                                  [kWh/year] [ positive real number]
        :param self: Feasibility object with costs and plant life
        :returns: the levelized cost of energy [currency/kWh]

        test: geothermal savings oil
        >>> feasability = Financial(7473340, 4918, 27)
        >>> feasability.lcoe(6962999, 0.03)
        0.05926970484809364

        test: geothermal savings gas
        """

        flows = []
        flows.append(self.investement_cost)

        for i in range(1, self.plant_life+1):
            flow_k = (self.yearly_cost *
                      np.power(float(1+i_r), -i))
            flows.append(flow_k)

        tot_inv_and_sum_annual_discounted_costs = sum(flows)

        discounted_ener = []

        for i in range(1, self.plant_life+1):
            discounted_ener_k = (energy_production *
                                 np.power(float(1+i_r), -i))
            discounted_ener.append(discounted_ener_k)

        total_discounted_energy = sum(discounted_ener)

        lcoe = tot_inv_and_sum_annual_discounted_costs/total_discounted_energy
        return lcoe


# TODO a class plant exists in many of our codes, we have to unify them
class Plant:
    """

        The class describes the financial feasibility of a plant providing
        methods to compute different indicators

        :param investement_cost: Total investment [positive real number]
        :param yearly_cost: (Outflow) variable cost [positive real number]
        :param plant_life: number of year of plant life [integer]
    """
    def __init__(self, id_plant, x=None, y=None, peak_power=None,
                 efficiency=None,
                 energy_production=None, financial=None):
        """Initialize the base and height attributes."""
        self.id = id_plant
        self.x = x
        self.y = y
        self.peak_power = peak_power
        self.energy_production = energy_production
        self.efficiency = efficiency

    def working_hours(self):
        """Calculate and return the area of the rectangle."""
        return self.energy_production / self.peak_power


class PV_plant(Plant):
    """
        The class describes a PV plant providing
        methods to compute different indicators. Additional parameters to
        Plant class

        :param k_pv: Module efficiency at Standard Test Conditions [kW m^{-2}]
    """
    def __init__(self, k_pv, **kwargs):
        """Initialize the base and height attributes."""
        self.k_pv = k_pv
        # TODO: acceptable list of attributes
        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def area(self):
        """Calculate and return the area of the pv system."""
        return self.peak_power / self.k_pv

    def compute_energy(self, irradiation):
        """Calculate the energy production on the base"""
        return irradiation * self.peak_power * self.efficiency


class ST_plant(Plant):
    """
        The class describes a ST plant providing
        methods to compute different indicators. Additional parameters to
        Plant class

        :param area: Surface area of the module [m^{2}]
    """
    def __init__(self, area, **kwargs):
        """Initialize the base and height attributes."""
        self.area = area
        # TODO: acceptable list of attributes
        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def compute_energy(self, irradiation):
        """Calculate the energy production on the base"""
        return irradiation * self.area * self.efficiency


class Wind_plant(Plant):
    """
        The class describes a wind plant providing
        methods to compute different indicators. Additional parameters to
        Plant class
    """
    def __init__(self, swept_area, cp=0.41, **kwargs):
        """Initialize the base and height attributes."""
        self.swept_area = swept_area
        self.cp = cp
        # TODO: acceptable list of attributes
        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def compute_energy(self, speed, rho=1.225, working_hours=1700,
                       conv=1/1000):
        """Calculate the energy production on the base of the mean
           velocity

        :param speed: wind mean velocity [m/s]
        :param rho: air density [kg/m3]
        :param conv: conversion from J to kWh

        return the energy production in kWh
        >>> plant = Wind_plant(id_plant="test", swept_area=8495)
        >>> plant.compute_energy(speed=12)
        6266802.276000001
        """
        e_p = (0.5 * self.cp * rho * self.swept_area *
               speed**3) * working_hours * conv
        return e_p


if __name__ == "__main__":
    import doctest
    doctest.testmod()
