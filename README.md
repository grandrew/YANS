# YANS 

## Yet Another Network Simulator

YANS is a [Docker](https://www.docker.com) based network simulator. It is lightening-fast. The screenplay below demonstrates that YANS can launch a simulated network in **under 3 seconds**.

<img src="./screenplay.gif">

# Install prerequisites:

Python >= 2.6 or >= 3.3

[Docker](https://download.docker.com/win/stable/Docker%20for%20Windows%20Installer.exe)

Clone repo

```bash
git clone https://github.com/rnunez95/YANS.git
```

Install pip packages

```bash
pip install -r requirements.txt
```

# Run

CD into YANS

```bash
cd ./YANS
```

Create a network topology file as a .yaml

```
links:
- name: link1
    nodes:
        - node1
        - node2
- name: link2
    nodes:
        - node1
- name: link3
```

To view all commands run

```
yans.py -h
```

Start the simulator

```
yans.py -V -t <path_to_topo.yaml> up
```
