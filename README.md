# Multi-Modal Transportation Instances and Validator

## Motivation

This repository provides instances for a multi-Modal Transportation problem. The instances are initially created as Thesis Data Challenge for Bachelor Students of Business Analytics department of University of Amsterdam.

## Content

```text
/multi-modal-logistics
│
├── 📂 INSTANCES
│   └── 📂 map_{NNN}_{MI}{MT}
│       ├── 📂 fleet_scenarios
│       │   └── 📊 fleet_{FI}{FD}.csv
│       ├── 📂 load_scenarios
│       │   └── 📊 loads_{LI}_{LN}{LD}.csv
│       ├── 📊 cities.csv
│       ├── 📊 airway.csv
│       ├── 📊 highway.csv
│       └── 📊 vehicle.csv
├── 📜 starter.ipynb
├── ❄️ transport_engine.py
├── 📊 thesis_instances.json
└── 📄 README.md
```

**Abbreviations**

NNN: 3-digit number of nodes

MI: 1-digit map index for that number of nodes

MT: map type (U: uniform, C: clustured)

FI: 2-digit fleet file index

FD: fleet difficulty (E: easy, M: medium, D: difficult) 

LI: 3-digit load file index

LN: 3-digit number of loads LD

load difficulty (E: easy, M: medium, D: difficult) 

## File Explanations

We can categorize the files into three categories according to their functionalities.

### Data

Instances exist under **INSTANCES** folder. Each folder under this folder corresponds to a map. For each map, node information (*cities.csv*), arc information (*higway.csv*, *airway.csv*) and vehicle information(*vehicle.csv*) exist.

Each map also has a *fleet_scenarios* folder that contains fleet information - which vehicle type is available at which locations. Fleet are created in three difficulty level. 'Easy' (E) has 2 to 3 highway vehicles at each location, 'Medium' (M) has 1 to 2 highway vehicles at each location, and 'Hard' (H) has no or 1 highway vehicle at each location.

Finally, each map has a  *load_scenarios* folder that contains different loads scenarios. Load scenearios can be created according to number of loads and three difficulty level. From 'Easy' (E) to 'Hard' (H) instances, likelihood of instance being 'urgent' increase while likelihood of instance being 'regular' decreases.

Additonally, some arcs can also be cancelled to challenge. In this case, some arcs can be removed from *higway.csv* or *airway.csv* in the same map.

By using this structure, I have created 100 instances for bachelor thesis. *thesis_instances.json* file that contains required information. Instances are created based varying number of nodes, number of loads, difficulty level of load scenario. The same instances are also augmented by breaking some arcs.

### Transport engine module

I provide a module to ease importing instances and validating the solution.

### Starter notebook

Starter notebook includes initial steps before diving into the problem. It shows examples of importing data, checking feasibility with provided transport engine module, and expected output format.


## Problem Definition

### Objective

These instances are created for a multi-modal logistics problem. The goal is to minimize total cost which consist of transportation costs and delay penalties. The default penalty coefficient (also for bachelor students' projects) is 2000 Euro per hour. Transportation costs are calculated according to vehicle type. Two types of cost calculation are included in the curret setting (i) Distance-based cost calculation, e.g. cost unit is euro per kilometer for trucks; (ii) time-based cost calculations, e.g. cost unit is euro per hour for cargo planes.

In short, the ultimate objective is to minimize sum of these two:
* Total transportation cost
* Total penalty due to delays

### Vehicle constraint

* Vehicles have a weight and a volume capacity. This cannot be exceeded in any moment during traveling.
* Vehicles belongs to certain locations, so they must return to their host location at the end any route.
* Vehicles are assumed to travel with their provided average speed.
* Physical constraints such as a vehicle not being able to be in multiple places at the same time.

### Load constraints

* A load must be taken from its origin and must be carried to its intended destionation.
* A load cannot be loaded to any vehicle before its release time.
* A load can be transfered to its destination after the deadline. However, penalties apply in this case.

### Transportation constraints
* All arcs are provided, so if no arc exists between two nodes, any vehicle cannot travel between these two cities.
* Arcs must be performed by proper vehicle types. For instance, a truck cannot travel on airway arcs, or a plane cannot travel on highway arcs.

## Solution format

This repository also provides a validator for a suggested solution format. This format consist of three dataframes: routes (for generic route information), route_arcs (for related movement on a route), and schedule of vehicles. Additional details are provided in *starter.ipynb* notebook.

## Licenses

This project is initially developed for Thesis Data Challenge for Bachelor Students of Business Analytics department of University of Amsterdam. Even though some instances are provided, data generation processes are handled internally to reduce boilerplate code for the end-user. Together with those hidden gems, the implementation of these methods has been done by the project owner and a sample of output instances are provided here. 








