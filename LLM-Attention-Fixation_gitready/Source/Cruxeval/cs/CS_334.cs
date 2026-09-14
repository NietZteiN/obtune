using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string a, List<string> b) {
        return string.Join(a, b);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("00"), (new List<string>(new string[]{(string)"nU", (string)" 9 rCSAz", (string)"w", (string)" lpA5BO", (string)"sizL", (string)"i7rlVr"}))).Equals(("nU00 9 rCSAz00w00 lpA5BO00sizL00i7rlVr")));
    }

}
