import java.util.HashMap;

public class BrokenJava {

    private Object resource1 = new Object();
    private Object resource2 = new Object();

    public void executeTask1() {
        synchronized(resource1) {
            System.out.println("Acquired lock 1");
            try { Thread.sleep(100); } catch(Exception e) {}
            
            synchronized(resource2) {
                System.out.println("Task 1 completely finished");
            }
        }
    }

    public void executeTask2() {
        synchronized(resource2) {
            System.out.println("Acquired lock 2");
            try { Thread.sleep(100); } catch(Exception e) {}
            
            synchronized(resource1) {
                System.out.println("Task 2 completely finished");
            }
        }
    }

    public static void main(String[] args) {
        HashMap<String, String> map = null;
        if (args.length > 0) {
            map = new HashMap<>();
            map.put("key", "value");
        }
        System.out.println("Map size: " + map.size());
        
        BrokenJava obj = new BrokenJava();
        new Thread(() -> obj.executeTask1()).start();
        new Thread(() -> obj.executeTask2()).start();
    }
}