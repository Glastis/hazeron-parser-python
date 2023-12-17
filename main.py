from xml.etree.ElementTree import parse

resources_to_check = [
    'Bolite',
    'Coal',
    'Crystals',
    'Gems',
    'Gold Ore',
    'Ice',
    'Lumenite',
    'Eludium',
    'Minerals',
    'Oil',
    'Phlogiston',
    'Ore',
    'Vulcanite',
    'Polytaride',
    'Radioactives',
    'Myrathane',
    'Air',
    'Magmex',
    'Adamantite',
    'Viathol',
    'Flomentum',
    'Borexino Precipitate',
    'Ioplasma',
    'Animal Carcass',
    'Beans',
    'Cheese',
    'Eggs',
    'Fertilizer',
    'Fruit',
    'Grain',
    'Grapes',
    'Herbs',
    'Hops',
    'Log',
    'Milk',
    'Nuts',
    'Plant Fiber',
    'Spices',
    'Vegetable',
    'Vegetation Density',
]

# script arguments:
# -i input file name, eg. -i "Star Map.xml". Required.
# -s systems to check, separated by comma, eg. -s "Alderaan,Coruscant". If not specified, all systems will be checked.
# --no-ring if specified, rings will be ignored.
# --no-asteroid or --no-planetoid if specified, asteroids will be ignored.
# --habitable if specified, only systems with habitable planets will be checked.

args = None
def parse_args():
    import argparse
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file name', required=True)
    parser.add_argument('-s', '--systems', help='systems to check, separated by comma', required=False)
    parser.add_argument('--no-ring', help='if specified, rings will be ignored', action='store_true')
    parser.add_argument('--no-asteroid', help='if specified, asteroids will be ignored, same as --no-planetoid', action='store_true')
    parser.add_argument('--no-planetoid', help='if specified, planetoids will be ignored, same as --no-asteroid', action='store_true')
    parser.add_argument('--habitable', help='if specified, only systems with habitable planets will be checked', action='store_true')
    args = parser.parse_args()
    if args.no_planetoid:
        args.no_asteroid = True

def prepare_resources_table():
    resources = []
    for resource in resources_to_check:
        resources.append({'name' : resource, 'quality' : 0, 'system' : '', 'planet' : '', 'zone' : '', 'planet_size' : '', 'planet_type' : '', 'system_have_habitable' : False})
    return resources

def does_system_have_habitable_planet(system):
    for planet in system.findall('planet'):
        type = planet.get('bodyType')
        if (type == 'Titan' or type == 'Planet') and planet.get('zone') == 'Habitable Zone':
            return True
    return False

def planet_get_size(planet):
    geosphere = planet.find('geosphere')
    return geosphere.get('diameter')

def get_resource_index_by_name(resources, name):
    i = 0
    while i < len(resources):
        if resources[i]['name'] == name:
            return i
        i += 1
    return -1

def parse_planet_part(system, planet, resources, part_name, zones_amount):
    part = planet.find(part_name)
    if part is None:
        print('No ' + part_name + ' on ' + planet.get('name'))
        return resources
    resources_on_planet = part.findall('resource')
    for resource in resources_on_planet:
        resource_name = resource.get('name')
        best_resource_index = get_resource_index_by_name(resources, resource_name)
        if best_resource_index == -1:
            continue
        i = 0
        while i < zones_amount:
            quality = int(resource.get('qualityZone' + str(i + 1)))
            if quality > resources[best_resource_index]['quality']:
                resources[best_resource_index]['quality'] = quality
                resources[best_resource_index]['system'] = system.get('name')
                resources[best_resource_index]['planet'] = planet.get('name')
                resources[best_resource_index]['zone'] = str(i + 1)
                resources[best_resource_index]['planet_size'] = planet_get_size(planet)
                resources[best_resource_index]['planet_type'] = planet.get('bodyType')
                resources[best_resource_index]['system_have_habitable'] = does_system_have_habitable_planet(system)
            i += 1
    return resources

def planet_get_zones_amount(planet):
    geosphere = planet.find('geosphere')
    return int(geosphere.get('resourceZones'))

def parse_planets(system, resources):
    for planet in system.findall('planet'):
        zones_amount = planet_get_zones_amount(planet)
        type = planet.get('bodyType')
        if (args.no_ring and type == 'Ring') or (args.no_asteroid and type == 'Planetoid') or (args.habitable and not does_system_have_habitable_planet(system)):
            continue
        resources = parse_planet_part(system, planet, resources, 'geosphere', zones_amount)
        resources = parse_planet_part(system, planet, resources, 'atmosphere', 1)
        if type != 'Ring':
            resources = parse_planet_part(system, planet, resources, 'biosphere', zones_amount)
            resources = parse_planet_part(system, planet, resources, 'hydrosphere', 1)
    return resources

def parse_systems(sector, resources):
    for system in sector.findall('system'):
        if (args.systems is None or system.get('name') in args.systems.split(',')) and system.get('eod') == 'Surveyed':
            resources = parse_planets(system, resources)
    return resources

def parse_sectors(galaxy, resources):
    for sector in galaxy.findall('sector'):
        resources = parse_systems(sector, resources)
    return resources

def parse_galaxies(root, resources):
    for galaxy in root.findall('galaxy'):
        resources = parse_sectors(galaxy, resources)
    return resources

def print_padded(text, length):
    print(str(text) + ' ' * (length - len(str(text))), end='')

def resources_pretty_print_get_longest_name(resources, attribute_label, attribute_name, padding=2):
    longest_name = len(str(attribute_label))
    for resource in resources:
        resource_len = len(str(resource[attribute_name]))
        if resource_len > longest_name:
            longest_name = resource_len
    return longest_name + padding

def resources_pretty_print_element(text, resources, label, attribute_name, padding=4):
    padding = resources_pretty_print_get_longest_name(resources, label, attribute_name, padding)
    print_padded(text, padding)

def resources_pretty_print(resources):
    resources_pretty_print_element('Name', resources, 'Name', 'name')
    resources_pretty_print_element('Quality', resources, 'Quality', 'quality')
    resources_pretty_print_element('System', resources, 'System', 'system')
    resources_pretty_print_element('Planet', resources, 'Planet', 'planet')
    resources_pretty_print_element('Zone', resources, 'Zone', 'zone')
    resources_pretty_print_element('Size', resources, 'Size', 'planet_size')
    resources_pretty_print_element('Type', resources, 'Type', 'planet_type')
    resources_pretty_print_element('Habitable', resources, 'Habitable', 'system_have_habitable')
    print()
    for resource in resources:
        resources_pretty_print_element(resource['name'], resources, 'Name', 'name')
        resources_pretty_print_element(resource['quality'], resources, 'Quality', 'quality')
        resources_pretty_print_element(resource['system'], resources, 'System', 'system')
        resources_pretty_print_element(resource['planet'], resources, 'Planet', 'planet')
        resources_pretty_print_element(resource['zone'], resources, 'Zone', 'zone')
        resources_pretty_print_element(resource['planet_size'], resources, 'Size', 'planet_size')
        resources_pretty_print_element(resource['planet_type'], resources, 'Type', 'planet_type')
        resources_pretty_print_element(resource['system_have_habitable'], resources, 'Habitable', 'system_have_habitable')
        print()

def main():
    parse_args()
    resources = prepare_resources_table()
    dom = parse(args.input)
    resources = parse_galaxies(dom.getroot(), resources)
    resources_pretty_print(resources)


if __name__ == '__main__':
    main()
