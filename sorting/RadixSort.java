import java.util.Arrays;

public class RadixSort {
    public static void main(String[] args) {
        int[] data = {122,431,565,22,1,47,787};
        System.out.println("Before sorting");
        System.out.println(Arrays.toString(data));
        RadixSort rs = new RadixSort();
        rs.radixsort(data,data.length);
        System.out.println("After sorting");
        System.out.println(Arrays.toString(data));
    }

    void countingsort(int array[],int size,int place)
    {
        int output[] = new int[size];

        int tempcount[] = new int[10];
        Arrays.fill(tempcount,0); //fill the tempcount arr with 0s

        for(int i=0;i<size;i++)
            tempcount[(array[i]/place) % 10]++;

        for(int i=1;i<10;i++)
            tempcount[i] = tempcount[i] + tempcount[i-1];

        for(int i=size-1;i>=0;i--)
        {
            output[tempcount[(array[i]/place) % 10]-1] = array[i];
            tempcount[(array[i]/place) % 10]--;
        }
        for(int i=0;i<size;i++)
            array[i] = output[i];


    }

    void radixsort(int array[],int size)
    {
        //get the max element
        int max = array[0];
        for(int i=1;i<size;i++)
        {
            if(max<array[i])
            {
                max = array[i];
            }
        }

        //apply counting sort digit by digit
        for(int p=1;max/p>0;p *= 10) 
        {
            countingsort(array,size,p);
        }
    }
}