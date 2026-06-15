# PX4 Drone Simulation Workspace

This workspace contains the simulation environment for the PX4 drone using Gazebo.

### 1. Setup & Build

Clone this repository into your `ros2_ws/src` folder, then build the workspace:

```bash
# In your ros2_ws/src directory
git clone <https://github.com/cleman/px4_drone_sim.git>
cd ..
colcon build --symlink-install
source install/setup.bash

```

### 2. World Configuration

To make the custom world ecn_campus available to PX4, you must copy them into the PX4 installation directory:

```bash
# Copy the .sdf file
cp ros2_ws/src/px4_drone_sim/worlds/ecn_campus/ecn_campus.sdf ~/PX4-Autopilot/Tools/simulation/gz/worlds/

# Copy the meshes folder (if required by your world)
cp -r ros2_ws/src/px4_drone_sim/worlds/ecn_campus/meshes ~/PX4-Autopilot/Tools/simulation/gz/worlds/

```


### 3. Dependencies (`px4_msgs`)

Currently, the `px4_msgs` package is missing from this workspace.

* **Fix:** For now, please copy the `px4_msgs` folder from your previous/original workspace into this `src` directory.
* *This will be properly managed/added in a future update.*

### 4. Launching the Simulation

Use the following command to launch the simulation with your specific world:

```bash
ros2 launch px4_drone_sim sim.launch.py world:=ecn_campus

```

Furthermore `walls` works also.