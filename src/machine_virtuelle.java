import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

public class machine_virtuelle {

    private boolean debug = false;
    private boolean running = false;
    private ArrayList<String> po; // Programme objet
    private int co;               // Compteur ordinal
    private ArrayList<Integer> pile;           // Pile
    private int ip;               

    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Veuillez mettre le fichier à exécuter en arguments: java machine_virtuelle <file>");
            System.exit(1);
        }
        else {
            ArrayList<String> programme = new ArrayList<>();
            try (BufferedReader br = new BufferedReader(
                new FileReader(args[0])
            )) {
                String ligne;
                while ((ligne = br.readLine()) != null) {
                    programme.add(ligne);
                }
            }
            catch (IOException e) {
                System.err.println("Erreur lors de la lecture du fichier : " + e.getMessage());
            }
            machine_virtuelle mv = new machine_virtuelle(programme);
            mv.run();
        }
    }

    public machine_virtuelle(ArrayList<String> po) {
        this.po = po;
    }

    public void run() {
        do {
            step();
        } while (running);
    }

    public void step() {
        if (running) {
            String instruction = po.get(co);
            if (debug) {
                System.out.print(instruction + "\t");
            }
            switch (instruction) {
                case "debutProg();":
                    debutProg(); // 1
                    break;
                
                case "finProg();":
                    finProg(); // 2
                    break;
                
                case "affectation();":
                    affectation(); // 6
                    break;
                
                case "valeurPile();":
                    valeurPile(); // 7
                    break;
            
                default:
                    if (!instruction.endsWith(");")) {
                        System.err.println("Instruction mal formée : " + instruction);
                        running = false;
                    }
                    else if (instruction.startsWith("reserver(")) {
                        String nStr = instruction.substring(9, instruction.length() - 2);
                        int n = Integer.parseInt(nStr);
                        reserver(n); // 3
                    }
                    else if (instruction.startsWith("empiler(")) {
                        String valStr = instruction.substring(8, instruction.length() - 2);
                        int val = Integer.parseInt(valStr);
                        empiler(val); // 4
                    }
                    else {
                        System.err.println("Instruction inconnue : " + instruction);
                        running = false;
                    }
                    break;
            }
            co = co + 1;
            if (debug) {
                System.out.println();
            }
        }
    }

    private void debutProg() { // 1
        running = true;
        co = 0;
        ip = 0;
    }

    private void finProg() { // 2
        running = false;
    }

    private void reserver(int n) { // 3
        ip += n;
        while (pile.size() < ip) {
            pile.add(0);
        }
        if (debug) {
            System.out.print("Taille de la pile : " + pile.size());
        }
    }

    private void empiler(int val) { // 4
        pile.add(val);
        ip += 1;
    }

    private void affectation() { // 6
        pile.set(pile.get(ip - 1), pile.get(ip));
        ip -= 2;
    }

    private void valeurPile() { // 7
        pile.set(ip, pile.get(pile.get(ip)));
    }
}
