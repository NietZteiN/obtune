using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string num, long l) {
        string t = "";
        while (l > num.Length) {
            t += '0';
            l--;
        }
        return t + num;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("1"), (3L)).Equals(("001")));
    }

}
