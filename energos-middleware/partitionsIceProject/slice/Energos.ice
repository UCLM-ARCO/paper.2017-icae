module Energos {

  struct ControlMsg {
    string resourceId;
    long timestamp;
    int eventType;
    int svStatus;
  };

  sequence<ControlMsg> ControlMsgSeq;
  interface ControlSink {
    ControlMsgSeq getList();
    void event(ControlMsg msg);
    void status(ControlMsg msg);
  };

};
