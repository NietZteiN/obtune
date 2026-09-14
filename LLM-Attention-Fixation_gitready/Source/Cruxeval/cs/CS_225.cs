using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        foreach(char c in text)
        {
            if (!Char.IsLower(c))
            {
                return false;
            }
        }
        return true;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("54882")) == (false));
    }

}
