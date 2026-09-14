using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string name) {
        return string.Join("*", name.Split(' '));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Fred Smith")).Equals(("Fred*Smith")));
    }

}
