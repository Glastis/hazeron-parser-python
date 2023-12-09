from xml.etree.ElementTree import parse

xml_filename = 'Star Map.xml'
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
    'Ioplasma'
]

def prepare_resources_table():
    resources = []
    for resource in resources_to_check:
        resources.append({'name' : resource, 'quality' : 0, 'system' : '', 'planet' : '', 'zone' : '', 'planet_size' : '', 'planet_type' : '', 'system_have_habitable' : False})
    return resources

def does_system_have_habitable_planet(system):
    for planet in system.findall('planet'):
        type = planet.get('bodyType')
        if type == 'Titan' or type == 'Planet' and planet.find('zone') == 'Habitable Zone':
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
        resources = parse_planet_part(system, planet, resources, 'geosphere', zones_amount)
        resources = parse_planet_part(system, planet, resources, 'atmosphere', 1)
        if type != 'Ring':
            resources = parse_planet_part(system, planet, resources, 'biosphere', zones_amount)
            resources = parse_planet_part(system, planet, resources, 'hydrosphere', 1)
    return resources

def parse_systems(sector, resources):
    for system in sector.findall('system'):
        if system.find('eod') != 'Unexplored':
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
    print(text + ' ' * (length - len(text)), end='')

def resources_pretty_print(resources):
    padding_normal = 21
    padding_small = 10
    padding_big = 30
    print_padded('Name', padding_normal)
    print_padded('Quality', padding_small)
    print_padded('System', padding_normal)
    print_padded('Planet', padding_big)
    print_padded('Zone', padding_normal)
    print_padded('Size', padding_normal)
    print_padded('Type', padding_normal)
    print_padded('Habitable', padding_small)
    print()
    for resource in resources:
        print_padded(resource['name'], padding_normal)
        print_padded(str(resource['quality']), padding_small)
        print_padded(resource['system'], padding_normal)
        print_padded(resource['planet'], padding_big)
        print_padded(resource['zone'], padding_normal)
        print_padded(resource['planet_size'], padding_normal)
        print_padded(resource['planet_type'], padding_normal)
        print_padded(str(resource['system_have_habitable']), padding_small)
        print()


def main():
    resources = prepare_resources_table()
    dom = parse(xml_filename)
    resources = parse_galaxies(dom.getroot(), resources)
    resources_pretty_print(resources)


if __name__ == '__main__':
    main()
