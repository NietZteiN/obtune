using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str) {
        if (!str.StartsWith("Nuva"))
        {
            return "no";
        }
        else
        {
            return str.TrimEnd();
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Nuva?dlfuyjys")).Equals(("Nuva?dlfuyjys")));
    }

}
