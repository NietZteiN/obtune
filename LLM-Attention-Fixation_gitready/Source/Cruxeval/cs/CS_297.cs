using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(long num) {
        if (0 < num && num < 1000 && num != 6174) {
            return "Half Life";
        }
        return "Not found";
    }
    public static void Main(string[] args) {
    Debug.Assert(F((6173L)).Equals(("Not found")));
    }

}
