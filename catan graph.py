import networkx as nx
from functools import reduce

# resources
ORE = "ORE"
WOOD = "WOOD"
WOOL = "WOOL"
WHEAT = "WHEAT"
BRICK = "BRICK"

# site states
OPEN = "OPEN"
CLOSED = "CLOSED"

class Tile:
    def __init__(self, resource=None, dice_num=0):
        self.resource = resource
        self.dice_num = dice_num
        self.id = None

    def __str__(self):
        return f"{self.resource} tile ({self.dice_num})"

# tiles
TILES = [
    [Tile(BRICK, 8), Tile(WOOD, 10), Tile(WOOL, 2)],
    [Tile(WOOD, 11), Tile(WHEAT, 9), Tile(ORE, 8), Tile(WHEAT, 3)],
    [Tile(WOOL, 9), Tile(ORE, 5), Tile(WOOL, 12), Tile(WOOL, 9), Tile(WOOD, 6)],
    [Tile(), Tile(BRICK, 3), Tile(WHEAT, 6), Tile(BRICK, 11)],
    [Tile(ORE, 4), Tile(WOOD, 5), Tile(WHEAT, 4)]
]

ID_TO_TILES = dict()

# tiles per row
TILES_PER_ROW = list(map(len, TILES))

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

def get_site_id(row, col):
    return NUM_SITES_PREFIX[row] + col

def get_tile_id(row, col):
    return NUM_TILES_PREFIX[row] + col

site_graph = nx.Graph()

# construct the site graph
for i, sites in enumerate(SITES_PER_ROW):

    # connect each site in this row
    for j in range(sites - 1):
        # sites are ordered from top to bottom, left to right
        current_site_name = f"{SITE_NAME_PREFIX}{get_site_id(i, j)}"
        next_site_name = f"{SITE_NAME_PREFIX}{get_site_id(i, j + 1)}"

        site_graph.add_edge(current_site_name, next_site_name)

    # if not the first row, connect sites vertically with previous row
    if i > 0:
        sites_in_row, sites_in_prev_row = None, None

        # if the number of sites between two rows are the same, there is a one to one mapping
        if SITES_PER_ROW[i] == SITES_PER_ROW[i-1]:
            sites_in_row = list(map(lambda s: get_site_id(i, s), range(sites)))
            sites_in_prev_row = list(map(lambda s: get_site_id(i - 1, s), range(sites)))

        # if this row has more tiles, then we haven't reached halfway yet
        elif SITES_PER_ROW[i] > SITES_PER_ROW[i-1]:
            sites_in_row = list(map(lambda s: get_site_id(i, s), range(1, sites, 2)))
            sites_in_prev_row = list(map(lambda s: get_site_id(i - 1, s), range(0, SITES_PER_ROW[i - 1], 2)))

        # if this row has less less, then we are past halfway
        elif SITES_PER_ROW[i] < SITES_PER_ROW[i-1]:
            sites_in_row = list(map(lambda s: get_site_id(i, s), range(0, sites, 2)))
            sites_in_prev_row = list(map(lambda s: get_site_id(i - 1, s), range(1, SITES_PER_ROW[i - 1], 2)))

        for prev, curr in zip(sites_in_prev_row, sites_in_row):
            site_graph.add_edge(f"{SITE_NAME_PREFIX}{prev}", f"{SITE_NAME_PREFIX}{curr}")

# maps each site to the tiles they're adjacent to
surrounding_tiles = { f"{SITE_NAME_PREFIX}{get_site_id(i, j)}" : list() for i, sites in enumerate(SITES_PER_ROW) for j in range(sites) }

# maps each tile to the sites that are adjacent to them
surrounding_sites = { f"{TILE_NAME_PREFIX}{get_tile_id(i, j)}" : list() for i, tiles in enumerate(TILES_PER_ROW) for j in range(tiles) }

# construct mapping from tiles to sites
# for each row of tiles
for i, tiles in enumerate(TILES_PER_ROW):
    # for each tile in the row
    for j in range(tiles):
        tile_name = f"{TILE_NAME_PREFIX}{get_tile_id(i, j)}"
        TILES[i][j].id = tile_name
        ID_TO_TILES[tile_name] = TILES[i][j]
        for k in range(3):
            if i == 0 or (tiles > TILES_PER_ROW[i-1] and tiles < TILES_PER_ROW[i+1]):
                # top sites
                surrounding_sites[tile_name].append(f"{SITE_NAME_PREFIX}{get_site_id(i, 2 * j + k)}")
                # bottom sites
                surrounding_sites[tile_name].append(f"{SITE_NAME_PREFIX}{get_site_id(i + 1, 2 * j + k + 1)}")
            elif i == len(TILES_PER_ROW) - 1 or (tiles < TILES_PER_ROW[i-1] and tiles > TILES_PER_ROW[i+1]):
                # top sites
                surrounding_sites[tile_name].append(f"{SITE_NAME_PREFIX}{get_site_id(i, 2 * j + k + 1)}")
                # bottom sites
                surrounding_sites[tile_name].append(f"{SITE_NAME_PREFIX}{get_site_id(i + 1, 2 * j + k)}")
            else:
                # top sites
                surrounding_sites[tile_name].append(f"{SITE_NAME_PREFIX}{get_site_id(i, 2 * j + k)}")
                # bottom sites
                surrounding_sites[tile_name].append(f"{SITE_NAME_PREFIX}{get_site_id(i + 1, 2 * j + k)}")

# generate inverse of surrounding_sites, i.e. surrounding_tiles
for tile, sites in surrounding_sites.items():
    for site in sites:
        surrounding_tiles[site].append(tile)

# store site states
site_states = { k : OPEN for k in surrounding_tiles.keys() }

# finds the best first settlement given a board state
def find_best_settlement(states, scorer):
    open_sites = list(filter(lambda k: states[k] == OPEN, states.keys()))
    return max(open_sites, key=scorer)

# mark a spot as taken and mark its adjacent sites as closed too
def place_site(site):
    site_states[site] = CLOSED
    for neighbor in site_graph[site]:
        site_states[neighbor] = CLOSED

    tile_id = surrounding_tiles[site][0]
    tile = int(tile_id[len(TILE_NAME_PREFIX):])
    settlement = surrounding_sites[tile_id].index(site)
    # TODO: render the site placement in code
    print(f"site @ ({tile},{settlement})")

# math constants
w = {
    None: 0,
    WHEAT: 0.79,
    WOOD: 0.63,
    ORE: 0.5466,
    WOOL: 0.09,
    BRICK: 0.04
}

xi = lambda r, count: w[r] ** count

delta = lambda t: {
    "0": -0.7,
    "1": -0.4,
    "2": -0.2,
    "3": 0
}.get(str(t), 0.2)

a = lambda R_i, t: 0 if R_i == 1 else delta(t) * xi(R_i)

p = {
    "0": 0,
    "2": 1 / 36,
    "3": 2 / 36,
    "4": 3 / 36,
    "5": 4 / 36,
    "6": 5 / 36,
    "12": 1 / 36,
    "11": 2 / 36,
    "10": 3 / 36,
    "9": 4 / 36,
    "8": 5 / 36
}

# scoring function for first settlement
def max_score_s1(turn):
    def scorer(site):
        neighbor_tiles = surrounding_tiles[site]
        tile_objects = list(map(lambda t: ID_TO_TILES[t], neighbor_tiles))
        resources = list(map(lambda t: t.resource, tile_objects))
        resource_score = sum(map(lambda t: p[str(t.dice_num)] * w[t.resource], tile_objects))
        adjustment = 0

        counter = dict()
        for r in resources:
            counter[r] = counter.get(r, 0) + 1

        for k, v in counter.items():
            if v > 1:
                adjustment = delta(turn) / xi(k, v)

        return resource_score + adjustment

    return scorer


# scoring function for second settlement
def max_score_s2(turn):
    def scorer(site):
        neighbor_tiles = surrounding_tiles[site]
        tile_objects = list(map(lambda t: ID_TO_TILES[t], neighbor_tiles))
        resources = set(map(lambda t: t.resource, tile_objects))
        resource_score = sum(map(lambda t: p[str(t.dice_num)] * w[t.resource], tile_objects))

        has_wood_and_brick = 1 if WOOD in resources and BRICK in resources else 0

        return resource_score + delta(turn) * (has_wood_and_brick - 0.4 * (5 - len(resources)))

    return scorer

for i in range(8):
    player = i if i < 4 else 7 - i
    scoring = max_score_s1(i) if i < 4 else max_score_s2(i)
    best_spot = find_best_settlement(site_states, scoring)
    print(f"Player {player} takes {best_spot}")
    place_site(best_spot)