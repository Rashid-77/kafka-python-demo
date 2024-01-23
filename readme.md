This demo uses confluent kafka python client and zookeeper in the docker.
Python3.10, docker V2

After start topics are created, then order service sends message "how many cups?". Product servic answers how many cups left and counts down it until they reach zero. Message log beetwen service are saving in the "log.log" file.

To start project, open terminal and run

<code>docker compose build</code>

<code>docker compose up</code>

Open second terminal and run:

<code>docker exec -it product /bin/bash</code>

<code>tail -f /code/log.log</code>

Open third terminal and run:

<code>docker exec -it order /bin/bash</code>

<code>tail -f /code/log.log</code>
