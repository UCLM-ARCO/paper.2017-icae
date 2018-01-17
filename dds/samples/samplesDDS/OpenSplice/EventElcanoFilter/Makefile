#
# Include paths
INCLUDES+=-Iidl
INCLUDES+=-I./bld
INCLUDES+=-I../../src
INCLUDES+=-I../../../../../common
INCLUDES+=-I$(OSPL_HOME)/include/dcps/C++/SACPP
INCLUDES+=-I$(OSPL_HOME)/include
INCLUDES+=-I$(OSPL_HOME)/include/sys

# C++ Compiler settings.
CXX=g++
CXXFLAGS=-g -c
CPPFLAGS=$(INCLUDES)

# Linker settings.
LD_SO=$(CXX)
LD_FLAGS=
LD_LIBS=-lstdc++

#OpenSplice idl preprocessor
OSPLICE_COMP=$(OSPL_HOME)/bin/idlpp -S -l cpp -d bld

OSPLICE_LIBS=-lddsdatabase -ldcpsgapi -ldcpssacpp -lddsos

DCPS_SRC_FILES = bld/EventElcanoFilter.cpp bld/EventElcanoFilterDcps_impl.cpp bld/EventElcanoFilterDcps.cpp bld/EventElcanoFilterSplDcps.cpp
DCPS_OBJ_FILES = $(patsubst %.cpp, %.o, $(DCPS_SRC_FILES))


bld/%.o : src/%.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< -o $@

all : dirs exec/EventElcanoFilterPublisher exec/EventElcanoFilterSubscriber
	@echo ">>>> all done"

dirs :
	@mkdir -p bld
	@mkdir -p exec

$(DCPS_SRC_FILES) : idl/EventElcanoFilter.idl
	@echo "Compiling $< with SPLICE IDL compiler"
	@mkdir -p bld
	@$(OSPLICE_COMP) $(INCLUDES) $<


exec/EventElcanoFilterPublisher : $(DCPS_OBJ_FILES) bld/EventElcanoFilterPublisher.o bld/CheckStatus.o  bld/DDSEntityManager.o
	@echo "Linking EventElcanoFilterPublisher"
	@mkdir -p exec
	$(LD_SO) $(LD_FLAGS) -L$(OSPL_HOME)/lib -o $@ $^ $(OSPLICE_LIBS) $(LD_LIBS)

exec/EventElcanoFilterSubscriber : $(DCPS_OBJ_FILES) bld/EventElcanoFilterSubscriber.o bld/CheckStatus.o bld/DDSEntityManager.o
	@echo "Linking EventElcanoFilterSubscriber"
	@mkdir -p exec
	$(LD_SO) $(LD_FLAGS) -L$(OSPL_HOME)/lib -o $@ $^ $(OSPLICE_LIBS) $(LD_LIBS)



clean :
	@rm -f *.o
	@rm -rf bld
	@rm -rf exec
