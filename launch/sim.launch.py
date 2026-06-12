"""
px4_drone_sim — sim.launch.py  (v4)
─────────────────────────────────────────────────────────────────────
Strategy:
  1. Launch Gazebo GUI  (`gz sim -g`)           — the rendering front-end
  2. Launch PX4 SITL    (`make px4_sitl ...`)   — boots gz server + drone
  3. Micro XRCE-DDS Agent                       — PX4 uORB ↔ ROS 2
  4. ros_gz_bridge                              — Gazebo topics ↔ ROS 2
  5. QGroundControl

Why split gz server and gui?
  PX4 SITL starts the Gazebo *server* (headless by default in recent
  PX4 versions). We separately launch `gz sim -g` (GUI only) which
  connects to the already-running server and gives you the window.
"""

import os
from pathlib import Path

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    TimerAction,
    LogInfo,
)
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

# ── paths ─────────────────────────────────────────────────────────
PX4_DIR      = str(Path.home() / "PX4-Autopilot")
QGC_APPIMAGE = str(Path.home() / "QGroundControl.AppImage")
UXRCE_PORT   = "8888"
 
# World name must match the <world name='...'> field in the SDF
GZ_WORLD     = "default"
ROBOT_MODEL  = "x500_lidar_2d"

PACKAGE_NAME  = "px4_drone_sim"
package_share_dir = get_package_share_directory(PACKAGE_NAME)
 
# Paths to optional config files (only needed if SLAM / Nav2 are enabled)
BRIDGE_CONFIG = os.path.join(package_share_dir, "config", "gz_bridge.yaml")
SLAM_PARAMS   = os.path.join(package_share_dir, "config", "slam_params.yaml")
NAV2_PARAMS   = os.path.join(package_share_dir, "config", "nav2_params.yaml")
RVIZ_CONFIG   = os.path.join(package_share_dir, "config", "rviz2_config.rviz")

for path in [BRIDGE_CONFIG, SLAM_PARAMS, NAV2_PARAMS, RVIZ_CONFIG]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

# ──────────────────────────────────────────────────────────────────

def generate_launch_description():

    # ── 1. PX4 SITL  (starts gz server + spawns drone) ───────────
    px4_sitl = ExecuteProcess(
        cmd=["make", "px4_sitl", "gz_x500_lidar_2d"],
        cwd=PX4_DIR,
        output="screen",
        name="px4_sitl",
    )

    # ── 2. Micro XRCE-DDS Agent ───────────────────────────────────
    uxrce_agent = ExecuteProcess(
        cmd=["MicroXRCEAgent", "udp4", "-p", UXRCE_PORT],
        output="screen",
        name="uxrce_dds_agent",
    )

    # ── 3. ros_gz_bridge ──────────────────────────────────────────
    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_bridge",
        arguments=["--ros-args", "-p", f"config_file:={BRIDGE_CONFIG}"],
        output="screen",
    )

    # ── 4. QGroundControl ─────────────────────────────────────────
    qgc = ExecuteProcess(
        cmd=[QGC_APPIMAGE],
        output="log",
        name="qgroundcontrol",
    )

    # ── 5. Waypoint Control Node ──────────────────────────────────
    # We override the parameter 'robot_name' to be empty so it maps 
    # directly to the global PX4 DDS topics (/fmu/...)
    waypoint_controller = Node(
        package="px4_control",
        executable="waypoint_control",
        name="waypoint_control_node",
        parameters=[
            {"robot_name": "px4_0"},       # Forces topics to match /fmu/ exactly
            {"control_mode": "offboard"},
            {"use_sim_time": True},
        ],
        output="screen",
    )

    # ── 6. Lidar scan bridge (LaserScan → /scan) ──────────────────
    # The x500_lidar_2d actually publishes a 2-D LaserScan (not PointCloud2).
    # This bridges it to /scan and remaps the long gz topic name.
    gz_scan_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_scan_bridge",
        arguments=[
            f"/world/{GZ_WORLD}/model/{ROBOT_MODEL}_0/link/link"
            f"/sensor/lidar_2d_v2/scan"
            f"@sensor_msgs/msg/LaserScan"
            f"[gz.msgs.LaserScan",
            "--ros-args",
            "-r",
            f"/world/{GZ_WORLD}/model/{ROBOT_MODEL}_0/link/link"
            f"/sensor/lidar_2d_v2/scan:=/scan",
            "-p", "use_sim_time:=true",
        ],
        output="screen",
    )
    lidar_stabilized_frame = Node(
        package="px4_drone_sim",
        executable="scan_stabilizer.py",
        name="scan_stabilizer",
    )

    # ── 7. Static TF: drone base_link → lidar frame ───────────────
    # Required so RViz / SLAM / Nav2 know the sensor position on the drone.
    # Adjust the translation/rotation (x y z roll pitch yaw) if your model
    # places the lidar elsewhere.
    static_tf_lidar = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_tf_base_to_lidar",
        arguments=[
            "0", "0", "0",          # x y z  (no offset)
            "0", "0", "0",          # roll pitch yaw
            f"{ROBOT_MODEL}_0/link/base_link",   # parent frame
            f"{ROBOT_MODEL}_0/link/lidar_2d_v2", # child frame
        ],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )
 
    # # ── 9. SLAM Toolbox  (uncomment to enable) ────────────────────
    # # Requires: sudo apt install ros-jazzy-slam-toolbox
    # slam_toolbox = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([
    #         FindPackageShare("slam_toolbox"), "/launch/online_async_launch.py"
    #     ]),
    #     launch_arguments={
    #         "slam_params_file": SLAM_PARAMS,
    #         "use_sim_time": "true",
    #     }.items(),
    # )
 
    # ── 10. Nav2 costmap  (uncomment to enable) ───────────────────
    # Requires: sudo apt install ros-jazzy-nav2-costmap-2d ros-jazzy-nav2-lifecycle-manager
    nav2_costmap = Node(
        package="nav2_costmap_2d",
        executable="nav2_costmap_2d",
        name="local_costmap",
        parameters=[NAV2_PARAMS, {"use_sim_time": True}],
        output="screen",
    )
    nav2_lifecycle = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_costmap",
        parameters=[{
            "use_sim_time": True,
            "node_names": ["local_costmap"],
            "autostart": True,
        }],
        output="screen",
    )

    ## ─ 11. Rviz2 ───────────────
    rviz = ExecuteProcess(
        cmd=["rviz2", "-d", RVIZ_CONFIG],
        output="screen",
        name="rviz2",
    )


    # Timing:
    #  - PX4 needs ~5 s to boot the gz server
    #  - GUI can then connect
    #  - Bridge should wait until the world is fully loaded
    delayed_uxrce   = TimerAction(period=6.0,  actions=[uxrce_agent])
    delayed_bridge  = TimerAction(period=10.0, actions=[gz_bridge])
    delayed_qgc     = TimerAction(period=12.0, actions=[qgc])
    delayed_controller = TimerAction(period=14.0, actions=[waypoint_controller])

    num_line = 9
    return LaunchDescription([
        # PX4 SITL + Gazebo GUI
        LogInfo(msg="[1/9] Starting PX4 SITL (gz server + drone spawn) ..."),
        px4_sitl,
        LogInfo(msg="[2/9] Micro XRCE-DDS Agent starts in 6 s ..."),
        delayed_uxrce,

        # Bridge
        LogInfo(msg="[3/9] ros_gz_bridge starts in 10 s ..."),      # clock
        delayed_bridge,

        # QGroundControl
        LogInfo(msg="[4/9] QGroundControl starts in 12 s ..."),     # QGroundControl
        delayed_qgc,
        
        # Waypoint Controller
        LogInfo(msg="[5/9] Launching Waypoint Controller Node in 14 s ..."),    # waypoint controller
        delayed_controller,

        # Lidar
        LogInfo(msg="[6/9] Starting Lidar scan bridge and stabilizer ..."),
        gz_scan_bridge,
        lidar_stabilized_frame,

        # Static TF
        LogInfo(msg="[7/9] Publishing static TF from base_link to lidar frame ..."),
        static_tf_lidar,

        # Cost Map
        LogInfo(msg="[8/9] Starting Nav2 costmap and lifecycle manager ..."),
        nav2_costmap,
        nav2_lifecycle,

        # Rviz2
        LogInfo(msg="[9/9] Starting Rviz2 ..."),
        rviz,
    ])