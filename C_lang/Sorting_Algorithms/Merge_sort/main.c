#include <stdio.h>
#include <stdbool.h> 
#include <stdlib.h>

void merging(int start, int mid, int end, int arr[]){
	int leftLen = mid - start + 1; //+1 because arr starts from 0, which is not recognised when declaring
	int rightLen = end - mid;
	int leftArr[leftLen]; //creating left part array
	int rightArr[rightLen]; //the same thing as before
	for (int i = 0; i < leftLen; i++){ //left arr filling
		leftArr[i] = arr[start + i]; //start till mid
	}
	for (int j = 0; j < rightLen; j++){ //right arr filling
		rightArr[j] = arr[(mid + 1) + j]; //mid+1 'cause left is start-mid, right must be mid+1-end
	}
	int i = 0, j = 0; //index for left and right arrays
	int k = start; //index for the actual index in the original arr
	while ((i < leftLen) && (j < rightLen)){ //copying the numbers that could be compared (pairs)
		if (leftArr[i] <= rightArr[j]){ 
			arr[k] = leftArr[i];
			i++;
		}
		else{
			arr[k] = rightArr[j];
			j++;
		}
        k++;
	}
    //these while loops are for reminding numbers, that could not be compared
    while (i<leftLen){ //if numbers in leftArr stayed
        arr[k] = leftArr[i];
        i++;
        k++;
    }
    while (j<rightLen){ //if numbers in rightArr stayed
        arr[k] = rightArr[j];
        j++;
        k++;
    }
}
void dividing(int start, int end, int arr[]){
	if (start>=end){
        return; //does nothing..., goes back to where it was called
    } 
    int mid = (end + start)/2;

    dividing(start, mid, arr); //left arr
    dividing(mid+1, end, arr); //right arr
    merging(start, mid, end, arr);
}
int main(){
	int start = 0;
	int arr[] = {4,1,3,2,5};
	int lenArr = (sizeof(arr))/(sizeof(arr[0]))-1; //not actual length, the max index
	dividing(start, lenArr, arr);
    printf("\nArray:\n");
    for (int i = 0; i <= lenArr; i++){ //printing arr
        printf("%d ", arr[i]);
    }
    printf("\n");
	return 0;
}