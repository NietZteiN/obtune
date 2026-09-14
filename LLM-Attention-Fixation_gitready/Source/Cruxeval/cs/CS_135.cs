using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F() {
        var d = new Dictionary<string, List<Tuple<string, string>>>()
        {
            { "Russia", new List<Tuple<string, string>>() { Tuple.Create("Moscow", "Russia"), Tuple.Create("Vladivostok", "Russia") } },
            { "Kazakhstan", new List<Tuple<string, string>>() { Tuple.Create("Astana", "Kazakhstan") } },
        };
        return d.Keys.ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F().SequenceEqual((new List<string>(new string[]{(string)"Russia", (string)"Kazakhstan"}))));
    }

}
