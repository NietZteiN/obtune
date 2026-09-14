using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        return string.Join(" ", text.Split().Select(str => str.TrimStart()));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("pvtso")).Equals(("pvtso")));
    }

}
