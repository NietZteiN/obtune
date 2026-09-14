using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string result = "";
        int i = text.Length - 1;
        while (i >= 0)
        {
            char c = text[i];
            if (char.IsLetter(c))
            {
                result += c;
            }
            i--;
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("102x0zoq")).Equals(("qozx")));
    }

}
