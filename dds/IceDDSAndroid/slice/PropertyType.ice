/* -*- mode: c++; coding: utf-8 -*- */

#ifndef PROPERTY_TYPE_ICE
#define PROPERTY_TYPE_ICE

#include <Ice/BuiltinSequences.ice>

// In order to reduce bandwidth we keep class names and module names
// as small as possible

module P {

    class T {};

    class BoolT extends T {
	bool value;
    };

    class ByteT extends T {
	byte value;
    };


    class ByteSeqT extends T {
      Ice::ByteSeq value;
    };


    class IntT extends T {
	int value;
    };

    class FloatT extends T {
	float value;
    };

    class StringT extends T {
	string value;
    };

    class StringSeqT extends T {
	Ice::StringSeq value;
    };

    class ObjectT extends T {
	Object* value;
    };

};

#endif
