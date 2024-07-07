from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir
from collections import namedtuple

class libprojectmRecipe(ConanFile):
    name = "libprojectm"
    version = "4.1.1"
    package_type = "library"

    # Optional metadata
    license = "LGPL 2.1"
    author = "The projectM team"
    url = "https://github.com/conan-io/conan-center-index/tree/master/recipes/libprojectm"
    description = "The most advanced open-source music visualizer library. Project page https://github.com/projectM-visualizer/projectm"
    topics = ("audio", "opengl", "visualizer", "graphics")
    exports_sources = "cmake/*", "src/*", "presets/*", "tests/*", "vendor/*", "CMakeLists.txt", "config.h.cmake.in", "features.cmake"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],

        # Enable building projectM playlist library
        "enable_playlist": [True, False],

        # Enable building projectM developer test UI (based on sdl2)
        "enable_sdl_ui": [True, False],

        # Enable using GLES instead of OpenGL Core Profile
        "enable_gles": [True, False],

        # Force using Boost filesystem instead of cpp 17 filesystem
        "enable_boost_filesystem": [True, False],

        # Enable using a Conan dependency for GLM instead of the version bundled with projectM
        "enable_dep_glm": [True, False],

        # Enable exporting C++ symbols for ProjectM and PCM classes, not only the C API. Warning: This is not very portable.
        "enable_cxx_interface": [True, False],

        # Build and execute unit tests during Conan package build
        "enable_tests": [True, False],

        # Enable building from a local source directory (for local projectM lib development only)
        "use_local_source_dir": [True, False],

        # Local source directory location
        "local_source_dir": ["ANY"]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_playlist": True,
        "enable_sdl_ui": False,
        "enable_gles": False,
        "enable_boost_filesystem": False,
        "enable_dep_glm": False,
        "enable_tests": True,
        "enable_cxx_interface": False,
        "use_local_source_dir": False,
        "local_source_dir": ''
    }

    # define projectM components
    _ProjectMComponent = namedtuple("_ProjectMComponent", ("option", "dependencies", "external_dependencies", "exported_libs"))
    _projectm_component_tree = {

        # projectM playlist library
        "playlist": _ProjectMComponent("enable_playlist", [], [], ["projectM-4-playlist"]),

        # projectM main library
        "projectm": _ProjectMComponent(None, ["playlist"], [], ["projectM-4"]),

        #projectM developer test ui app
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

        if self.options.enable_dep_glm:
            self._projectm_component_tree["projectm"].external_dependencies.append("glm::glm")

        if self.settings.os == "Windows":
            self._projectm_component_tree["projectm"].external_dependencies.append("glew::glew")

        if self.options.enable_tests:
            self._projectm_component_tree["projectm"].external_dependencies.append("gtest::gtest")

        if self.options.enable_boost_filesystem:
            self._projectm_component_tree["projectm"].external_dependencies.append("boost::filesystem")
            self._projectm_component_tree["projectm-test-ui"].external_dependencies.append("boost::filesystem")

    def layout(self):
        cmake_layout(self)

    def source(self):
        if self.info.options.use_local_source_dir:
            copy(self,
                 '*',
                 self.info.options.local_source_dir.value,
                 '.'
                 )
        else:
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

        if self.options.enable_dep_glm:
            self.requires(f"glm/{deps['glm']}")

        if self.options.enable_sdl_ui:
            self.requires(f"sdl/{deps['sdl']}")

        if self.settings.os == "Windows":
            self.requires(f"glew/{deps['glew']}")

        if self.options.enable_tests:
            self.requires(f"gtest/{deps['gtest']}")

        if self.options.enable_boost_filesystem:
            self.requires(f"boost/{deps['boost']}")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables['ENABLE_EMSCRIPTEN'] = False
        tc.variables['BUILD_TESTING'] = self.options.enable_tests
        tc.variables['BUILD_DOCS'] = False
        tc.variables['ENABLE_SDL_UI'] = self.options.enable_sdl_ui
        tc.variables['ENABLE_PLAYLIST'] = self.options.enable_playlist
        tc.variables['ENABLE_GLES'] = self.options.enable_gles
        tc.variables['ENABLE_SYSTEM_GLM'] = False
        tc.variables['ENABLE_INSTALL'] = True
        tc.variables['ENABLE_CXX_INTERFACE'] = self.options.enable_cxx_interface
        tc.variables['ENABLE_BOOST_FILESYSTEM'] = self.options.enable_boost_filesystem
        tc.variables['ENABLE_SYSTEM_PROJECTM_EVAL'] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self.info.options.enable_tests:
            cmake.test()

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
                    self.cpp_info.components[conan_component].libs = [ l + ("d" if self.settings.build_type == "Debug" else "") for l in comp.exported_libs ]
                if requires:
                    self.cpp_info.components[conan_component].requires = requires
