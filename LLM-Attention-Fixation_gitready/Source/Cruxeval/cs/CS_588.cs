using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<string> items, string target) {
        if (items.Contains(target)) {
            return items.IndexOf(target);
        }
        return -1;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"1", (string)"+", (string)"-", (string)"**", (string)"//", (string)"*", (string)"+"})), ("**")) == (3L));
    }

}
