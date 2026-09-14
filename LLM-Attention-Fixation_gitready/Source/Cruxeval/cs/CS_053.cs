using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(string text) {
        Dictionary<string, long> occ = new Dictionary<string, long>();
        foreach (var ch in text)
        {
            Dictionary<string, string> name = new Dictionary<string, string>(){
                {"a", "b"}, {"b", "c"}, {"c", "d"}, {"d", "e"}, {"e", "f"}
            };
            name.TryGetValue(ch.ToString(), out string value);
            value = value ?? ch.ToString();
            if (occ.ContainsKey(value))
            {
                occ[value] = occ[value] + 1;
            }
            else
            {
                occ.Add(value, 1);
            }

        }
        return occ.Values.ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("URW rNB")).SequenceEqual((new List<long>(new long[]{(long)1L, (long)1L, (long)1L, (long)1L, (long)1L, (long)1L, (long)1L}))));
    }

}
