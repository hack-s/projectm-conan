from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir
from conan.tools.files import apply_conandata_patches, export_conandata_patches
from conan.tools.system import package_manager
from conan.tools.gnu import PkgConfig

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

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
#        "enable_emscrpten": [True, False],
        "enable_playlist": [True, False],
        "enable_sdl_ui": [True, False],
        "enable_gles": [True, False],
        "enable_boost_filesystem": [True, False],
        "enable_system_glm": [True, False],
        "enable_cxx_interface": [True, False],
#        "build_docs": [True, False],
        "build_testing": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
#        "enable_emscrpten": False,
        "enable_playlist": True,
        "enable_sdl_ui": False,
        "enable_gles": False,
        "enable_boost_filesystem": False,
        "enable_system_glm": False,
#        "build_docs": False,
        "build_testing": False,
        "enable_cxx_interface": False
    }

    # Sources are located in the same place as this recipe, copy them to the recipe
    # exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")


    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

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
        self.requires(f"opengl/{deps['opengl']}")
        if self.options.enable_system_glm:
            self.requires(f"glm/{deps['glm']}")
        if self.options.enable_sdl_ui:
            self.requires(f"sdl/{deps['sdl']}")
        #if self.options.enable_gles:
        #    self.requires(f"gles/{deps['gles']}")

        if self.settings.os == "Windows":
            self.requires(f"glew/{deps['glew']}")
        if self.options.build_docs:
            self.requires(f"doxygen/{deps['doxygen']}")


    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables['ENABLE_EMSCRIPTEN'] = False #self.options.enable_emscrpten
        tc.variables['BUILD_TESTING'] = self.options.build_testing
        tc.variables['BUILD_DOCS'] = False #self.options.build_docs
        tc.variables['ENABLE_SDL_UI'] = self.options.enable_sdl_ui
        tc.variables['ENABLE_PLAYLIST'] = self.options.enable_playlist
        tc.variables['ENABLE_GLES'] = self.options.enable_gles
        tc.variables['ENABLE_SYSTEM_GLM'] = self.options.enable_system_glm
        tc.variables['ENABLE_INSTALL'] = True
        tc.variables['ENABLE_CXX_INTERFACE'] = self.options.enable_cxx_interface
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["projectM-4", "projectM-4-playlist"]
