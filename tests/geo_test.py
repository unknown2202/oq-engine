import unittest

import numpy

from nhe import geo
from nhe.geo import _utils as geo_utils


class PointTestCase(unittest.TestCase):

    def test_point_at_1(self):
        p1 = geo.Point(0.0, 0.0, 10.0)
        expected = geo.Point(0.0635916667129, 0.0635916275455, 15.0)
        self.assertEqual(expected, p1.point_at(10.0, 5.0, 45.0))

    def test_point_at_2(self):
        p1 = geo.Point(0.0, 0.0, 10.0)
        expected = geo.Point(0.0635916667129, 0.0635916275455, 5.0)
        self.assertEqual(expected, p1.point_at(10.0, -5.0, 45.0))

    def test_azimuth(self):
        p1 = geo.Point(0.0, 0.0)
        p2 = geo.Point(0.5, 0.5)

        self.assertAlmostEqual(44.9989091554, p1.azimuth(p2))

    def test_azimuth_over_180_degree(self):
        p1 = geo.Point(0.0, 0.0)
        p2 = geo.Point(0.5, 0.5)
        self.assertAlmostEqual(225.0010908, p2.azimuth(p1))

    def test_horizontal_distance(self):
        p1 = geo.Point(0.0, 0.0)
        p2 = geo.Point(0.5, 0.5)

        self.assertAlmostEqual(78.6261876769, p1.horizontal_distance(p2), 4)

    def test_distance(self):
        p1 = geo.Point(0.0, 0.0, 0.0)
        p2 = geo.Point(0.5, 0.5, 5.0)

        self.assertAlmostEqual(78.7849704355, p1.distance(p2))

    def test_equally_spaced_points_1(self):
        p1 = geo.Point(0.0, 0.0)
        p2 = geo.Point(0.190775520815, 0.190774854966)

        points = p1.equally_spaced_points(p2, 10.0)
        self.assertEqual(4, len(points))

        self.assertEqual(p1, points[0]) # first point is the start point
        self.assertEqual(p2, points[3]) # last point is the end point

        expected = geo.Point(0.0635916966572, 0.0635916574897, 0.0)
        self.assertEqual(expected, points[1])

        expected = geo.Point(0.127183510817, 0.127183275812, 0.0)
        self.assertEqual(expected, points[2])

    def test_equally_spaced_points_2(self):
        p1 = geo.Point(0.0, 0.0, 0.0)
        p2 = geo.Point(0.134898484431, 0.134898249018, 21.2132034356)

        points = p1.equally_spaced_points(p2, 10.0)
        self.assertEqual(4, len(points))

        self.assertEqual(p1, points[0]) # first point is the start point
        self.assertEqual(p2, points[3]) # last point is the end point

        expected = geo.Point(0.0449661107016, 0.0449660968538, 7.07106781187)
        self.assertEqual(expected, points[1])

        expected = geo.Point(0.0899322629466, 0.0899321798598, 14.1421356237)
        self.assertEqual(expected, points[2])

    def test_equally_spaced_points_3(self):
        """
        Corner case where the end point is equal to the start point.
        In this situation we have just one point (the start/end point).
        """

        p1 = geo.Point(0.0, 0.0)
        p2 = geo.Point(0.0, 0.0)

        points = p1.equally_spaced_points(p2, 10.0)

        self.assertEqual(1, len(points))
        self.assertEqual(p1, points[0])
        self.assertEqual(p2, points[0])

    def test_equally_spaced_points_4(self):
        p1 = geo.Point(0, 0, 10)
        p2 = geo.Point(0, 0, 7)
        points = p1.equally_spaced_points(p2, 1)
        self.assertEqual(points,
                         [p1, geo.Point(0, 0, 9), geo.Point(0, 0, 8), p2])

    def test_equally_spaced_points_last_point(self):
        points = geo.Point(0, 50).equally_spaced_points(geo.Point(10, 50), 10)
        self.assertAlmostEqual(points[-1].latitude, 50, places=2)

    def test_longitude_inside_range(self):
        self.assertRaises(RuntimeError, geo.Point, 180.1, 0.0, 0.0)
        self.assertRaises(RuntimeError, geo.Point, -180.1, 0.0, 0.0)

        geo.Point(180.0, 0.0)
        geo.Point(-180.0, 0.0)

    def test_latitude_inside_range(self):
        self.assertRaises(RuntimeError, geo.Point, 0.0, 90.1, 0.0)
        self.assertRaises(RuntimeError, geo.Point, 0.0, -90.1, 0.0)

        geo.Point(0.0, 90.0, 0.0)
        geo.Point(0.0, -90.0, 0.0)


class LineTestCase(unittest.TestCase):

    def test_resample(self):
        p1 = geo.Point(0.0, 0.0, 0.0)
        p2 = geo.Point(0.0, 0.127183341091, 14.1421356237)
        p3 = geo.Point(0.134899286793, 0.262081472606, 35.3553390593)

        resampled = geo.Line([p1, p2, p3]).resample(10.0)

        p1 = geo.Point(0.0, 0.0, 0.0)
        p2 = geo.Point(0.0, 0.0635916705456, 7.07106781187)
        p3 = geo.Point(0.0, 0.127183341091, 14.1421356237)
        p4 = geo.Point(0.0449662998195, 0.172149398777, 21.2132034356)
        p5 = geo.Point(0.0899327195183, 0.217115442616, 28.2842712475)
        p6 = geo.Point(0.134899286793, 0.262081472606, 35.3553390593)

        expected = geo.Line([p1, p2, p3, p4, p5, p6])
        self.assertEqual(expected, resampled)

    def test_resample_2(self):
        """
        Line made of 3 points (aligned in the same direction) equally spaced
        (spacing equal to 10 km). The resampled line contains 2 points
        (with spacing of 30 km) consistent with the number of points
        as predicted by n = round(20 / 30) + 1.
        """

        p1 = geo.Point(0.0, 0.0)
        p2 = geo.Point(0.0, 0.089932202939476777)
        p3 = geo.Point(0.0, 0.1798644058789465)

        self.assertEqual(2, len(geo.Line([p1, p2, p3]).resample(30.0)))

    def test_resample_3(self):
        """
        Line made of 3 points (aligned in the same direction) equally spaced
        (spacing equal to 10 km). The resampled line contains 1 point
        (with spacing of 50 km) consistent with the number of points
        as predicted by n = round(20 / 50) + 1.
        """

        p1 = geo.Point(0.0, 0.0)
        p2 = geo.Point(0.0, 0.089932202939476777)
        p3 = geo.Point(0.0, 0.1798644058789465)

        self.assertEqual(1, len(geo.Line([p1, p2, p3]).resample(50.0)))

        self.assertEqual(geo.Line([p1]), geo.Line(
                [p1, p2, p3]).resample(50.0))

    def test_resample_4(self):
        """
        When resampling a line with a single point, the result
        is a one point line with the same point.
        """

        p1 = geo.Point(0.0, 0.0)

        self.assertEqual(geo.Line([p1]), geo.Line([p1]).resample(10.0))

    def test_one_point_needed(self):
        self.assertRaises(RuntimeError, geo.Line, [])

    def test_remove_adjacent_duplicates(self):
        p1 = geo.Point(0.0, 0.0, 0.0)
        p2 = geo.Point(0.0, 1.0, 0.0)
        p3 = geo.Point(0.0, 1.0, 0.0)
        p4 = geo.Point(0.0, 2.0, 0.0)
        p5 = geo.Point(0.0, 3.0, 0.0)
        p6 = geo.Point(0.0, 3.0, 0.0)

        expected = [p1, p2, p4, p5]
        self.assertEquals(expected, geo.Line([p1, p2, p3, p4, p5, p6]).points)

    def test_must_not_intersect_itself(self):
        p1 = geo.Point(0.0, 0.0)
        p2 = geo.Point(0.0, 1.0)
        p3 = geo.Point(1.0, 1.0)
        p4 = geo.Point(0.0, 0.5)

        self.assertRaises(RuntimeError, geo.Line, [p1, p2, p3, p4])

        # doesn't take into account depth
        p1 = geo.Point(0.0, 0.0, 1.0)
        p2 = geo.Point(0.0, 1.0, 1.0)
        p3 = geo.Point(1.0, 1.0, 1.0)
        p4 = geo.Point(0.0, 0.5, 1.5)

        self.assertRaises(RuntimeError, geo.Line, [p1, p2, p3, p4])

    def test_invalid_line_crossing_international_date_line(self):
        broken_points = [geo.Point(178, 0), geo.Point(178, 10),
                         geo.Point(-178, 0), geo.Point(170, 5)]
        self.assertRaises(RuntimeError, geo.Line, broken_points)

    def test_valid_line_crossing_international_date_line(self):
        points = [geo.Point(178, 0), geo.Point(178, 10),
                  geo.Point(179, 5), geo.Point(-178, 5)]
        geo.Line(points)


class PolygonCreationTestCase(unittest.TestCase):
    def assert_failed_creation(self, points, exc, msg):
        with self.assertRaises(exc) as ae:
            geo.Polygon(points)
        self.assertEqual(ae.exception.message, msg)

    def test_less_than_three_points(self):
        msg = 'polygon must have at least 3 unique vertices'
        self.assert_failed_creation([], RuntimeError, msg)
        self.assert_failed_creation([geo.Point(1, 1)], RuntimeError, msg)
        self.assert_failed_creation([geo.Point(1, 1),
                                     geo.Point(2, 1)], RuntimeError, msg)

    def test_less_than_three_unique_points(self):
        msg = 'polygon must have at least 3 unique vertices'
        points = [geo.Point(1, 2)] * 3 + [geo.Point(4, 5)]
        self.assert_failed_creation(points, RuntimeError, msg)

    def test_intersects_itself(self):
        msg = 'polygon perimeter intersects itself'
        points = [geo.Point(0, 0), geo.Point(0, 1),
                  geo.Point(1, 1), geo.Point(-1, 0)]
        self.assert_failed_creation(points, RuntimeError, msg)

    def test_intersects_itself_being_closed(self):
        msg = 'polygon perimeter intersects itself'
        points = [geo.Point(0, 0), geo.Point(0, 1),
                  geo.Point(1, 0), geo.Point(1, 1)]
        self.assert_failed_creation(points, RuntimeError, msg)

    def test_valid_points(self):
        points = [geo.Point(170, -10), geo.Point(170, 10), geo.Point(176, 0),
                  geo.Point(-170, -5), geo.Point(-175, -10),
                  geo.Point(-178, -6)]
        polygon = geo.Polygon(points)
        self.assertEqual(polygon.num_points, 6)
        self.assertEqual(list(polygon.lons),
                         [170,  170,  176, -170, -175, -178])
        self.assertEqual(list(polygon.lats), [-10, 10, 0, -5, -10, -6])
        self.assertEqual(polygon.lons.dtype, 'float')
        self.assertEqual(polygon.lats.dtype, 'float')


class PolygonResampleSegmentsTestCase(unittest.TestCase):
    def test_1(self):
        poly = geo.Polygon([geo.Point(-2, -2), geo.Point(0, -2),
                            geo.Point(0, 0), geo.Point(-2, 0)])
        lons, lats = poly._get_resampled_coordinates()
        expected_lons = [-2, -1,  0,  0, -1, -2, -2]
        expected_lats = [-2, -2, -2,  0,  0,  0, -2]
        self.assertTrue(
            numpy.allclose(lons, expected_lons, atol=1e-3, rtol=0),
            msg='%s != %s' % (lons, expected_lons)
        )
        self.assertTrue(
            numpy.allclose(lats, expected_lats, atol=1e-3, rtol=0),
            msg='%s != %s' % (lats, expected_lats)
        )

    def test_international_date_line(self):
        poly = geo.Polygon([
            geo.Point(177, 40), geo.Point(179, 40), geo.Point(-179, 40),
            geo.Point(-177, 40),
            geo.Point(-177, 43), geo.Point(-179, 43), geo.Point(179, 43),
            geo.Point(177, 43)
        ])
        lons, lats = poly._get_resampled_coordinates()
        self.assertTrue(all(-180 < lon <= 180 for lon in lons))
        expected_lons = [177, 178, 179, 180, -179, -178, -177,
                         -177, -178, -179, 180, 179, 178, 177, 177]
        self.assertTrue(
            numpy.allclose(lons, expected_lons, atol=1e-4, rtol=0),
            msg='%s != %s' % (lons, expected_lons)
        )


class PolygonDiscretizeTestCase(unittest.TestCase):
    def test_mesh_spacing_uniformness(self):
        MESH_SPACING = 10
        tl = geo.Point(60, 60)
        tr = geo.Point(70, 60)
        bottom_line = [geo.Point(lon, 58) for lon in xrange(70, 59, -1)]
        poly = geo.Polygon([tl, tr] + bottom_line)
        mesh = list(poly.discretize(mesh_spacing=MESH_SPACING))

        for i, point in enumerate(mesh):
            if i == len(mesh) - 1:
                # the point is last in the mesh
                break
            next_point = mesh[i + 1]
            if next_point.longitude < point.longitude:
                # this is the next row (down along the meridian).
                # let's check that the new row stands exactly
                # mesh spacing kilometers below the previous one.
                self.assertAlmostEqual(
                    point.distance(geo.Point(point.longitude,
                                             next_point.latitude)),
                    MESH_SPACING, places=4
                )
                continue
            dist = point.distance(next_point)
            self.assertAlmostEqual(MESH_SPACING, dist, places=4)

    def test_polygon_on_international_date_line(self):
        MESH_SPACING = 10
        bl = geo.Point(177, 40)
        bml = geo.Point(179, 40)
        bmr = geo.Point(-179, 40)
        br = geo.Point(-177, 40)
        tr = geo.Point(-177, 43)
        tmr = geo.Point(-179, 43)
        tml = geo.Point(179, 43)
        tl = geo.Point(177, 43)
        poly = geo.Polygon([bl, bml, bmr, br, tr, tmr, tml, tl])
        mesh = list(poly.discretize(mesh_spacing=MESH_SPACING))

        west = east = mesh[0]
        for point in mesh:
            if geo_utils.get_longitudinal_extent(point.longitude,
                                                 west.longitude) > 0:
                west = point
            if geo_utils.get_longitudinal_extent(point.longitude,
                                                 east.longitude) < 0:
                east = point

        self.assertLess(west.longitude, 177.15)
        self.assertGreater(east.longitude, -177.15)

    def test_no_points_outside_of_polygon(self):
        dist = 1e-4
        points = [
            geo.Point(0, 0),
            geo.Point(dist * 4.5, 0),
            geo.Point(dist * 4.5, -dist * 4.5),
            geo.Point(dist * 3.5, -dist * 4.5),
            geo.Point(dist * (4.5 - 0.8), -dist * 1.5),
            geo.Point(0, -dist * 1.5)
        ]
        poly = geo.Polygon(points)
        mesh = list(poly.discretize(mesh_spacing=1.1e-2))
        self.assertEqual(mesh, [
            geo.Point(dist, -dist),
            geo.Point(dist * 2, -dist),
            geo.Point(dist * 3, -dist),
            geo.Point(dist * 4, -dist),

            geo.Point(dist * 4, -dist * 2),
            geo.Point(dist * 4, -dist * 3),
            geo.Point(dist * 4, -dist * 4),
        ])

    def test_longitudinally_extended_boundary(self):
        points = [geo.Point(lon, -60) for lon in xrange(-10, 11)]
        points += [geo.Point(10, -60.1), geo.Point(-10, -60.1)]
        poly = geo.Polygon(points)
        mesh = list(poly.discretize(mesh_spacing=10.62))

        south = mesh[0]
        for point in mesh:
            if point.latitude < south.latitude:
                south = point

        # the point with the lowest latitude should be somewhere
        # in the middle longitudinally (around Greenwich meridian)
        # and be below -60th parallel.
        self.assertTrue(-0.1 < south.longitude < 0.1)
        self.assertTrue(-60.5 < south.latitude < -60.4)
