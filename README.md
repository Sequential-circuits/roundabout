# roundabout
A Big Data architecture based on a 2-way data transmission using Spark Streaming and multiple scripts.

Modern cities replaced the stop lights in its traffic system for roundabouts. These, besides requiring no maintenance, prevent collisions, and improve traffic flow in general. In a similar way, Big Data systems today rely on semaphore-based systems in which one script can only run after the other has started, of after it has received some data, etc. This eventually becomes a nightmare to manage and are thus prone to failure.

I propose a system where several scripts (developed in Python, Java, Scala, etc) feed with data a central script running on Spark Streaming. This central script, the "roundabout", runs continuously, gathering data from those scripts (the "cars"), processing that data, and forwarding to other scripts once they enter the roundabout.

This way, the automation is seamless, as data is kept by Spark until the script which needs it shows up, without the need for external job managers.

This simple implementation is based on 2 scripts developed in Python. One, the "roundabout", runs continously waiting for the "cars" to show up with data. These "cars", feed data to Spark Streaming and ALSO receives data from other cars or from computation done by the roundabout.

For example, one car connects with HDFS and pulls data from a file. It enters the roundabout and unloads its data from it. Another car pulls data from a Hbase DB, also enters the roundabout, and also unloads its data. These 2 data are then combined by Spark Streaming, which keeps it until a 3rd car enters the roundabout to receive it.
