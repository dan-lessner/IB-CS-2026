#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

void sorting(int arr[], int lenArr){
    bool sorted = false;
    int current = 0;
    while (sorted != true && current<=lenArr){
        int minVal = arr[current];
        for (int i=current; i<lenArr; i++){
            if (arr[i] < minVal){
                int temp = minVal;
                minVal = arr[i];
                arr[i] = temp;
            }
        }
        arr[current] = minVal;
        current++;
    }
}

int main(){
    int arr[] = {4,3,1,2,5};
    int lenArr = sizeof(arr)/sizeof(arr[0]);
    sorting(arr, lenArr);
    for (int i=0; i<lenArr; i++){
        printf("%d, ", arr[i]);
    }
    printf("\n");
    return 0;
}