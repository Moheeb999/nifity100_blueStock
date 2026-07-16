import java.util.*;

public class Demo {

    public static String keysGenerated(int digits){
        String x="";
        for(int i=0;i<digits;i++){
            x+=i;
        }
        return x;
    }
    public static HashSet<String> uniqueKey(int n,int digits){
        HashSet<String> set = new HashSet<>();
        for(int i=0;i<n;i++){
            if(set.contains(keysGenerated(digits))){
                continue;
            }
            else{
                set.add(keysGenerated(digits));
            }
        }
        return set;

    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int digits=sc.nextInt();
        int n=sc.nextInt();
        
    }
}