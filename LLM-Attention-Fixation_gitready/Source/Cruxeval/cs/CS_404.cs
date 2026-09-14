using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<string> no) {
        Dictionary<string, bool> d = new Dictionary<string, bool>();
        foreach (var item in no)
        {
            d[item] = false;
        }
        return d.Keys.Count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"l", (string)"f", (string)"h", (string)"g", (string)"s", (string)"b"}))) == (6L));
    }

}
