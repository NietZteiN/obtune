using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(long num, string name) {
        string f_str = "quiz leader = {1}, count = {0}";
        return string.Format(f_str, num, name);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((23L), ("Cornareti")).Equals(("quiz leader = Cornareti, count = 23")));
    }

}
