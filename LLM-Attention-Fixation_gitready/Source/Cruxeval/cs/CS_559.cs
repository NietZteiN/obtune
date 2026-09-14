using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string n) {
        n = n.ToString();
        return n[0] + "." + n.Substring(1).Replace("-", "_");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("first-second-third")).Equals(("f.irst_second_third")));
    }

}
