#include "projectM-4/projectM.h"

int main() {
    auto str = projectm_alloc_string(10);
    projectm_free_string(str);
}
