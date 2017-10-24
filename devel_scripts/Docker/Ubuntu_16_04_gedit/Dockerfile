# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/

FROM ubuntu:16.04

RUN apt-get update && apt-get install -y gedit

# Replace 1000 with your user / group id
# id -u $USER
# id -g $USER 
RUN export uid=502 gid=20 && \
    mkdir -p /home/developer && \
    mkdir -p /home/developer/Desktop && \
    mkdir -p /home/developer/pwd && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    mkdir -p /etc/sudoers.d && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer

USER developer
ENV HOME /home/developer

# Run command
CMD /usr/bin/gedit
