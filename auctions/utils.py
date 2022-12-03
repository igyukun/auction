import datetime as d

def DEBUG_PRINT(txt):
    """
    This function prints text, passed as an argument, into the 
    'debug.txt' file, preceeded with the current timestamp
    Args:
        txt (string): debug text
    """
    with open('debug.txt', 'a', encoding="utf-8") as f:
        f.write(f"{d.datetime.now()}:{txt}\n")
    