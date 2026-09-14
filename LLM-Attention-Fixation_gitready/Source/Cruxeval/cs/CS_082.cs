using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string a, string b, string c, string d) {
        return a != "" ? b : (c != "" ? d : "");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("CJU"), ("BFS"), ("WBYDZPVES"), ("Y")).Equals(("BFS")));
    }

}
