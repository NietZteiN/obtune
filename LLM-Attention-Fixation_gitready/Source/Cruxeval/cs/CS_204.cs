using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string name) {
        return new List<string> {name[0].ToString(), name[1].ToString()};
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("master. ")).SequenceEqual((new List<string>(new string[]{(string)"m", (string)"a"}))));
    }

}
