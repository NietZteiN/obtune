using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str, string prefix) {
        if (str.StartsWith(prefix)) {
            return str.Substring(prefix.Length);
        }
        return str;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Vipra"), ("via")).Equals(("Vipra")));
    }

}
