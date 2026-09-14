using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string s) {
        char[] l = s.ToLower().ToCharArray();
        foreach (char c in l)
        {
            if (!char.IsDigit(c))
            {
                return false;
            }
        }
        return true;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("")) == (true));
    }

}
