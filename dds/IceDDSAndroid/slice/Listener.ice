/* -*- coding: utf-8; mode: c++ -*- */
#include <MLP/Shape.ice>

module Event {
  interface Listener {
    void sendData(MLP::Coord n);
  };
};
