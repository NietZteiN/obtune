using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string tokens) {
        var tokensArray = tokens.Split();
        if (tokensArray.Length == 2)
        {
            Array.Reverse(tokensArray);
        }
        string result = $"{tokensArray[0].PadRight(5)} {tokensArray[1].PadRight(5)}";
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("gsd avdropj")).Equals(("avdropj gsd  ")));
    }

}
