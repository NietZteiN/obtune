using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string title) {
        return title.ToLower();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("   Rock   Paper   SCISSORS  ")).Equals(("   rock   paper   scissors  ")));
    }

}
