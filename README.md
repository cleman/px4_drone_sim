# PX4 Drone Simulation Workspace

This workspace contains the simulation environment for the PX4 drone using Gazebo.

### 1. [Install ROS2](https://docs.ros.org/en/jazzy/Installation.html) (developed with ROS2 Jazzy)

### 2. Install dependencies
```sh
sudo apt update && sudo apt install -y --no-install-recommends git cmake wget lsb-release gnupg libqt5gui5 ubuntu-gnome-desktop g++ python3 freeglut3-dev tmux nano gdb
sudo apt install ros-jazzy-ros-gz-bridge \
                 ros-jazzy-nav2-costmap-2d \
                 ros-jazzy-nav2-lifecycle-manager \
                 ros-jazzy-slam-toolbox \
                 ros-jazzy-tf2-ros \
                 ros-jazzy-tf-transformations
```

### 3. Install Gazebo (developed with Gazebo Harmonic)
```sh
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg 
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt update && sudo apt install -y \

sudo apt install libgz-transport14-dev python3-gz-transport14 python3-gz-msgs12
sudo apt install ros-jazzy-ros-gz-sim ros-jazzy-gz-sim-vendor gz-harmonic
```

### 4. Install PX4 Autopilot (developed with PX4 1.16)
```sh
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive --branch release/1.16

# If you want to use Gazebo Harmonic with the PX4 Autopilot, you need this commit, but it is not needed for Gazebo Garden:
cd PX4-Autopilot
git fetch https://github.com/jmackay2/PX4-Autopilot.git fix_gazebo_harmonic:fix_gazebo_harmonic
git cherry-pick -X theirs bf4408b772f2bc398a5398dabd4bfa67a96ec1b5

cd PX4-Autopilot 

./Tools/setup/ubuntu.sh

make px4_sitl_default

cd ~

# Install MicroXRCE-DDS Agent
git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git && \
    cd Micro-XRCE-DDS-Agent && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make
sudo make install
sudo ldconfig /usr/local/lib/
```

### 5. Ground Control Station

Install [QGroundControl](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/getting_started/download_and_install.html). \
It is necessary to launch **QGroundControl** alongside the simulation to monitor the PX4 heartbeat, home setup, and flight modes.

### 6. Source ROS2 in the `.bashrc`
```sh
export ROS_WS=/home/$USERNAME/(your_workspace)

echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && \
    echo "source $ROS_WS$/install/setup.bash" >> ~/.bashrc && \
    echo "export GZ_SIM_RESSOURCE_PATH=/home/$USERNAME/PX4-Autopilot/Tools/simulation/gz/models" >> ~/.bashrc && \
    echo "export ROS_WS=$ROS_WS$" >> ~/.bashrc && \
    echo "export GZ_CONFIG_PATH=/usr/share/gz:$GZ_CONFIG_PATH" >> ~/.bashrc && \
    echo "export ROS_DOMAIN_ID=1" >> ~/.bashrc
```

### 7. Setup & Build

Clone this repository into your `ros2_ws/src` folder, then build the workspace:

```bash
# In your ros2_ws/src directory
git clone <https://github.com/cleman/px4_drone_sim.git>
# Clone px4_msgs here so it is available to the workspace
git clone https://github.com/PX4/px4_msgs.git
cd ..
colcon build --symlink-install
source install/setup.bash

```

### 8. World Configuration

To make the custom world ecn_campus available to PX4, you must copy them into the PX4 installation directory:

```bash
# Copy the .sdf file
cp src/px4_drone_sim/worlds/ecn_campus/ecn_campus.sdf ~/PX4-Autopilot/Tools/simulation/gz/worlds/

# Copy the meshes folder (if required by your world)
cp -r src/px4_drone_sim/worlds/ecn_campus/meshes ~/PX4-Autopilot/Tools/simulation/gz/worlds/

```

## Usage Guide

### 1. Launching the Simulation

Use the following command to launch the simulation with your specific world:

```bash
ros2 launch px4_drone_sim sim.launch.py world:=ecn_campus

```

Furthermore `walls` works also.

### 2. Drone Control & Modes
The default mode is `Offboard` (controlled by computer). \
You can switch how the drone is controlled via ROS2 parameters:

* **Position Mode (Manual control):**
```sh
ros2 param set /waypoint_control control_mode position
```

* **Offboard Mode (Computer control):**
```sh
roos2 param set /waypoint_control control_mode offboard
```

### 3. Local Mapping (Nav2)
The simulation includes a local costmap for obstacle avoidance.

* **Configuration file:** `/src/config/nav2_params.yaml``(includes wall inflation parameters).

* **Costmap Topics:** You can visualize or access the costmap via:
    * `/costmap`
    * `/costmap_update`

### 4. Scenario Management

The `scenarioManager` node automatically generates mission targets to test your drone's navigation system.

**Interface for your Controller:**

- Subscribe to: `/current_goal` (`geometry_msgs/msg/PoseStamped`)
- The node automatically publishes the next target in the sequence once the current one is reached (distance < 2.0m)

**Integration**
Connect your navigation controller to the `current_goal` topic to receive automated mission targets.

**Remark:** \
The ROS2 environment runs into the ROS_DOMAIN_ID 1. By default this parameter is set to 0. A command above set the parameter modification in the .bashrc file.