import math
import random
import itertools
from sklearn.cluster import AgglomerativeClustering
import pygame


# function that calculates the distance between two circles
def get_distance(circle1, circle2):
    return math.dist(circle1.get_center(), circle2.get_center())


def inverse_color(color):
    color = color[0:3]
    red, green, blue = color
    return 255 - red, 255 - green, 255 - blue


# gets the total length of all the line segments combined
def get_length(circles):
    length = 0

    # goes through the indices of all the circles
    for i in range(len(circles)):
        j = (i + 1) % len(circles)

        length += get_distance(circles[i], circles[j])

    return length


# loops through and gets all of the circle centers
def get_centers(circles):
    centers = []
    for circle in circles:
        centers.append(circle.get_center())
    return centers


# randomly orders the circles
def random_order(circles):
    random.shuffle(circles)
    return circles


# takes the foremost circle and find the closest one to it
def closest_order(circles):
    # initialize the set
    temp_circles = circles

    # goes through all the circle indices
    for i in range(len(temp_circles)):

        # initializes the shortest distance and closest circle
        shortest_distance = 0
        closest_circle = None
        # goes through all the following indices
        for j in range(i + 1, len(temp_circles)):
            # calculates the distance to the other circle
            temp_distance = get_distance(circles[i], circles[j])

            # if the distance is shorter than a previous one or there is not saved value
            # then it is saved as the new shortest distance and closest circle
            if temp_distance < shortest_distance or shortest_distance == 0:
                shortest_distance = temp_distance
                closest_circle = circles[j]

        # places the closest circle earlier in the list
        if closest_circle is not None:
            temp_circles.remove(closest_circle)
            temp_circles.insert(i + 1, closest_circle)

    # reassigns the new set to the circles variable
    return temp_circles


# find the optimal order of the set by going through all possible combinations
def optimal_order(circles):
    # initialize optimal order and minimum length
    optimal_circles = None
    min_length = 0

    # loops through all possible combinations of the circles
    for temp_circles in itertools.permutations(circles):

        # gets the length of the order of circles
        temp_length = get_length(temp_circles)

        # checks if this is the first or smallest length by far and assigns it accordingly
        if temp_length < min_length or min_length == 0:
            min_length = temp_length
            optimal_circles = temp_circles

    # converts to list for easier use
    return list(optimal_circles)


# clusters the circles and sorts each cluster before combining them together
def cluster_order(circles, max_size):
    # defines the number of clusters for the clustering algorithm
    count = len(circles)
    const = 1
    a = 0.15
    cluster_count = math.ceil(a * count + const)

    # gets the centers off all the circles for the clustering
    centers = get_centers(circles)

    # clusters the circles together
    clustering = AgglomerativeClustering(cluster_count).fit(centers)

    # gets the groupings of the circles as a list of integers with each integer representing a group
    labels = list(clustering.labels_)

    # checks if the number of clusters is too big and returns the original array if so
    if cluster_count > max_size or len(circles) > 4 * max_size:
        return circles

    # checks if any of clusters are too big and returns the original array if so
    # the clusters can have two more items since the first and last elements are not permuted
    for i in range(cluster_count):
        if labels.count(i) > max_size + 2:
            return circles

    # goes through all of the cluster values and groups each cluster into their own array
    # these array are then combined together into a larger array
    # also assigns each circle a new colour based on its cluster
    clustered_array = []
    for i in range(cluster_count):
        temp_array = []
        for j in range(count):
            if labels[j] == i:
                temp_circle = circles[j]
                if cluster_count > 1:
                    col_val = 255 / (cluster_count - 1) * i
                    color = (255 - col_val, abs(128 - col_val), col_val)
                    temp_circle.set_color(color)
                temp_array.append(temp_circle)
        clustered_array.append(temp_array)

    # gets the centers of each cluster and then makes them into a circle which is then added to an array
    cluster_circles = []
    cluster_centers = []
    for cluster in clustered_array:
        cluster_center = get_cluster_center(cluster)
        cluster_centers.append(cluster_center)
        cluster_circles.append(Circle(cluster_center, 0, None))

    # uses the provided ordering function to order the circles representing the clusters
    ordered_cluster_circles = optimal_order(cluster_circles)

    # gets gets the ordered cluster circles and then adds the respective clusters to a new array
    # this is done in the order of the cluster circles so they are in the order function order
    ordered_cluster_array = []
    for cluster_circle in ordered_cluster_circles:
        index = cluster_centers.index(cluster_circle.get_center())
        ordered_cluster_array.append(clustered_array[index])

    # gets the closest endpoints between all of the clusters
    endpoints = closest_endpoints(ordered_cluster_array)

    # for each cluster the endpoints are moved to the outside of the cluster
    # the left endpoint is moved to the first index
    # the right endpoint is moved to the last index
    for i in range(cluster_count):

        # avoids clusters of length 1
        if len(ordered_cluster_array[i]) > 1:
            cluster = ordered_cluster_array[i]
            first_circle = endpoints[i][0]
            last_circle = endpoints[i][1]

            cluster = to_front(cluster, first_circle)
            cluster = to_back(cluster, last_circle)

            ordered_cluster_array[i] = cluster

    # each cluster has its circles ordered and then reassigned to the cluster array
    for i in range(cluster_count):
        ordered_cluster_array[i] = cluster_optimal_order(ordered_cluster_array[i])

    # adds all of the circles of all the clusters to one array of just circles that is then returned
    ord_circles = []
    for cluster in ordered_cluster_array:
        ord_circles.extend(cluster)

    return ord_circles


# orders optimally for the clusters
def cluster_optimal_order(circles):
    # initialize optimal order and minimum length
    optimal_circles = None
    min_length = 0

    # splits the array into the first, last and middle circles
    first_circle = circles[0]
    last_circle = circles[-1]
    middle_circles = circles[1:-1]

    # loops through all possible combinations of the middle circles
    for temp_circles in itertools.permutations(middle_circles):

        # adds the first and last circle here so they are always the same
        temp_circles = list(temp_circles)
        temp_circles.insert(0, first_circle)
        temp_circles.append(last_circle)

        # gets the length of the order of circles
        temp_length = get_length(temp_circles)

        # checks if this is the first or smallest length by far and assigns it accordingly
        if temp_length < min_length or min_length == 0:
            min_length = temp_length
            optimal_circles = temp_circles

    # converts to list for easier use
    return list(optimal_circles)


# gets the average center of all the circles in the set
def get_cluster_center(cluster):
    # x and y values to count total amounts
    x_total = 0
    y_total = 0

    # sums all of the x and y values in the set
    for circle in cluster:
        x, y = circle.get_center()
        x_total += x
        y_total += y

    # divides the total to get the average
    x_avg = round(x_total / len(cluster))
    y_avg = round(y_total / len(cluster))

    # assigns the values to a tuple for the center and returns it
    cluster_center = (x_avg, y_avg)
    return cluster_center


# gets all the possible combinations of endpoints
def get_endpoints(cluster):
    endpoints = []

    if len(cluster) > 1:
        for i in range(0, len(cluster)):
            for j in range(i + 1, len(cluster)):
                # makes sure that both the forward and reverse combinations are gotten
                endpoints.append([cluster[i], cluster[j]])
                endpoints.append([cluster[j], cluster[i]])
    else:
        endpoints.append([cluster[0], cluster[0]])
    return endpoints


# find the shortest ordering of endpoints
def closest_endpoints(cluster_array):
    reduced_cluster_array = []

    for i in range(len(cluster_array)):
        j = (i + 1) % len(cluster_array)
        k = (i - 1) % len(cluster_array)

        # gets the nearest two clusters
        cluster = cluster_array[i]
        cluster_after = cluster_array[j]
        cluster_before = cluster_array[k]

        # gets the closest points from the cluster to the the nearest two clusters
        reduced_cluster = []
        reduced_cluster.extend(closest_two(cluster_before, cluster))
        reduced_cluster.extend(closest_two(cluster_after, cluster))

        # removes duplicates values from the cluster
        reduced_cluster = list(dict.fromkeys(reduced_cluster))

        reduced_cluster_array.append(reduced_cluster)

    endpoints_array = []

    # gets all the of possible ordering of endpoints for all clusters
    for cluster in reduced_cluster_array:
        endpoints = get_endpoints(cluster)
        endpoints_array.append(endpoints)

    # variables to store best performing ordering
    min_length = 0
    closest_ordering = None

    # gets all the possible combinations of all the possible endpoints
    for endpoints_ordering in itertools.product(*endpoints_array):
        total_distance = 0

        # gets all the distances between just the specified endpoints
        for i in range(len(endpoints_ordering)):
            j = (i + 1) % len(endpoints_ordering)

            total_distance += get_distance(endpoints_ordering[i][1], endpoints_ordering[j][0])

        # checks if this is the first or best result so far and saves it if it is
        if total_distance < min_length or min_length == 0:
            min_length = total_distance
            closest_ordering = endpoints_ordering

    return closest_ordering


def closest_two(cluster1, cluster2):
    # holds the number of closest circles to be found
    closest_circle_1 = None
    closest_circle_2 = None

    # holds the minimum distances found for each closest circle
    min_length_1 = 0
    min_length_2 = 0

    # loops through all possible combinations of both sets
    for circle1 in cluster1:
        for circle2 in cluster2:
            temp_distance = get_distance(circle1, circle2)

            if temp_distance < min_length_1 or min_length_1 == 0:

                if closest_circle_1 == circle2:
                    min_length_1 = temp_distance
                    closest_circle_1 = circle2

                else:
                    min_length_2 = min_length_1
                    closest_circle_2 = closest_circle_1

                    min_length_1 = temp_distance
                    closest_circle_1 = circle2

            elif (temp_distance < min_length_2 or min_length_2 == 0) and closest_circle_1 != circle2:

                min_length_2 = temp_distance
                closest_circle_2 = circle2

    return closest_circle_1, closest_circle_2


# moves an element to the front of a list
def to_front(array, element):
    length = len(array)

    if length > 1:
        array.remove(element)
        array.insert(0, element)

    return array


# moves an element to the back of a list
def to_back(array, element):
    length = len(array)

    if length > 1:
        array.remove(element)
        array.append(element)

    return array


# class that represents a whole set of circle objects
class CircleSet:

    def __init__(self, count, radius, width, surface, color, circles=None):
        # initializing variables including the smaller circle
        self.count = count
        self.radius = radius
        self.width = width
        self.surface = surface
        self.color = inverse_color(color)
        self.inner_color = color[0:3]
        self.inner_radius = radius / 2

        # holds the first circle of the set
        self.first_circle = None
        red, green, blue = self.color
        self.first_color = (255 - red, 255 - green, blue)

        # variable that represents the minimum distance allowed with a little buffer
        self.buffer = surface.get_width() // 100
        self.min_distance = 2 * self.radius + self.buffer

        # if a count of 0 is passed then circles is defined as an empty set
        # assigns circle to an empty set and then assign it using generate circles
        # if a set of circles is passed into the class then that set is used instead
        if count == 0:
            self.circles = []
        elif circles is None:
            self.circles = []
            self.generate_circles()
        else:
            try:
                self.first_circle = circles[0]
                self.circles[0].set_color(self.first_color)
            except IndexError:
                pass
            self.circles = circles

    # getters and setters
    def get_circles(self):
        return self.circles

    def set_circles(self, circles):
        self.circles = circles

    # generates and returns a set of circles equal to the value of count
    def generate_circles(self):
        # initial empty set
        circles = []

        # loops until the number of circles equals the count
        while len(circles) < self.count:
            # initial boolean
            valid_circle = True

            # two random values are generated which are set so that the circle does not go over the window boundary
            # two values are then assigned to a variable which represents a new circle center
            x = random.randint(self.min_distance, self.surface.get_width() - self.min_distance)
            y = random.randint(self.min_distance, self.surface.get_height() - self.min_distance)
            center = (x, y)

            # loops through the current circles and check if the distance is enough so that they don't overlap
            for circle in circles:
                if math.dist(center, circle.get_center()) <= self.min_distance:
                    valid_circle = False
                    break

            # only adds the circle if it does not overlap with any of the other circles
            if valid_circle:
                circles.append(Circle(center, self.radius, self.surface, self.color))

        # assigns the generated array to self
        self.circles = circles

        # changes the first circle to a different color
        try:
            self.first_circle = circles[0]
            self.circles[0].set_color(self.first_color)
        except IndexError:
            pass

    # adds a circle to the already existing set
    def add_circle(self, center):

        # initial boolean
        valid_circle = True

        # gets the x and y values of the center
        x, y = center

        # define the borders that the circles must be within
        left = self.min_distance
        right = self.surface.get_width() - self.min_distance
        top = self.min_distance
        bottom = self.surface.get_height() - self.min_distance

        # checks if the center is within the allowed range and if not then checks for intersections
        if x < left or x > right or y < top or y > bottom:
            valid_circle = False
        else:
            # loops through the current circles and check if the distance is enough so that they don't overlap
            for circle in self.circles:
                if math.dist(center, circle.get_center()) <= self.min_distance:
                    valid_circle = False
                    break

        # only adds the circle if it does not overlap with any of the other circles and is within the correct range
        # also increments the total count of circles
        if valid_circle:
            # changes the first circle to a different color
            if self.count == 0:
                self.circles.append(Circle(center, self.radius, self.surface, self.first_color))
                self.first_circle = self.circles[0]
            else:
                self.circles.append(Circle(center, self.radius, self.surface, self.color))

            self.count += 1

    # removes a circle from the set
    def remove_circle(self, location):
        # initial boolean
        touching_circle = None

        # loops through all the circles and checks if the location is within any of the radii
        # if so then that circle is saved
        for circle in self.circles:
            if math.dist(location, circle.get_center()) <= self.radius:
                touching_circle = circle
                break

        # if a circle was found it is then removed from the set
        # also the count is decreased by one
        if touching_circle is not None:
            index = self.circles.index(touching_circle)
            color = self.circles[index].get_color()
            self.circles.remove(touching_circle)
            self.count -= 1

            if touching_circle.get_center() == self.first_circle.get_center() and self.count > 0:
                self.first_circle = self.circles[0]
                if touching_circle.get_color() == self.first_color:
                    self.circles[0].set_color(color)

    # find the center of the circle if it is within the location pressed and then returns it
    def find_center(self, location):
        # loops through all the circles and checks if the location is within any of the radii
        # if so then that circle's center is returned
        for circle in self.circles:
            if math.dist(location, circle.get_center()) <= self.radius:
                return circle.get_center()

    # resets the color for all of the circles
    def reset_colors(self):
        for circle in self.circles:
            if circle.get_center() == self.first_circle.get_center():
                circle.set_color(self.first_color)
            else:
                circle.set_color(self.color)

    # draws all of the circles in the set to the screen
    def draw_circles(self):
        # goes through and draws all of the circles
        for circle in self.circles:
            circle.draw()

    # draws all of the line corresponding to the circle set to the screen
    def draw_lines(self):
        # resets surface before drawing to it
        self.surface.fill(self.inner_color)

        # goes through the indices of all the circles
        for i in range(len(self.circles)):
            j = (i + 1) % len(self.circles)

            pygame.draw.line(
                self.surface, self.color,
                self.circles[i].get_center(), self.circles[j].get_center(), self.width)


# class which holds the properties of a circle
class Circle:

    def __init__(self, center, radius, surface, color=(255, 255, 255)):
        # initializing variables
        self.center = center
        self.radius = radius
        self.surface = surface
        self.color = color

        # creates a smaller circle inside of the larger circle with the opposite colors
        red, green, blue = color
        self.inner_color = (255 - red, 255 - green, 255 - blue)
        self.inner_radius = radius / 2

    # getters and setters
    def get_center(self):
        return self.center

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color
        self.inner_color = inverse_color(color)

    def set_radius(self, radius):
        self.radius = radius
        self.inner_radius = radius / 2

    # draws both the main and smaller circles to screen
    def draw(self):
        pygame.draw.circle(self.surface, self.color, self.center, self.radius)
        pygame.draw.circle(self.surface, self.inner_color, self.center, self.inner_radius)
