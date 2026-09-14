using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string from_c, string to_c) {
        var table = new Dictionary<int, int>();
        for (int i = 0; i < from_c.Length; i++) {
            table.Add(from_c[i], to_c[i]);
        }

        var sb = new StringBuilder(s.Length);
        foreach (var c in s) {
            if (table.ContainsKey(c)) {
                sb.Append((char)table[c]);
            } else {
                sb.Append(c);
            }
        }

        return sb.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("aphid"), ("i"), ("?")).Equals(("aph?d")));
    }

}
