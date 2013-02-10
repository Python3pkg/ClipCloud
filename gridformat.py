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
    total = sum(widths)

    # Try to determine the width of the user's terminal window in characters
    # so the rows can be truncated if they are too long
    try:
        import subprocess
        terminal_width = int(subprocess.check_output('stty size').split()[1])

    except:
        print 'The size of your terminal window could not be determined so ' \
            'the layout of the grid below may be broken due to text wrapping.'

        # Default width for a lot of systems
        terminal_width = 80

    # If the grid is wider than the terminal window work out the difference between them -
    # this is the number of characters by which the table should be truncated
    terminal_diff = None

    if total > terminal_width:
        if truncatable_column is not None:
            # 12 is the number of dividers and spaces added
            terminal_diff = terminal_width - total - 12
            # Reduce the width of the column by the difference
            widths[2] += terminal_diff

        else:
            print 'The grid is wider than your terminal but no columns can be truncated so ' \
                'some columns may not be visible.'

    # Final grid array
    a = []

    for row in grid:
        # Truncate column 3 if the table would be wider than the terminal window
        # id, url and date don't vary much in width, only the local path is worth truncating
        if truncatable_column is not None and terminal_diff is not None and \
            len(row[truncatable_column]) > widths[truncatable_column]:
            row[truncatable_column] = row[truncatable_column][:terminal_diff - 3] + '...'

        # Format the cells into a string with dividers between and add the row to the final grid
        # and pad with spaces so all cells in the column are the same width
        s = ((' {:%d} |' * len(widths))[:-1] % tuple(widths)).format(*row)
        a.append(s)

    # Add a horizontal divider below the column titles
    width = len(s)

    for pos, i in zip(divider_positions, xrange(len(divider_positions))):
        a.insert(pos + i, '-' * width)

    # Create the final string and trim the last line break
    return '\n' + '\n'.join(a)[:-1]
