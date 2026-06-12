# px4_drone_sim

Minimal ROS 2 **Jazzy** package to simulate a **PX4 x500_lidar_2d** drone in
**Gazebo Harmonic**, bridged to ROS 2 via **Micro XRCE-DDS**, with
**QGroundControl** launched automatically.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Gazebo Harmonic                      │
│   x500_lidar_2d  (physics + sensors)                    │
│       │  gz topics (lidar, IMU, odom)                   │
└───────┼─────────────────────────────────────────────────┘
        │ ros_gz_bridge (gz_bridge.yaml)
┌───────▼──────────────────────────────────────────────────┐
│                      ROS 2 Jazzy                         │
│  /lidar/points   /imu/data   /model/.../odometry  /clock │
└───────────────────────────────────────────────────────────┘
        ▲
        │ Micro XRCE-DDS (UDP :8888)
┌───────┴──────────────────────────────────────────────────┐
│  PX4 SITL  (px4_sitl_default)                           │
│  uORB topics → /fmu/in/* and /fmu/out/*                 │
└──────────────────────────────────────────────────────────┘
        ▲
        │ MAVLink UDP
┌───────┴─────────┐
│ QGroundControl  │
└─────────────────┘
```

---

## Prerequisites

### 1. PX4-Autopilot (built at least once for SITL)

```bash
git clone https://github.com/PX4/PX4-Autopilot.git --recursive ~/PX4-Autopilot
cd ~/PX4-Autopilot
# First-time full build (creates the binary we launch):
make px4_sitl gz_x500_lidar_2d
```

### 2. Micro XRCE-DDS Agent

```bash
pip install --user pyserial
git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install        # puts MicroXRCEAgent on PATH
```

### 3. QGroundControl AppImage

```bash
wget https://github.com/mavlink/qgroundcontrol/releases/latest/download/QGroundControl.AppImage \
     -O ~/QGroundControl.AppImage
chmod +x ~/QGroundControl.AppImage
```

### 4. ROS 2 dependencies

```bash
sudo apt install \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-px4-msgs
```

---

## Build & install the package

```bash
# Place (or symlink) this folder inside your ROS 2 workspace:
mkdir -p ~/ros2_ws/src
cp -r px4_drone_sim ~/ros2_ws/src/

cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select px4_drone_sim
source install/setup.bash
```

---

## Run

```bash
ros2 launch px4_drone_sim sim.launch.py
```

### Optional overrides

```bash
ros2 launch px4_drone_sim sim.launch.py \
  px4_dir:=/opt/PX4-Autopilot \
  drone_model:=x500_lidar_2d \
  uxrce_port:=8888
```

---

## Verify it works

```bash
# PX4 uORB topics via Micro XRCE-DDS
ros2 topic list | grep fmu

# Gazebo sensor topics via ros_gz_bridge
ros2 topic echo /lidar/points --once
ros2 topic echo /imu/data --once
```

---

## Useful commands during simulation

```bash
# Arm & takeoff via PX4 CLI (in the PX4 shell that appears in the terminal)
commander takeoff

# Or send a MAVLink command from ROS 2 (requires px4_ros_com):
ros2 run px4_ros_com offboard_control
```

---

## File layout

```
px4_drone_sim/
├── CMakeLists.txt
├── package.xml
├── config/
│   └── gz_bridge.yaml     # Gazebo ↔ ROS 2 topic mapping
└── launch/
    └── sim.launch.py      # Single entry-point launch file
```
