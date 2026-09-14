using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        char[] r = new char[s.Length];
        int index = 0;
        for (int i = s.Length - 1; i >= 0; i--) {
            r[index] = s[i];
            index++;
        }
        return new string(r);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("crew")).Equals(("werc")));
    }

}
