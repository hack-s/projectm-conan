from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir
from collections import namedtuple

class libprojectmRecipe(ConanFile):
    name = "libprojectm"
    version = "4.1.0"
    package_type = "library"

    # Optional metadata
    license = "LGPL 2.1"
    author = "The projectM team"
    url = "https://github.com/conan-io/conan-center-index/tree/master/recipes/libprojectm"
    description = "The most advanced open-source music visualizer library. Project page https://github.com/projectM-visualizer/projectm"
    topics = ("audio", "opengl", "visualizer", "graphics")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_playlist": [True, False],
        "enable_sdl_ui": [True, False],
        "enable_gles": [True, False],
        "enable_boost_filesystem": [True, False],
        "enable_system_glm": [True, False],
        "enable_cxx_interface": [True, False],
        "build_testing": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_playlist": True,
        "enable_sdl_ui": False,
        "enable_gles": False,
        "enable_boost_filesystem": False,
        "enable_system_glm": False,
        "build_testing": False,
        "enable_cxx_interface": False
    }

    _ProjectMComponent = namedtuple("_ProjectMComponent", ("option", "dependencies", "external_dependencies", "exported_libs"))
    _projectm_component_tree = {
        "playlist": _ProjectMComponent("enable_playlist", [], [], ["projectM-4-playlist"]),
        "projectm": _ProjectMComponent(None, ["playlist"], [], ["projectM-4"]),
        "projectm-test-ui": _ProjectMComponent("enable_sdl_ui", ["projectm"], ["sdl::sdl"], []),
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if self.options.enable_gles:
            self._projectm_component_tree["projectm"].external_dependencies.append("gles::gles")
        else:
            self._projectm_component_tree["projectm"].external_dependencies.append("opengl::opengl")

        if self.options.enable_system_glm:
            self._projectm_component_tree["projectm"].external_dependencies.append("glm::glm")

        if self.settings.os == "Windows":
            self._projectm_component_tree["projectm"].external_dependencies.append("glew::glew")

        if self.options.build_testing:
            self._projectm_component_tree["projectm"].external_dependencies.append("gtest::gtest")

        if self.options.enable_boost_filesystem:
            self._projectm_component_tree["projectm"].external_dependencies.append("boost::filesystem")
            self._projectm_component_tree["projectm-test-ui"].external_dependencies.append("boost::filesystem")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True
        )

    def requirements(self):
        deps = self.conan_data["dependencies"][self.version]

        if self.options.enable_gles:
            self.requires(f"gles/{deps['gles']}")
        else:
            self.requires(f"opengl/{deps['opengl']}")

        if self.options.enable_system_glm:
            self.requires(f"glm/{deps['glm']}")

        if self.options.enable_sdl_ui:
            self.requires(f"sdl/{deps['sdl']}")

        if self.settings.os == "Windows":
            self.requires(f"glew/{deps['glew']}")

        if self.options.build_testing:
            self.requires(f"gtest/{deps['gtest']}")

        if self.options.enable_boost_filesystem:
            self.requires(f"boost/{deps['boost']}")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables['ENABLE_EMSCRIPTEN'] = False
        tc.variables['BUILD_TESTING'] = self.options.build_testing
        tc.variables['BUILD_DOCS'] = False
        tc.variables['ENABLE_SDL_UI'] = self.options.enable_sdl_ui
        tc.variables['ENABLE_PLAYLIST'] = self.options.enable_playlist
        tc.variables['ENABLE_GLES'] = self.options.enable_gles
        tc.variables['ENABLE_SYSTEM_GLM'] = self.options.enable_system_glm
        tc.variables['ENABLE_INSTALL'] = True
        tc.variables['ENABLE_CXX_INTERFACE'] = self.options.enable_cxx_interface
        tc.variables['ENABLE_BOOST_FILESYSTEM'] = self.options.enable_boost_filesystem
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        for compname, comp in self._projectm_component_tree.items():
            if comp.option is None or self.options.get_safe(comp.option):
                conan_component = f"{compname.lower()}"
                requires = [f"{dependency.lower()}" for dependency in comp.dependencies] + comp.external_dependencies
                self.cpp_info.components[conan_component].set_property("cmake_target_name", f"libprojectm::{compname}")

                if comp.exported_libs:
                    self.cpp_info.components[conan_component].libs = comp.exported_libs

                if requires:
                    self.cpp_info.components[conan_component].requires = requires
