import csv
from math import *
import matplotlib.pyplot as plt
from varianceWVM import *

# Kalman Filter Constants
initialGuess = 645.0
initialGuessVariance = 10.0
measurementVariance = 2.54
scaleValue = 1.0

# Car/ sensor parameters
MIN_CAR_LENGTH = 1.0 # 1 meter minimum car length
MAX_CAR_LENGTH = 5.0 # 5 meter maximum car length
MIN_CAR_DISTANCE = 0
MAX_CAR_DISTANCE = 260
SENSOR_FREQUENCY = 20 #20 Hz Ultrasonic Sensors

#The filename of the csv file that contains the raw data
filename = '/Users/jason/Documents/Data.csv'
"""
supplying 'U' opens the file as a text file, but lines may be terminated by any of the following: the Unix end-of-line convention '\n', the Macintosh convention '\r', or the Windows convention '\r\n'.
datareader = csv.reader(datafile)
"""
datafile = open(filename, 'U') #Opens the file with the mode universal.

"""
These lists are of the same size. Each element corresponds to the same time as 
the same position element in the other list.
"""
data_list = [] #A list to hold the raw ultrasonic data.
speed_list = [] #A list to hold the speed of the vehicle (m/s)

"""
The csv file had the format:
    collumn 1: ultrasonic data
    collumn 3: speed data (km/h)

    row is a list of strings.
    Each element in the list corresponds to the collumn number.
"""
for row in datareader:
    if (row[0] == ''):
        break
    data_list.append(float(row[0]))
    speed_list.append(float(row[2])/3.6) #Convert to m/s

def Kalman(data):
    """
    Kalman - filters the data, using a modified kalman filter method.

    Arguments:
        data - a list of data to be filtered.

    Returns:
        estimation_list - a list of filtered data.
    """

    estimation_list = [] # Creates the empty list for the filtered data.
    measured = data[0]

    # The guess variance is the variance of the given piece of data.
    guessVariance = initialGuessVariance
    guess = initialGuess

    #Loops through all data points in the given data set and filters accoringly.
    for i in range(len(data)):
        #Limits the data so that it does not exceed 700 (cm)
        #the ultrasonic sensor cannot read that far.
        if (data[i] >700):
            data[i] = 600

        weight = Weight(guessVariance)
        guess = Estimate(data[i], guess, weight)
        estimation_list.append(guess)

        #Using the modified kalman filter - absolute difference method.
        #Since there is no previous data, the variance must be calculated
        # from an initial guess.
        # comment this section if not using this method.
        if i == 0:
            guessVariance = Variance(guessVariance, data[i], initialGuess)
        else:
            guessVariance = Variance(guessVariance, data[i], data[i-1])

        # Using the modified kalman filter - windowed variance method.
        # uncomment if you want to use this method.
        ## guessVariance = VarianceCalc(data, window)

    return estimation_list


def errorCalc(data, filtered_list):
    """
    errorCalc - calculates the percentage difference between two data sets.

    This function is unused, however it could be used to check how significant
    the effect of the filtering was.

    Arguments:
        data:   a list of data points before filtering.
        filtered_list:  a list of data points corresponding to the data variable
                        after filtering has occured.

    Returns:
        the percentage difference bewteen the two data sets.
    """

    error_sum = 0
    if len(data) == len(filtered_list):
        for i in range(len(data)):
            error_sum = error_sum + filtered_list[i]/data[i]
    return error_sum/(len(data))


def Weight(guessVariance):
    """
    Weight - calcualtes the weight of the given variance. (Uses a typical kalman
            filter weight calcualtion.

    Arguments:
        guessVariance:  the vaiance calulated by the kalman filter.

    Returns
        the weighting of the given variance.

    """
    weight = guessVariance/sqrt(guessVariance**2+measurementVariance**2)
    return weight

def Variance(oldVar, measuredValue, previousValue):
    """
    Variance - calculates the variance of a measured value using the absolute
                difference method.
                scale = 1 for this scenario.

    Absolute Difference Method:
        variance_i = scale * |data_i - data_(i-1)|
                                /sqrt(variance_(i-1)**2-measurement_variance**2)

    Arguments:
        oldVar: the variance of the previous value.
        measuredValue:  the value of which the variance is being calcualted.
        previousValue:  the value of which is previous to the measured value.

    Returns:
        the variance of a measured value
    """
    result = scaleValue*abs(measuredValue-previousValue)\
            /sqrt(oldVar**2+measurementVariance**2)
    return result

def Estimate(measured,guess,Weight):
    """
    Estiamte - calculates a filtered data point for using the kalman filter.

    Arguments:
        measured:   the raw reading/ the unfiltered point
        guess:  a point at which the filter calculated
        weight: the likelyhood that the measured value is correct (0-1)

    Returns:
        estimate: the final filtered value.
    """
    estimate = guess+Weight*(measured-guess)
    return estimate

def MakeDiscrete(estimation_list):
    """
    MakeDiscrete - a function that converts the filtered data into low and high
    values.

    Arguments:
        estimation_list:    a list of the filtered data

    Returns:
        new_data:   a list of digital values (0 and 1), that correspond to
                    the distance of the object. 
                    0 being within the range of a car, 1 being other values
    """

    new_data = []
    #Loops through all elements in the filtered data list and digitises 
    #the values.
    for i in range(len(estimation_list)):
        # Determines the digital values of the filtered data.
        # Checks if the value is in the range of a car.
        if estimation_list[i] < MAX_CAR_DISTANCE and\
                estimation_list[i] > MIN_CAR_DISTANCE:
            new_data.append(0)
        else:
            new_data.append(1)

    return new_data

def CarChecker(discrete_data):
    """
    CarChecker - determines where cars are from a given set of digitised data.

    Arguments:
        discrete_data:  a list of digitised (0 or 1's) values.
                        0's correspond to within the range of a car
                        1's are other

    Returns:
        number_of_cars: a counter of how many cars there are from a given set
                        of data.
        is_car: a list of digital (0 or 1's) that correspond to the location of
                a car.
                0's correspond to no car
                1's correspond to a car
    """
    is_car = []
    speed_sum = 0 

    # Loops through the elements in the digital data.
    # 1. inverses the digital data - 0's -> 1's vice versa.
    # 2. creates a list of 0's in the is_car list.
    for i in range(len(discrete_data)):
        discrete_data[i] = 1 - discrete_data[i]
        is_car.append(0)

    marker = 0  # a marker that indicates the position of the 
                # beginning of a possible car.
    prev_marker = 0 # the previous marker.
    number_of_cars = 0 # a counter for the number of cars.

    # Loops through the digital data and sets a 1 at values where a car is.
    for i in range(len(discrete_data)):
        # If the digital value is 0, then there is no car there.
        if discrete_data[i] == 0:
            marker = 0
            speed_sum = 0

        # If the digital value is 1 and the marker has not been set.
        # This indicates the beginning of a car.
        elif discrete_data[i] == 1 and marker == 0:
            # Resets the a timer and the marker.
            time_since_marker = 0
            marker = i

        # If the digital value is 1 and the marker has been set.
        # This indicates any location along a car.
        elif discrete_data[i] == 1:

            # speed_sum is the sum of the speeds since the marker.
            speed_sum = speed_sum + speed_list[i]
            # average_speed is the average of the speeds since the marker.
            average_speed = speed_sum/(i - marker+1)
            time_since_marker = (1.0/SENSOR_FREQUENCY)*(i - marker)
            length = average_speed*time_since_marker

            # If the length of the car exceeds the minimum car length
            # set from the marker to the current point to 1.
            if MIN_CAR_LENGTH < length:
                for j in range(i-marker+1):
                    is_car[marker+j] = 1

            # If the length of the car exceeds the maximum car length
            # treat that point as a new car.
            if MAX_CAR_LENGTH < length:
                #Sets the current point to a cleared point.
                # i.e. 0 in the digital point, clears the marker, 
                # resets the speed.
                is_car[i] = 0
                marker = 0
                speed_sum = 0
    # Loops through the is_car data and looks for falling edges. This indicates
    # a new car.
    for i in range(1, len(is_car)):
        if is_car[i] == 0 and is_car[i-1] == 1:
            number_of_cars += 1

    return number_of_cars, is_car

def writeCsvFile(fname, data, *args, **kwargs):
    """
    writeCsvFile - creates a single column csv file.

    Arguments:
        fname - the filename of the new csv file.
        data - a list data points
    """
    mycsv = csv.writer(open(fname, 'wb'), *args, **kwargs)
    for row in data:
        mycsv.writerow(row)

if __name__ == '__main__':
    estimation_list = Kalman(data_list)
    estimation_list = Kalman(estimation_list)
    estimation_list = Kalman(estimation_list)
    new_data = MakeDiscrete(estimation_list)
    number_of_cars, is_car = CarChecker(new_data)
    print number_of_cars

    csvList = []
    for item in estimation_list:
        tempList = [item]
        csvList.append(tempList)

    csvList1 = []
    for item in is_car:
        tempList = [item]
        csvList1.append(tempList)

    writeCsvFile(r'/Users/jason/Documents/FilteredData.csv', csvList)
    writeCsvFile(r'/Users/jason/Documents/DigitalData.csv',csvList1)
