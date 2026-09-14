using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        var d = s.LastIndexOf("ar");
        return $"{s.Substring(0, d)} ar {s.Substring(d + 2)}";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("xxxarmmarxx")).Equals(("xxxarmm ar xx")));
    }

}
