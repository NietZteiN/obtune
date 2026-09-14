using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string name) {
        if (name.ToLower() == name) {
            name = name.ToUpper();
        }
        else {
            name = name.ToLower();
        }
        return name;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Pinneaple")).Equals(("pinneaple")));
    }

}
