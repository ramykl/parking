#dataPoints = [600.0,610.0,650.0,600.0,590.0,600.0]
initialGuessVariance = 50.0

def VarianceCalc(data,window, index):
    """
    VarianceCalc - calculates the variance of a given set of values in a window.

    Arguments:
        data: the entire list of pre-filtered data.
        window: the size of the window.
        index: the point at which the window ends.
    """
    dataPoints = data[:] #duplicates the list

    # Scales the data points so that small changes mean less.
    scale_value = 20.0
    for i in range(len(dataPoints)):
        dataPoints[i] = dataPoints[i]/scale_value

    total = 0.0
    squaredSum = 0.0
    differenceSquared =[]

    # if the window size is larger than the index
    # this means there are not enough points in the data set to 
    if index < window:
        variance = initialGuessVariance
    else:
        # Grabs the window finishing at index.
        dataSelection = dataPoints[(index-window): index]

        # Calculates the variance using:
        # variance = sum ( x_i - x) / (n-1) : i=1 to n
        for j in dataSelection:
            total +=j
        average = total/len(dataSelection)
        for k in dataSelection:
            differenceSquared.append((k-average)**2)
        for l in differenceSquared:
            squaredSum +=l
        variance = squaredSum/(window-1)

    return variance

