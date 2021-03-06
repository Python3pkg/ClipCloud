from settings import DEBUG


def format_grid(grid, divider_positions=[], truncatable_column=None):
    """
    Create a string that displays a 2D array of values in a formatted and aligned table

    grid - A rectangular 2D array of values
    divider_positions - An array of integers specifying the indices of the rows of the grid
                        to add dividers to. Defaults to no dividers.
    truncatable_column - The index of a column whose data can be sensibly truncated

    Returns the grid as a nicely formatted string, with padding, dividers and
    truncation if it is wider than the terminal window
    """

    # Find the longest cell in each column so the minimum width is known
    widths = [max([len(cell) for cell in row]) for row in zip(*grid)]
    # Total number of characters in the contents of the widest row in the table
    total = sum(widths)
    # Number of columns in the grid
    num_columns = len(grid[0])
    # Number of characters in the string used to separate columns
    separator_width = 3
    # Total number of characters used by all column separators in one row of the grid
    separators_width = num_columns * separator_width
    # Default width for a lot of systems
    terminal_width = 80
    # Format string for each cell of the table
    cell_template = ' {:%d} |'
    # Format string for each row of the table
    row_template = (cell_template * len(widths))[:-1]
    # String used to signify that a string has been truncated
    truncation_marker = '...'

    # Try to determine the width of the user's terminal window in characters
    # so the rows can be truncated if they are too long
    try:
        import subprocess
        terminal_width = int(subprocess.check_output(['stty', 'size']).split()[1])

    except Exception as error:
        if DEBUG:
            print(error)
        print('The size of your terminal window could not be determined so ' \
            'the layout of the grid below may be broken due to text wrapping.')

    # If the grid is wider than the terminal window work out the difference between them -
    # this is the number of characters by which the table should be truncated
    terminal_diff = None

    if total > terminal_width:
        if truncatable_column is not None:
            terminal_diff = terminal_width - total - separators_width
            # Reduce the width of the column by the difference
            widths[truncatable_column] += terminal_diff

        else:
            print('The grid is wider than your terminal but no columns can be truncated so ' \
                'some columns may not be visible.')

    # Interpolate the widths of each column of the table into the row format string
    row_template = row_template % tuple(widths)

    # Final grid array
    a = []

    for row in grid:
        # Truncate column 3 if the table would be wider than the terminal window
        # id, url and date don't vary much in width, only the local path is worth truncating
        if truncatable_column is not None and terminal_diff is not None and \
            len(row[truncatable_column]) > widths[truncatable_column]:
            row[truncatable_column] = row[truncatable_column][:terminal_diff - len(truncation_marker)] + truncation_marker

        # Format the cells into a string with dividers between and add the row to the final grid
        # and pad with spaces so all cells in the column are the same width
        a.append(row_template.format(*row))

    # Add a horizontal divider below the column titles
    width = len(a[0])

    for pos, i in zip(divider_positions, range(len(divider_positions))):
        a.insert(pos + i, '-' * width)

    # Create the final string and trim the last line break
    return '\n' + '\n'.join(a)[:-1]
