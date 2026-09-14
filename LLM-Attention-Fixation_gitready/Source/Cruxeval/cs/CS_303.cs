using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int i = (text.Length + 1) / 2;
        var result = text.ToCharArray();
        while (i < text.Length)
        {
            char t = char.ToLower(result[i]);
            if (t == result[i])
            {
                i += 1;
            }
            else
            {
                result[i] = t;
            }
            i += 2;
        }
        return new string(result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("mJkLbn")).Equals(("mJklbn")));
    }

}
