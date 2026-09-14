using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string n) {
        if (n.Contains('.'))
        {
            return (int.Parse(n) + 2.5).ToString();
        }
        return n;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("800")).Equals(("800")));
    }

}
