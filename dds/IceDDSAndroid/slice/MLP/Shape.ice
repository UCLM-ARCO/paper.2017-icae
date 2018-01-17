/* -*- c++ -*-

   5.2.2.5 Shape Element Definitions

   History:
   22/05/2008   C. Martin    Removed methods from Shape
   12/03/2008   F. Moya      Initial revision
*/

#ifndef SHAPE_ICE
#define SHAPE_ICE


#include <PropertyType.ice>


module MLP {

  struct Coord {
    double x;
    double y;
    double z;
  };

  sequence<Coord> CoordSeq;

  class Shape extends P::T {
  };

  class Point extends Shape {
    Coord center;
  };

  sequence<Point> PointSeq;

  class LineString extends Shape {
    ["uml:multi:2..n"] CoordSeq points;
  };

  sequence<LineString> LineStringSeq;

  class Box extends Shape {
    Coord topLeft;
    Coord bottomRight;
  };

  class LinearRing extends Shape {
    ["uml:multi:3..n"] CoordSeq points;
  };

  sequence<LinearRing> LinearRingSeq;

  class PolygonBase extends Shape {
  };

  sequence<PolygonBase> PolygonBaseSeq;

  class Polygon extends PolygonBase {
    LinearRing outerBoundaryIs;
    ["uml:multi:0..n"] LinearRingSeq innerBoundaryIs;
  };

  class CircularArcArea extends PolygonBase {
    Coord center;
    double inRadius;
    double outRadius;
    double startAngle;
    double stopAngle;
  };

  class CircularArea extends PolygonBase {
    Coord center;
    double radius;
  };

  class EllipticalArea extends PolygonBase {
    Coord center;
    double angle;
    double semiMinor;
    double semiMajor;
  };

  class MultiLineString extends Shape {
    ["uml:multi:1..n"] LineStringSeq lines;
  };

  class MultiPoint extends Shape {
    ["uml:multi:1..n"] PointSeq points;
  };

  class MultiPolygon extends Shape {
    ["uml:multi:1..n"] PolygonBaseSeq polygons;
  };

};


#endif
