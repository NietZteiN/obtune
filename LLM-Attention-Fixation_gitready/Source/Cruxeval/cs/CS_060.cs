using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string doc) {
        foreach (char x in doc) {
            if (char.IsLetter(x)) {
                return char.ToUpper(x).ToString();
            }
        }
        return "-";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("raruwa")).Equals(("R")));
    }

}
