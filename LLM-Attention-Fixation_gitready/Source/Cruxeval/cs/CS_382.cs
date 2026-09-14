using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(Dictionary<long,string> a) {
        var s = new Dictionary<long, string>(a.Reverse());
        return string.Join(" ", s.Select(i => $"({i.Key}, '{i.Value}')"));
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<long,string>(){{15L, "Qltuf"}, {12L, "Rwrepny"}})).Equals(("(12, 'Rwrepny') (15, 'Qltuf')")));
    }

}
