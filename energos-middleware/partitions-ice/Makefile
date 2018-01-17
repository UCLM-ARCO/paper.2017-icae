CLASSPATH=-classpath /usr/share/java/Ice.jar:.

all: Energos Subscriber.class Publisher.class

%.class: %.java
	javac $(CLASSPATH) $<

Energos: Energos.ice
	slice2java $<

clean:
	$(RM) -r ./db
	$(RM) *.class *~
	$(RM) -r Energos


run-subscriber: Subscriber.class
	java $(CLASSPATH) Subscriber --Ice.Config=subscriber.config

run-publisher: Publisher.class
	java $(CLASSPATH) Publisher --Ice.Config=publisher.config

start: /usr/bin/icebox /usr/bin/icestormadmin
	@if ! [ -d db ]; then mkdir db; fi
	icebox --Ice.Config=icebox.config &
	sleep 3

stop:
	killall icebox
