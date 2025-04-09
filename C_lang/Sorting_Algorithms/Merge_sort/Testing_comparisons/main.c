/*This version of Merge Sort is made for statistical purposes*/
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>

int numCompares = 0; //making general, so i dont need to forward it more

void merging(int start, int mid, int end, int arr[]){
	int leftLen = mid - start + 1;
	int rightLen = end - mid;
	int leftArr[leftLen];
	int rightArr[rightLen]; 
	for (int i = 0; i < leftLen; i++){ 
		leftArr[i] = arr[start + i]; 
	}
	for (int j = 0; j < rightLen; j++){ 
		rightArr[j] = arr[(mid + 1) + j]; 
	}
	int i = 0, j = 0; 
	int k = start; 
	while ((i < leftLen) && (j < rightLen)){ 
		numCompares++;
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
    while (i<leftLen){ 
        arr[k] = leftArr[i];
        i++;
        k++;
    }
    while (j<rightLen){ 
        arr[k] = rightArr[j];
        j++;
        k++;
    }
}

void dividing(int start, int end, int arr[]){
	if (start>=end){
        return; 
    } 
    int mid = (end + start)/2;

    dividing(start, mid, arr);
    dividing(mid+1, end, arr);
    merging(start, mid, end, arr);
}

void randomArray(int nowLen, int tillLen){
	int arr[tillLen]; 
	int start = 0;
	for (int i = 0; i<nowLen; i++){
		int randNum = rand() % 100; //num from 0 to 99
		arr[i] = randNum;
	}
	int lenArr = nowLen-1;
	dividing(start, lenArr, arr);
}

int main(){
	//file manipulation
	FILE *fptr;
	fptr = fopen("data.txt", "w"); //rewrites everytime
	//random num seed thingy
	srand(time(NULL));

	unsigned int tillLen; //till what array length
	printf("\nTill what length: ");
	scanf("%u", &tillLen);
	int nowLen = 0;
	while (nowLen < tillLen){
		nowLen += 1;
		randomArray(nowLen,tillLen);
		fprintf(fptr, "%d:%d\n", nowLen, numCompares);
		numCompares = 0; //will reset the value
	}
	fclose(fptr);
	return 0;
}