def getStatusColor(status):
    if status == 1:
        return "grey"
    elif status == 2:
        return "green"
    else:
        return "red"

def getStatusName(status):
    if status == 1:
        return "Pending"
    elif status == 2:
        return "Accepted"
    else:
        return "Declined"