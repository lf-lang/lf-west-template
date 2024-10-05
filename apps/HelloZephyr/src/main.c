#include <zephyr/kernel.h>
#include <zephyr/types.h>

K_MUTEX_DEFINE(mutex);
K_CONDVAR_DEFINE(condvar);

int main(void) {
  k_mutex_lock(&mutex, K_FOREVER);
  printk("Hello\n");
  k_condvar_wait(&condvar, &mutex, K_NO_WAIT);
  printk("Waited\n");
  return 0;
}
