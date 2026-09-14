using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<string> array) {
        string s = " ";
        s += string.Join("", array);
        return s;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)" ", (string)"  ", (string)"    ", (string)"   "}))).Equals(("           ")));
    }

}
