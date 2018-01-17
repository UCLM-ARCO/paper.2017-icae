// -*- mode:c++ -*-

module TestDoubles  {

  struct Coord {
    double x;
    double y;
    double z;
  };

  struct ControlMsg {
    string source;
    string resourceId;
    long timestamp;
    int eventType;
    int svStatus;
    string eventValueQuality;
  };


  interface Spy {
    void singleIntArg(int n);
    void sendData(Coord n);
    void notice(Coord n);
    void event(ControlMsg msg);
    void status(ControlMsg msg);
  };
};
