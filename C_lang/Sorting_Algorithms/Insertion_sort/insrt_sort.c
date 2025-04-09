#include <stdio.h>
#include <stdlib.h>

void sorting(int arr[], int lenArr){
    for (int i=1; i<lenArr;i++){
        int key = arr[i];
        int j = i-1;
        while (j>=0 && key<arr[j]){
            //printf("%d|%d\n", key, arr[j]);
            arr[j+1] = arr[j];
            arr[j] = key;
            j-=1;
        }
    }
}

int main(){
    int arr[] = {4,2,3,5,1};
    int lenArr = sizeof(arr)/sizeof(arr[0]);
    sorting(arr, lenArr);
    for (int i=0; i<lenArr; i++){
        printf("%d ", arr[i]);
    }
    printf("\n");
    return 0;
}