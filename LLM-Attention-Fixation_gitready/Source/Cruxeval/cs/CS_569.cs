using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string txt) {
        Dictionary<char, int> coincidences = new Dictionary<char, int>();
        foreach (char c in txt)
        {
            if (coincidences.ContainsKey(c))
            {
                coincidences[c]++;
            }
            else
            {
                coincidences[c] = 1;
            }
        }
        return coincidences.Values.Sum();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("11 1 1")) == (6L));
    }

}
