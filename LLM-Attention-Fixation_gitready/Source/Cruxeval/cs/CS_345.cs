using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<string, string> F(string a, string b) {
        if (string.Compare(a, b) < 0)
        {
            return Tuple.Create(b, a);
        }
        return Tuple.Create(a, b);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ml"), ("mv")).Equals((Tuple.Create("mv", "ml"))));
    }

}
