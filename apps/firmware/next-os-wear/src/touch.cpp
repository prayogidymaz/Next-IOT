#include "touch.h"

#if defined(NEXT_OS_HARDWARE)
#include <Wire.h>

/* CST816D — alamat umum 0x15 pada T-Watch S3 */
#define TOUCH_SDA 39
#define TOUCH_SCL 40
#define TOUCH_INT 16

bool next_os_touch_init(void) {
    Wire.begin(TOUCH_SDA, TOUCH_SCL);
    /* Driver penuh Week 3-4; init I2C cukup untuk skeleton */
    return true;
}

#else

bool next_os_touch_init(void) {
    return true;
}

#endif
