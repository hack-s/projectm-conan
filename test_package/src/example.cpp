#include "libprojectM/projectM.h"
#include "libprojectM/playlist.h"

int main() {
    auto projectMHandle = projectm_create();

    auto playlistHandle = projectm_playlist_create(projectMHandle);
    projectm_playlist_destroy(playlistHandle);

    projectm_destroy(projectMHandle);
}
