using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(Dictionary<long,string> a, long b, string c, string d, float e) {
        string key = d;
        string num = string.Empty;

        if (a.ContainsKey(key[0]))
        {
            num = a[key[0]];
            a.Remove(key[0]);
        }
        if (b > 3)
        {
            return string.Join("", c);
        }
        else
        {
            return num;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<long,string>(){{7L, "ii5p"}, {1L, "o3Jwus"}, {3L, "lot9L"}, {2L, "04g"}, {9L, "Wjf"}, {8L, "5b"}, {0L, "te6"}, {5L, "flLO"}, {6L, "jq"}, {4L, "vfa0tW"}}), (4L), ("Wy"), ("Wy"), (1.0f)).Equals(("Wy")));
    }

}
