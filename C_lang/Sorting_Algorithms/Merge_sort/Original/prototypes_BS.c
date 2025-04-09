//Ultra first
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

void actualSort(int lenList1, int *list1){
    int startIndex = 0;
    int endIndex = lenList1-1;
    int midIndex = lenList1/2;
    int tempList1[lenList1];
    int lenTemp;
    bool sorted = false;
    
    while (sorted != false){
        for (int i = 0; i<midIndex; i++){
            tempList1[i] = list1[startIndex+1];
        }
        lenTemp = sizeof(tempList1)/sizeof(tempList1[0])-1;
        if ()

    } 

}

int main(){
    int list1[] = {4,2,7,1};
    int lenList1 = sizeof(list1)/sizeof(list1[0]);
    if (lenList1 <= 0){
        printf("\nAlready sorted!");
    }
    else{
        actualSort;
    }

    return 0;
}

//1st prototype
void divide(int end){
	int start, mid = 0;
	bool divided = false;
	while (divided == false){
		if ((end-start) <= 1){ //checks if already done
			merge(start, end, mid);
			//divided = true;
		}
		mid = (start + end)/2;
	}
}
void merge(start, end, mid){
	bool sorted = false;
	int tempNum;
	while (sorted == false){
		for (int i = start; i<=end;i++){
			if (arr[i] > arr[i+1] && (i+1) <= mid)

		}

	}

}

//2nd prototype
void divide(int end, int start){
	int mid = ((end-start)/2) + start; //mid creation, + start for future itterations
	bool separated = false;
	bool firstHalf = true;
	while (separated == false){
		mid /= 2; //mid division 
		if (((mid-start) < 1) && firstHalf == true){

			comparison(start, mid);
		}
		else if (((end-mid) < 1) && firstHalf == false){
			
			comparison(mid, end);
		}
	}
}

void comparison(int start, int end){
	int tempNum;
	for (int i = start; i <= end; i++){
		if ((arr[i+1] < arr[i]) && (i+1 <= lenArr)){ //musnt exceed the length
			tempNum = arr[i];
			arr[i] = arr[i+1];
			arr[i+1] = tempNum;
		}
	}
	if
}
