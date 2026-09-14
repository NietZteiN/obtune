using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        string result = s.Substring(3) + s[2] + s.Substring(5);
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("jbucwc")).Equals(("cwcuc")));
    }

}
