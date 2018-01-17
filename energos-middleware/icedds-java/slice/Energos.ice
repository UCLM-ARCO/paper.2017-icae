
module Energos {
  struct MeasureMsg {
    string source;
    string resourceId;
    long timestamp;
    string measurementValueQuality1;
    string measurementValueQuality2;
    string measurementValueQuality3;
    string measurementValueQuality4;
    double analogValue1;
    double analogValue2;
    double analogValue3;
    double analogValue4;
    long measurementUnit;
    long period;
    long season;
  };

  interface MeasureSink {
    void activePower(MeasureMsg msg);
    void reactivePower(MeasureMsg msg);
    void voltage(MeasureMsg msg);
    void Intensity(MeasureMsg msg);
    void oilTemperature(MeasureMsg msg);
  };

  struct ControlMsg {
    string source;
    string resourceId;
    long timestamp;
    int eventType;
    int svStatus;
    string eventValueQuality;
  };

  interface ControlSink {
    void event(ControlMsg msg);
    void status(ControlMsg msg);
  };

  struct DataValues {
    double value1;
    double value2;
    double value3;
    double value4;
  };

  // typedef sequence<DataValues> DataSeq;

  // struct shortDurationMsg {
  //   string source;
  //   string resourceId;
  //   long timestamp;
  //   short sampleTime;
  //   float latitude;
  //   float longitude;
  //   DataSeq voltage;
  //   DataSeq current;
  // };

  // struct powerQualityEvent {
  //   string source;
  //   string resourceId;
  //   long timeStamp;
  //   short sampleTime;
  //   float latitude;
  //   float longitude;
  //   double voltageValue[][];
  //   double currentValue[][];
  // }

  struct powerQualityResultMsg {
    string source;
    string resourceId;
    float resourceLatitude;
    float resourceLongitude;
    long timeStamp;
    short sampleTime;
    double elapsedTimeA;
    double elapsedTimeB;
    double elapsedTimeC;
    double elapsedTimeMax;
    float minVoltage;
    float maxCurrent;
    double faultImpedance;
    short sourceLocation;
    float faultSourceDistance;
    float latitudeFaultSource;
    float longitudeFaultSource;
    float preFaultVoltage;
    float preFaultCurrent;
  };

  // interface WaveQualitySink {
  //   void shortDurationEvent(shortDurationMsg msg);
  //   void powerQualityResult(powerQualityResultMsg msg);
  // };

};
