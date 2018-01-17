module Example {
  struct Event {
    int x;
  };

  interface Listener {
    void sendData(Event n);
  };
};
