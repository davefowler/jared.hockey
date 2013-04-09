#! /usr/bin/env python

def mult(x, y): return x*y

def bestfit(x, y):
    """Usage: bestfit(x, y)
    x   array of x coordinates
    y   array of y coordinates

    returns the slope, y-intercept, and autocorrelation of the bestfit line
    return m, b, r"""
    sx = sum(x)
    sy = sum(y)
    sxy = sum(map(mult, x, y))
    sxx = sum(map(mult, x, x))
    syy = sum(map(mult, y, y))
    sx2 = pow(sx, 2)
    sy2 = pow(sy, 2)
    n = len(x)
    if not(n): n = .00001
    #slope
    try:
        m = (n*sxy - sx*sy)/(n*sxx-sx2)
    except:
        m = 9999

    #y intercept
    b = (sy - m*sx)/n

    #auto correlation
    try:
        r = (n*sxy-sx*sy)/(pow(n*sxx-sx2, .5)*pow(n*syy-sy2, .5))
    except:
        r = 1

    return m, b, r

def mky(y, Y, k):
    """Make Y.  Return a propogated value for y.  This accounts for the fact that on odd bounces the y is traveling in reverse direction.
    y   Raw Coordinate
    Y   Max Width in Y direction
    k   Number of bounces
    """
    odd = k%2
    if odd:
        return k*Y + (Y-y)
    return Y*k+y


def imky(y, Y, k):
    """Inverse Make Y"""
    odd = k%2
    if odd:
        return Y+(k*Y-y)
    return y-k*Y


def DT(x, y, newx, newy, Y):
    """The Dave Transform: transforms data confined by the y direction,
    bouncing off the borders at a known distance Y, into its unconfined x, y dimensions.

    The dave transform recognizes bounces assuming a constant velocity in the x and y directions with reflections having the same exiting angle as incident.

    USAGE: DT(x,y, newx, newy, Y, offset)

    x     array of past DT'd x coordinates
    y     array of past DT'd y coordinates
    newx  new un transformed x coordinate
    newy  new un transformed y coordinate
    Y     Max widht in y direction

    """
    n = len(x) + 1
    x.append(newx)
    if n < 3:
        y.append(newy)
        return x, y

    elif n == 3:
        #do a longer transform to make sure the first two points were aligned

        k = y[-1]/Y
        y1, y2 = [a for a in y]
        y2b = imky(y2, Y, k)

        #Try all possible orderings of y

    #positive reflection possibilities

        #reflection after 1st point
        y_opt2 = [y1, mky(y2b, Y, k+1), mky(newy, Y, k+1)]
        #reflection after 2nd point
        y_opt3 = [y1, y2, mky(newy, Y, k+1)]

    options = [y_opt2, y_opt3]

    # negative reflections

        #no reflections
        y_opt1 = [y1, y2, mky(newy, Y, k)]
        #reflection after 1st point
        y_opt2 = [y1, mky(y2b, Y, k-1), mky(newy, Y, k-1)]
        #reflection after 2nd point
        y_opt3 = [y1, y2, mky(newy, Y, k-1)]

    options.extend([y_opt1, y_opt2, y_opt3])


        #find the option that best fits a line

    rs = [abs(bestfit(x, y_opt)[2]) for y_opt in options]


        #return the cordinates that best fit the line
        return x, options[ rs.index(max(rs)) ]

    elif n > 3:

        #it must determine whether the puck fits the line better
        #assuming a bounce or assuming no bounce
        k = y[-1]/Y
        y_nobounce = [a for a in y]
        y_nobounce.append(mky(newy, Y, k))
        y_bounce = [a for a in y]
        y_bounce.append(mky(newy, Y, k+1))
    y_negbounce = [a for a in y]
    y_negbounce.append(mky(newy, Y, k-1))

    options = [y_bounce, y_nobounce, y_negbounce]
    rs = [abs(bestfit(x, y_opt)[2]) for y_opt in options]
        return x, options[ rs.index(max(rs)) ]


def iDT(x, y, Y):
    """The inverse Dave Transform
    USAGE: iDT(x, y, Y):

    x array of DT'd x coordinates
    y array of DT'd y coordinates
    Y max width in Y direction

    returns inverse DT array coordinates x, y
    """
    y = [imky(b, Y, b/Y) for b in y]
    return x, y

#for testing purposes
if __name__ == "__main__":
    """This just handles a test case if the module is run."""
    dtx = []
    dty = []
    offset = 0

    Y = 10
    #z = 0;
    #print DT(dtx, dty, z+1, z+1, 10)
    f = [1,2,3,4,5,6,7,8,9,10,9,8,7,6,5,4,3,2,1,0,1,2,3,4]
    f = [Y - a for a in f]

    for g in range(23):
        z = f[g]
        print 'for newx = '+str(g+1)+ ' newy = '+str(z)
        dtx, dty = DT(dtx, dty, g+1, z, Y)
        #print dtx
        #print dty


    print ''
    print f
    print dty
