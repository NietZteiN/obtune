using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string s) {
        Dictionary<string, int> d = s.ToCharArray().Distinct().ToDictionary(c => c.ToString(), c => 0);
        return d.Keys.ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("12ab23xy")).SequenceEqual((new List<string>(new string[]{(string)"1", (string)"2", (string)"a", (string)"b", (string)"3", (string)"x", (string)"y"}))));
    }

}
