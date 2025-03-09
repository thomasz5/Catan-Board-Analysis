from graphviz import Graph
from functools import reduce

# tiles per row
TILES_PER_ROW = [3, 4, 5, 4, 3]

# number of sites per row
SITES_PER_ROW = []
for i, tiles in enumerate(TILES_PER_ROW):
    SITES_PER_ROW.append(2 * tiles + 1)

    # middle row of tiles contribut to two rows of sites
    if i == len(TILES_PER_ROW) // 2:
        SITES_PER_ROW.append(2 * tiles + 1)

# site name prefix
SITE_NAME_PREFIX = "s_"

# tile name prefix
TILE_NAME_PREFIX = "t_"

# number sites that have appeared in earlier rows
reducer = lambda prev, curr: prev + [prev[-1] + curr]
NUM_SITES_PREFIX = reduce(reducer, SITES_PER_ROW[:-1], [0])

# number of tiles that appeared in earlier rows
NUM_TILES_PREFIX = reduce(reducer, TILES_PER_ROW[:-1], [0])

def get_site_num(row, col):
    return NUM_SITES_PREFIX[row] + col

def get_tile_num(row, col):
    return NUM_TILES_PREFIX[row] + col

site_graph = Graph("sites", "Represents the sites on the Catan board")

# construct the site graph
for i, sites in enumerate(SITES_PER_ROW):

    # connect each site in this row
    for j in range(sites - 1):
        # sites are ordered from top to bottom, left to right
        current_site_name = f"{SITE_NAME_PREFIX}{get_site_num(i, j)}"
        next_site_name = f"{SITE_NAME_PREFIX}{get_site_num(i, j + 1)}"

        site_graph.edge(current_site_name, next_site_name)

    # if not the first row, connect sites vertically with previous row
    if i > 0:
        sites_in_row, sites_in_prev_row = None, None

        # if the number of sites between two rows are the same, there is a one to one mapping
        if SITES_PER_ROW[i] == SITES_PER_ROW[i-1]:
            sites_in_row = list(map(lambda s: get_site_num(i, s), range(sites)))
            sites_in_prev_row = list(map(lambda s: get_site_num(i - 1, s), range(sites)))

        # if this row has more tiles, then we haven't reached halfway yet
        elif SITES_PER_ROW[i] > SITES_PER_ROW[i-1]:
            sites_in_row = list(map(lambda s: get_site_num(i, s), range(1, sites, 2)))
            sites_in_prev_row = list(map(lambda s: get_site_num(i - 1, s), range(0, SITES_PER_ROW[i - 1], 2)))

        # if this row has less less, then we are past halfway
        elif SITES_PER_ROW[i] < SITES_PER_ROW[i-1]:
            sites_in_row = list(map(lambda s: get_site_num(i, s), range(0, sites, 2)))
            sites_in_prev_row = list(map(lambda s: get_site_num(i - 1, s), range(1, SITES_PER_ROW[i - 1], 2)))

        for prev, curr in zip(sites_in_prev_row, sites_in_row):
            site_graph.edge(f"{SITE_NAME_PREFIX}{prev}", f"{SITE_NAME_PREFIX}{curr}")

site_graph.save()

# maps each site to the tiles they're adjacent to
surrounding_tiles = { f"{SITE_NAME_PREFIX}{get_site_num(i, j)}" : set() for i, sites in enumerate(SITES_PER_ROW) for j in range(sites) }

# maps each tile to the sites that are adjacent to them
surrounding_sites = { f"{TILE_NAME_PREFIX}{get_tile_num(i, j)}" : set() for i, tiles in enumerate(TILES_PER_ROW) for j in range(tiles) }

# construct mapping from tiles to sites
# for each row of tiles
for i, tiles in enumerate(TILES_PER_ROW):
    # for each tile in the row
    for j in range(tiles):
        tile_name = f"{TILE_NAME_PREFIX}{get_tile_num(i, j)}"
        for k in range(3):
            # top sites
            surrounding_sites[tile_name].add(f"{SITE_NAME_PREFIX}{get_site_num(i, 2 * j + k)}")
            # bottom sites
            surrounding_sites[tile_name].add(f"{SITE_NAME_PREFIX}{get_site_num(i + 1, 2 * j + k)}")

# generate inverse of surrounding_sites, i.e. surrounding_tiles
for tile, sites in surrounding_sites.items():
    for site in sites:
        surrounding_tiles[site].add(tile)