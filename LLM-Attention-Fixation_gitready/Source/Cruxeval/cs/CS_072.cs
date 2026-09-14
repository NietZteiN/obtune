using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        foreach (char c in text)
        {
            if(!char.IsNumber(c))
            {
                return false;
            }
        }
        return !string.IsNullOrEmpty(text);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("99")) == (true));
    }

}
