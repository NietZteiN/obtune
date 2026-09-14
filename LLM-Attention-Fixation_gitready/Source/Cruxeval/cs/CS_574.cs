using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<string> simpons) {
        while (simpons.Count > 0)
        {
            string pop = simpons[simpons.Count - 1];
            simpons.RemoveAt(simpons.Count - 1);
            if (pop == char.ToUpper(pop[0]) + pop[1..])
            {
                return pop;
            }
        }
        return simpons[simpons.Count - 1];
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"George", (string)"Michael", (string)"George", (string)"Costanza"}))).Equals(("Costanza")));
    }

}
