import java.util.HashMap;
import java.util.Map;
import java.util.Random;

/**
 * Settlers of Catan — Dice probability simulator and analyzer.
 *
 * Simulates millions of 2d6 rolls to compute empirical probabilities
 * and expected resource distributions for each hex number token.
 * Useful for evaluating settlement placement strategy.
 */
public class DiceSimulator {

    private final Random rng;
    private final int[] rollCounts = new int[13]; // indices 2-12
    private int totalRolls = 0;

    public DiceSimulator() {
        this.rng = new Random();
    }

    public DiceSimulator(long seed) {
        this.rng = new Random(seed);
    }

    /**
     * Roll two six-sided dice and return the sum.
     */
    public int roll() {
        int d1 = rng.nextInt(6) + 1;
        int d2 = rng.nextInt(6) + 1;
        int total = d1 + d2;
        rollCounts[total]++;
        totalRolls++;
        return total;
    }

    /**
     * Simulate a given number of rolls and record results.
     */
    public void simulate(int numRolls) {
        for (int i = 0; i < numRolls; i++) {
            roll();
        }
    }

    /**
     * Get the empirical probability of rolling a given total.
     */
    public double empiricalProbability(int total) {
        if (total < 2 || total > 12 || totalRolls == 0) {
            return 0.0;
        }
        return (double) rollCounts[total] / totalRolls;
    }

    /**
     * Get the theoretical probability of rolling a given total with 2d6.
     */
    public static double theoreticalProbability(int total) {
        if (total < 2 || total > 12) {
            return 0.0;
        }
        int combos = 6 - Math.abs(7 - total);
        return combos / 36.0;
    }

    /**
     * Calculate expected resources per turn for a settlement adjacent
     * to tiles with the given number tokens.
     */
    public static double expectedResourcesPerTurn(int... numberTokens) {
        double expected = 0.0;
        for (int token : numberTokens) {
            expected += theoreticalProbability(token);
        }
        return expected;
    }

    /**
     * Rank all hex number tokens by production frequency.
     * Returns a map of number -> expected hits per 36 rolls.
     */
    public static Map<Integer, Integer> productionRanking() {
        Map<Integer, Integer> ranking = new HashMap<>();
        for (int n = 2; n <= 12; n++) {
            if (n == 7) continue; // robber
            ranking.put(n, 6 - Math.abs(7 - n));
        }
        return ranking;
    }

    /**
     * Evaluate a settlement position by computing total expected resources.
     * Takes the number tokens of adjacent hex tiles.
     *
     * @param adjacentNumbers number tokens on the 1-3 adjacent hexes
     * @return expected resources per 36 rolls (higher is better)
     */
    public static int evaluateSettlement(int... adjacentNumbers) {
        int totalDots = 0;
        for (int n : adjacentNumbers) {
            if (n < 2 || n > 12 || n == 7) continue;
            totalDots += 6 - Math.abs(7 - n);
        }
        return totalDots;
    }

    /**
     * Compute the probability of rolling a 7 (robber activation).
     */
    public double robberFrequency() {
        return empiricalProbability(7);
    }

    /**
     * Print a frequency distribution report.
     */
    public void printReport() {
        System.out.println("=== Dice Simulation Report ===");
        System.out.printf("Total rolls: %,d%n%n", totalRolls);
        System.out.printf("%-8s %-12s %-12s %-10s%n", "Roll", "Empirical", "Theoretical", "Deviation");
        System.out.println("-".repeat(45));

        for (int i = 2; i <= 12; i++) {
            double emp = empiricalProbability(i);
            double theo = theoreticalProbability(i);
            double dev = emp - theo;
            System.out.printf("%-8d %-12.4f %-12.4f %+.4f%n", i, emp, theo, dev);
        }

        System.out.println();
        System.out.println("=== Settlement Evaluation Examples ===");
        System.out.printf("Settlement on 6/8/5:  %d dots (%.1f%% per roll)%n",
                evaluateSettlement(6, 8, 5), expectedResourcesPerTurn(6, 8, 5) * 100);
        System.out.printf("Settlement on 2/3/11: %d dots (%.1f%% per roll)%n",
                evaluateSettlement(2, 3, 11), expectedResourcesPerTurn(2, 3, 11) * 100);
        System.out.printf("Settlement on 9/10/4: %d dots (%.1f%% per roll)%n",
                evaluateSettlement(9, 10, 4), expectedResourcesPerTurn(9, 10, 4) * 100);

        System.out.println();
        System.out.println("=== Production Ranking ===");
        Map<Integer, Integer> ranking = productionRanking();
        ranking.entrySet().stream()
                .sorted((a, b) -> b.getValue() - a.getValue())
                .forEach(e -> {
                    String dots = "*".repeat(e.getValue());
                    System.out.printf("  %2d: %-6s (%d/36)%n", e.getKey(), dots, e.getValue());
                });
    }

    /**
     * Check if empirical results match theoretical within a tolerance.
     * Useful for verifying dice fairness.
     */
    public boolean isWithinTolerance(double tolerance) {
        for (int i = 2; i <= 12; i++) {
            double diff = Math.abs(empiricalProbability(i) - theoreticalProbability(i));
            if (diff > tolerance) {
                return false;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        int numRolls = 1_000_000;
        if (args.length > 0) {
            try {
                numRolls = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.err.println("Usage: java DiceSimulator [numRolls]");
                System.exit(1);
            }
        }

        DiceSimulator sim = new DiceSimulator(42);
        sim.simulate(numRolls);
        sim.printReport();

        System.out.println();
        boolean fair = sim.isWithinTolerance(0.005);
        System.out.printf("Dice fairness check (tolerance 0.5%%): %s%n",
                fair ? "PASSED" : "FAILED");
    }
}
