using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        var ls = text.ToCharArray();
        ls[0] = Char.ToUpper(ls[ls.Length - 1]);
        ls[ls.Length - 1] = Char.ToUpper(ls[0]);
        return new string(ls).Substring(1).Equals(new string(ls).Substring(1).ToUpper());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Josh")) == (false));
    }

}
