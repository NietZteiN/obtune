using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(long number) {
        Dictionary<string, int> transl = new Dictionary<string, int>() { { "A", 1 }, { "B", 2 }, { "C", 3 }, { "D", 4 }, { "E", 5 } };
        List<string> result = new List<string>();
        foreach (var pair in transl)
        {
            if (pair.Value % number == 0)
            {
                result.Add(pair.Key);
            }
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((2L)).SequenceEqual((new List<string>(new string[]{(string)"B", (string)"D"}))));
    }

}
