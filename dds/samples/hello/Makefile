
all:

clean:
	$(RM) *~
	$(RM) -r db

start:  icebox.config icestorm.config
	@if ! [ -d db ]; then mkdir db; fi
	icebox --Ice.Config=icebox.config &
	sleep 2
	../../src/tools/IceDDS_Admin.py --Ice.Config=IceDDSAdmin.config
	sleep 3

stop: icestorm.config
	killall icebox
