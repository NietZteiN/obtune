using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string x) {
        if (x.ToLower() == x)
        {
            return x;
        }
        else
        {
            char[] charArray = x.ToCharArray();
            Array.Reverse(charArray);
            return new string(charArray);
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ykdfhp")).Equals(("ykdfhp")));
    }

}
