#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    int n, min, max, num;
    printf("Сколько чисел сгенерировать: ");
    scanf("%d", &n);
    printf("Минимум: "); scanf("%d", &min);
    printf("Максимум: "); scanf("%d", &max);

    FILE *f = fopen("randoms.txt", "w");
    if (!f) { printf("Ошибка файла\n"); return 1; }
    srand(time(0));
    for (int i = 0; i < n; ++i) {
        num = min + rand() % (max - min + 1);
        fprintf(f, "%d\n", num);
    }
    fclose(f);
    printf("Готово! Числа — в randoms.txt\n");
    return 0;
}
