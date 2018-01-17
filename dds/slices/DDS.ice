/* -*- coding: utf-8; mode: c++ -*- */
#include <Ice/BuiltinSequences.ice>
#include <IceStorm/IceStorm.ice>

module DDS  {

  struct VariableTypeCode {
    string variableName;
    string variableType;
  };

  sequence<VariableTypeCode> TypeCode;

  // struct Filter {
  //   string expression;
  // };

  sequence<string> FilterSeq;

  exception FilterError {
	string msg;
  };

  interface Topic {
    void setFilters(FilterSeq filters);
    FilterSeq getFilters();

    string getName();

    Object* subscribeAndGetPublisher(Object* subscriber);
    Topic* subscribeWithFilters(Object* subscriber,
                                FilterSeq filters) throws FilterError;
    void unsubscribe(Object* subscriber);


    Object* getPublisher();
    Object* getFilteredPublisher(string publisherName,
                                 FilterSeq filters) throws FilterError;

    void link(Topic* linkTo, int cost);
    void unlink(Topic* linkTo);

    void linkFiltered(Object* publisher);
    void unlinkFiltered(Object* publisher);

    void destroy();
  };

  dictionary<string, Topic*> TopicDict;

  interface TopicManager {
    Topic* createTopic(string name, TypeCode eventTypecode);
    Topic* createFilteredTopic(string name,
                               TypeCode eventTypecode,
                               FilterSeq filters);
    Topic* retrieve(string name);
    TopicDict retrieveAll();
  };

};
