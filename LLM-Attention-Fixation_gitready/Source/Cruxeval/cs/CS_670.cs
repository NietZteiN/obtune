using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<string> a, List<long> b) {
        var d = a.Zip(b, (key, value) => new { key, value })
            .ToDictionary(x => x.key, x => x.value);
        a.Sort((x, y) => d[y].CompareTo(d[x]));
        return a.Select(x => d[x]).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"12", (string)"ab"})), (new List<long>(new long[]{(long)2L, (long)2L}))).SequenceEqual((new List<long>(new long[]{(long)2L, (long)2L}))));
    }

}
