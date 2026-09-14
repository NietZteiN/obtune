using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string challenge) {
        return challenge.ToLower().Replace('l', ',');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("czywZ")).Equals(("czywz")));
    }

}
