import subprocess

def format_grid(grid):
    """
    Format a 2d array of values in to a well-formatted, aligned gridstring
    Arguments:
    - grid: A rectangular 2d array of values
    Returns: The grid as a nicely formatted string, with padding, dividers and
    truncation if it is wider than the terminal window.
    """
    header = grid[0]

    widths = [len(thing) for thing in header]

    for row in grid:
        # find the longest cell in the column so the minimum width is known
        # python's zip() function would be a cleaner way to do this than incrementing a variable
        # but for some reason it didn't work as expected
        i = 0
        for thing in row:
            length = len(thing)
            if length > widths[i]:
                widths[i] = length
            i += 1

    gridstring = '\n'
    total = sum(widths)

    # try to determine the width of the user's terminal window in characters
    # so the rows can be truncated if they are too long
    try:
        terminal_width = int(subprocess.check_output('stty size').split()[1])
    except:
        print 'The size of your terminal window could not be determined'
        print 'The layout of the grid below may be broken due to text wrapping'
        terminal_width = 80  # default width for a lot of systems

    # if the grid is wider than the terminal window work out the difference between them
    # this is the amount to truncate the grid by
    needs_truncating = False
    if total > terminal_width:
        terminal_diff = terminal_width - total - 12  # 12 is the number of dividers and spaces added
        needs_truncating = True
        widths[2] += terminal_diff  # reduce the width of the column by the difference

    for row in grid:
        i = 0
        rowstring = ''

        for cell in row:
            # truncate this column if the table would be wider than the terminal window
            # id, url and date don't vary much in width, only the local path is worth truncating
            if i == 2 and needs_truncating and len(cell) > widths[2]:
                cell = cell[:terminal_diff - 3] + '...'

            # pad with spaces so all cells in the column are the same width
            diff = widths[i] - len(cell)
            padding = ' ' * diff
            cell = ' ' + cell + padding

            rowstring += cell + ' |'  # add a divider between columns

            i += 1

        rowstring = rowstring[:-2]  # trim the last space and divider
        gridstring += rowstring + '\n'  # add the row to the final grid

        # add a horizontal divider only below the header
        if row == header:
            gridstring += '-' * len(rowstring) + '\n'

    return gridstring[:-1]  # trim the last line break
