arch = i86Linux2.6gcc4.1.1

BASE=HelloMsg
GENERATED=$(addsuffix .h,   $(BASE) $(BASE)Plugin $(BASE)Support)\
	  $(addsuffix .cxx, $(BASE) $(BASE)Plugin $(BASE)Support)

all: $(BASE).h
	$(MAKE) -f makefile_$(BASE)_$(arch)


$(BASE).h: $(BASE).idl
	rtiddsgen -language C++ -replace $^

clean:
	$(RM) $(GENERATED)
	$(RM) -r */
