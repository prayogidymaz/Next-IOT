#include <unity.h>

#include "theme.h"

void test_color_constants(void) {
    TEST_ASSERT_EQUAL_HEX32(0xF5EFE0, NEXT_OS_COLOR_CREAM);
    TEST_ASSERT_EQUAL_HEX32(0x556B4A, NEXT_OS_COLOR_OLIVE);
    TEST_ASSERT_EQUAL_HEX32(0x1F1F1F, NEXT_OS_COLOR_DARK);
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_color_constants);
    return UNITY_END();
}
