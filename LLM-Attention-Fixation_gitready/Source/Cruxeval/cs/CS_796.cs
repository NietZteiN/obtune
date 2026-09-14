using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str, string toget) {
        if (str.StartsWith(toget)) {
            return str.Substring(toget.Length);
        } else {
            return str;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("fnuiyh"), ("ni")).Equals(("fnuiyh")));
    }

}
