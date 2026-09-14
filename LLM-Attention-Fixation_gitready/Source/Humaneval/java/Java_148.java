import java.util.*;
import java.lang.*;

class Solution {
    /**
    There are eight planets in our solar system: the closerst to the Sun
    is Mercury, the next one is Venus, then Earth, Mars, Jupiter, Saturn,
    Uranus, Neptune.
    Write a function that takes two planet names as strings planet1 and planet2.
    The function should return a tuple containing all planets whose orbits are
    located between the orbit of planet1 and the orbit of planet2, sorted by
    the proximity to the sun.
    The function should return an empty tuple if planet1 or planet2
    are not correct planet names.
    Examples
    bf("Jupiter", "Neptune") ==> ["Saturn", "Uranus"]
    bf("Earth", "Mercury") ==> ["Venus"]
    bf("Mercury", "Uranus") ==> ["Venus", "Earth", "Mars", "Jupiter", "Saturn"]
     */
    public List<String> bf(String planet1, String planet2) {

        List<String> planet_names = Arrays.asList("Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune");
        if (!planet_names.contains(planet1) || !planet_names.contains(planet2) || planet1.equals(planet2)) {
            return List.of();
        }
        int planet1_index = planet_names.indexOf(planet1);
        int planet2_index = planet_names.indexOf(planet2);
        if (planet1_index < planet2_index) {
            return planet_names.subList(planet1_index + 1, planet2_index);
        } else {
            return planet_names.subList(planet2_index + 1, planet1_index);
        }
    }
}

public class Java_148 {
    public static void main(String[] args) {
        Solution s = new Solution();
        List<Boolean> correct = Arrays.asList(
                s.bf("Jupiter", "Neptune").equals(Arrays.asList("Saturn", "Uranus")),
                s.bf("Earth", "Mercury").equals(List.of("Venus")),
                s.bf("Mercury", "Uranus").equals(Arrays.asList("Venus", "Earth", "Mars", "Jupiter", "Saturn")),
                s.bf("Neptune", "Venus").equals(Arrays.asList("Earth", "Mars", "Jupiter", "Saturn", "Uranus")),
                s.bf("Earth", "Earth").equals(List.of()),
                s.bf("Mars", "Earth").equals(List.of()),
                s.bf("Jupiter", "Makemake").equals(List.of())
        );
        if (correct.contains(false)) {
            throw new AssertionError();
        }
    }
}
