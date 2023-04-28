from datetime import datetime

def savefig(figure, name):
    '''Save figure including timestamp to avoid
    overwriting old figures.'''
    now = datetime.now()
    timestmp = now.strftime("%Y-%m-%d-%H%M%S")
    figure.savefig("figures/%s-%s" %(timestmp, name))