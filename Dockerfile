FROM amazonlinux:2

# Install Python 3.9 and system tools
RUN yum install -y gcc gcc-c++ make zip tar \
    wget git \
    python39 python39-devel python3-pip

# Set Python 3.9 as default
RUN alternatives --install /usr/bin/python python /usr/bin/python3.9 1
RUN alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Setup build directory
WORKDIR /opt

# Install from requirements.txt (copy it in first)
COPY requirements.txt .
RUN mkdir -p /opt/python && pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt -t /opt/python

# Clean out large unnecessary deps (already in layer)
RUN rm -rf /opt/python/pandas* /opt/python/numpy* /opt/python/tzdata* /opt/python/dateutil* /opt/python/six*

