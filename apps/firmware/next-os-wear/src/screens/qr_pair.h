#ifndef NEXT_OS_SCREENS_QR_PAIR_H
#define NEXT_OS_SCREENS_QR_PAIR_H

#include <lvgl.h>

typedef void (*next_os_qr_pair_dismiss_fn)(void);

void next_os_qr_pair_show(lv_obj_t *overlay, next_os_qr_pair_dismiss_fn on_dismiss);

#endif /* NEXT_OS_SCREENS_QR_PAIR_H */
