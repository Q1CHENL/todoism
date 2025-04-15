FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and pip
RUN apt update && apt install -y python3 python3-pip nano && apt clean

# Install todoism Python package
RUN pip3 install todoism

CMD ["bash"]
