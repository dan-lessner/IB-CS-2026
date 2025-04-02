import java.util.LinkedList;
import java.util.List;
import java.util.Collections;

public class DualPivotQuicksort {

    public static boolean is_empty(List<?> list) {
        return list.isEmpty();
    }

    public static void dualPivotQuicksort(LinkedList<Integer> list) {
        if (list.size() < 2) {
            return; 
        }
        
        
        int pivot1 = list.getFirst();
        int pivot2 = list.getLast();
        
        // Ensure pivot1 is smaller than pivot2
        if (pivot1 > pivot2) {
            Collections.swap(list, 0, list.size() - 1);
            pivot1 = list.getFirst();
            pivot2 = list.getLast();
        }
        
        // Creating partitions
        LinkedList<Integer> less = new LinkedList<>(); 
        LinkedList<Integer> middle = new LinkedList<>(); 
        LinkedList<Integer> greater = new LinkedList<>(); 

        // Distribute elements into partitions
        for (int num : list) {
            if (num < pivot1) {
                less.add(num);
            } else if (num > pivot2) {
                greater.add(num);
            } else {
                middle.add(num);
            }
        }
        
        // Recursively sort the partitions
        dualPivotQuicksort(less);
        dualPivotQuicksort(greater);
        
        // Combine partitions back into the original list
        list.clear();
        list.addAll(less);
        list.addAll(middle);
        list.addAll(greater);
    }

    public static void main(String[] args) {
        LinkedList<Integer> list = new LinkedList<>();

        Collections.addAll(list, 24, 3, 45, 29, 15, 10, 5, 1, 8, 7, 6, 2, 4, 9);


        if (is_empty(list)) {
            System.out.println("This array is empty.");
        } else {
            System.out.println("Original list: " + list);
            dualPivotQuicksort(list);
            System.out.println("Sorted list: " + list);
        }
    }
}