import sys

# Function to print to standard error for debugging
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)