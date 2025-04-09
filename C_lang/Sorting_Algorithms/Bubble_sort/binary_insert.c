#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int binarySearch(int arr[], int key, int start, int end){
    int pos; //index of where it needs to be inserted

    if (start > end){
        return start;
    }
    int mid = start + (end - start) / 2;
    
    if (key == arr[mid] ){
        pos = mid;
        return pos;
    }
    else if (key < arr[mid]){
        return binarySearch(arr,key,start, mid-1);
    }
    else { //(key > arr[mid])
        return binarySearch(arr,key,mid+1,end);
    }
}

void sorting(int arr[], int lenArr){
    for (int i=1; i<lenArr;i++){
        int key = arr[i];
        int j = i-1;
        int pos = binarySearch(arr,key,0,j);
        int k = i;
        while (k > pos) {
            arr[k] = arr[k - 1];
            k--;
        }
        arr[pos] = key;
    }
}

int main(){
    clock_t startTime = clock();
    int size,j=0;
    printf("\nChoose size of a list: ");
    scanf("%d",&size);

    int *malArr = (int*)malloc(size*sizeof(int));
    if (malArr == NULL) {
        printf("Allocation failed");
        exit(0);
    }    
    for (int i = 0; i < size; i++) {
        malArr[i] = size - i;
    }
    printf("\nOriginal list: ");
    for (int i=0; i<size;i++){
        printf("%d ", malArr[i]);
    }
    sorting(malArr, size);
    printf("\n\nNew list: ");
    for (int i=0; i<size;i++){
        printf("%d ", malArr[i]);
    }
    printf("\n");
    free(malArr); //frees memory
    clock_t endTime = clock();
    double totTime = (double)(endTime-startTime)/CLOCKS_PER_SEC;
    printf("\nTime: %.5f\n", totTime);
    return 0;
}