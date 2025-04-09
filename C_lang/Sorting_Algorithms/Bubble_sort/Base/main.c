#include <stdio.h>

int main() {
    int i,x,y,j;
    int list1[] = {9,1,3,4,8,7,2,5,6,10};
    //int list1[] = {6,2,3,5,4};
    int lenList1 = sizeof(list1)/sizeof(list1[0]);
    printf("%d", lenList1);
    for (j = 0; j < lenList1-1; j++){
        for (i = 0; i < lenList1-1; i++) {
            x = list1[i];
            y = list1[i+1];
            if (i > lenList1-1) {
                break;
            }
            //printf("\nX: %d; Y: %d", x,y);
            if (x > y) {
                list1[i] = y;
                list1[i+1] = x;
            }
        }
    }
    printf("\n");
    for (i = 0; i < lenList1; i++) {
        printf("%d ", list1[i]);
    }
    return 0;
}