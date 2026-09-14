using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        string[] endings = { ".", "!", "?" };
        foreach (string ending in endings)
        {
            if (text.EndsWith(ending))
            {
                return true;
            }
        }
        return false;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((". C.")) == (true));
    }

}
