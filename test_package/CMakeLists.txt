cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(libprojectm CONFIG REQUIRED)

if(ENABLE_BOOST_FILESYSTEM OR NOT STD_FILESYSTEM_EXISTS)
    find_package(Boost REQUIRED COMPONENTS Filesystem)
endif()

add_executable(example src/example.cpp)

if(ENABLE_BOOST_FILESYSTEM OR NOT STD_FILESYSTEM_EXISTS)
    target_link_libraries(example libprojectm::libprojectm)
else()
    target_link_libraries(example libprojectm::libprojectm Boost::filesystem)
endif()
