using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<string> l, string c) {
        return string.Join(c, l);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"many", (string)"letters", (string)"asvsz", (string)"hello", (string)"man"})), ("")).Equals(("manylettersasvszhelloman")));
    }

}
