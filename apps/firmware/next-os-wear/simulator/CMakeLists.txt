cmake_minimum_required(VERSION 3.16)
project(next_os_wear_simulator C CXX)

set(CMAKE_CXX_STANDARD 17)

find_package(SDL2 REQUIRED)
find_package(PkgConfig)

include_directories(
    ${CMAKE_SOURCE_DIR}/../include
    ${CMAKE_SOURCE_DIR}/../src
    ${SDL2_INCLUDE_DIRS}
)

file(GLOB SCREEN_SOURCES ../src/screens/*.cpp)
add_executable(next_os_wear_sim
    main_sim.cpp
    ../src/app.cpp
    ${SCREEN_SOURCES}
)

target_compile_definitions(next_os_wear_sim PRIVATE NEXT_OS_SIMULATOR=1 LV_CONF_INCLUDE_SIMPLE)
target_link_libraries(next_os_wear_sim PRIVATE SDL2::SDL2)

message(STATUS "Alternatif build: cmake -B build && cmake --build build")
