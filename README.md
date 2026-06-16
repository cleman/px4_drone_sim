# PX4 Drone Simulation Workspace

This workspace contains the simulation environment for the PX4 drone using Gazebo.

### 1. Setup & Build

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

### 2. World Configuration

To make the custom world ecn_campus available to PX4, you must copy them into the PX4 installation directory:

```bash
# Copy the .sdf file
cp src/px4_drone_sim/worlds/ecn_campus/ecn_campus.sdf ~/PX4-Autopilot/Tools/simulation/gz/worlds/

# Copy the meshes folder (if required by your world)
cp -r src/px4_drone_sim/worlds/ecn_campus/meshes ~/PX4-Autopilot/Tools/simulation/gz/worlds/

```


### 3. Launching the Simulation

Use the following command to launch the simulation with your specific world:

```bash
ros2 launch px4_drone_sim sim.launch.py world:=ecn_campus

```

Furthermore `walls` works also.