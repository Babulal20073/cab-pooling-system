from math import floor, radians, sin, cos, sqrt, atan2


GRID_SIZE = 0.005
EARTH_RADIUS_KM = 6371.0

#first create grids by doing separatoin aroud 500 meter separation as 111/0.005 is around this
def get_grid_cell(lat: float, lng: float) -> tuple[int, int]:
    lat_cell = floor(lat / GRID_SIZE)
    lng_cell = floor(lng / GRID_SIZE)

    return lat_cell, lng_cell


#here we use haversine formula becuawe each is not flat but spherical so we can't just use manhatten or other one 

def get_neighboring_cells(
    cell: tuple[int, int],
) -> list[tuple[int, int]]:
    lat_cell, lng_cell = cell

    neighbors = []

    for lat_offset in (-1, 0, 1):
        for lng_offset in (-1, 0, 1):
            neighbors.append(
                (
                    lat_cell + lat_offset,
                    lng_cell + lng_offset,
                )
            )

    return neighbors


def haversine_distance(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
) -> float:

    lat1 = radians(lat1)
    lng1 = radians(lng1)

    lat2 = radians(lat2)
    lng2 = radians(lng2)

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlng / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return EARTH_RADIUS_KM * c