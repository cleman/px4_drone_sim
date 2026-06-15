cmake_minimum_required(VERSION 3.8)
project(px4_drone_sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

find_package(rclcpp REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(px4_msgs REQUIRED)

add_executable(
  waypoint_control src/waypoint_control.cpp
)

ament_target_dependencies(
  waypoint_control
  rclcpp
  px4_msgs
  geometry_msgs
)

target_link_libraries(waypoint_control
  Eigen3::Eigen
)

target_include_directories(waypoint_control PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include/${PROJECT_NAME}
  ${CMAKE_SOURCE_DIR}/../common/include
)

install(PROGRAMS
  scripts/scan_stabilizer.py
  scripts/scenarioManager.py
  scripts/gz_pose_relay.py
  DESTINATION lib/${PROJECT_NAME}
)

install(TARGETS
  waypoint_control
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY 
  launch
  config
  worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
