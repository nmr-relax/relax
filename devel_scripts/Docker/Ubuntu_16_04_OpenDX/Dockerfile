# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/

FROM ubuntu:16.04

RUN apt-get update && apt-get install -y dx

RUN useradd -ms /bin/bash developer
# -m : Create the home directory if it does not exist.
# -s : User's login shell, which defaults to /bin/bash
USER developer
WORKDIR /home/developer

# Run command
CMD /usr/bin/dx
