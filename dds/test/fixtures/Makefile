
all:

clean:
	$(RM) *~
	$(RM) -r db

start-local:  icebox.config icestorm.config
	@if ! [ -d db ]; then mkdir db; fi
	icebox --Ice.Config=icebox.config &
	sleep 3

stop-local: icestorm.config
	killall icebox

start-android:  iceboxAndroid.config icestormAndroid.config
	@if ! [ -d db ]; then mkdir db; fi
	icebox --Ice.Config=iceboxAndroid.config &
	sleep 3

stop-android: icestormAndroid.config
	killall icebox
