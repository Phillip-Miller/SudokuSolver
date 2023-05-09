VALUES_9 = "123456789"
VALUES_16 = "123456789ABCDEFG"
VALUES_25 = "ABCDEFGHIJKLMNOPQRSTUVWXY"
SIZE_DICT = {9: 3, 16: 4, 25: 5}


class FilledTileError(Exception):
    pass


class ViolateSudokuError(Exception):
    pass


class FinishedSudoku(Exception):
    pass


class SudokuMatrix:
    """
    All methods and variables are private. Only accsess by iterating and setting
    Implements cutoffs: possible solution exists, invalid assignments, possible_values
    Implements heuristics: most constrained tile first, and try most unique value first on tile

    I commonly use r,c for iterating and row col to refer to modified value.
    """

    def __init__(self, size: int):
        self.size = size
        self.size_root = SIZE_DICT[size]
        self.all_values = VALUES_9 if size == 9 else VALUES_16 if size == 16 else VALUES_25
        self.num_empty_tiles = self.size * self.size
        self.matrix = [['_'] * size for _ in range(size)]

        # if values = 0 then you have impossible fill, if value is set will be size 1
        self.tile_possible_values = [[set(self.all_values) for _ in range(size)] for _ in range(size)]
        self.tiles_with_x_possible_values = {k: set() for k in [*range(1, self.size + 1)]}

        # initially all tiles have size possible values
        for row in range(self.size):
            for col in range(self.size):
                self.tiles_with_x_possible_values[self.size].add((row, col))

        self.boxToCoords = {k: [] for k in [*range(size)]}  # f: box numer -> all coords that share same box
        self.coordsToBox = {}  # f: coordinate -> box number
        for row in range(self.size):
            for col in range(self.size):
                # size root is the size of the sub boxes
                box_num = self.size_root * divmod(row, self.size_root)[0] + divmod(col, self.size_root)[0]
                self.coordsToBox[(row, col)] = box_num
                self.boxToCoords[box_num].append((row, col))

        self.num_times_val_in_possible_val_per_row = [{k: size for k in self.all_values} for _ in range(size)]
        self.num_times_val_in_possible_val_per_col = [{k: size for k in self.all_values} for _ in range(size)]
        self.num_times_val_in_possible_val_per_box = [{k: size for k in self.all_values} for _ in range(size)]

        self.values_in_row_x = [set() for _ in range(size)]
        self.values_in_col_x = [set() for _ in range(size)]
        self.values_in_box_x = [set() for _ in range(size)]

    def check_possible_solution_exists(self, row, col):
        """
        row,col = cell that was modified
        Iterates through to make sure union of possible values for each tile in row/col/box contain all values needed
        ie: col with (2,3) (2,3) (2,3) for 3x3 would not have a valid solution as 1 not in any possible values
        """
        row_values = set(self.all_values)
        col_values = set(self.all_values)
        box_values = set(self.all_values)

        for r in range(self.size):
            col_values -= self.tile_possible_values[r][col]

        for c in range(self.size):
            row_values -= self.tile_possible_values[row][c]

        for r, c in self.boxToCoords[self.coordsToBox[(row, col)]]:
            box_values -= self.tile_possible_values[r][c]

        if not (len(col_values) == len(row_values) == len(box_values) == 0):
            raise ViolateSudokuError

    def get_least_possible_values_tile(self):
        """
        Searches through dict to find the tile with the fewest possible values
        """
        for num_possible_values in range(1, self.size + 1):
            if self.tiles_with_x_possible_values[num_possible_values]:  # non-empty
                return self.tiles_with_x_possible_values[num_possible_values].pop()
        return None

    def get_ordered_values(self, row, col):
        """
        Returns iterable that is ordered by the most unique possible value

        ie (1,2) (2,3) (2,3) -> if we pick col 0 first choose value 1 first (1 is the only possible value)
        """

        if len(self.tile_possible_values[row][col]) == 1:  # if one values dont do anything
            return list(self.tile_possible_values[row][col])

        values_set = self.tile_possible_values[row][col]
        row_values = dict.fromkeys(values_set, 0)
        col_values = dict.fromkeys(values_set, 0)
        box_values = dict.fromkeys(values_set, 0)

        for r in range(self.size):
            for k in col_values.keys() & self.tile_possible_values[r][col]:
                col_values[k] += 1

        for c in range(self.size):
            for k in row_values.keys() & self.tile_possible_values[row][c]:
                row_values[k] += 1

        for r, c in self.boxToCoords[self.coordsToBox[(row, col)]]:
            for k in box_values.keys() & self.tile_possible_values[r][c]:
                box_values[k] += 1

        combined_dict = {}
        for key in values_set:
            combined_dict[key] = min(row_values[key], col_values[key], box_values[key])

        ordered_list = list(values_set)
        ordered_list.sort(key=lambda value: combined_dict[value])

        if combined_dict[ordered_list[0]] == 1:
            if combined_dict[ordered_list[1]] == 1:
                raise ViolateSudokuError  # two values in tile that are only possible on that square
            else:
                ordered_list = ordered_list[0:1]  # if value is only possible on this tile -> only value to check
        return ordered_list

    def update_num_times_possible_value_occurs(self, row, col, box, value):
        """
        finding how many times a value occurs in possible values for row,col,box
        """

        self.num_times_val_in_possible_val_per_row[row][value] -= 1 if value not in self.values_in_row_x[row] else 0
        self.num_times_val_in_possible_val_per_col[col][value] -= 1 if value not in self.values_in_col_x[col] else 0
        self.num_times_val_in_possible_val_per_box[box][value] -= 1 if value not in self.values_in_box_x[box] else 0

        if self.num_times_val_in_possible_val_per_row[row][value] == 1:
            for c in range(self.size):  # find the tile
                if self.matrix[row][c] == "_" and value in self.tile_possible_values[row][c]:
                    for v in self.tile_possible_values[row][c] - {value}:
                        self.remove_value_from_possible_values(row, c, v)
                    break

        if self.num_times_val_in_possible_val_per_col[col][value] == 1:
            for r in range(self.size):
                if self.matrix[r][col] == "_" and value in self.tile_possible_values[r][col]:
                    for v in self.tile_possible_values[r][col] - {value}:
                        self.remove_value_from_possible_values(r, col, v)
                    break

        if self.num_times_val_in_possible_val_per_box[box][value] == 1:
            for r, c in self.boxToCoords[box]:
                if self.matrix[r][c] == "_" and value in self.tile_possible_values[r][c]:
                    for v in self.tile_possible_values[r][c] - {value}:
                        self.remove_value_from_possible_values(r, c, v)
                    break

    def remove_value_from_possible_values(self, row, col, value):
        try:
            self.tile_possible_values[row][col].remove(value)
        except KeyError:  # value not in set -> no further computation
            return
        else:  # size of set decreased
            if len(self.tile_possible_values[row][col]) == 0:
                raise ViolateSudokuError
            else:
                box = self.coordsToBox[(row, col)]
                self.tiles_with_x_possible_values[len(self.tile_possible_values[row][col]) + 1].remove((row, col))
                self.tiles_with_x_possible_values[len(self.tile_possible_values[row][col])].add((row, col))
                self.update_num_times_possible_value_occurs(row, col, box, value)

    def update_possible_values_upon_assignment(self, og_row, og_col, box, value):
        """
        Updates possible values and union of possible values upon assigning a tile (thus removing all the other possible
        values from its list).

        filled tile will have 1 possible value (its fill)
        """

        # all the values the tile could previously be are removed but not actual value since that is covered lower
        for possible_value in self.tile_possible_values[og_row][og_col] - {value}:
            self.num_times_val_in_possible_val_per_row[og_row][possible_value] -= 1
            self.num_times_val_in_possible_val_per_col[og_col][possible_value] -= 1
            self.num_times_val_in_possible_val_per_box[box][possible_value] -= 1

        self.num_times_val_in_possible_val_per_row[og_row][value] = 0
        self.num_times_val_in_possible_val_per_col[og_col][value] = 0
        self.num_times_val_in_possible_val_per_box[box][value] = 0

        # no longer want it anywhere as it is assigned
        self.tiles_with_x_possible_values[len(self.tile_possible_values[og_row][og_col])].discard((og_row, og_col))
        self.tile_possible_values[og_row][og_col] = {value}

        # updates in + shape from where rc is
        for i in range(self.size):
            # make sure not to remove value from tile we are fixing
            if i != og_col:
                self.remove_value_from_possible_values(og_row, i, value)
            if i != og_row:
                self.remove_value_from_possible_values(i, og_col, value)

        # in box but not in same og_row or og_col
        for r, c in self.boxToCoords[box]:
            if r != og_row and c != og_col:
                self.remove_value_from_possible_values(r, c, value)

    def __iter__(self):
        return self

    def __next__(self):
        if self.num_empty_tiles == 0:
            raise StopIteration
        return self.get_least_possible_values_tile()

    def __getitem__(self, rc: tuple) -> str:
        return self.matrix[rc[0]][rc[1]]

    def __setitem__(self, rc_key: tuple, new_value: str):
        r, c = rc_key
        box = self.coordsToBox[(rc_key)]
        if self.matrix[r][c] != '_':
            raise FilledTileError

        self.matrix[r][c] = new_value
        self.num_empty_tiles -= 1

        self.values_in_row_x[r].add(new_value)
        self.values_in_col_x[c].add(new_value)
        self.values_in_box_x[box].add(new_value)

        self.update_possible_values_upon_assignment(r, c, box, new_value)
        self.check_possible_solution_exists(r, c)  # cheeky cutoff
