using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static long F(string value, string character) {
        int total = 0;
        foreach (char c in value)
        {
            if (c == character[0] || c == char.ToLower(character[0]))
            {
                total += 1;
            }
        }
        return total;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("234rtccde"), ("e")) == (1L));
    }

}
