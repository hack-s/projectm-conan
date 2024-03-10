#include "libprojectM/projectM.h"

int main() {
    auto projectm = projectm_create();
    projectm_destroy(projectm);
}
