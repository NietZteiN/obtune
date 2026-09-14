using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string use) {
        return text.Replace(use, "");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Chris requires a ride to the airport on Friday."), ("a")).Equals(("Chris requires  ride to the irport on Fridy.")));
    }

}
