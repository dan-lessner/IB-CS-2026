#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void sorting(int arr[], int lenArr){
    for (int i=1; i<lenArr;i++){
        int key = arr[i];
        int j = i-1;
        while (j>=0 && key<arr[j]){
            arr[j+1] = arr[j];
            arr[j] = key;
            j-=1;
        }
    }
}

int main() {
    FILE *fptr = fopen("data.txt", "w");
    if (fptr == NULL) {
        printf("Error opening file!\n");
        return 1;
    }

    int size;
    printf("Enter the final size of the list: ");
    scanf("%d", &size);

    for (int currentSize = 0; currentSize <= size; currentSize++) {
        int *malArr = (int *)malloc(currentSize * sizeof(int));
        if (malArr == NULL) {
            printf("Allocation failed\n");
            fclose(fptr);
            return 1;
        }
        for (int i = 0; i < currentSize; i++) {
            malArr[i] = currentSize - i;
        }
        clock_t startTime = clock();
        sorting(malArr, currentSize);
        clock_t endTime = clock();
        double totTime = (double)(endTime - startTime) / CLOCKS_PER_SEC;
        fprintf(fptr, "%d:%.5f\n", currentSize, totTime);
        printf("Size: %d, Time: %.5f seconds\n", currentSize, totTime);
        free(malArr);
    }

    fclose(fptr);
    return 0;
}