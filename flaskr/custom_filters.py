def getStatusColor(status):
    """
        The getStatusColor acts as a custom flask template filter to format the status of a user edit to a specific color. 

        Args:
            status: An integer which represents status of an edit to an uploaded page in our wiki website.

        Returns:
            A string representing a color which identifies the current status of the edit. 
            Returns red if the edit has been declined, grey if it is pending, and green if the edit has been accepted.
    """
    if status == 1:
        return "grey"
    elif status == 2:
        return "green"
    else:
        return "red"


def getStatusName(status):
    """
        The getStatusName acts as a custom flask template filter to return the alphabetical status of an edit.

        Args:
            status: An integer which represents the current status of an edit to an uploaded page in our wiki website.

        Returns:
            A string representing the current status of the edit.
            Returns Pending if the status is 1, Accepted if the status is 2, and Declined if the status is 3.
    """
    if status == 1:
        return "Pending"
    elif status == 2:
        return "Accepted"
    else:
        return "Declined"
