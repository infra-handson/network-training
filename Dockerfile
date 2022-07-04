# there is orzohmygodorz/mininet:2.9.0, but does not have python3 (used as http.server).
FROM orzohmygodorz/mininet:latest AS baseimage
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    iputils-ping \
    traceroute \
    patch \
    less \
    xterm \
    x11-xserver-utils \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# patch ref:
# * OVS Switch batch shutdown crashes when used with Floodlight · Issue #724 · mininet/mininet
#   https://github.com/mininet/mininet/issues/724
COPY resources/util.py.patch /usr/lib/python2.7/dist-packages/mininet
RUN cd /usr/lib/python2.7/dist-packages/mininet \
  && patch < util.py.patch

# install goss
COPY resources/goss /usr/local/bin

# install training contents
COPY exercise /exercise

CMD ["/bin/bash", "-c", "ovs-ctl start && tail -f /dev/null"]
