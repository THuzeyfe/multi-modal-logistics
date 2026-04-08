import pandas as pd

def load_instance(instance):
    """
    This function helps to laod instances.
    This requires a single argument which is a dictionary with keys:
    * map : folder name that contains cities, airway, highway, vehicle data; and fleet and load scenarios folders
    * fleet : fleet file (must exist in fleet_scenarios file)
    * loads : loads file (must exist in loads_scenarios file)
    * broken_arcs : list of broken highway arcs
    """
    cities = pd.read_csv(instance['map'] + "/cities.csv", index_col=0)
    highway = pd.read_csv(instance['map'] + "/highway.csv", index_col=0)
    airway = pd.read_csv(instance['map'] + "/airway.csv", index_col=0)
    vehicle = pd.read_csv(instance['map'] + "/vehicle.csv", index_col=0)
    fleet = pd.read_csv(instance['map'] + f"/fleet_scenarios/{instance['fleet']}.csv", index_col=0)
    loads = pd.read_csv(instance['map'] + f"/load_scenarios/{instance['loads']}.csv", index_col=0)

    cities.index = cities.index.astype(int)
    highway['from_city_id'] = highway['from_city_id'].apply(int)
    highway['to_city_id'] = highway['to_city_id'].apply(int)
    airway['from_city_id'] = airway['from_city_id'].apply(int)
    airway['to_city_id'] = airway['to_city_id'].apply(int)
    fleet['station'] = fleet['station'].apply(int)
    loads['from'] = loads['from'].apply(int)
    loads['to'] = loads['to'].apply(int)

    highway.drop(instance['broken_arcs'], inplace=True)
    # highway['active'] = True

    # for arc_id in instance['broken_arcs']:
    #     highway.loc[arc_id]['active'] = False

    return cities, highway, airway, vehicle, fleet, loads


def validator(instance, routes, moves, vehicle_schedule, delay_penalty=2000):
    """
    This function checks if a solution is feasible or not. It also returns
    
    This requires five arguments:
    * instance: dictionary of intance information (as provided)
    * routes : generic route information
    * moves : each movement in routes
    * vehicle_schedule : schedule of vehicles
    * delay_penalty : penalty coefficient for delaying a load per hour

    It returns three objects:
    * messages: This is a list of warnings, errors, and feasibility checks. An correct output must have an empty list, so you should take care of every messages.
    * route_costs: A dictionary with keys being route id and values being calculated cost of it
    * penalties: A dictionary with keys being load id and values being calculated penalty for it
    """
    def calculate_cost(road_type, arc_id, vehicle_type_id):
        if road_type == 'highway':
            arc_df = highway
        elif road_type == 'airway':
            arc_df = airway
        else:
            raise f"Unknown route type."
        
        if vehicle.loc[vehicle_type_id]['price_unit'] == 'euro/km':
            time = arc_df.loc[arc_id]['distance'] / vehicle.loc[vehicle_type_id]['speed']
            cost = arc_df.loc[arc_id]['distance'] * vehicle.loc[vehicle_type_id]['price']
        elif vehicle.loc[vehicle_type_id]['price_unit'] == 'euro/hour':
            time = arc_df.loc[arc_id]['distance'] / vehicle.loc[vehicle_type_id]['speed']
            cost = time * vehicle.loc[vehicle_type_id]['price']
        else:
            raise f"Unknown price_unit for vehicle type id {vehicle_type_id}"

        return time, cost
    
    cities, highway, airway, vehicle, fleet, loads = load_instance(instance)
    all_loads = list(loads.index)
    load_moves = dict()
    for _l in all_loads:
        load_moves[_l] = []

    veh_schedule = list() #dict()

    messages = list()
    route_costs = dict()
    load_delay_penalties = dict()

    for route_id, route_info in routes.iterrows():
        if route_info['type'] == 'highway':  # ensure if vehicle types match
            arc_df = highway
        elif route_info['type'] == 'airway':
            arc_df = airway
        else:
            messages.append(f"Unknown route type for route #{route_id}. Route type must be 'highway' or 'airway'.")

        if vehicle.loc[fleet.loc[route_info['vehicle_id']]['vehicle_type']]['vehicle_type'] != route_info['type']:
            messages.append(f"Vehicle {route_info['vehicle_id']} is not suitable {route_info['type']}. Check route {route_id}")

        _count = 0
        _st = 0
        # _veh_speed = vehicle.loc[fleet.loc[route_info['vehicle_id']]['vehicle_type']]['speed']
        current_loads = []
        previos_arrive = 0
        related_moves = moves[moves['route_id'] == route_id].sort_values("order")

        if len(related_moves) == 0:
            messages.append(f"Route {route_id} does not have any movements in route arcs dataframe.")

        #vehicle schedule control
        route_st = related_moves['start_time'].min()
        route_end = related_moves['end_time'].max()
        route_costs[route_id] = 0

        for veh_id, _ ,ss, ee in veh_schedule:
            if veh_id == route_info['vehicle_id']:
                if ss >= route_st and ss<route_end:
                    messages.append(f"Vehicle {route_info['vehicle_id']} has conflict in its schedule. Check route {route_id}")
                elif ee > route_st and ee<=route_st: #ear
                    messages.append(f"Vehicle {route_info['vehicle_id']} has conflict in its schedule. Check route {route_id}")

        veh_schedule.append([route_info['vehicle_id'], route_id ,route_st,route_end])

        if veh_schedule[-1] not in vehicle_schedule.values:
            messages.append(f"Vehicle schedule is not added for route {route_id}. Check vehicle schedule dataframe.")

        involved_loads = list()

        for _, arc_info in related_moves.iterrows():
            _count += 1
            #order control
            if arc_info['order'] != _count:
                messages.append(f"Order must starts from 1 and incremented by 1. Check moves of route {route_id}")

            _fr = arc_df.loc[arc_info['arc_id']]['from_city_id']
            
            if arc_info['order'] == 1:
                if fleet.loc[route_info['vehicle_id']]['station'] != _fr:
                    messages.append(f"Vehicle {route_info['vehicle_id']} does not belong to location {_fr} in route {route_id}")
            elif _fr != _to:
                messages.append(f"Route {route_id} skip nodes between {arc_info['order']-1} and {arc_info['order']}")
            _to = arc_df.loc[arc_info['arc_id']]['to_city_id']
            # dist = arc_df.loc[arc_info['arc_id']]['distance']
            # duration = dist / _veh_speed
            duration, arc_cost = calculate_cost(route_info['type'], arc_info['arc_id'], fleet.loc[route_info['vehicle_id']]['vehicle_type'])

            #duration control
            if abs(arc_info['end_time'] - arc_info['start_time'] - duration) > 0.01:
                messages.append(f"Time does not match with the vehicle's speed in row {_} of movement database")   

            if arc_info['start_time'] < _st:
                messages.append(f"A move cannot executed before previous one ends or time 0 in row {_} of movement database")
            
            #load origin and destination controls #FIX THIS: RECORD LOADS ALL MOVES THEN CHECK AFTERWARDS
            for _load in arc_info['loads_on']:
                if _load not in current_loads:
                    load_moves[_load].append([route_id, arc_info['start_time'], _fr])
                    involved_loads.append(_load)
                    if _load not in route_info['loads']:
                        messages.append(f"Load {_load} is not in the list of carried loads of route {route_id}")


            for _load in current_loads:
                if _load not in arc_info['loads_on']:
                    load_moves[_load][-1].append(_st)
                    load_moves[_load][-1].append(_fr)

            _st = arc_info['end_time']
            current_loads = arc_info['loads_on'].copy()
            #weight control
            if sum([loads.loc[_l]['weight'] for _l in current_loads]) > vehicle.loc[fleet.loc[route_info['vehicle_id']]['vehicle_type']]['weight_capacity']:
                messages.append(f"Weight capacity of the vehicle is exceeded in {arc_info['order']} leg of route {route_id}")
            #volume control
            if sum([loads.loc[_l]['volume'] for _l in current_loads]) > vehicle.loc[fleet.loc[route_info['vehicle_id']]['vehicle_type']]['volume_capacity']:
                messages.append(f"Volume capacity of the vehicle is exceeded in {arc_info['order']} leg of route {route_id}")


            previos_arrive = arc_info['end_time']
            route_costs[route_id] += arc_cost
        
        if fleet.loc[route_info['vehicle_id']]['station'] != _to:
            messages.append(f"Vehicle {route_info['vehicle_id']} must return to {fleet.loc[route_info['vehicle_id']]['station']} not to location {_to} in route {route_id}")

        for _load in current_loads:
            load_moves[_load][-1].append(arc_info['end_time'])
            load_moves[_load][-1].append(_to)
        
        for _load in route_info['loads']:
            if _load not in involved_loads:
                messages.append(f"Load {_load} is never loaded to vehicle, but listed in carried loads of route {route_id}")
            
    for _load, transfer_info in load_moves.items():
        if len(transfer_info) == 0:
            messages.append(f"Load {_load} is not carried over with any of the routes")
            continue

        sorted_list = sorted(transfer_info, key=lambda x: x[1])

        start_ = sorted_list[0][1] #first movement
        end_ = sorted_list[-1][3] #delivered
        _lfrom = sorted_list[0][2]
        _lto = sorted_list[-1][4]
        if start_ < loads.loc[_load]['release']:
            messages.append(f"Load {_load} has not been released at time {arc_info['start_time']:.2f} in row {_} of movement database")

        if end_ > loads.loc[_load]['deadline']:
            load_delay_penalties[_load] = delay_penalty * (end_ - loads.loc[_load]['deadline'])

        if _lfrom != loads.loc[_load]['from']:
            messages.append(f"Load {_load} is loaded at wrong origin {_lfrom}. Check movement database for route {sorted_list[0][0]}")

        if _lto != loads.loc[_load]['to']:
            messages.append(f"Load {_load} is unloaded at wrong destination {_lto}. Check movement database for route {sorted_list[-1][0]}")

        for _i in range(len(sorted_list)-1):
            if sorted_list[_i][3] > sorted_list[_i+1][1]:
                messages.append(f"Schedule conflicts in transfering load {_load} from route {sorted_list[_i][0]} to {sorted_list[_i+1][0]}. Load must be taken to tranfer location before next movement can be executed.")
            if sorted_list[_i][4] != sorted_list[_i+1][2]:
                messages.append(f"Schedule conflicts in transfering load {_load} from route {sorted_list[_i][0]} to {sorted_list[_i+1][0]}. Load must be transfered at the same location.")



    for _ind, _sch in enumerate(vehicle_schedule.values):
        if list(_sch) not in veh_schedule:
            messages.append(f"Row {_ind} in vehicle_schedule dataframe does not match with routes")

        for r in route_costs:
            route_costs[r] = round(route_costs[r], 2)

        for l in load_delay_penalties:
            load_delay_penalties[l] = round(load_delay_penalties[l], 2)


    return messages, route_costs, load_delay_penalties