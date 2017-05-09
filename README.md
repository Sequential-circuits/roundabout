# roundabout
A Big Data architecture based on a 2-way data transmission using Spark Streaming and multiple scripts

Modern cities replaced the stop lights in its traffic system for roundabouts. These, besides requiring no maintenance, prevent collisions, and improve traffic flow in general. In a similar way, Big Data systems today rely on semaphore-based systems in which one script can only run after the other has started, of after it has received some data, etc. This eventually becomes a nightmare to manage and are thus prone to failure.

I propose a system where several scripts (developed in Python, Java, Scala, etc) feed with data a central script running on Spark Streaming. This central script, the "roundabout", runs continuously, gathering data from those scripts (the "cars"), processing that data, and forwarding to other scripts once they enter the roundabout.
