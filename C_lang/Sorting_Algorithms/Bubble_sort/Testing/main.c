#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>	
#include <time.h>

int numCompares = 0;

void general(int list1[], int lenList1) { 
    int i, x, y, j;
    for (j = 0; j < lenList1-1; j++){
        for (i = 0; i < lenList1-1; i++) {
            numCompares++; 
            x = list1[i];
            y = list1[i+1];
            if (x > y) {
                list1[i] = y;
                list1[i+1] = x;
            }
        }
    }
}

void randomArray(int nowLen, int tillLen){
	int arr[nowLen];
	int start = 0;
	for (int i = 0; i < nowLen; i++){
		int randNum = rand() % 100; //num from 0 to 99
		arr[i] = randNum;
	}
	general(arr, nowLen); 
}

int main(){
	FILE *fptr;
	fptr = fopen("data.txt", "w");
	if (fptr == NULL) {
		printf("Error opening file!\n");
		return 1;
	}

	srand(time(NULL));

	unsigned int tillLen; 
	printf("\nTill what length: ");
	scanf("%u", &tillLen);
	int nowLen = 0;
	while (nowLen < tillLen){
		nowLen += 1;
		randomArray(nowLen, tillLen);
		fprintf(fptr, "%d:%d\n", nowLen, numCompares);
		numCompares = 0; 
	}
	fclose(fptr);
	return 0;
}