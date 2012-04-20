def format_grid(grid, divider_positions=[]):
    """
    Format a 2d array of values in to a well-formatted, aligned gridstring
    Arguments:
    - grid: A rectangular 2d array of values
    - divider_positions: an array of integers specifying the rows of the grid to add dividers to
    defaults to no dividers.
    Returns: The grid as a nicely formatted string, with padding, dividers and
    truncation if it is wider than the terminal window.
    """
    # find the longest cell in the column so the minimum width is known
    widths = []
    for y in [x for x in zip(*grid)]:
        widths.append(max([len(z) for z in y]))

    total = sum(widths)

    # try to determine the width of the user's terminal window in characters
    # so the rows can be truncated if they are too long
    try:
        import subprocess
        terminal_width = int(subprocess.check_output('stty size').split()[1])
    except:
        print 'The size of your terminal window could not be determined'
        print 'The layout of the grid below may be broken due to text wrapping'
        terminal_width = 80  # default width for a lot of systems

    # if the grid is wider than the terminal window work out the difference between them
    # this is the amount to truncate the grid by
    terminal_diff = None
    if total > terminal_width:
        terminal_diff = terminal_width - total - 12  # 12 is the number of dividers and spaces added
        widths[2] += terminal_diff  # reduce the width of the column by the difference

    a = []  # final grid array
    for row in grid:
        # truncate column 3 if the table would be wider than the terminal window
        # id, url and date don't vary much in width, only the local path is worth truncating
        if terminal_diff is not None and len(row[2]) > widths[2]:
            row[2] = row[2][:terminal_diff - 3] + '...'

        # format the cells into a string with dividers between and add the row to the final grid
        # and pad with spaces so all cells in the column are the same width
        s = ((' {:%d} |' * len(widths))[:-1] % tuple(widths)).format(*row)
        a.append(s)

    # add a horizontal divider only below the header
    width = len(s)
    for pos, i in zip(divider_positions, xrange(len(divider_positions))):
        a.insert(pos + i, '-' * width)

    return '\n' + '\n'.join(a)[:-1]  # convert to the final string and trim the last line break
