from __future__ import division

# So it doesn't have to calculate sin, cos all the time (makes rotating faster)
global angles
angles = []
for a in range(0, 360, 1):
    angle = a * PI / 180
    angles.append([sin(angle), cos(angle)])

class Point:  # Represents a single point

    def __init__(self, x, y, edges):
        # The coordinates
        self.x = x
        self.y = y
        # self.id = id # Each point has a unique ID number that other objects
        # use to refer to it
        # The other points this point is connected to by an edge
        self.edges = edges

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_x(self, new_x):
        self.x = new_x

    def set_y(self, new_y):
        self.y = new_y

    def is_connected_to(self, p):  # Returns whether the point p is in edges
        return p in self.edges

    def add_edge(self, p):  # Adds a new point to the edges
        # For later, we will want the edges always to be sorted by the
        # x-position of the destination point
        if len(self.edges) == 0:
            self.edges.append(p)
        elif len(self.edges) == 1:
            # If the new point is farther to the right than the one already in
            # there:
            if self.edges[0].get_x() < p.get_x():
                self.edges.append(p)
            else:
                self.edges.insert(0, p)
        else:  # If there are already ≥2 edges:
            raise Exception('Tried to add a third connection to a point')

    # Replaces the edges this point is connected to
    def replace_edges(self, new_edges):
        if len(new_edges) > 2:
            raise Exception('Tried to add a third connection to a point')
        else:
            sorted_new_edges = new_edges[:1]
            if new_edges[1].get_x() > new_edges[0].get_x():
                sorted_new_edges.append(new_edges[1])
            else:
                sorted_new_edges.insert(0, new_edges[1])
            self.edges = sorted_new_edges

    def display(self):
        stroke(255, 0, 0)
        strokeWeight(1)
        noFill()
        for e in self.edges:
            line(self.x, self.y, e.get_x(), e.get_y())
        noStroke()
        fill(255, 0, 0)
        ellipse(self.x, self.y, 5, 5)

class Row:  # All the points at a particular height

    def __init__(self, y):
        self.points = []  # The list of points
        self.y = y

    def get_points(self):
        return self.points

    def add_point(self, p):
        # Adds in a new point p, and keeps the list of points sorted by the
        # x-coordinates
        if len(self.points) == 0:
            self.points.append(p)
        else:
            i = 0
            while i < len(self.points) and self.points[i].get_x() < p.get_x():
                i += 1
            self.points.insert(i, p)

    def get_y(self):
        return self.y

    def display(self):
        for p in self.points:
            p.display()

# A slice of the shape, with one row on the top and one on the bottom
class Slice:

    def __init__(self, top, bottom):
        self.top = top
        self.bottom = bottom
        self.y_top = top.get_y()
        self.y_bottom = bottom.get_y()
        self.parts = []  # The list of parts
        # Based on the top and bottom points, figures out what the parts are
        top_points = top.get_points()
        bottom_points = bottom.get_points()
        # Each part is represented by a list of all the points on the top and a
        # list of all the points on the bottom
        # When building a part, top_start is the index in top_points of the
        # leftmost top point in the part
        top_start = None
        bottom_start = None  # Same for bottom
        building = False  # Whether we’re currently building a part
        for t in top_points:  # Go through all the points on the top
            for b in bottom_points:  # Go through all the points on the bottom
                if t.is_connected_to(b):  # If there’s an edge between them
                    if not building:  # If we aren’t building a part yet:
                        building = True  # Start one
                        # The start indices are where we currently are
                        top_start = t
                        bottom_start = b
                    else:  # If we are building a part
                        building = False  # Then stop
                        top_end = t
                        bottom_end = b
                        # We now know the start and end for top and bottom, so
                        # build the part out of that
                        part = [[top_start.get_x(), top_end.get_x()], [
                            bottom_start.get_x(), bottom_end.get_x()]]
                        # And add it to the list of parts
                        self.parts.append(part)
        # Now, find where each part should go to make everything centered
        self.destinations = []  # Where each part should go
        self.top_length = 0
        self.bottom_length = 0
        # The total length of the top and bottom edges of the parts
        for part in self.parts:  # Go through all the parts
            # For each one, add the top and bottom lengths to the totals
            self.top_length += part[0][1] - part[0][0]
            self.bottom_length += part[1][1] - part[1][0]
        # Figure out where each of the lines will start
        top_start = width / 2 - self.top_length / 2
        bottom_start = width / 2 - self.bottom_length / 2
        # Then, go through each part and add them in from left to right to fill up the destination
        # How far past the start each part is:
        top_sum = 0
        bottom_sum = 0
        for part in self.parts:
            # How far we are on the top
            current_top_start = top_start + top_sum
            current_bottom_start = bottom_start + bottom_sum  # and the bottom
            # The top length of the current part
            current_top_length = part[0][1] - part[0][0]
            current_bottom_length = part[1][
                1] - part[1][0]  # And the bottom length
            # Then form the part out of these:
            new_top = [
                current_top_start, current_top_start + current_top_length]
            new_bottom = [
                current_bottom_start, current_bottom_start + current_bottom_length]
            # And add it to the list of part destinations
            self.destinations.append([new_top, new_bottom])
            # Then increase the sums for the next part
            top_sum += current_top_length
            bottom_sum += current_bottom_length

    def get_y_top(self):
        return self.y_top

    def get_y_bottom(self):
        return self.y_bottom

    def get_top_length(self):
        return self.top_length

    def get_bottom_length(self):
        return self.bottom_length

    def display_top(self):
        self.top.display()

    def display(self, a):
        # Displays the slice a between the start and end
        # The list of slices in the middle of transforming (or at the beginning
        # or end if a is 0 or 1)
        middle_parts = []
        for i in range(len(self.parts)):  # Go through all the parts
            start_part = self.parts[i]  # The ith part at the beginning
            end_part = self.destinations[i]  # The ith part at the end
            # Figure out where all four corners are at position a
            middle_top_left = lerp(start_part[0][0], end_part[0][0], a)
            middle_top_right = lerp(start_part[0][1], end_part[0][1], a)
            middle_bottom_left = lerp(start_part[1][0], end_part[1][0], a)
            middle_bottom_right = lerp(start_part[1][1], end_part[1][1], a)
            # Construct the part out of them
            middle_part = [[middle_top_left, middle_top_right],
                           [middle_bottom_left, middle_bottom_right]]
            # And add it to the list
            middle_parts.append(middle_part)
        # Now display each of them
        for part in middle_parts:
            s = createShape()
            s.beginShape()
            s.noStroke()
            s.fill(0)
            # Add the four vertices of the part
            s.vertex(part[0][0], self.y_top)  # The upper left vertex
            s.vertex(part[0][1], self.y_top)  # The upper right vertex
            s.vertex(part[1][1], self.y_bottom)  # The bottom right vertex
            s.vertex(part[1][0], self.y_bottom)  # The bottom left vertex
            s.endShape(CLOSE)
            shape(s, 0, 0)
        # Draw lines at the top of the slice
        stroke(0)
        strokeWeight(0.5)
        noFill()
        for i in range(len(middle_parts)):
            part = middle_parts[i]
            if i == 0 and part[1][0] - part[0][0] > 5:
                line(part[0][0] + 5, self.y_top, part[0][1], self.y_top)
            elif i == len(middle_parts) - 1 and part[1][0] - part[0][0] > 5:
                line(part[0][0], self.y_top, part[0][1] - 5, self.y_top)
            else:
                line(part[0][0], self.y_top, part[0][1], self.y_top)

class Shape:

    def __init__(self):
        self.points = []  # The list of points
        self.fill = 0
        self.stroke = None
        self.weight = 2
        self.slices = []

    def add_point(self, x, y):  # Add a point to the shape
        p = Point(x, y, [])  # The point to be added
        self.points.append(p)  # Add it to the end of the list
        if len(self.points) > 1:  # If there’s something else to connect it to:
            q = self.points[-2]
            p.add_edge(q)
            q.add_edge(p)

    # Close the shape by connecting the first and last points
    def close_shape(self):
        p = self.points[0]
        q = self.points[-1]
        p.add_edge(q)
        q.add_edge(p)
        # Slice into pieces
        # First, add points to equalize vertices on each side
        # The set of all the y-coordinates we’ve already seen
        looked_at_already = set()
        for p in self.points:  # Look at each vertex
            # If we haven’t already looked at this y-position:
            if p.get_y() not in looked_at_already:
                looked_at_already.add(p.get_y())  # Then mark that we have
                i = 0
                # Look at all the points in the polygon
                while i < len(self.points):
                    # If p is vertically between this one (at i) and the one
                    # after
                    one = self.points[i]
                    two = self.points[(i + 1) % len(self.points)]
                    if (one.get_y() < p.get_y() and p.get_y() < two.get_y()) or (one.get_y() > p.get_y() and p.get_y() > two.get_y()):
                        # Form the new point to be added in between point one and point two
                        # x and y of this new point
                        point_x = lerp(
                            one.get_x(), two.get_x(), (p.get_y() - one.get_y()) / (two.get_y() - one.get_y()))
                        point_y = p.get_y()
                        # The connections of this new point
                        point_connections = [one, two]
                        new_point = Point(point_x, point_y, point_connections)
                        # Insert the new point into the shape
                        self.points[i].replace_edges(
                            [self.points[(i - 1) % len(self.points)], new_point])
                        self.points[
                            (i + 1) % len(self.points)].replace_edges([new_point, self.points[(i + 2) % len(self.points)]])
                        self.points.insert(
                            (i + 1) % len(self.points), new_point)
                    i += 1
        # Now, find the rows in the shape
        shape_rows = []  # A list of all the rows in the shape
        ys = list(looked_at_already)
        ys.sort()  # A sorted list of all the y-coordinates in the shape
        for y in ys:  # Go through each y-coordinate and make a row based on it
            row = Row(y)  # A row at y-coordinate y
            for p in self.points:  # Then go through all the points
                if p.get_y() == y:  # And for any point that has y-coordinate y
                    row.add_point(p)  # Add it to the row at y
            # Now row contains every point at y
            shape_rows.append(row)  # So add it to the list of rows
        # Now create the slices
        # Go through every adjacent pair of rows
        for i in range(len(shape_rows) - 1):
            # Form a slice out of the pair
            s = Slice(shape_rows[i], shape_rows[i + 1])
            self.slices.append(s)

    def set_fill(self, fill):
        self.fill = fill

    def set_stroke(self, stroke):
        self.stroke = stroke

    def set_weight(self, weight):
        self.weight = weight

    def display_polygon(self):  # Draw as a polygon
        s = createShape()
        s.beginShape()
        if self.fill == None:
            s.noFill()
        else:
            s.fill(self.fill)
        if self.stroke == None:
            s.noStroke()
        else:
            s.stroke(self.stroke)
            s.strokeWeight(self.weight)
        for p in self.points:
            s.vertex(p.get_x(), p.get_y())
        s.endShape(CLOSE)
        stroke(255, 0, 0)
        noFill()
        shape(s, 0, 0)

    def display_slices(self, a):  # Draw the slices
        for s in self.slices:
            s.display(a)

    # Return a new shape, the result of squishing this shape
    def destination(self):
        new_shape = Shape()  # The shape that will be returned
        # Now go through all the slices, from top to bottom, and add the left
        # point of that slice’s top destination to the shape
        for i in range(len(self.slices)):
            s = self.slices[i]
            new_shape.add_point(
                width / 2 - s.get_top_length() / 2, s.get_y_top())
        s = self.slices[-1]  # Then add the bottom row of the bottom slice
        new_shape.add_point(
            width / 2 - s.get_bottom_length() / 2, s.get_y_bottom())
        new_shape.add_point(
            width / 2 + s.get_bottom_length() / 2, s.get_y_bottom())
        # Then go backwards and look at the right points of the tops again:
        for i in range(len(self.slices) - 1, -1, -1):
            s = self.slices[i]
            new_shape.add_point(
                width / 2 + s.get_top_length() / 2, s.get_y_top())
        new_shape.close_shape()
        return new_shape

    # Rotate the shape a radians about (xc, yc)
    def rotate_shape(self, xc, yc, a):
        new_shape = Shape()
        for p in self.points:
            x = p.get_x()
            y = p.get_y()
            rotated_coordinates = rotate_point(x, y, xc, yc, a)
            new_shape.add_point(rotated_coordinates[0], rotated_coordinates[1])
        new_shape.close_shape()
        return new_shape

    # Removes points that are (basically) in between two other points
    def simplify(self):
        # All the x and y coordinates of the points
        xs = [p.get_x() for p in self.points]
        ys = [p.get_y() for p in self.points]
        shape_size = max(max(xs) - min(xs), max(ys) - min(ys))
        # A list of all the points, which we will take away from
        points = self.points
        i = 0
        while i < len(points):
            p = points[i]
            before = (i - 1) % len(points)
            after = (i + 1) % len(points)
            p_before = points[before]
            p_after = points[after]
            a1 = atan2(
                p.get_y() - p_before.get_y(), p.get_x() - p_before.get_x())
            a2 = atan2(
                p_after.get_y() - p.get_y(), p_after.get_x() - p.get_x())
            d1 = dist(p_before.get_x(), p_before.get_y(), p.get_x(), p.get_y())
            d2 = dist(p.get_x(), p.get_y(), p_after.get_x(), p_after.get_y())
            max_angle = 0.03
            max_dist = shape_size / 100
            remove_close_angles = True
            remove_close_points = True
            if (remove_close_angles and abs(a1 - a2) < max_angle) or (remove_close_points and d1 < max_dist and d2 < max_dist):
                del points[i]
            else:
                i += 1
        s = Shape()
        for p in points:
            s.add_point(p.get_x(), p.get_y())
        s.close_shape()
        return s

    # Detects if it’s circular; if it is, return the radius; if not, return
    # False
    def is_circle(self):
        # The list of distances of all the points and midpoints from the center
        distances = []
        for i in range(len(self.points)):
            p1 = self.points[i]  # This point
            p2 = self.points[(i + 1) % len(self.points)]  # The next point
            # The distance from the center to this point
            distances.append(
                dist(width / 2, height / 2, p1.get_x(), p1.get_y()))
            # The distance from the center to the midpoint between this and the
            # next point
            distances.append(dist(
                width / 2, height / 2, (p1.get_x() + p2.get_x()) / 2, (p1.get_y() + p2.get_y()) / 2))
        high = max(distances)  # The farthest away point
        low = min(distances)  # The closest point
        # If the highest and lowest differ by less than 1%
        if (high - low) / high < 0.01:
            return (high + low) / 2  # Then it’s a circle with this radius
        else:
            return False  # Otherwise, it’s not a circle

# Rotate the point (x, y) a radians about (xc, yc)
def rotate_point(x, y, xc, yc, a):
    global angles
    a_index = int((a % TWO_PI) * 180 / PI)
    sin_a = angles[a_index][0]
    cos_a = angles[a_index][1]
    new_x = xc + (x - xc) * cos_a - (y - yc) * sin_a
    new_y = yc + (x - xc) * sin_a + (y - yc) * cos_a
    return [new_x, new_y]

def ease(a):
    return (sin(PI * a - HALF_PI) + 1) / 2

def reset():
    global mode
    mode = 'drawing'
    global s
    s = Shape()
    global changing_start
    changing_start = None
    global destination
    destination = None
    global angle
    angle = random(-PI, PI)
    global last_point
    last_point = None
    global num_points
    num_points = 0
    global radius
    radius = None
    global screenshot
    screenshot = False

def setup():
    size(1000, 1000)
    pixelDensity(2)
    global mode
    reset()

def draw():
    background(255)
    global mode
    global s
    global changing_start
    global angle
    global last_point
    global num_points
    global radius
    global screenshot
    fc = frameCount
    if mode == 'drawing':
        if mousePressed and not [mouseX, mouseY] == last_point:
            s.add_point(mouseX, mouseY)
            last_point = [mouseX, mouseY]
            num_points += 1
        s.set_stroke(0)
        s.set_weight(1)
        s.set_fill(None)
        s.display_polygon()
    elif mode == 'changing':
        wait1 = 5  # Amount of frames to wait before changing
        change_time = 30  # Amount of frames to change
        wait2 = 5  # Amount of frames to wait before rotating
        should_rotate = True
        random_angle = True
        rotate_time = 15  # Amount of frames to rotate
        if not random_angle:
            angle = 0.3
        if fc < changing_start + wait1:  # Pause and show the shape
            s.set_stroke(None)
            s.set_fill(0)
            s.display_polygon()
        # Squish the shape
        elif fc < changing_start + wait1 + change_time:
            s.display_slices(
                ease((fc - changing_start - wait1) / change_time))
            if fc == changing_start + wait1 + change_time - 1:
                s = s.destination()  # Change the shape to the destination
        # Wait again
        elif fc < changing_start + wait1 + change_time + wait2:
            s.set_stroke(None)
            s.set_fill(0)
            s.display_polygon()
        # Rotate the shape
        elif should_rotate and fc < changing_start + wait1 + change_time + wait2 + rotate_time:
            if fc == changing_start + wait1 + change_time + wait2 + int(rotate_time / 4):
                s = s.simplify()
            a = angle * \
                ease(
                    (fc - changing_start - wait1 - change_time - wait2) / rotate_time)
            t = s.rotate_shape(width / 2, height / 2, a)
            t.display_polygon()
        else:
            if not should_rotate:
                s = s.simplify()
            s = s.rotate_shape(width / 2, height / 2, angle)
            s.display_polygon()
            changing_start = fc
            if random_angle:
                angle = random(-PI, PI)
            radius = s.is_circle()
            if radius != False:
                mode = 'circle'
    elif mode == 'circle':
        fill(0)
        noStroke()
        ellipse(width / 2, height / 2, radius * 2, radius * 2)
    if screenshot:
        saveFrame()
        screenshot = False

def keyPressed():
    global s
    global mode
    global changing_start
    global destination
    global angle
    global last_point
    global num_points
    global radius
    global screenshot
    if key == 's':
        screenshot = True
    elif mode == 'drawing' and num_points > 1:
        mode = 'changing'
        s.close_shape()
        changing_start = frameCount
    elif mode in ['changing', 'circle']:
        reset()
