from xml.etree.ElementTree import parse

# xml_filename = 'Star Map.xml'
xml_filename = 'French Empire Star Map.xml'
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
    'Plant Fiber'
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
        if system.get('eod') == 'Surveyed':
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

def resources_pretty_print_get_longest_name(resources, attribute_label, attribute_name, padding=4):
    longest_name = len(attribute_label)
    for resource in resources:
        resource_len = len(str(resource[attribute_name]))
        if resource_len > longest_name:
            longest_name = resource_len
    return longest_name + padding


def resources_pretty_print(resources):
    print_padded('Name', resources_pretty_print_get_longest_name(resources, 'Name', 'name'))
    print_padded('Quality', resources_pretty_print_get_longest_name(resources, 'Quality', 'quality'))
    print_padded('System', resources_pretty_print_get_longest_name(resources, 'System', 'system'))
    print_padded('Planet', resources_pretty_print_get_longest_name(resources, 'Planet', 'planet'))
    print_padded('Zone', resources_pretty_print_get_longest_name(resources, 'Zone', 'zone'))
    print_padded('Size', resources_pretty_print_get_longest_name(resources, 'Size', 'planet_size'))
    print_padded('Type', resources_pretty_print_get_longest_name(resources, 'Type', 'planet_type'))
    print_padded('Habitable', resources_pretty_print_get_longest_name(resources, 'Habitable', 'system_have_habitable'))
    print()
    for resource in resources:
        print_padded(resource['name'], resources_pretty_print_get_longest_name(resources, 'Name', 'name'))
        print_padded(str(resource['quality']), resources_pretty_print_get_longest_name(resources, 'Quality', 'quality'))
        print_padded(resource['system'], resources_pretty_print_get_longest_name(resources, 'System', 'system'))
        print_padded(resource['planet'], resources_pretty_print_get_longest_name(resources, 'Planet', 'planet'))
        print_padded(resource['zone'], resources_pretty_print_get_longest_name(resources, 'Zone', 'zone'))
        print_padded(resource['planet_size'], resources_pretty_print_get_longest_name(resources, 'Size', 'planet_size'))
        print_padded(resource['planet_type'], resources_pretty_print_get_longest_name(resources, 'Type', 'planet_type'))
        print_padded(str(resource['system_have_habitable']), resources_pretty_print_get_longest_name(resources, 'Habitable', 'system_have_habitable'))
        print()


def main():
    resources = prepare_resources_table()
    dom = parse(xml_filename)
    resources = parse_galaxies(dom.getroot(), resources)
    resources_pretty_print(resources)


if __name__ == '__main__':
    main()
